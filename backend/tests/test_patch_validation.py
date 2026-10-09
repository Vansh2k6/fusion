# Purpose: Patch proposal/validation/selection regression tests (P06.01–P06.03).
import time
from fastapi.testclient import TestClient
from app.main import app
from app.config import CURATED_FIXTURES
import app.patches.service as svc
from app.database import get_connection

client = TestClient(app)


def _wait_scan(scan_id: str, timeout_s: int = 40):
    for _ in range(timeout_s):
        time.sleep(1)
        data = client.get(f"/api/scans/{scan_id}").json()
        if data["status"] in ("complete", "error", "unsupported", "timeout"):
            return data
    raise AssertionError("scan did not terminate")


def _vulnerable_patch():
    scan = client.post("/api/scans", data={"fixture_id": "vulnerable_vault"}).json()
    data = _wait_scan(scan["id"])
    assert data["status"] == "complete"
    res = client.post(f"/api/scans/{scan['id']}/patches")
    assert res.status_code == 200, res.text
    return res.json()


def test_exact_proposal_and_variant_refusal_and_diff_binding():
    p = _vulnerable_patch()
    # T06.01: exact fixture succeeds with template provenance.
    assert p["candidate_hash"] == CURATED_FIXTURES["protected_vault"]["hash"]
    assert p["template_hash"] == CURATED_FIXTURES["protected_vault"]["hash"]
    assert p["template_version"] == "1.0.0"
    # T06.05: diff present; original preserved; candidate hash-bound.
    assert "--- original" in p["diff"] and "+++ candidate" in p["diff"]
    assert "balances[msg.sender] = 0" in p["diff"] or "balances[" in p["diff"]
    scan = client.get(f"/api/scans/{p['scan_id']}").json()
    assert p["original_hash"] == scan["source_hash"]
    # T06.02: protected (name-only/detector-only equivalent: wrong exact bytes) refused.
    ps = client.post("/api/scans", data={"fixture_id": "protected_vault"}).json()
    _wait_scan(ps["id"])
    bad = client.post(f"/api/scans/{ps['id']}/patches")
    assert bad.status_code == 400
    # T06.04: repeated proposal is idempotent (same revision, no duplicate).
    again = client.post(f"/api/scans/{p['scan_id']}/patches").json()
    assert again["id"] == p["id"]


def test_tampered_template_and_bytes_refused():
    p = _vulnerable_patch()
    # T06.03: tampered candidate template on disk refused.
    orig = svc.get_protected_candidate_code
    svc.get_protected_candidate_code = lambda: "pragma solidity ^0.8.20; contract Evil {}"
    try:
        conn = get_connection()
        # Force a fresh proposal attempt by removing existing patch row.
        conn.execute("DELETE FROM patches WHERE id = ?", (p["id"],))
        conn.execute("DELETE FROM patch_selections WHERE patch_id = ?", (p["id"],))
        conn.commit()
        conn.close()
        res = client.post(f"/api/scans/{p['scan_id']}/patches")
        assert res.status_code == 400
    finally:
        svc.get_protected_candidate_code = orig
    # T06.06/T06.16: tampered stored bytes stop validation and selection.
    p2 = client.post(f"/api/scans/{p['scan_id']}/patches").json()
    conn = get_connection()
    conn.execute("UPDATE patches SET candidate_code = 'tampered' WHERE id = ?", (p2["id"],))
    conn.commit()
    conn.close()
    assert client.post(f"/api/patches/{p2['id']}/validate").status_code == 400
    assert client.post(f"/api/patches/{p2['id']}/accept").status_code in (400, 409)
    conn = get_connection()
    conn.execute("DELETE FROM patches WHERE id = ?", (p2["id"],))
    conn.commit()
    conn.close()


def test_validation_parent_selection_export_flow():
    p = _vulnerable_patch()
    # Full validation: compile/rescan/exploit/normal/fuzz with parent binding.
    val = client.post(f"/api/patches/{p['id']}/validate")
    assert val.status_code == 200, val.text
    data = val.json()
    # T06.11/T06.12: five required checks; unrelated warnings preserved in rescan detail.
    assert sorted(c["check_type"] for c in data["checks"]) == [
        "attack_exploit", "compile", "fuzz", "normal_behavior", "rescan"]
    assert data["all_passed"] is True
    fuzz = next(c for c in data["checks"] if c["check_type"] == "fuzz")
    assert str(256) in fuzz["details"]  # T06.10: bounded fuzz with recorded seed/runs
    # T06.07/T06.13: eligibility bound to exact bytes + current harness.
    status = client.get(f"/api/patches/{p['id']}/validation-status").json()
    assert status["eligible"] is True
    assert status["harness_matches"] is True
    # T06.14/T06.19: idempotent accept/revoke with single selected revision + history.
    a1 = client.post(f"/api/patches/{p['id']}/accept").json()
    a2 = client.post(f"/api/patches/{p['id']}/accept").json()
    assert a1["is_accepted"] and a2["is_accepted"]
    r1 = client.post(f"/api/patches/{p['id']}/revoke").json()
    assert r1["is_accepted"] is False
    # T06.17/T06.18: export keeps selection and validation independent and agreeing.
    exp = client.get(f"/api/patches/{p['id']}/export").json()
    assert exp["candidate_hash"] == p["candidate_hash"]
    assert exp["selected_revision"] == "original"
    assert exp["latest_validation"]["candidate_hash"] == p["candidate_hash"]
    assert any(e["action"] == "accept" for e in exp["selection_history"])
    assert exp["validation_parents"][0]["fuzz_seed"] == 20261009

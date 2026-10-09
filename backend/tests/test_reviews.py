# Purpose: Review workflow regression tests (P05.02, T05.08–T05.12).
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_review_persists_and_stale_write_conflicts():
    scan = client.post("/api/scans", data={"fixture_id": "vulnerable_vault"}).json()
    scan_id = scan["id"]
    key = "reentrancy-eth_0"
    created = client.put(
        f"/api/scans/{scan_id}/reviews/{key}",
        json={"state": "triaged", "reason": "looking", "version": 0},
    )
    assert created.status_code == 200
    assert created.json()["version"] == 1
    stale = client.put(
        f"/api/scans/{scan_id}/reviews/{key}",
        json={"state": "resolved", "reason": "x", "version": 0},
    )
    assert stale.status_code == 409  # concurrent stale edits conflict, never silent overwrite
    ok = client.put(
        f"/api/scans/{scan_id}/reviews/{key}",
        json={"state": "in_progress", "reason": "investigating", "version": 1},
    )
    assert ok.json()["version"] == 2
    listed = client.get(f"/api/scans/{scan_id}/reviews").json()
    assert any(r["finding_key"] == key and r["state"] == "in_progress" for r in listed)


def test_resolved_requires_reason():
    scan = client.post("/api/scans", data={"fixture_id": "protected_vault"}).json()
    res = client.put(
        f"/api/scans/{scan['id']}/reviews/some-key",
        json={"state": "resolved", "reason": "", "version": 0},
    )
    assert res.status_code == 400

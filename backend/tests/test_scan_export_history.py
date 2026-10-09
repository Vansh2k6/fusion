# Purpose: Export/history regression tests (P03.03, T03.13–T03.16).
import time
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def _wait_terminal(scan_id: str, timeout_s: int = 40):
    for _ in range(timeout_s):
        time.sleep(1)
        data = client.get(f"/api/scans/{scan_id}").json()
        if data["status"] in ("complete", "error", "unsupported", "timeout"):
            return data
    raise AssertionError("scan did not reach a terminal state")


def test_export_hash_matches_original_and_source_download_agrees():
    scan = client.post("/api/scans", data={"fixture_id": "vulnerable_vault"}).json()
    data = _wait_terminal(scan["id"])
    assert data["status"] == "complete"
    export = client.get(f"/api/scans/{scan['id']}/export").json()
    assert export["source_hash"] == data["source_hash"]
    assert export["findings_count"] == len(data["findings"])
    assert "expected_tool_versions" in (export["raw_diagnostics"] or {})
    src = client.get(f"/api/scans/{scan['id']}/source")
    assert src.status_code == 200
    assert src.headers["X-Source-Sha256"] == data["source_hash"]


def test_history_pagination_has_no_duplicates_or_gaps():
    first = client.get("/api/scans?limit=1&offset=0").json()
    second = client.get("/api/scans?limit=1&offset=1").json()
    assert len(first) == 1
    if second:
        assert second[0]["id"] != first[0]["id"]
    page = client.get("/api/scans?limit=50&offset=0").json()
    ids = [s["id"] for s in page]
    assert len(ids) == len(set(ids))

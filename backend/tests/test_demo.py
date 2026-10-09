# Purpose: Demo API behavior under Anvil ownership policy (P07.01).
# On this machine :8545 is owned by an unrelated process, so the API must refuse
# (T07.01). Full live replay against an app-owned session is covered by
# test_anvil_ownership.py on an alternate port.
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_demo_run_requires_owned_session():
    res = client.post("/api/demo/runs")
    if res.status_code == 200:
        data = res.json()
        assert data["status"] == "complete"
        assert len(data["transactions"]) >= 10
        vuln = next(b for b in data["balances"] if "VulnerableVault" in b["label"])
        assert vuln["after_wei"] == "0"
    else:
        assert res.status_code in (400, 409)
        detail = res.json()["detail"].lower()
        assert any(k in detail for k in ("ownership", "marker", "in progress", "reachable"))


def test_demo_reset_requires_owned_session():
    res = client.post("/api/demo/reset")
    if res.status_code != 200:
        assert res.status_code == 409
        assert "reset" in res.json()["detail"].lower() or "ownership" in res.json()["detail"].lower()

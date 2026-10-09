# Purpose: Automated integration test suite validating M1 and M2 requirements.
import pytest
import time
from fastapi.testclient import TestClient
from app.main import app
from app.config import CURATED_FIXTURES

client = TestClient(app)

def test_health_check():
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "tool_versions" in data

def test_list_fixtures():
    response = client.get("/api/fixtures")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 3
    fixture_ids = [f["id"] for f in data]
    assert "vulnerable_vault" in fixture_ids
    assert "protected_vault" in fixture_ids
    assert "malformed_vault" in fixture_ids

def test_arbitrary_source_is_disabled_without_isolation():
    response = client.post(
        "/api/scans",
        data={
            "filename": "Unknown.sol",
            "source_code": "pragma solidity ^0.8.20; contract Unknown {}",
        },
    )
    assert response.status_code == 503
    assert "isolated analysis worker" in response.json()["detail"]

def test_scan_vulnerable_vault():
    response = client.post("/api/scans", data={"fixture_id": "vulnerable_vault"})
    assert response.status_code == 200
    scan = response.json()
    scan_id = scan["id"]
    assert scan["source_hash"] == CURATED_FIXTURES["vulnerable_vault"]["hash"]

    # Poll until completed
    for _ in range(30):
        time.sleep(1)
        res = client.get(f"/api/scans/{scan_id}")
        data = res.json()
        if data["status"] in ["complete", "error", "unsupported", "timeout"]:
            break

    assert data["status"] == "complete"
    detector_ids = [f["detector_id"] for f in data["findings"]]
    assert "reentrancy-eth" in detector_ids

    # Find the reentrancy finding
    reentrancy = next(f for f in data["findings"] if f["detector_id"] == "reentrancy-eth")
    assert reentrancy["impact"] == "High"
    assert reentrancy["confidence"] in ["Medium", "High"]
    assert reentrancy["start_line"] in [18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28]
    assert "Checks-Effects-Interactions" in reentrancy["recommendation"]

    # Test export
    export_res = client.get(f"/api/scans/{scan_id}/export")
    assert export_res.status_code == 200
    export_data = export_res.json()
    assert export_data["source_hash"] == scan["source_hash"]
    assert export_data["findings_count"] > 0
    assert "solc" in export_data["tool_versions"]

    # Test patch proposal (M2)
    patch_res = client.post(f"/api/scans/{scan_id}/patches")
    assert patch_res.status_code == 200
    patch_data = patch_res.json()
    patch_id = patch_data["id"]
    assert patch_data["candidate_hash"] == CURATED_FIXTURES["protected_vault"]["hash"]
    assert "--- original" in patch_data["diff"]
    assert "+++ candidate" in patch_data["diff"]
    assert patch_data["is_accepted"] is False

    # Test patch validation (M2)
    val_res = client.post(f"/api/patches/{patch_id}/validate")
    assert val_res.status_code == 200
    val_data = val_res.json()
    assert val_data["all_passed"] is True
    check_types = [c["check_type"] for c in val_data["checks"]]
    assert "compile" in check_types
    assert "rescan" in check_types
    assert "attack_exploit" in check_types
    assert "normal_behavior" in check_types

    # Test accept
    accept_res = client.post(f"/api/patches/{patch_id}/accept")
    assert accept_res.status_code == 200
    assert accept_res.json()["is_accepted"] is True

    # Test revoke
    revoke_res = client.post(f"/api/patches/{patch_id}/revoke")
    assert revoke_res.status_code == 200
    assert revoke_res.json()["is_accepted"] is False

    # Test re-accept (repeatability)
    reaccept_res = client.post(f"/api/patches/{patch_id}/accept")
    assert reaccept_res.status_code == 200
    assert reaccept_res.json()["is_accepted"] is True

def test_scan_protected_vault():
    response = client.post("/api/scans", data={"fixture_id": "protected_vault"})
    assert response.status_code == 200
    scan = response.json()
    scan_id = scan["id"]

    for _ in range(30):
        time.sleep(1)
        res = client.get(f"/api/scans/{scan_id}")
        data = res.json()
        if data["status"] in ["complete", "error", "unsupported", "timeout"]:
            break

    assert data["status"] == "complete"
    detector_ids = [f["detector_id"] for f in data["findings"]]
    # Reentrancy-eth must be ABSENT
    assert "reentrancy-eth" not in detector_ids
    # Informational or version findings remain visible
    assert len(data["findings"]) >= 1

def test_scan_malformed_vault():
    response = client.post("/api/scans", data={"fixture_id": "malformed_vault"})
    assert response.status_code == 200
    scan = response.json()
    scan_id = scan["id"]

    for _ in range(30):
        time.sleep(1)
        res = client.get(f"/api/scans/{scan_id}")
        data = res.json()
        if data["status"] in ["complete", "error", "unsupported", "timeout"]:
            break

    # Must be error status, NEVER complete or clean
    assert data["status"] == "error"
    assert "Compilation failed" in data["error_message"] or "Expected" in data["error_message"]
    assert len(data["findings"]) == 0

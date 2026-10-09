# Purpose: Regression tests for bounded ingestion (P01.01) and failure surfacing (P00.03).
import io
import pytest
from fastapi.testclient import TestClient

import app.config as config
import app.database as database
import app.storage as storage
from app.main import app


@pytest.fixture()
def isolated_client(tmp_path, monkeypatch):
    """Point DB and artifact roots at a temp dir so tests never touch user data (T00.10)."""
    data_dir = tmp_path / "data"
    (data_dir / "scans").mkdir(parents=True)
    monkeypatch.setattr(config, "DATA_DIR", data_dir)
    monkeypatch.setattr(config, "DB_PATH", data_dir / "test.db")
    monkeypatch.setattr(database, "DB_PATH", data_dir / "test.db")
    monkeypatch.setattr(storage, "DATA_DIR", data_dir)
    database.init_db()
    return TestClient(app)


def test_exactly_one_input_method_required(isolated_client):
    res = isolated_client.post(
        "/api/scans",
        data={"fixture_id": "vulnerable_vault", "source_code": "pragma solidity ^0.8.20; contract X {}"},
    )
    assert res.status_code == 400
    assert "exactly one" in res.json()["detail"]


def test_oversized_upload_refused_during_read(isolated_client):
    big = b"a" * (config.MAX_UPLOAD_SIZE + 1)
    res = isolated_client.post(
        "/api/scans",
        files={"file": ("big.sol", io.BytesIO(big), "text/plain")},
    )
    assert res.status_code in (400, 413)


def test_invalid_utf8_refused(isolated_client):
    res = isolated_client.post(
        "/api/scans",
        files={"file": ("bad.sol", io.BytesIO(b"\xff\xfe\x00invalid"), "text/plain")},
    )
    assert res.status_code == 400


def test_injected_tool_failure_surfaces_error(isolated_client, monkeypatch):
    import app.analysis.runner as runner
    monkeypatch.setattr(runner, "SLITHER_BIN", "definitely_missing_slither_binary_xyz")
    res = isolated_client.post("/api/scans", data={"fixture_id": "malformed_vault"})
    assert res.status_code == 200
    scan_id = res.json()["id"]
    import time
    for _ in range(20):
        time.sleep(1)
        data = isolated_client.get(f"/api/scans/{scan_id}").json()
        if data["status"] in ("complete", "error", "unsupported", "timeout"):
            break
    assert data["status"] == "error"  # missing tool is failure, never a clean scan

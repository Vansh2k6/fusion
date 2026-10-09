# Purpose: Fail-closed arbitrary-execution gate tests (P02.02/P02.03, T02.16).
import app.worker as worker


def test_spoofed_flag_without_worker_image_still_refuses(monkeypatch):
    monkeypatch.setattr(worker, "ARBITRARY_SCAN_ISOLATION_ENABLED", True)
    monkeypatch.setattr(worker, "_self_check_cache", None)
    ok, reason = worker.arbitrary_scan_allowed("00" * 32)
    assert ok is False
    assert reason  # explains why, not a silent refusal


def test_curated_bytes_allowed_without_worker():
    from app.config import CURATED_FIXTURES
    h = next(iter(CURATED_FIXTURES.values()))["hash"]
    ok, _ = worker.arbitrary_scan_allowed(h)
    assert ok is True

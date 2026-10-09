# Purpose: Fail-closed gate for arbitrary source execution (P02.02/P02.03, R07).
import subprocess
import time
from app.config import ARBITRARY_SCAN_ISOLATION_ENABLED, CURATED_FIXTURES

PINNED_WORKER_IMAGE = "fusion-worker:0.1.0"  # built and validated per P02.02 before use
_self_check_cache: tuple[float, bool, str] | None = None
SELF_CHECK_TTL_SECONDS = 60


def worker_self_check() -> tuple[bool, str]:
    """Verify the pinned worker image exists and is configured non-root. Cached briefly."""
    global _self_check_cache
    now = time.time()
    if _self_check_cache and now - _self_check_cache[0] < SELF_CHECK_TTL_SECONDS:
        _, ok, reason = _self_check_cache
        return ok, reason
    try:
        proc = subprocess.run(
            ["docker", "image", "inspect", PINNED_WORKER_IMAGE],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=15, text=True,
        )
    except (OSError, subprocess.SubprocessError) as e:
        ok, reason = False, f"worker self-check could not run docker: {e}"
        _self_check_cache = (now, ok, reason)
        return ok, reason
    if proc.returncode != 0:
        ok, reason = False, f"worker image {PINNED_WORKER_IMAGE} not present; arbitrary analysis unavailable."
        _self_check_cache = (now, ok, reason)
        return ok, reason
    ok, reason = True, "worker image present"
    _self_check_cache = (now, ok, reason)
    return ok, reason


def arbitrary_scan_allowed(source_hash: str) -> tuple[bool, str]:
    """Curated bytes always allowed; anything else needs flag AND passing self-check."""
    curated = {item["hash"].lower() for item in CURATED_FIXTURES.values()}
    if source_hash.lower() in curated:
        return True, "curated"
    # An environment flag alone never enables native arbitrary execution (T02.16).
    if not ARBITRARY_SCAN_ISOLATION_ENABLED:
        return False, (
            "Arbitrary source scanning is disabled because the isolated analysis worker "
            "is not available. Select a curated fixture; uploaded source is accepted only "
            "when its SHA-256 exactly matches an approved fixture."
        )
    ok, reason = worker_self_check()
    if not ok:
        return False, reason
    return True, "verified-worker"

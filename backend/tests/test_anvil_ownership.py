# Purpose: Anvil ownership, session safety, and real-transaction evidence (P07.01–P07.02).
import os
import subprocess
import time

import pytest
import psutil

import app.monitoring.observer as obs
from app.monitoring.observer import _tx_fee_wei


class _FakeConn:
    def __init__(self, pid):
        self.pid = pid
        self.status = "LISTEN"
        self.laddr = type("A", (), {"port": 8545})()


def _patch_process(monkeypatch, pid, exe, create_time):
    class P:
        def __init__(self, p):
            assert p == pid
        def exe(self):
            return exe
        def create_time(self):
            return create_time
    monkeypatch.setattr(psutil, "Process", P)


def test_foreign_listener_on_8545_is_refused(monkeypatch, tmp_path):
    monkeypatch.setattr(obs, "_anvil_proc", None)
    (tmp_path / "m").write_text("1234:1111.0", encoding="ascii")
    monkeypatch.setattr(obs, "ANVIL_PID_PATH", tmp_path / "m")
    _patch_process(monkeypatch, 1234, str(obs.Path(obs.ANVIL_BIN).resolve()), 1111.0)
    monkeypatch.setattr(psutil, "net_connections",
                        lambda kind: [_FakeConn(9999)])  # someone else owns 8545
    with pytest.raises(RuntimeError, match="not owned by the managed Anvil process"):
        obs._verify_anvil_ownership()


def test_stale_pid_reuse_and_wrong_exe_refused(monkeypatch, tmp_path):
    monkeypatch.setattr(obs, "_anvil_proc", None)
    marker = tmp_path / "m"
    monkeypatch.setattr(obs, "ANVIL_PID_PATH", marker)
    monkeypatch.setattr(psutil, "net_connections", lambda kind: [_FakeConn(1234)])
    # Stale: same pid, different start time.
    marker.write_text("1234:1111.0", encoding="ascii")
    _patch_process(monkeypatch, 1234, str(obs.Path(obs.ANVIL_BIN).resolve()), 9999.0)
    with pytest.raises(RuntimeError, match="stale"):
        obs._verify_anvil_ownership()
    # Wrong executable.
    marker.write_text("1234:9999.0", encoding="ascii")
    _patch_process(monkeypatch, 1234, "/bin/something-else", 9999.0)
    with pytest.raises(RuntimeError, match="unexpected executable"):
        obs._verify_anvil_ownership()
    # Invalid marker.
    marker.write_text("not-a-marker", encoding="ascii")
    with pytest.raises(RuntimeError, match="invalid"):
        obs._verify_anvil_ownership()


def test_reset_refuses_to_interleave_with_running_demo():
    assert obs._demo_lock.acquire(blocking=False)
    try:
        with pytest.raises(RuntimeError, match="in progress"):
            obs.reset_local_chain()
    finally:
        obs._demo_lock.release()


def test_fee_helper_reports_actual_or_unavailable():
    class R:
        gasUsed = 21000
        def get(self, k, default=None):
            return {"effectiveGasPrice": 1000000000}.get(k, default)
    assert _tx_fee_wei(R()) == str(21000 * 1000000000)
    class NoPrice:
        gasUsed = 21000
        def get(self, k, default=None):
            return default
    assert _tx_fee_wei(NoPrice()) == "unavailable"


def test_tampered_protected_artifact_refuses_demo_build(monkeypatch):
    from app.config import CONTRACTS_DIR
    real = (CONTRACTS_DIR / "src" / "ProtectedVault.sol").read_bytes()
    (CONTRACTS_DIR / "src" / "ProtectedVault.sol").write_bytes(real + b"\n// tamper")
    try:
        with pytest.raises(RuntimeError, match="approved curated revision"):
            obs._build_verified_demo_artifacts()
    finally:
        (CONTRACTS_DIR / "src" / "ProtectedVault.sol").write_bytes(real)


LIVE_PORT = 8546
LIVE_RPC = f"http://127.0.0.1:{LIVE_PORT}"


@pytest.fixture(scope="module")
def owned_anvil():
    """App-owned Anvil on an alternate loopback port; the user's :8545 is untouched."""
    from app.config import ANVIL_BIN
    try:
        proc = subprocess.Popen(
            [ANVIL_BIN, "--host", "127.0.0.1", "--port", str(LIVE_PORT),
             "--chain-id", "31337", "--silent"],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except OSError:
        pytest.skip("anvil binary unavailable")
    for _ in range(20):
        time.sleep(0.5)
        try:
            import urllib.request
            req = urllib.request.Request(
                LIVE_RPC, data=b'{"jsonrpc":"2.0","method":"web3_clientVersion","params":[],"id":1}',
                headers={"Content-Type": "application/json"})
            if b"anvil" in urllib.request.urlopen(req, timeout=5).read().lower():
                break
        except OSError:
            pass
    else:
        proc.terminate()
        pytest.skip("owned anvil did not start")
    marker_path = obs.ANVIL_PID_PATH
    saved = marker_path.read_bytes() if marker_path.exists() else None
    marker_path.write_text(
        f"{proc.pid}:{psutil.Process(proc.pid).create_time()}", encoding="ascii")
    old_url, old_port = obs.ANVIL_RPC_URL, obs.ANVIL_PORT
    obs.ANVIL_RPC_URL, obs.ANVIL_PORT = LIVE_RPC, LIVE_PORT
    assert obs._demo_lock.acquire(blocking=False)
    obs._demo_lock.release()
    yield proc
    obs.ANVIL_RPC_URL, obs.ANVIL_PORT = old_url, old_port
    if saved is not None:
        marker_path.write_bytes(saved)  # restore the user's marker untouched
    else:
        marker_path.unlink(missing_ok=True)
    proc.terminate()  # only the process this fixture started (T07.06)


def test_live_owned_replay_records_real_receipts_and_balances(owned_anvil):
    res, err = obs.run_attack_defense_demo()
    assert err is None, err
    assert res.status == "complete"
    assert len(res.transactions) >= 10
    vuln = next(b for b in res.balances if "VulnerableVault" in b.label)
    prot = next(b for b in res.balances if "ProtectedVault" in b.label)
    # T07.07: original loses victim funds; exact integers as decimal strings.
    assert vuln.after_wei == "0"
    assert vuln.before_wei.isdigit() and vuln.delta_wei.lstrip("-").isdigit()
    # T07.08: candidate preserves balance; normal use round-trips to zero accounting.
    assert prot.after_wei == prot.before_wei
    assert all(len(t.tx_hash) == 64 and all(c in "0123456789abcdef" for c in t.tx_hash)
               for t in res.transactions)  # stored raw hex; UI prefixes 0x for display
    assert all((t.fee_wei or "unavailable").replace("-", "").isdigit() or t.fee_wei == "unavailable"
               for t in res.transactions)
    blocked = next(t for t in res.transactions if "Blocked by CEI" in t.label)
    assert blocked.status == "reverted"  # T07.12: honest revert semantics
    assert res.alert is not None and res.alert.observation != res.alert.hypothesis
    # Reset marks evidence historical and forces redeploy (T07.05).
    out = obs.reset_local_chain()
    assert out["status"] == "reset"
    from app.database import get_connection
    conn = get_connection()
    try:
        row = conn.execute("SELECT is_historical FROM demo_runs WHERE id = ?",
                           (res.id,)).fetchone()
    finally:
        conn.close()
    assert row["is_historical"] == 1

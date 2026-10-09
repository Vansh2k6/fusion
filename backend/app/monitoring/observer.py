# Purpose: Manage local Anvil instance, orchestrate real attack/defense deployments, and observe receipts and balance deltas.
import subprocess
import time
import json
import uuid
import threading
import psutil
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
from web3 import Web3
from web3.exceptions import ContractCustomError, ContractLogicError
from app.config import (
    ANVIL_BIN, ANVIL_RPC_URL, ANVIL_CHAIN_ID, ANVIL_PID_PATH, ANVIL_PORT, CONTRACTS_DIR,
    CURATED_FIXTURES, FORGE_BIN, PINNED_VERSIONS, VALIDATION_TIMEOUT_SECONDS
)
from app.database import get_connection, now_iso
from app.schemas import TxReceipt, BalanceDelta, IncidentAlert, DemoRunResponse
from app.storage import compute_sha256

_anvil_proc: Optional[subprocess.Popen] = None
_demo_lock = threading.Lock()

def ensure_anvil_running() -> Web3:
    """Ensure local Anvil node is active and return Web3 instance."""
    global _anvil_proc
    w3 = Web3(Web3.HTTPProvider(ANVIL_RPC_URL, request_kwargs={"timeout": 10}))
    if w3.is_connected():
        _verify_anvil_ownership()
        _verify_anvil_identity(w3)
        return w3

    # Start Anvil subprocess on 127.0.0.1:8545
    cmd = [
        ANVIL_BIN,
        "--host", "127.0.0.1",
        "--port", "8545",
        "--chain-id", str(ANVIL_CHAIN_ID),
        "--silent"
    ]
    _anvil_proc = subprocess.Popen(
        cmd,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    ANVIL_PID_PATH.write_text(
        f"{_anvil_proc.pid}:{psutil.Process(_anvil_proc.pid).create_time()}", encoding="ascii")

    # Wait for node to be responsive (up to 8 seconds)
    for _ in range(16):
        time.sleep(0.5)
        if w3.is_connected():
            _verify_anvil_ownership()
            _verify_anvil_identity(w3)
            return w3

    raise RuntimeError("Failed to connect to local Anvil RPC instance.")

def _read_ownership_marker() -> tuple[int, float]:
    """Parse the pid:start-time marker; reject stale or PID-reused markers (T07.02)."""
    try:
        raw = ANVIL_PID_PATH.read_text(encoding="ascii").strip()
    except OSError as exc:
        raise RuntimeError(
            "Anvil is reachable but Fusion has no ownership marker. Stop it and restart with scripts/start.ps1."
        ) from exc
    try:
        pid_text, _, start_text = raw.partition(":")
        return int(pid_text), float(start_text)
    except ValueError as exc:
        raise RuntimeError("Fusion Anvil ownership marker is invalid.") from exc


def _verify_anvil_ownership() -> None:
    """Require the RPC process to be the Anvil executable launched for Fusion,
    started at the recorded time, and owning the 8545 listener."""
    if _anvil_proc is not None and _anvil_proc.poll() is None:
        pid = _anvil_proc.pid
        try:
            start_time = psutil.Process(pid).create_time()
        except (psutil.Error, OSError) as exc:
            raise RuntimeError("Fusion Anvil process vanished during verification.") from exc
    else:
        pid, start_time = _read_ownership_marker()

    try:
        process = psutil.Process(pid)
        expected = Path(ANVIL_BIN).resolve()
        actual = Path(process.exe()).resolve()
    except (psutil.Error, OSError) as exc:
        raise RuntimeError("Fusion Anvil ownership marker points to no running process.") from exc
    if actual != expected:
        raise RuntimeError(f"Fusion Anvil marker points to unexpected executable: {actual}")
    if abs(process.create_time() - start_time) > 1.0:
        raise RuntimeError(
            "Fusion Anvil marker is stale: PID was reused by a different process start.")

    # The recorded process must own the loopback listener, not merely share a chain id.
    try:
        listeners = [c for c in psutil.net_connections(kind="inet")
                     if c.status == "LISTEN" and c.laddr.port == ANVIL_PORT]
    except (psutil.Error, OSError) as exc:
        raise RuntimeError("Could not verify the Anvil listener ownership.") from exc
    if not any(c.pid == pid for c in listeners):
        raise RuntimeError(
            "Port 8545 is not owned by the managed Anvil process; refusing an unrelated service.")

def _verify_anvil_identity(w3: Web3) -> None:
    """Reject unrelated JSON-RPC services before using unlocked disposable accounts."""
    actual_chain_id = w3.eth.chain_id
    client_version = w3.client_version.lower()
    if actual_chain_id != ANVIL_CHAIN_ID:
        raise RuntimeError(
            f"Refusing RPC with chain id {actual_chain_id}; expected managed local chain {ANVIL_CHAIN_ID}."
        )
    if "anvil" not in client_version:
        raise RuntimeError(f"Refusing non-Anvil RPC client: {w3.client_version}")
    if len(w3.eth.accounts) < 4:
        raise RuntimeError("Managed Anvil RPC does not expose the required disposable demo accounts.")

def _wait_receipt(w3: Web3, tx_hash: Any):
    """Wait a bounded time for a receipt so local-node failures cannot hang the API."""
    return w3.eth.wait_for_transaction_receipt(tx_hash, timeout=20, poll_latency=0.2)


def _tx_fee_wei(receipt) -> str:
    """Actual fee paid for a transaction (gasUsed x effective price).

    Reverted transactions still pay fees (R11); a missing price is reported as
    unavailable, never invented."""
    try:
        price = receipt.get("effectiveGasPrice", None)
        if price is None:
            price = receipt.get("gasPrice", None)
        if price is None:
            return "unavailable"
        return str(int(receipt.gasUsed) * int(price))
    except (AttributeError, TypeError, ValueError):
        return "unavailable"

def reset_local_chain() -> Dict[str, Any]:
    """Reset Anvil node and mark all existing runs as historical.

    Serialized against demo runs so reset and execution cannot interleave (T07.03).
    A failed reset changes nothing and reports failure, never success (T07.04)."""
    if not _demo_lock.acquire(blocking=False):
        raise RuntimeError("A demo run is currently in progress; reset refused to avoid interleaving.")
    try:
        w3 = Web3(Web3.HTTPProvider(ANVIL_RPC_URL, request_kwargs={"timeout": 10}))
        if not w3.is_connected():
            raise RuntimeError("Managed Anvil RPC is not reachable; no state was changed.")
        _verify_anvil_ownership()
        _verify_anvil_identity(w3)
        reset_response = w3.provider.make_request("anvil_reset", [])
        if reset_response.get("error") or "result" not in reset_response:
            raise RuntimeError(f"Anvil reset was not confirmed: {reset_response}")

        conn = get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
            UPDATE demo_runs
            SET is_historical = 1, status = 'historical'
            WHERE is_historical = 0
            """)
            conn.commit()
        except Exception:
            conn.rollback()
            raise RuntimeError(
                "Chain reset succeeded but history persistence failed; new replay is blocked until reconciled.")
        finally:
            conn.close()

        return {"status": "reset", "message": "Local chain reset. Prior demo runs marked as historical."}
    finally:
        _demo_lock.release()

def load_artifact(contract_name: str) -> Tuple[List[Dict[str, Any]], str]:
    artifact_path = CONTRACTS_DIR / "out" / f"{contract_name}.sol" / f"{contract_name}.json"
    if not artifact_path.exists():
        raise FileNotFoundError(f"Artifact {contract_name}.json not found at {artifact_path}. Run forge build first.")
    data = json.loads(artifact_path.read_text(encoding="utf-8"))
    abi = data["abi"]
    bytecode = data["bytecode"]["object"]
    return abi, bytecode

def _build_verified_demo_artifacts() -> None:
    """Rebuild controlled artifacts after verifying the protected source is the approved revision."""
    protected_source = CONTRACTS_DIR / "src" / "ProtectedVault.sol"
    expected_hash = CURATED_FIXTURES["protected_vault"]["hash"]
    if compute_sha256(protected_source.read_bytes()) != expected_hash:
        raise RuntimeError("ProtectedVault source does not match the approved curated revision.")
    result = subprocess.run(
        [FORGE_BIN, "build", "--force"],
        cwd=str(CONTRACTS_DIR),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        timeout=VALIDATION_TIMEOUT_SECONDS,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    if result.returncode != 0:
        raise RuntimeError(f"Verified demo artifact build failed: {(result.stderr + result.stdout)[:800]}")

def run_attack_defense_demo() -> Tuple[Optional[DemoRunResponse], Optional[str]]:
    """Execute complete attack/defense scenario on local Anvil."""
    if not _demo_lock.acquire(blocking=False):
        return None, "A demo run is currently in progress. Duplicate execution prevented."

    try:
        w3 = ensure_anvil_running()
        _build_verified_demo_artifacts()
        accounts = w3.eth.accounts
        if len(accounts) < 4:
            return None, "Insufficient accounts available on local chain."

        deployer = accounts[0]
        victim = accounts[1]
        attacker = accounts[2]
        normal_user = accounts[3]

        transactions: List[TxReceipt] = []

        # Load ABIs and bytecode
        vuln_abi, vuln_bc = load_artifact("VulnerableVault")
        prot_abi, prot_bc = load_artifact("ProtectedVault")
        att_abi, att_bc = load_artifact("Attacker")

        # 1. Deploy VulnerableVault
        VulnContract = w3.eth.contract(abi=vuln_abi, bytecode=vuln_bc)
        tx_hash = VulnContract.constructor().transact({"from": deployer})
        receipt = _wait_receipt(w3, tx_hash)
        vuln_addr = receipt.contractAddress
        transactions.append(TxReceipt(
            label="Deploy VulnerableVault",
            tx_hash=tx_hash.hex(),
            from_address=deployer,
            to_address=vuln_addr,
            status="success" if receipt.status == 1 else "reverted",
            gas_used=str(receipt.gasUsed),
            fee_wei=_tx_fee_wei(receipt),
        ))

        # 2. Deploy ProtectedVault
        ProtContract = w3.eth.contract(abi=prot_abi, bytecode=prot_bc)
        tx_hash = ProtContract.constructor().transact({"from": deployer})
        receipt = _wait_receipt(w3, tx_hash)
        prot_addr = receipt.contractAddress
        transactions.append(TxReceipt(
            label="Deploy ProtectedVault (CEI Patched)",
            tx_hash=tx_hash.hex(),
            from_address=deployer,
            to_address=prot_addr,
            status="success" if receipt.status == 1 else "reverted",
            gas_used=str(receipt.gasUsed),
            fee_wei=_tx_fee_wei(receipt),
        ))

        # 3. Victim deposits 5 ETH in VulnerableVault
        vuln_inst = w3.eth.contract(address=vuln_addr, abi=vuln_abi)
        deposit_amount = w3.to_wei(5, "ether")
        tx_hash = vuln_inst.functions.deposit().transact({"from": victim, "value": deposit_amount})
        receipt = _wait_receipt(w3, tx_hash)
        transactions.append(TxReceipt(
            label="Victim deposit 5 ETH (VulnerableVault)",
            tx_hash=tx_hash.hex(),
            from_address=victim,
            to_address=vuln_addr,
            status="success" if receipt.status == 1 else "reverted",
            gas_used=str(receipt.gasUsed),
            fee_wei=_tx_fee_wei(receipt),
        ))

        # 4. Victim deposits 5 ETH in ProtectedVault
        prot_inst = w3.eth.contract(address=prot_addr, abi=prot_abi)
        tx_hash = prot_inst.functions.deposit().transact({"from": victim, "value": deposit_amount})
        receipt = _wait_receipt(w3, tx_hash)
        transactions.append(TxReceipt(
            label="Victim deposit 5 ETH (ProtectedVault)",
            tx_hash=tx_hash.hex(),
            from_address=victim,
            to_address=prot_addr,
            status="success" if receipt.status == 1 else "reverted",
            gas_used=str(receipt.gasUsed),
            fee_wei=_tx_fee_wei(receipt),
        ))

        # Capture balances before attacks
        vuln_bal_before = w3.eth.get_balance(vuln_addr)
        prot_bal_before = w3.eth.get_balance(prot_addr)
        attacker_bal_before = w3.eth.get_balance(attacker)
        normal_bal_before = w3.eth.get_balance(normal_user)

        # 5. Attacker deploys Attacker against VulnerableVault
        AttContract = w3.eth.contract(abi=att_abi, bytecode=att_bc)
        tx_hash = AttContract.constructor(vuln_addr).transact({"from": attacker})
        receipt = _wait_receipt(w3, tx_hash)
        att_vuln_addr = receipt.contractAddress
        transactions.append(TxReceipt(
            label="Deploy Attacker against VulnerableVault",
            tx_hash=tx_hash.hex(),
            from_address=attacker,
            to_address=att_vuln_addr,
            status="success" if receipt.status == 1 else "reverted",
            gas_used=str(receipt.gasUsed),
            fee_wei=_tx_fee_wei(receipt),
        ))

        # 6. Attacker calls attack with 1 ETH on VulnerableVault -> Drains vault
        att_vuln_inst = w3.eth.contract(address=att_vuln_addr, abi=att_abi)
        attack_amount = w3.to_wei(1, "ether")
        tx_hash = att_vuln_inst.functions.attack().transact({"from": attacker, "value": attack_amount, "gas": 3000000})
        receipt = _wait_receipt(w3, tx_hash)
        transactions.append(TxReceipt(
            label="Exploit execution on VulnerableVault (1 ETH deposit + reentrancy)",
            tx_hash=tx_hash.hex(),
            from_address=attacker,
            to_address=att_vuln_addr,
            status="success" if receipt.status == 1 else "reverted",
            gas_used=str(receipt.gasUsed),
            fee_wei=_tx_fee_wei(receipt),
        ))

        # Attacker withdraws stolen proceeds
        tx_hash = att_vuln_inst.functions.withdrawProceeds().transact({"from": attacker})
        receipt = _wait_receipt(w3, tx_hash)
        transactions.append(TxReceipt(
            label="Attacker withdraws extracted funds to EOA",
            tx_hash=tx_hash.hex(),
            from_address=attacker,
            to_address=att_vuln_addr,
            status="success" if receipt.status == 1 else "reverted",
            gas_used=str(receipt.gasUsed),
            fee_wei=_tx_fee_wei(receipt),
        ))

        # 7. Attacker deploys Attacker against ProtectedVault
        tx_hash = AttContract.constructor(prot_addr).transact({"from": attacker})
        receipt = _wait_receipt(w3, tx_hash)
        att_prot_addr = receipt.contractAddress
        transactions.append(TxReceipt(
            label="Deploy Attacker against ProtectedVault",
            tx_hash=tx_hash.hex(),
            from_address=attacker,
            to_address=att_prot_addr,
            status="success" if receipt.status == 1 else "reverted",
            gas_used=str(receipt.gasUsed),
            fee_wei=_tx_fee_wei(receipt),
        ))

        # 8. Attacker attempts attack on ProtectedVault -> Reverts
        att_prot_inst = w3.eth.contract(address=att_prot_addr, abi=att_abi)
        revert_reason = "Protected exploit transaction reverted; trace/reason unavailable."
        try:
            # We attempt the call directly or via transaction
            # In web3, a transaction that reverts will either raise or return a receipt with status=0
            tx_hash = att_prot_inst.functions.attack().transact({"from": attacker, "value": attack_amount, "gas": 3000000})
            receipt = _wait_receipt(w3, tx_hash)
            revert_tx_hash = tx_hash.hex()
            status_str = "success" if receipt.status == 1 else "reverted"
            gas_used = str(receipt.gasUsed)
            if receipt.status == 1:
                raise RuntimeError("Protected exploit transaction unexpectedly succeeded; demo aborted.")
        except Exception as e:
            if "unexpectedly succeeded" in str(e):
                raise
            raise RuntimeError(
                "Protected exploit attempt failed before a verifiable receipt was obtained; "
                f"no transaction evidence was recorded: {str(e)[:300]}"
            ) from e

        transactions.append(TxReceipt(
            label="Exploit attempt against ProtectedVault (Blocked by CEI)",
            tx_hash=revert_tx_hash,
            from_address=attacker,
            to_address=att_prot_addr,
            status=status_str,
            gas_used=gas_used,
            fee_wei=_tx_fee_wei(receipt),
            revert_reason=revert_reason
        ))

        # 9. Normal user performs legitimate deposit of 2 ETH on ProtectedVault
        norm_amount = w3.to_wei(2, "ether")
        tx_hash = prot_inst.functions.deposit().transact({"from": normal_user, "value": norm_amount})
        receipt = _wait_receipt(w3, tx_hash)
        transactions.append(TxReceipt(
            label="Normal user deposit 2 ETH (ProtectedVault)",
            tx_hash=tx_hash.hex(),
            from_address=normal_user,
            to_address=prot_addr,
            status="success" if receipt.status == 1 else "reverted",
            gas_used=str(receipt.gasUsed),
            fee_wei=_tx_fee_wei(receipt),
        ))

        # 10. Normal user performs legitimate withdrawal of 2 ETH from ProtectedVault
        tx_hash = prot_inst.functions.withdraw().transact({"from": normal_user})
        receipt = _wait_receipt(w3, tx_hash)
        transactions.append(TxReceipt(
            label="Normal user withdrawal 2 ETH (ProtectedVault)",
            tx_hash=tx_hash.hex(),
            from_address=normal_user,
            to_address=prot_addr,
            status="success" if receipt.status == 1 else "reverted",
            gas_used=str(receipt.gasUsed),
            fee_wei=_tx_fee_wei(receipt),
        ))

        # Capture balances after
        vuln_bal_after = w3.eth.get_balance(vuln_addr)
        prot_bal_after = w3.eth.get_balance(prot_addr)
        attacker_bal_after = w3.eth.get_balance(attacker)
        normal_bal_after = w3.eth.get_balance(normal_user)

        if vuln_bal_after != 0:
            raise RuntimeError("Controlled vulnerable-vault exploit did not drain the expected balance.")
        if prot_bal_after != prot_bal_before:
            raise RuntimeError("Protected vault balance changed during the blocked exploit/normal round trip.")
        if prot_inst.functions.balances(normal_user).call() != 0:
            raise RuntimeError("Normal-user accounting did not return to zero after withdrawal.")

        balances = [
            BalanceDelta(
                address=vuln_addr,
                label="VulnerableVault (ETH Balance)",
                before_wei=str(vuln_bal_before),
                after_wei=str(vuln_bal_after),
                delta_wei=str(vuln_bal_after - vuln_bal_before)
            ),
            BalanceDelta(
                address=prot_addr,
                label="ProtectedVault (ETH Balance)",
                before_wei=str(prot_bal_before),
                after_wei=str(prot_bal_after),
                delta_wei=str(prot_bal_after - prot_bal_before)
            ),
            BalanceDelta(
                address=attacker,
                label="Attacker EOA",
                before_wei=str(attacker_bal_before),
                after_wei=str(attacker_bal_after),
                delta_wei=str(attacker_bal_after - attacker_bal_before)
            ),
            BalanceDelta(
                address=normal_user,
                label="Normal User EOA",
                before_wei=str(normal_bal_before),
                after_wei=str(normal_bal_after),
                delta_wei=str(normal_bal_after - normal_bal_before)
            ),
        ]

        alert = IncidentAlert(
            severity="high",
            title="Reentrancy Attack Prevented on Protected Vault",
            observation=(
                f"VulnerableVault balance was fully drained from {vuln_bal_before} to {vuln_bal_after} wei (delta {vuln_bal_after - vuln_bal_before} wei). "
                f"ProtectedVault balance remained intact at {prot_bal_after} wei after blocking the attacker's re-entrant call. "
                "Normal user deposit and withdrawal succeeded with exact accounting balance."
            ),
            hypothesis=(
                "Checks-Effects-Interactions (CEI) state reordering zeroed the caller balance before external ETH transfer, "
                "causing the re-entrant call's require(balance > 0) guard to revert and thwart exploit execution."
            ),
            suggested_action=(
                "Verify CEI across all asset transfer routines and consider OpenZeppelin ReentrancyGuard for defense in depth."
            )
        )

        run_id = f"demo_{uuid.uuid4().hex[:12]}"
        created_at = now_iso()

        response = DemoRunResponse(
            id=run_id,
            status="complete",
            rpc_url=ANVIL_RPC_URL,
            chain_id=w3.eth.chain_id,
            original_vault=vuln_addr,
            protected_vault=prot_addr,
            attacker=attacker,
            normal_user=normal_user,
            transactions=transactions,
            balances=balances,
            alert=alert,
            is_historical=False,
            created_at=created_at,
            logs=(
                "Real Anvil attack/defense simulation executed successfully. "
                "Receipt status and balance evidence were recorded; call trace diagnostics are unavailable in this prototype."
            )
        )

        # Store in database
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
        INSERT INTO demo_runs (
            id, status, rpc_url, chain_id, original_vault, protected_vault, attacker, normal_user,
            transactions_json, balances_json, alert_json, is_historical, logs, created_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 0, ?, ?)
        """, (
            run_id,
            "complete",
            ANVIL_RPC_URL,
            ANVIL_CHAIN_ID,
            vuln_addr,
            prot_addr,
            attacker,
            normal_user,
            json.dumps([t.model_dump() for t in transactions]),
            json.dumps([b.model_dump() for b in balances]),
            json.dumps(alert.model_dump()),
            response.logs,
            created_at
        ))
        conn.commit()
        conn.close()

        return response, None

    except Exception as e:
        return None, f"Demo execution failed: {str(e)}"
    finally:
        _demo_lock.release()

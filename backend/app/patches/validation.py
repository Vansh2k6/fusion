# Purpose: Validate the exact stored candidate revision in a fresh, hash-bound workspace.
import shutil
import subprocess
import time
import uuid
from pathlib import Path
from typing import List, Optional, Tuple

from app.analysis.runner import kill_process_tree, run_slither_analysis
from app.config import (
    CONTRACTS_DIR,
    DATA_DIR,
    FORGE_BIN,
    FUZZ_RUNS,
    FUZZ_SEED,
    MAX_TOOL_OUTPUT_BYTES,
    REQUIRED_VALIDATION_CHECKS,
    VALIDATION_TIMEOUT_SECONDS,
)
from app.database import get_connection, now_iso
from app.schemas import ValidationCheck, ValidationResponse
from app.storage import compute_sha256
from app.tooling import observed_tool_versions
import json


def compute_harness_hash() -> str:
    """Hash the approved harness/config files a validation run executes (T06.13)."""
    digest = compute_sha256(
        (CONTRACTS_DIR / "foundry.toml").read_bytes()
        + (CONTRACTS_DIR / "test" / "Vault.t.sol").read_bytes()
        + (CONTRACTS_DIR / "src" / "VulnerableVault.sol").read_bytes()
        + (CONTRACTS_DIR / "src" / "Attacker.sol").read_bytes()
    )
    return digest


def _run_bounded(command: List[str], cwd: Path) -> Tuple[int, str, str, bool, int]:
    """Run a trusted tool command with bounded captured output and process-tree timeout."""
    started = time.time()
    stdout_path = cwd / ".validation.stdout.log"
    stderr_path = cwd / ".validation.stderr.log"
    with stdout_path.open("wb") as stdout_file, stderr_path.open("wb") as stderr_file:
        process = subprocess.Popen(command, cwd=str(cwd), stdout=stdout_file, stderr=stderr_file)
        timed_out = False
        try:
            process.wait(timeout=VALIDATION_TIMEOUT_SECONDS)
        except subprocess.TimeoutExpired:
            timed_out = True
            kill_process_tree(process.pid)

    def read_output(path: Path) -> str:
        raw = path.read_bytes()
        suffix = b"\n[output truncated]" if len(raw) > MAX_TOOL_OUTPUT_BYTES else b""
        return (raw[:MAX_TOOL_OUTPUT_BYTES] + suffix).decode("utf-8", errors="replace")

    return (
        process.returncode if process.returncode is not None else -1,
        read_output(stdout_path),
        read_output(stderr_path),
        timed_out,
        int((time.time() - started) * 1000),
    )


def _prepare_workspace(run_id: str, candidate_code: str, candidate_hash: str) -> Tuple[Optional[Path], Optional[str]]:
    """Materialize the candidate and controlled harness, then prove every copied source hash."""
    actual_hash = compute_sha256(candidate_code)
    if actual_hash != candidate_hash:
        return None, "Stored candidate hash does not match candidate bytes; validation refused."

    workspace = DATA_DIR / "validation" / run_id / "contracts"
    (workspace / "src").mkdir(parents=True, exist_ok=False)
    (workspace / "test").mkdir(parents=True, exist_ok=True)
    shutil.copy2(CONTRACTS_DIR / "foundry.toml", workspace / "foundry.toml")
    shutil.copy2(CONTRACTS_DIR / "src" / "VulnerableVault.sol", workspace / "src" / "VulnerableVault.sol")
    shutil.copy2(CONTRACTS_DIR / "src" / "Attacker.sol", workspace / "src" / "Attacker.sol")
    shutil.copy2(CONTRACTS_DIR / "test" / "Vault.t.sol", workspace / "test" / "Vault.t.sol")
    candidate_path = workspace / "src" / "ProtectedVault.sol"
    candidate_path.write_bytes(candidate_code.encode("utf-8"))

    if compute_sha256(candidate_path.read_bytes()) != candidate_hash:
        return None, "Materialized candidate hash mismatch; validation refused."
    return workspace, None


def _command_check(check_type: str, command: List[str], workspace: Path, success_details: str) -> ValidationCheck:
    code, stdout, stderr, timed_out, duration_ms = _run_bounded(command, workspace)
    if timed_out:
        return ValidationCheck(
            check_type=check_type,
            status="timeout",
            duration_ms=duration_ms,
            details=f"{check_type} timed out after {VALIDATION_TIMEOUT_SECONDS} seconds.",
            log_output=stderr + "\n" + stdout,
        )
    passed = code == 0 and (check_type == "compile" or "[PASS]" in stdout)
    return ValidationCheck(
        check_type=check_type,
        status="passed" if passed else "failed",
        duration_ms=duration_ms,
        details=success_details if passed else f"{check_type} failed with exit code {code}.",
        log_output=stdout if passed else stderr + "\n" + stdout,
    )


def run_candidate_validation(patch_id: str) -> Tuple[Optional[ValidationResponse], Optional[str]]:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM patches WHERE id = ?", (patch_id,))
    patch = cursor.fetchone()
    if not patch:
        conn.close()
        return None, "Patch not found"

    run_id = f"val_{uuid.uuid4().hex[:12]}"
    candidate_hash = patch["candidate_hash"]
    original_hash = patch["original_hash"]
    harness_hash = compute_harness_hash()
    tools = observed_tool_versions()
    workspace, preparation_error = _prepare_workspace(run_id, patch["candidate_code"], candidate_hash)
    if preparation_error or workspace is None:
        conn.close()
        return None, preparation_error or "Unable to prepare validation workspace"

    # Parent run first: one identity binds candidate/harness/tool/seed evidence (T06.11).
    created_at = now_iso()
    cursor.execute(
        "INSERT INTO validation_parents (run_id, patch_id, candidate_hash, original_hash, harness_hash,"
        " tool_versions_json, fuzz_seed, fuzz_runs, status, eligible, created_at)"
        " VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'running', 0, ?)",
        (run_id, patch_id, candidate_hash, original_hash, harness_hash,
         json.dumps(tools), FUZZ_SEED, FUZZ_RUNS, created_at),
    )
    conn.commit()

    checks: List[ValidationCheck] = []
    checks.append(_command_check(
        "compile",
        [FORGE_BIN, "build"],
        workspace,
        "The exact hash-bound candidate compiled successfully in a fresh workspace.",
    ))
    compile_ok = checks[-1].status == "passed"

    scan_dir = workspace.parent / "scan"
    scan_dir.mkdir(parents=True, exist_ok=True)
    scan_candidate = scan_dir / "ProtectedVault.sol"
    scan_candidate.write_bytes(patch["candidate_code"].encode("utf-8"))
    if compute_sha256(scan_candidate.read_bytes()) != candidate_hash:
        conn.close()
        return None, "Rescan candidate hash mismatch; validation refused."

    scan_started = time.time()
    scan_result = run_slither_analysis(
        scan_candidate,
        "ProtectedVault.sol",
        timeout=VALIDATION_TIMEOUT_SECONDS,
    )
    duration_ms = int((time.time() - scan_started) * 1000)
    if scan_result["status"] != "complete":
        checks.append(ValidationCheck(
            check_type="rescan",
            status=scan_result["status"] if scan_result["status"] == "timeout" else "failed",
            duration_ms=duration_ms,
            details=f"Candidate rescan did not complete: {scan_result.get('error_message') or 'unknown analyzer failure'}",
            log_output=(scan_result.get("stderr") or "") + "\n" + (scan_result.get("stdout") or ""),
        ))
    else:
        detector_ids = {finding.detector_id for finding in scan_result["findings"]}
        target_detectors = {"reentrancy-eth", "reentrancy-events"}
        remaining = sorted(target_detectors & detector_ids)
        checks.append(ValidationCheck(
            check_type="rescan",
            status="failed" if remaining else "passed",
            duration_ms=duration_ms,
            details=(
                f"Candidate still triggers target detectors: {', '.join(remaining)}."
                if remaining
                else f"Exact candidate rescan completed without target reentrancy detectors; {len(detector_ids)} other findings remain visible."
            ),
            log_output=scan_result.get("stdout") or scan_result.get("stderr"),
        ))

    # Runtime checks depend on a successful compile; skip them honestly when it
    # fails instead of running against stale artifacts (T06.11).
    if compile_ok:
        checks.append(_command_check(
            "attack_exploit",
            [FORGE_BIN, "test", "--match-test", "test_protected_vault_blocks_attack", "-vv"],
            workspace,
            "Exploit replay was blocked and the controlled test asserted the protected vault balance.",
        ))
        checks.append(_command_check(
            "normal_behavior",
            [FORGE_BIN, "test", "--match-test", "test_protected_vault_legitimate_use|test_protected_vault_zero|test_protected_vault_reverting_receiver", "-vv"],
            workspace,
            "Legitimate deposit, withdrawal, zero-deposit, double-withdrawal revert, and reverting-receiver accounting passed for the exact candidate.",
        ))
        checks.append(_command_check(
            "fuzz",
            [FORGE_BIN, "test", "--match-test", "testFuzz", "--fuzz-runs", str(FUZZ_RUNS),
             "--fuzz-seed", str(FUZZ_SEED), "-vv"],
            workspace,
            f"Bounded fuzz executed {FUZZ_RUNS} runs (seed {FUZZ_SEED}) over the full deposit/withdraw domain with conservation assertions.",
        ))
    else:
        for check_type in ("attack_exploit", "normal_behavior", "fuzz"):
            checks.append(ValidationCheck(
                check_type=check_type,
                status="skipped",
                duration_ms=0,
                details=f"{check_type} skipped: compile failed, so no runtime artifact was available.",
                log_output=None,
            ))

    created_at = now_iso()
    all_passed = len(checks) == len(REQUIRED_VALIDATION_CHECKS) and all(check.status == "passed" for check in checks)
    for check in checks:
        cursor.execute(
            """
            INSERT INTO validation_runs (id, patch_id, candidate_hash, check_type, status, duration_ms, details, log_output, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                f"{run_id}:{check.check_type}", patch_id, candidate_hash, check.check_type,
                check.status, check.duration_ms, check.details, check.log_output, created_at,
            ),
        )
    conn.commit()
    cursor.execute(
        "UPDATE validation_parents SET status='complete', eligible=? WHERE run_id=?",
        (1 if all_passed else 0, run_id),
    )
    conn.commit()
    conn.close()

    return ValidationResponse(
        id=run_id,
        patch_id=patch_id,
        candidate_hash=candidate_hash,
        checks=checks,
        all_passed=all_passed,
        created_at=created_at,
    ), None

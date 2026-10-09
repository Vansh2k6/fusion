# Purpose: Propose reviewed patch templates, compute diffs, and manage accept/revoke lifecycle.
import difflib
import uuid
from typing import Optional, Dict, Any, Tuple
from app.database import get_connection, now_iso
from app.storage import compute_sha256
from app.config import FIXTURES_DIR, CURATED_FIXTURES

VULNERABLE_HASH = CURATED_FIXTURES["vulnerable_vault"]["hash"]
PROTECTED_HASH = CURATED_FIXTURES["protected_vault"]["hash"]

TEMPLATE_ID = "cei_reentrancy_mitigation"
TEMPLATE_VERSION = "1.0.0"
TEMPLATE_NAME = "Checks-Effects-Interactions (CEI) State Reordering"

def get_protected_candidate_code() -> str:
    path = FIXTURES_DIR / "ProtectedVault.sol"
    return path.read_text(encoding="utf-8")

def compute_diff(original_text: str, candidate_text: str, orig_name: str = "original.sol", cand_name: str = "candidate.sol") -> str:
    diff_lines = list(difflib.unified_diff(
        original_text.splitlines(keepends=True),
        candidate_text.splitlines(keepends=True),
        fromfile=orig_name,
        tofile=cand_name,
        n=3
    ))
    return "".join(diff_lines)

def propose_patch_for_scan(scan_id: str) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
    """Propose a reviewed patch template if the scan's source matches the curated vulnerable fixture."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, source_hash, source_code, filename FROM scans WHERE id = ?", (scan_id,))
    row = cursor.fetchone()
    if not row:
        conn.close()
        return None, "Scan not found"

    source_hash = row["source_hash"].lower()
    source_code = row["source_code"]
    filename = row["filename"]

    # Match exact hash rule R05
    if source_hash != VULNERABLE_HASH:
        conn.close()
        return None, "Automatic patch review unavailable: contract hash does not match curated vault template. Manual review required."

    candidate_code = get_protected_candidate_code()
    candidate_hash = compute_sha256(candidate_code)
    # Tampered candidate template on disk must be refused, never proposed (T06.03).
    if candidate_hash != PROTECTED_HASH:
        conn.close()
        return None, "Reviewed candidate template bytes do not match the approved revision; proposal refused."
    diff = compute_diff(source_code, candidate_code, orig_name=f"original/{filename}", cand_name=f"candidate/{filename}")

    # Check if patch already proposed for this scan
    cursor.execute("SELECT * FROM patches WHERE scan_id = ? AND candidate_hash = ?", (scan_id, candidate_hash))
    existing = cursor.fetchone()
    if existing:
        conn.close()
        return dict(existing), None

    patch_id = f"patch_{uuid.uuid4().hex[:12]}"
    template_id = TEMPLATE_ID
    template_name = TEMPLATE_NAME
    explanation = (
        "Reorders state modifications before the external ETH transfer in withdraw(). "
        "The depositor balance is updated to zero before invoking msg.sender.call{value: balance}(\"\"), "
        "preventing subsequent re-entrant invocations from extracting additional funds. "
        "The contract name changes from VulnerableVault to ProtectedVault; behavior is otherwise preserved. "
        f"Reviewed template {template_id} version {TEMPLATE_VERSION}, candidate bytes {candidate_hash[:16]}…."
    )
    created_at = now_iso()

    cursor.execute("""
    INSERT INTO patches (
        id, scan_id, original_hash, candidate_hash, candidate_code, template_id, template_name,
        template_hash, template_version,
        explanation, diff, is_accepted, accepted_at, created_at
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 0, NULL, ?)
    """, (
        patch_id,
        scan_id,
        source_hash,
        candidate_hash,
        candidate_code,
        template_id,
        template_name,
        candidate_hash,
        TEMPLATE_VERSION,
        explanation,
        diff,
        created_at
    ))
    conn.commit()

    cursor.execute("SELECT * FROM patches WHERE id = ?", (patch_id,))
    created = cursor.fetchone()
    conn.close()
    return dict(created), None

def _record_selection(conn, patch_id: str, new_selected: str, acknowledged_unvalidated: bool) -> Dict[str, Any]:
    """Transactionally set the single selected revision and append history (T06.14, T06.19)."""
    cur = conn.cursor()
    cur.execute("SELECT * FROM patch_selections WHERE patch_id = ?", (patch_id,))
    current = cur.fetchone()
    previous = current["selected"] if current else "original"
    if current and current["selected"] == new_selected:
        return dict(current)  # idempotent repeat: same version, no new event
    now = now_iso()
    if current:
        cur.execute(
            "UPDATE patch_selections SET selected=?, version=version+1, acknowledged_unvalidated=?, updated_at=? WHERE patch_id=?",
            (new_selected, 1 if acknowledged_unvalidated else 0, now, patch_id),
        )
    else:
        cur.execute(
            "INSERT INTO patch_selections (patch_id, selected, version, acknowledged_unvalidated, updated_at)"
            " VALUES (?, ?, 1, ?, ?)",
            (patch_id, new_selected, 1 if acknowledged_unvalidated else 0, now),
        )
    cur.execute(
        "INSERT INTO selection_events (id, patch_id, action, previous, new_selected, acknowledged_unvalidated, created_at)"
        " VALUES (?, ?, ?, ?, ?, ?, ?)",
        (f"sel_{uuid.uuid4().hex[:12]}", patch_id,
         "accept" if new_selected == "candidate" else "revoke",
         previous, new_selected, 1 if acknowledged_unvalidated else 0, now),
    )
    conn.commit()
    cur.execute("SELECT * FROM patch_selections WHERE patch_id = ?", (patch_id,))
    return dict(cur.fetchone())


def accept_patch(patch_id: str, acknowledged_unvalidated: bool = False) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM patches WHERE id = ?", (patch_id,))
        row = cursor.fetchone()
        if not row:
            conn.close()
            return None, "Patch not found"

        # Recheck stored bytes before selection (T06.16): stale/tampered rows refused.
        if compute_sha256(row["candidate_code"]) != row["candidate_hash"]:
            conn.close()
            return None, "Stored candidate bytes do not match recorded hash; selection refused."

        accepted_at = now_iso()
        cursor.execute("UPDATE patches SET is_accepted = 1, accepted_at = ? WHERE id = ?", (accepted_at, patch_id))
        _record_selection(conn, patch_id, "candidate", acknowledged_unvalidated)

        cursor.execute("SELECT * FROM patches WHERE id = ?", (patch_id,))
        updated = cursor.fetchone()
        conn.close()
        return dict(updated), None
    except Exception:
        try:
            conn.rollback()
        finally:
            conn.close()
        raise


def revoke_patch(patch_id: str) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM patches WHERE id = ?", (patch_id,))
        row = cursor.fetchone()
        if not row:
            conn.close()
            return None, "Patch not found"

        cursor.execute("UPDATE patches SET is_accepted = 0, accepted_at = NULL WHERE id = ?", (patch_id,))
        _record_selection(conn, patch_id, "original", False)

        cursor.execute("SELECT * FROM patches WHERE id = ?", (patch_id,))
        updated = cursor.fetchone()
        conn.close()
        return dict(updated), None
    except Exception:
        try:
            conn.rollback()
        finally:
            conn.close()
        raise

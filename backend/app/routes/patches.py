# Purpose: Define endpoints for patch proposal, validation checks, accept/revoke, and export.
from fastapi import APIRouter, HTTPException
from typing import Dict, Any
from app.database import get_connection, now_iso
from app.patches.service import propose_patch_for_scan, accept_patch, revoke_patch
from app.patches.validation import run_candidate_validation
from app.schemas import PatchResponse, ValidationResponse

router = APIRouter(prefix="/api", tags=["patches"])

@router.post("/scans/{scan_id}/patches", response_model=PatchResponse)
def propose_patch(scan_id: str):
    patch_data, error = propose_patch_for_scan(scan_id)
    if error:
        raise HTTPException(status_code=400, detail=error)
    return PatchResponse(
        id=patch_data["id"],
        scan_id=patch_data["scan_id"],
        original_hash=patch_data["original_hash"],
        candidate_hash=patch_data["candidate_hash"],
        candidate_code=patch_data["candidate_code"],
        template_id=patch_data["template_id"],
        template_name=patch_data["template_name"],
        template_hash=patch_data.get("template_hash"),
        template_version=patch_data.get("template_version"),
        explanation=patch_data["explanation"],
        diff=patch_data["diff"],
        is_accepted=bool(patch_data["is_accepted"]),
        accepted_at=patch_data["accepted_at"],
        created_at=patch_data["created_at"]
    )

@router.get("/patches/{patch_id}", response_model=PatchResponse)
def get_patch(patch_id: str):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM patches WHERE id = ?", (patch_id,))
    row = cursor.fetchone()
    conn.close()
    if not row:
        raise HTTPException(status_code=404, detail="Patch not found.")
    return PatchResponse(
        id=row["id"],
        scan_id=row["scan_id"],
        original_hash=row["original_hash"],
        candidate_hash=row["candidate_hash"],
        candidate_code=row["candidate_code"],
        template_id=row["template_id"],
        template_name=row["template_name"],
        template_hash=row["template_hash"] if "template_hash" in row.keys() else None,
        template_version=row["template_version"] if "template_version" in row.keys() else None,
        explanation=row["explanation"],
        diff=row["diff"],
        is_accepted=bool(row["is_accepted"]),
        accepted_at=row["accepted_at"],
        created_at=row["created_at"]
    )

@router.post("/patches/{patch_id}/validate", response_model=ValidationResponse)
def validate_patch(patch_id: str):
    res, error = run_candidate_validation(patch_id)
    if error:
        raise HTTPException(status_code=400, detail=error)
    return res

@router.get("/patches/{patch_id}/validation-status")
def validation_status(patch_id: str):
    """Latest parent run for these exact bytes: eligible only if every required
    check passed under the same candidate/harness binding (T06.07, T06.13)."""
    from app.patches.validation import compute_harness_hash
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM patches WHERE id = ?", (patch_id,))
        patch = cursor.fetchone()
        if not patch:
            raise HTTPException(status_code=404, detail="Patch not found.")
        current_harness = compute_harness_hash()
        cursor.execute(
            "SELECT * FROM validation_parents WHERE patch_id = ? ORDER BY created_at DESC LIMIT 5",
            (patch_id,),
        )
        for parent in cursor.fetchall():
            if parent["candidate_hash"] != patch["candidate_hash"]:
                continue  # a pass for older bytes never transfers (T06.07)
            return {
                "run_id": parent["run_id"],
                "eligible": bool(parent["eligible"]) and parent["harness_hash"] == current_harness,
                "harness_matches": parent["harness_hash"] == current_harness,
                "parent_harness_hash": parent["harness_hash"],
                "current_harness_hash": current_harness,
                "fuzz_seed": parent["fuzz_seed"],
                "fuzz_runs": parent["fuzz_runs"],
            }
        return {"run_id": None, "eligible": False, "harness_matches": False,
                "parent_harness_hash": None, "current_harness_hash": current_harness,
                "fuzz_seed": None, "fuzz_runs": None}
    finally:
        conn.close()

@router.post("/patches/{patch_id}/accept", response_model=PatchResponse)
def accept(patch_id: str, acknowledged_unvalidated: bool = False):
    """Select the candidate revision. Validation outcome is independent (R06);
    acknowledged_unvalidated records the explicit bypass, which never enables
    the validated replay gate."""
    patch_data, error = accept_patch(patch_id, acknowledged_unvalidated=acknowledged_unvalidated)
    if error:
        raise HTTPException(status_code=400, detail=error)
    return PatchResponse(
        id=patch_data["id"],
        scan_id=patch_data["scan_id"],
        original_hash=patch_data["original_hash"],
        candidate_hash=patch_data["candidate_hash"],
        candidate_code=patch_data["candidate_code"],
        template_id=patch_data["template_id"],
        template_name=patch_data["template_name"],
        template_hash=patch_data.get("template_hash"),
        template_version=patch_data.get("template_version"),
        explanation=patch_data["explanation"],
        diff=patch_data["diff"],
        is_accepted=bool(patch_data["is_accepted"]),
        accepted_at=patch_data["accepted_at"],
        created_at=patch_data["created_at"]
    )

@router.post("/patches/{patch_id}/revoke", response_model=PatchResponse)
def revoke(patch_id: str):
    patch_data, error = revoke_patch(patch_id)
    if error:
        raise HTTPException(status_code=400, detail=error)
    return PatchResponse(
        id=patch_data["id"],
        scan_id=patch_data["scan_id"],
        original_hash=patch_data["original_hash"],
        candidate_hash=patch_data["candidate_hash"],
        candidate_code=patch_data["candidate_code"],
        template_id=patch_data["template_id"],
        template_name=patch_data["template_name"],
        template_hash=patch_data.get("template_hash"),
        template_version=patch_data.get("template_version"),
        explanation=patch_data["explanation"],
        diff=patch_data["diff"],
        is_accepted=bool(patch_data["is_accepted"]),
        accepted_at=patch_data["accepted_at"],
        created_at=patch_data["created_at"]
    )

@router.get("/patches/{patch_id}/export")
def export_patch(patch_id: str):
    """Export candidate patch package including validation records."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM patches WHERE id = ?", (patch_id,))
    patch = cursor.fetchone()
    if not patch:
        conn.close()
        raise HTTPException(status_code=404, detail="Patch not found.")

    cursor.execute("SELECT * FROM validation_runs WHERE patch_id = ? ORDER BY created_at DESC", (patch_id,))
    val_rows = cursor.fetchall()

    grouped_runs: Dict[str, Dict[str, Any]] = {}
    legacy_records = []
    for value in val_rows:
        record_id = value["id"]
        record = {
            "id": record_id,
            "candidate_hash": value["candidate_hash"],
            "check_type": value["check_type"],
            "status": value["status"],
            "duration_ms": value["duration_ms"],
            "details": value["details"],
            "created_at": value["created_at"],
        }
        if ":" not in record_id:
            legacy_records.append(record)
            continue
        run_id = record_id.split(":", 1)[0]
        run = grouped_runs.setdefault(run_id, {
            "id": run_id,
            "candidate_hash": value["candidate_hash"],
            "created_at": value["created_at"],
            "checks": [],
        })
        run["checks"].append(record)

    from app.config import REQUIRED_VALIDATION_CHECKS
    cursor.execute(
        "SELECT * FROM validation_parents WHERE patch_id = ? ORDER BY created_at DESC", (patch_id,)
    )
    parents = [dict(p) for p in cursor.fetchall()]
    cursor.execute(
        "SELECT * FROM patch_selections WHERE patch_id = ?", (patch_id,)
    )
    sel_row = cursor.fetchone()
    cursor.execute(
        "SELECT * FROM selection_events WHERE patch_id = ? ORDER BY created_at ASC", (patch_id,)
    )
    selection_history = [dict(e) for e in cursor.fetchall()]
    conn.close()

    validation_history = []
    for run in grouped_runs.values():
        required = [c for c in run["checks"] if c["check_type"] in REQUIRED_VALIDATION_CHECKS]
        run["all_passed"] = len(required) == len(REQUIRED_VALIDATION_CHECKS) and all(
            check["status"] == "passed" for check in required
        )
        validation_history.append(run)

    latest_current_validation = next(
        (run for run in validation_history if run["candidate_hash"] == patch["candidate_hash"]),
        None,
    )

    return {
        "export_version": "1.0.0",
        "exported_at": now_iso(),
        "patch_id": patch["id"],
        "scan_id": patch["scan_id"],
        "original_hash": patch["original_hash"],
        "candidate_hash": patch["candidate_hash"],
        "candidate_code": patch["candidate_code"],
        "template_id": patch["template_id"],
        "template_hash": patch["template_hash"] if "template_hash" in patch.keys() else None,
        "template_version": patch["template_version"] if "template_version" in patch.keys() else None,
        "template_name": patch["template_name"],
        "is_accepted": bool(patch["is_accepted"]),
        "accepted_at": patch["accepted_at"],
        "selected_revision": sel_row["selected"] if sel_row else "original",
        "selection_history": selection_history,
        "latest_validation": latest_current_validation,
        "validation_runs": validation_history,
        "validation_parents": parents,
        "legacy_validation_records": legacy_records,
    }

# Purpose: Scoped dashboard aggregates over stored evidence (P08.01). Every value
# carries its scope/window/denominator; unknown stays unavailable, never zero-filled.
from fastapi import APIRouter
from typing import Any, Dict, List
from app.config import REQUIRED_VALIDATION_CHECKS
from app.database import get_connection

router = APIRouter(prefix="/api", tags=["dashboard"])

PROFILE_ID = "validation-v1"
ACTIVITY_LIMIT = 25


@router.get("/dashboard")
def dashboard() -> Dict[str, Any]:
    conn = get_connection()
    try:
        cur = conn.cursor()
        scans = cur.execute("SELECT id, filename, status, created_at FROM scans").fetchall()
        findings = cur.execute(
            "SELECT id, scan_id, detector_id, impact FROM findings").fetchall()
        reviews = cur.execute(
            "SELECT scan_id, finding_key, state FROM finding_reviews").fetchall()
        demos = cur.execute(
            "SELECT id, status, is_historical, created_at FROM demo_runs").fetchall()
        parents = cur.execute(
            "SELECT run_id, patch_id, candidate_hash, status, eligible, created_at"
            " FROM validation_parents ORDER BY created_at DESC").fetchall()

        review_state = {(r["scan_id"], r["finding_key"]): r["state"] for r in reviews}
        open_count = 0
        for f in findings:
            # DB id is {scan_id}_{finding.id}; review keys use the finding suffix.
            suffix = f["id"][len(f["scan_id"]) + 1:] if f["id"].startswith(f["scan_id"] + "_") else f["id"]
            state = review_state.get((f["scan_id"], suffix), "open")
            if state not in ("resolved", "canceled"):
                open_count += 1

        live_incidents = [d for d in demos if not d["is_historical"]]

        latest_parent = parents[0] if parents else None
        passed = required = len(REQUIRED_VALIDATION_CHECKS)
        duration_ms = None
        checks_scope = "no validation runs yet"
        if latest_parent:
            rows = cur.execute(
                "SELECT status, duration_ms FROM validation_runs WHERE id LIKE ?",
                (latest_parent["run_id"] + ":%",)).fetchall()
            required_rows = [r for r in rows]
            passed = sum(1 for r in required_rows if r["status"] == "passed")
            required = len(REQUIRED_VALIDATION_CHECKS)  # denominator keeps unrun/skipped
            duration_ms = sum(r["duration_ms"] or 0 for r in required_rows) or None
            checks_scope = f"profile {PROFILE_ID} · run {latest_parent['run_id']}"

        activity: List[Dict[str, Any]] = []
        for s in scans:
            activity.append({"id": s["id"], "kind": "scan",
                             "title": f"Scan {s['filename']} · {s['status']}",
                             "ref": s["id"], "created_at": s["created_at"]})
        for p in parents:
            activity.append({"id": p["run_id"], "kind": "validation",
                             "title": f"Validation run · {'eligible' if p['eligible'] else 'not eligible'}",
                             "ref": p["patch_id"], "created_at": p["created_at"]})
        for d in demos:
            activity.append({"id": d["id"], "kind": "incident",
                             "title": f"Local replay · {d['status']}"
                             + (" · historical" if d["is_historical"] else ""),
                             "ref": d["id"], "created_at": d["created_at"]})
        for e in cur.execute(
                "SELECT id, action, patch_id, created_at FROM selection_events").fetchall():
            activity.append({"id": e["id"], "kind": "selection",
                             "title": f"Revision {e['action']}",
                             "ref": e["patch_id"], "created_at": e["created_at"]})
        activity.sort(key=lambda a: a["created_at"], reverse=True)
        activity = activity[:ACTIVITY_LIMIT]
    finally:
        conn.close()

    return {
        "open_review_findings": {
            "value": open_count,
            "scope": f"all completed scans in this workspace · {len(findings)} findings total",
        },
        "recorded_incidents": {
            "value": len(live_incidents),
            "scope": "non-historical local replay runs in this workspace",
        },
        "required_checks": {
            "passed": passed if latest_parent else 0,
            "required": required,
            "profile": PROFILE_ID,
            "scope": checks_scope,
        },
        "validation_duration_ms": {
            "value": duration_ms,
            "scope": f"sum of check durations · {checks_scope}",
        },
        "activity": activity,
    }

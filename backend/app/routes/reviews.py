# Purpose: Finding review-state endpoints (P05.02): versioned mutations, conflict on stale writes.
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from app.database import get_connection, now_iso

router = APIRouter(prefix="/api", tags=["reviews"])

REVIEW_STATES = {"open", "triaged", "in_progress", "resolved", "canceled"}


class Review(BaseModel):
    scan_id: str
    finding_key: str
    state: str
    reason: str = ""
    reviewer: Optional[str] = None
    review_date: Optional[str] = None
    version: int = 1
    updated_at: str


class ReviewUpdate(BaseModel):
    state: str
    reason: str = ""
    reviewer: Optional[str] = None
    review_date: Optional[str] = None
    version: int  # expected current version; stale writes get 409


def _row_to_review(r) -> Review:
    return Review(
        scan_id=r["scan_id"], finding_key=r["finding_key"], state=r["state"],
        reason=r["reason"] or "", reviewer=r["reviewer"], review_date=r["review_date"],
        version=r["version"], updated_at=r["updated_at"],
    )


@router.get("/scans/{scan_id}/reviews", response_model=List[Review])
def list_reviews(scan_id: str):
    conn = get_connection()
    try:
        rows = conn.execute(
            "SELECT * FROM finding_reviews WHERE scan_id = ?", (scan_id,)
        ).fetchall()
    finally:
        conn.close()
    return [_row_to_review(r) for r in rows]


@router.put("/scans/{scan_id}/reviews/{finding_key}", response_model=Review)
def update_review(scan_id: str, finding_key: str, update: ReviewUpdate):
    if update.state not in REVIEW_STATES:
        raise HTTPException(status_code=400, detail=f"Unknown review state '{update.state}'.")
    if update.state == "resolved" and not update.reason.strip():
        raise HTTPException(status_code=400, detail="Resolving a finding requires a review reason.")
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute(
            "SELECT * FROM finding_reviews WHERE scan_id = ? AND finding_key = ?",
            (scan_id, finding_key),
        )
        row = cur.fetchone()
        if row is None:
            if update.version != 0:
                raise HTTPException(status_code=409, detail="Review was created concurrently; reload and retry.")
            cur.execute(
                "INSERT INTO finding_reviews (scan_id, finding_key, state, reason, reviewer, review_date, version, updated_at)"
                " VALUES (?, ?, ?, ?, ?, ?, 1, ?)",
                (scan_id, finding_key, update.state, update.reason, update.reviewer,
                 update.review_date, now_iso()),
            )
        else:
            if update.version != row["version"]:
                raise HTTPException(status_code=409, detail="Stale review edit; reload and retry.")
            cur.execute(
                "UPDATE finding_reviews SET state=?, reason=?, reviewer=?, review_date=?, version=version+1, updated_at=? "
                "WHERE scan_id=? AND finding_key=?",
                (update.state, update.reason, update.reviewer, update.review_date,
                 now_iso(), scan_id, finding_key),
            )
        conn.commit()
        cur.execute(
            "SELECT * FROM finding_reviews WHERE scan_id = ? AND finding_key = ?",
            (scan_id, finding_key),
        )
        return _row_to_review(cur.fetchone())
    finally:
        conn.close()

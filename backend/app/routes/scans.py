# Purpose: Define endpoints for scan upload, status polling, findings, export, and fixtures.
import json
from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from typing import List, Optional
from app.config import (
    ARBITRARY_SCAN_ISOLATION_ENABLED,
    CURATED_FIXTURES,
    FIXTURES_DIR,
    MAX_UPLOAD_SIZE,
    PINNED_VERSIONS,
)
from app.database import get_connection, now_iso
from app.storage import validate_source_safety, compute_sha256
from app.jobs import enqueue_scan_job, QueueOverloadError, CuratedPolicyError
from app.tooling import observed_tool_versions
from app.worker import arbitrary_scan_allowed
from app.schemas import ScanResponse, Finding, ScanExport, FixtureInfo, CreateScanRequest

router = APIRouter(prefix="/api", tags=["scans"])

@router.get("/fixtures", response_model=List[FixtureInfo])
def list_fixtures():
    """List curated educational fixtures and their provenance metadata."""
    res = []
    for f_id, meta in CURATED_FIXTURES.items():
        file_path = FIXTURES_DIR / meta["name"]
        code = file_path.read_text(encoding="utf-8") if file_path.exists() else ""
        res.append(FixtureInfo(
            id=meta["id"],
            name=meta["name"],
            hash=meta["hash"],
            description=meta["description"],
            expected_detector=meta["expected_detector"],
            source_code=code
        ))
    return res

@router.post("/scans", response_model=ScanResponse)
async def create_scan(
    file: Optional[UploadFile] = File(None),
    fixture_id: Optional[str] = Form(None),
    source_code: Optional[str] = Form(None),
    filename: Optional[str] = Form("contract.sol")
):
    """Upload a .sol contract file or select a bundled fixture for Slither analysis."""
    provided = [bool(file and (file.filename or True)), bool(fixture_id), bool(source_code)]
    if sum(provided) != 1:
        raise HTTPException(status_code=400, detail="Provide exactly one of file upload, fixture_id, or source_code.")
    final_code = ""
    final_name = filename or "contract.sol"
    source_hash: str | None = None

    if file:
        # Bounded read: enforce MAX_UPLOAD_SIZE during read, before decode.
        content_bytes = b""
        while len(content_bytes) <= MAX_UPLOAD_SIZE:
            chunk = await file.read(MAX_UPLOAD_SIZE + 1 - len(content_bytes))
            if not chunk:
                break
            content_bytes += chunk
        if len(content_bytes) > MAX_UPLOAD_SIZE:
            raise HTTPException(status_code=413, detail=f"File size exceeds {MAX_UPLOAD_SIZE // 1024} KiB limit.")
        try:
            final_code = content_bytes.decode("utf-8")
        except UnicodeDecodeError:
            raise HTTPException(status_code=400, detail="File is not valid UTF-8 text.")
        final_name = file.filename or "uploaded.sol"
        source_hash = compute_sha256(content_bytes)  # hash exact bytes, not display string
    elif fixture_id:
        if fixture_id not in CURATED_FIXTURES:
            raise HTTPException(status_code=400, detail=f"Unknown fixture ID '{fixture_id}'.")
        meta = CURATED_FIXTURES[fixture_id]
        file_path = FIXTURES_DIR / meta["name"]
        if not file_path.exists():
            raise HTTPException(status_code=404, detail="Fixture file not found on disk.")
        final_code = file_path.read_text(encoding="utf-8")
        final_name = meta["name"]
    elif source_code:
        final_code = source_code
        final_name = filename or "contract.sol"
    else:
        raise HTTPException(status_code=400, detail="Must provide either a file upload, fixture_id, or source_code.")

    # Validate source safety (path traversal, URI imports, size limit)
    is_safe, reason = validate_source_safety(final_code)
    if not is_safe:
        raise HTTPException(status_code=400, detail=reason)

    if source_hash is None:
        source_hash = compute_sha256(final_code.encode("utf-8"))
    source_hash = source_hash or ""
    allowed, reason = arbitrary_scan_allowed(source_hash)
    if not allowed:
        raise HTTPException(status_code=503, detail=reason)

    try:
        scan_id = enqueue_scan_job(final_name, final_code)
    except QueueOverloadError as e:
        raise HTTPException(status_code=429, detail=str(e))
    except CuratedPolicyError as e:
        raise HTTPException(status_code=503, detail=str(e))

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM scans WHERE id = ?", (scan_id,))
    row = cursor.fetchone()
    conn.close()

    return ScanResponse(
        id=row["id"],
        filename=row["filename"],
        source_hash=row["source_hash"],
        source_code=row["source_code"],
        status=row["status"],
        error_message=row["error_message"],
        findings=[],
        compiler_version=row["compiler_version"],
        analyzer_version=row["analyzer_version"],
        duration_ms=row["duration_ms"],
        created_at=row["created_at"],
        updated_at=row["updated_at"]
    )

@router.get("/scans", response_model=List[ScanResponse])
def list_scans(limit: int = 20, offset: int = 0):
    """Retrieve stable paginated scan history (newest first, id as deterministic tiebreak)."""
    limit = max(1, min(limit, 100))
    offset = max(0, offset)
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM scans ORDER BY created_at DESC, id DESC LIMIT ? OFFSET ?",
        (limit, offset),
    )
    rows = cursor.fetchall()

    res = []
    for r in rows:
        cursor.execute("SELECT * FROM findings WHERE scan_id = ?", (r["id"],))
        finding_rows = cursor.fetchall()
        findings = [
            Finding(
                id=f["id"],
                detector_id=f["detector_id"],
                impact=f["impact"],
                confidence=f["confidence"],
                message=f["message"],
                file=f["file"],
                start_line=f["start_line"],
                end_line=f["end_line"],
                start_col=f["start_col"],
                end_col=f["end_col"],
                explanation=f["explanation"],
                recommendation=f["recommendation"],
                reference_url=f["reference_url"],
                raw_element=json.loads(f["raw_element_json"]) if f["raw_element_json"] else None
            )
            for f in finding_rows
        ]
        res.append(ScanResponse(
            id=r["id"],
            filename=r["filename"],
            source_hash=r["source_hash"],
            source_code=r["source_code"],
            status=r["status"],
            error_message=r["error_message"],
            findings=findings,
            compiler_version=r["compiler_version"],
            analyzer_version=r["analyzer_version"],
            duration_ms=r["duration_ms"],
            created_at=r["created_at"],
            updated_at=r["updated_at"]
        ))
    conn.close()
    return res

@router.get("/scans/{scan_id}", response_model=ScanResponse)
def get_scan(scan_id: str):
    """Retrieve scan status and normalized findings."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM scans WHERE id = ?", (scan_id,))
    row = cursor.fetchone()
    if not row:
        conn.close()
        raise HTTPException(status_code=404, detail="Scan not found.")

    cursor.execute("SELECT * FROM findings WHERE scan_id = ?", (scan_id,))
    finding_rows = cursor.fetchall()
    conn.close()

    findings = [
        Finding(
            id=f["id"],
            detector_id=f["detector_id"],
            impact=f["impact"],
            confidence=f["confidence"],
            message=f["message"],
            file=f["file"],
            start_line=f["start_line"],
            end_line=f["end_line"],
            start_col=f["start_col"],
            end_col=f["end_col"],
            explanation=f["explanation"],
            recommendation=f["recommendation"],
            reference_url=f["reference_url"],
            raw_element=json.loads(f["raw_element_json"]) if f["raw_element_json"] else None
        )
        for f in finding_rows
    ]

    return ScanResponse(
        id=row["id"],
        filename=row["filename"],
        source_hash=row["source_hash"],
        source_code=row["source_code"],
        status=row["status"],
        error_message=row["error_message"],
        findings=findings,
        compiler_version=row["compiler_version"],
        analyzer_version=row["analyzer_version"],
        duration_ms=row["duration_ms"],
        created_at=row["created_at"],
        updated_at=row["updated_at"]
    )

@router.get("/scans/{scan_id}/source")
def export_scan_source(scan_id: str):
    """Download the exact immutable source bytes stored for a scan (hash-verified)."""
    from fastapi.responses import PlainTextResponse
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT filename, source_code, source_hash FROM scans WHERE id = ?", (scan_id,))
    row = cursor.fetchone()
    conn.close()
    if not row:
        raise HTTPException(status_code=404, detail="Scan not found.")
    body: str = row["source_code"]
    digest = compute_sha256(body.encode("utf-8"))
    if digest != row["source_hash"]:
        raise HTTPException(status_code=409, detail="Stored source hash mismatch; artifact integrity error.")
    safe = row["filename"] or "contract.sol"
    return PlainTextResponse(
        body,
        headers={
            "X-Source-Sha256": row["source_hash"],
            "Content-Disposition": f'attachment; filename="{safe}"',
        },
    )

@router.get("/scans/{scan_id}/export", response_model=ScanExport)
def export_scan_report(scan_id: str):
    """Export structured scan report containing source hash, timestamp, tool versions, and findings."""
    scan = get_scan(scan_id)
    observed = observed_tool_versions()
    return ScanExport(
        export_version="1.0.0",
        exported_at=now_iso(),
        scan_id=scan.id,
        filename=scan.filename,
        source_hash=scan.source_hash,
        tool_versions=observed,
        status=scan.status,
        findings_count=len(scan.findings),
        findings=scan.findings,
        raw_diagnostics={
            "compiler": scan.compiler_version,
            "analyzer": scan.analyzer_version,
            "expected_tool_versions": PINNED_VERSIONS,
            "duration_ms": scan.duration_ms,
            "error_message": scan.error_message
        }
    )

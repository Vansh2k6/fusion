# Purpose: Orchestrate one bounded analysis job at a time and record honest lifecycle transitions.
import threading
import uuid
import json
from pathlib import Path
from typing import Optional

class QueueOverloadError(RuntimeError):
    pass

class CuratedPolicyError(ValueError):
    pass
from app.database import get_connection, now_iso
from app.storage import save_scan_artifact
from app.analysis.slither import analyze_file
from app.config import PINNED_VERSIONS

_job_lock = threading.Lock()
_active_slots = threading.Semaphore(1)  # one active execution slot (P02.01)
_queue_depth = 0
_queue_lock = threading.Lock()
MAX_QUEUED_JOBS = 4  # bounded queue; flood beyond capacity gets explicit overload

def enqueue_scan_job(filename: str, source_code: str) -> str:
    global _queue_depth
    with _queue_lock:
        if _queue_depth >= MAX_QUEUED_JOBS:
            raise QueueOverloadError(f"Job queue full ({MAX_QUEUED_JOBS} waiting); retry later.")
        _queue_depth += 1
    # Defense in depth: executor enforces curated policy itself (route checks alone insufficient).
    from app.config import ARBITRARY_SCAN_ISOLATION_ENABLED, CURATED_FIXTURES
    from app.storage import compute_sha256 as _hash
    if not ARBITRARY_SCAN_ISOLATION_ENABLED:
        curated = {item["hash"].lower() for item in CURATED_FIXTURES.values()}
        if _hash(source_code) not in curated:
            with _queue_lock:
                _queue_depth -= 1
            raise CuratedPolicyError("Source bytes are not an approved curated fixture.")
    scan_id = f"scan_{uuid.uuid4().hex[:12]}"
    source_file, source_hash = save_scan_artifact(scan_id, filename, source_code)

    conn = get_connection()
    cursor = conn.cursor()
    created_at = now_iso()
    cursor.execute("""
    INSERT INTO scans (id, filename, source_hash, source_code, status, error_message, compiler_version, analyzer_version, created_at, updated_at)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        scan_id,
        filename,
        source_hash,
        source_code,
        "queued",
        None,
        PINNED_VERSIONS["solc"],
        PINNED_VERSIONS["slither"],
        created_at,
        created_at
    ))
    conn.commit()
    conn.close()

    # Launch background execution thread with single worker lock
    t = threading.Thread(target=_run_scan_worker, args=(scan_id, source_file, filename), daemon=True)
    t.start()

    return scan_id

def _run_scan_worker(scan_id: str, source_file: Path, filename: str):
    global _queue_depth
    if not _active_slots.acquire(blocking=False):
        # No free slot: leave queued; the poll loop will pick it up when a slot frees.
        # To keep ordering simple, block here instead of dropping the job.
        _active_slots.acquire()
    try:
        with _job_lock:
            conn = get_connection()
            cursor = conn.cursor()

            # Transition: compiling
            cursor.execute("UPDATE scans SET status = ?, updated_at = ? WHERE id = ?", ("compiling", now_iso(), scan_id))
            conn.commit()

            # Transition: analyzing
            cursor.execute("UPDATE scans SET status = ?, updated_at = ? WHERE id = ?", ("analyzing", now_iso(), scan_id))
            conn.commit()
            conn.close()

        result = analyze_file(source_file, filename)

        conn = get_connection()
        cursor = conn.cursor()
        updated_at = now_iso()

        status = result["status"]
        error_msg = result.get("error_message")
        stdout = result.get("stdout")
        stderr = result.get("stderr")
        raw_report = json.dumps(result.get("raw_report")) if result.get("raw_report") else None
        duration_ms = result.get("duration_ms", 0)

        cursor.execute("""
        UPDATE scans 
        SET status = ?, error_message = ?, stdout = ?, stderr = ?, raw_report_json = ?, duration_ms = ?,
            compiler_version = ?, analyzer_version = ?, updated_at = ?
        WHERE id = ?
        """, (
            status, error_msg, stdout, stderr, raw_report, duration_ms,
            result.get("compiler_version"), result.get("analyzer_version"), updated_at, scan_id,
        ))

        # Insert findings
        for f in result.get("findings", []):
            finding_id = f"{scan_id}_{f.id}"
            cursor.execute("""
            INSERT OR REPLACE INTO findings (
                id, scan_id, detector_id, impact, confidence, message, file, start_line, end_line,
                start_col, end_col, explanation, recommendation, reference_url, raw_element_json
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                finding_id,
                scan_id,
                f.detector_id,
                f.impact,
                f.confidence,
                f.message,
                f.file,
                f.start_line,
                f.end_line,
                f.start_col,
                f.end_col,
                f.explanation,
                f.recommendation,
                f.reference_url,
                json.dumps(f.raw_element) if f.raw_element else None
            ))

        conn.commit()
        conn.close()
    except Exception as e:
        try:
            conn = get_connection()
            conn.execute(
                "UPDATE scans SET status = ?, error_message = ?, updated_at = ? WHERE id = ?",
                ("error", f"Worker failed: {str(e)[:300]}", now_iso(), scan_id),
            )
            conn.commit()
            conn.close()
        except Exception:
            pass
    finally:
        with _queue_lock:
            _queue_depth -= 1
        _active_slots.release()

def recover_interrupted_jobs():
    """Mark interrupted running jobs on system startup."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
    UPDATE scans 
    SET status = 'error', error_message = 'Job interrupted by server restart', updated_at = ?
    WHERE status IN ('queued', 'compiling', 'analyzing')
    """, (now_iso(),))
    conn.commit()
    conn.close()

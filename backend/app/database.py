# Purpose: Manage SQLite persistence for jobs, immutable revision references, validation, and incidents.
import sqlite3
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional, List, Dict, Any
from app.config import DB_PATH

def get_connection() -> sqlite3.Connection:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(DB_PATH), check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn

def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS scans (
        id TEXT PRIMARY KEY,
        filename TEXT NOT NULL,
        source_hash TEXT NOT NULL,
        source_code TEXT NOT NULL,
        status TEXT NOT NULL,
        error_message TEXT,
        stdout TEXT,
        stderr TEXT,
        raw_report_json TEXT,
        compiler_version TEXT,
        analyzer_version TEXT,
        duration_ms INTEGER,
        created_at TEXT NOT NULL,
        updated_at TEXT NOT NULL
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS findings (
        id TEXT PRIMARY KEY,
        scan_id TEXT NOT NULL,
        detector_id TEXT NOT NULL,
        impact TEXT NOT NULL,
        confidence TEXT NOT NULL,
        message TEXT NOT NULL,
        file TEXT NOT NULL,
        start_line INTEGER NOT NULL,
        end_line INTEGER NOT NULL,
        start_col INTEGER,
        end_col INTEGER,
        explanation TEXT NOT NULL,
        recommendation TEXT NOT NULL,
        reference_url TEXT,
        raw_element_json TEXT,
        FOREIGN KEY(scan_id) REFERENCES scans(id) ON DELETE CASCADE
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS patches (
        id TEXT PRIMARY KEY,
        scan_id TEXT NOT NULL,
        original_hash TEXT NOT NULL,
        candidate_hash TEXT NOT NULL,
        candidate_code TEXT NOT NULL,
        template_id TEXT NOT NULL,
        template_name TEXT NOT NULL,
        explanation TEXT NOT NULL,
        diff TEXT NOT NULL,
        is_accepted INTEGER NOT NULL DEFAULT 0,
        accepted_at TEXT,
        created_at TEXT NOT NULL,
        FOREIGN KEY(scan_id) REFERENCES scans(id) ON DELETE CASCADE
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS validation_runs (
        id TEXT PRIMARY KEY,
        patch_id TEXT NOT NULL,
        candidate_hash TEXT NOT NULL,
        check_type TEXT NOT NULL,
        status TEXT NOT NULL,
        duration_ms INTEGER NOT NULL,
        details TEXT NOT NULL,
        log_output TEXT,
        created_at TEXT NOT NULL,
        FOREIGN KEY(patch_id) REFERENCES patches(id) ON DELETE CASCADE
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS demo_runs (
        id TEXT PRIMARY KEY,
        status TEXT NOT NULL,
        rpc_url TEXT NOT NULL,
        chain_id INTEGER NOT NULL,
        original_vault TEXT NOT NULL,
        protected_vault TEXT NOT NULL,
        attacker TEXT NOT NULL,
        normal_user TEXT NOT NULL,
        transactions_json TEXT NOT NULL,
        balances_json TEXT NOT NULL,
        alert_json TEXT,
        is_historical INTEGER NOT NULL DEFAULT 0,
        logs TEXT,
        created_at TEXT NOT NULL
    )
    """)

    conn.commit()
    conn.close()
    conn = get_connection()
    try:
        migrate(conn)
    finally:
        conn.close()

SCHEMA_VERSION = 4  # v1: base; v2: schema_meta + source_revisions; v3: finding_reviews; v4: template cols + validation_parents + selections

def migrate(conn: sqlite3.Connection) -> int:
    """Idempotent versioned migration; safe to run on fresh DBs and repeats (T01.08)."""
    cur = conn.cursor()
    cur.execute("CREATE TABLE IF NOT EXISTS schema_meta (key TEXT PRIMARY KEY, value TEXT NOT NULL)")
    cur.execute("SELECT value FROM schema_meta WHERE key = 'version'")
    row = cur.fetchone()
    version = int(row["value"]) if row else 1
    cur.execute("""
    CREATE TABLE IF NOT EXISTS source_revisions (
        id TEXT PRIMARY KEY,
        byte_sha256 TEXT NOT NULL,
        byte_size INTEGER NOT NULL,
        artifact_id TEXT,
        display_name TEXT NOT NULL,
        kind TEXT NOT NULL,
        created_at TEXT NOT NULL
    )
    """)
    cur.execute("CREATE UNIQUE INDEX IF NOT EXISTS idx_revisions_sha ON source_revisions(byte_sha256)")
    if version < 3:
        cur.execute("""
        CREATE TABLE IF NOT EXISTS finding_reviews (
            scan_id TEXT NOT NULL,
            finding_key TEXT NOT NULL,
            state TEXT NOT NULL,
            reason TEXT NOT NULL DEFAULT '',
            reviewer TEXT,
            review_date TEXT,
            version INTEGER NOT NULL DEFAULT 1,
            updated_at TEXT NOT NULL,
            PRIMARY KEY (scan_id, finding_key)
        )
        """)
        cur.execute("INSERT OR REPLACE INTO schema_meta (key, value) VALUES ('version', '3')")
        version = 3
    if version < 4:
        # P06: template provenance on proposals; validation parent runs; single
        # selected revision per patch plus append-only selection history.
        existing_cols = {r["name"] for r in cur.execute("PRAGMA table_info(patches)").fetchall()}
        if "template_hash" not in existing_cols:
            cur.execute("ALTER TABLE patches ADD COLUMN template_hash TEXT")
        if "template_version" not in existing_cols:
            cur.execute("ALTER TABLE patches ADD COLUMN template_version TEXT")
        cur.execute("""
        CREATE TABLE IF NOT EXISTS validation_parents (
            run_id TEXT PRIMARY KEY,
            patch_id TEXT NOT NULL,
            candidate_hash TEXT NOT NULL,
            original_hash TEXT NOT NULL,
            harness_hash TEXT NOT NULL,
            tool_versions_json TEXT NOT NULL,
            fuzz_seed INTEGER NOT NULL,
            fuzz_runs INTEGER NOT NULL,
            status TEXT NOT NULL,
            eligible INTEGER NOT NULL DEFAULT 0,
            created_at TEXT NOT NULL,
            FOREIGN KEY(patch_id) REFERENCES patches(id) ON DELETE CASCADE
        )
        """)
        cur.execute("""
        CREATE TABLE IF NOT EXISTS patch_selections (
            patch_id TEXT PRIMARY KEY,
            selected TEXT NOT NULL,
            version INTEGER NOT NULL DEFAULT 1,
            acknowledged_unvalidated INTEGER NOT NULL DEFAULT 0,
            updated_at TEXT NOT NULL,
            FOREIGN KEY(patch_id) REFERENCES patches(id) ON DELETE CASCADE
        )
        """)
        cur.execute("""
        CREATE TABLE IF NOT EXISTS selection_events (
            id TEXT PRIMARY KEY,
            patch_id TEXT NOT NULL,
            action TEXT NOT NULL,
            previous TEXT,
            new_selected TEXT NOT NULL,
            acknowledged_unvalidated INTEGER NOT NULL DEFAULT 0,
            created_at TEXT NOT NULL,
            FOREIGN KEY(patch_id) REFERENCES patches(id) ON DELETE CASCADE
        )
        """)
        cur.execute("INSERT OR REPLACE INTO schema_meta (key, value) VALUES ('version', '4')")
        version = 4
    # Idempotent backfill on every startup: new legacy scans gain a revision row,
    # still marked legacy (no provenance upgrade by migration). INSERT OR IGNORE
    # keeps this safe for repeats.
    cur.execute("""
    INSERT OR IGNORE INTO source_revisions (id, byte_sha256, byte_size, display_name, kind, created_at)
    SELECT 'rev_' || substr(source_hash, 1, 16), source_hash, length(source_code), filename, 'legacy', created_at
    FROM scans
    """)
    conn.commit()
    return version

def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()

# Ensure schema exists on module load
init_db()

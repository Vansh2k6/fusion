# Purpose: Migration regression tests (P01.02, T01.07/T01.08).
import sqlite3
import app.database as database


def test_fresh_db_migrates_to_current_version(tmp_path, monkeypatch):
    db = tmp_path / "fresh.db"
    monkeypatch.setattr(database, "DB_PATH", db)
    database.init_db()
    conn = sqlite3.connect(str(db))
    version = conn.execute("SELECT value FROM schema_meta WHERE key='version'").fetchone()[0]
    assert version == str(database.SCHEMA_VERSION)
    conn.close()


def test_repeated_migration_succeeds_and_retains_rows(tmp_path, monkeypatch):
    db = tmp_path / "repeat.db"
    monkeypatch.setattr(database, "DB_PATH", db)
    database.init_db()
    conn = database.get_connection()
    conn.execute(
        "INSERT INTO scans (id, filename, source_hash, source_code, status, created_at, updated_at)"
        " VALUES ('s1', 'a.sol', 'ab', 'code', 'error', 't', 't')"
    )
    conn.commit()
    conn.close()
    database.init_db()  # repeat must succeed
    conn = database.get_connection()
    assert conn.execute("SELECT COUNT(*) FROM scans").fetchone()[0] == 1
    revs = conn.execute("SELECT byte_sha256, kind FROM source_revisions").fetchall()
    conn.close()
    assert ("ab", "legacy") in [(r[0], r[1]) for r in revs]  # legacy kept, marked legacy

# Purpose: Store immutable source and report artifacts in per-job directories with SHA-256 references.
import hashlib
import os
import re
from pathlib import Path
from typing import Tuple
from app.config import DATA_DIR, MAX_UPLOAD_SIZE

def compute_sha256(content: str | bytes) -> str:
    """Compute SHA-256 hex digest of source string or bytes."""
    if isinstance(content, str):
        content = content.encode("utf-8")
    return hashlib.sha256(content).hexdigest().lower()

def sanitize_filename(filename: str) -> str:
    """Strip dangerous characters and ensure a safe filename ending with .sol."""
    base = os.path.basename(filename)
    # Remove any traversal or control characters
    safe = re.sub(r"[^a-zA-Z0-9_\-\.]", "_", base)
    if not safe.endswith(".sol"):
        safe = safe + ".sol"
    return safe

def validate_source_safety(source_code: str) -> Tuple[bool, str]:
    """Validate size, import statements, and basic structural safety."""
    raw_bytes = source_code.encode("utf-8")
    if len(raw_bytes) > MAX_UPLOAD_SIZE:
        return False, f"File size ({len(raw_bytes)} bytes) exceeds 256 KiB limit."

    # Reject absolute path imports, traversal imports, remote URI imports
    lines = source_code.splitlines()
    for line in lines:
        stripped = line.strip()
        if stripped.startswith("import"):
            # Check for http://, https://, ipfs://, ftp://
            if re.search(r"['\"][a-zA-Z]+://", stripped):
                return False, f"Unsupported remote URI import found: {stripped}"
            # Check for path traversal (..)
            if ".." in stripped:
                return False, f"Relative path traversal import rejected: {stripped}"
            # Check for absolute path imports (/ or C:\)
            if re.search(r"['\"]([a-zA-Z]:|[\\/])", stripped):
                return False, f"Absolute path import rejected: {stripped}"

    return True, ""

def save_scan_artifact(scan_id: str, filename: str, source_code: str) -> Tuple[Path, str]:
    """Save original source immutably in a dedicated scan directory."""
    scan_dir = DATA_DIR / "scans" / scan_id
    scan_dir.mkdir(parents=True, exist_ok=True)

    safe_name = sanitize_filename(filename)
    source_file = scan_dir / safe_name
    
    # Write atomically
    tmp_file = scan_dir / f"{safe_name}.tmp"
    tmp_file.write_text(source_code, encoding="utf-8")
    tmp_file.replace(source_file)

    source_hash = compute_sha256(source_code)
    
    # Save hash file
    (scan_dir / "source.sha256").write_text(source_hash, encoding="utf-8")

    return source_file, source_hash

def get_scan_dir(scan_id: str) -> Path:
    scan_dir = (DATA_DIR / "scans" / scan_id).resolve()
    # Confinement check
    if not str(scan_dir).startswith(str((DATA_DIR / "scans").resolve())):
        raise ValueError("Path confinement violation")
    return scan_dir

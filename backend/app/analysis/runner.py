# Purpose: Execute Slither in an isolated subprocess with argument arrays and timeout controls.
import os
import subprocess
import json
import time
import psutil
from pathlib import Path
from typing import Dict, Any
from app.config import (
    SLITHER_BIN,
    ANALYSIS_TIMEOUT_SECONDS,
    MAX_REPORT_BYTES,
    MAX_TOOL_OUTPUT_BYTES,
)
from app.schemas import Finding
from app.analysis.normalize import normalize_slither_json
from app.tooling import observed_tool_versions

def kill_process_tree(pid: int):
    """Safely terminate a process and all its children."""
    try:
        parent = psutil.Process(pid)
        children = parent.children(recursive=True)
        processes = children + [parent]
        for process in processes:
            try:
                process.terminate()
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
        _gone, alive = psutil.wait_procs(processes, timeout=2)
        for p in alive:
            try:
                p.kill()
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
        if alive:
            psutil.wait_procs(alive, timeout=2)
    except (psutil.NoSuchProcess, psutil.AccessDenied):
        pass
    except psutil.TimeoutExpired:
        pass

def run_slither_analysis(source_file: Path, filename: str, timeout: int = ANALYSIS_TIMEOUT_SECONDS) -> Dict[str, Any]:
    """Execute Slither on a source file using safe subprocess argument arrays."""
    start_time = time.time()
    scan_dir = source_file.parent
    report_json_path = scan_dir / "slither_report.json"
    observed_versions = observed_tool_versions()

    # Fresh report per attempt: never read a stale report from an earlier attempt (T03.02).
    for stale in (report_json_path, scan_dir / "slither.stdout.log", scan_dir / "slither.stderr.log"):
        try:
            stale.unlink()
        except FileNotFoundError:
            pass

    def with_versions(result: Dict[str, Any]) -> Dict[str, Any]:
        result["compiler_version"] = observed_versions["solc"]
        result["analyzer_version"] = observed_versions["slither"]
        return result

    # Command arguments array with NO shell
    cmd = [
        SLITHER_BIN,
        str(source_file.resolve()),
        "--json",
        str(report_json_path.resolve()),
        "--fail-none",
        "--compile-force-framework",
        "solc",
        "--solc-disable-warnings"
    ]

    try:
        stdout_path = scan_dir / "slither.stdout.log"
        stderr_path = scan_dir / "slither.stderr.log"
        clean_env = {
            key: value for key, value in os.environ.items()
            if key.upper() in {
                "APPDATA", "LOCALAPPDATA", "PATH", "PATHEXT", "PROGRAMDATA",
                "PROGRAMFILES", "SYSTEMROOT", "TEMP", "TMP", "USERPROFILE", "WINDIR",
            }
        }
        with stdout_path.open("wb") as stdout_file, stderr_path.open("wb") as stderr_file:
            proc = subprocess.Popen(
                cmd,
                stdout=stdout_file,
                stderr=stderr_file,
                cwd=str(scan_dir.resolve()),
                env=clean_env,
            )

            try:
                proc.wait(timeout=timeout)
            except subprocess.TimeoutExpired:
                kill_process_tree(proc.pid)
                duration_ms = int((time.time() - start_time) * 1000)
                return with_versions({
                    "status": "timeout",
                    "error_message": f"Slither analysis timed out after {timeout} seconds.",
                    "stdout": "",
                    "stderr": "Analysis process tree killed due to timeout.",
                    "findings": [],
                    "raw_report": None,
                    "duration_ms": duration_ms
                })

        def read_bounded(path: Path) -> str:
            raw = path.read_bytes()
            suffix = b"\n[output truncated]" if len(raw) > MAX_TOOL_OUTPUT_BYTES else b""
            return (raw[:MAX_TOOL_OUTPUT_BYTES] + suffix).decode("utf-8", errors="replace")

        stdout = read_bounded(stdout_path)
        stderr = read_bounded(stderr_path)

        duration_ms = int((time.time() - start_time) * 1000)

        # Check if json report was generated
        if report_json_path.exists():
            try:
                if report_json_path.stat().st_size > MAX_REPORT_BYTES:
                    raise ValueError(f"Slither JSON report exceeds {MAX_REPORT_BYTES} byte limit")
                raw_json = json.loads(report_json_path.read_text(encoding="utf-8"))
                if not isinstance(raw_json, dict) or raw_json.get("success") is not True:
                    failure = raw_json.get("error") if isinstance(raw_json, dict) else None
                    raise ValueError(f"Slither reported unsuccessful analysis: {failure or 'unknown error'}")
                detectors = raw_json.get("results", {}).get("detectors")
                if not isinstance(detectors, list):
                    raise ValueError("Slither report is missing results.detectors list")
                findings = normalize_slither_json(raw_json, filename)
                return with_versions({
                    "status": "complete",
                    "error_message": None,
                    "stdout": stdout,
                    "stderr": stderr,
                    "findings": findings,
                    "raw_report": raw_json,
                    "duration_ms": duration_ms
                })
            except Exception as e:
                return with_versions({
                    "status": "error",
                    "error_message": f"Failed to parse Slither JSON output: {str(e)}",
                    "stdout": stdout,
                    "stderr": stderr,
                    "findings": [],
                    "raw_report": None,
                    "duration_ms": duration_ms
                })

        # If no json report was produced, inspect exit code and stderr for compilation or analyzer failures
        combined_err = (stderr + "\n" + stdout).strip()
        
        # Check for compilation error
        if "InvalidCompilation" in combined_err or "Error: Expected" in combined_err or "ParserError" in combined_err or "DeclarationError" in combined_err or "TypeError" in combined_err:
            clean_error = combined_err
            if "Invalid solc compilation" in combined_err:
                clean_error = combined_err.split("Invalid solc compilation")[-1].strip()
            return with_versions({
                "status": "error",
                "error_message": f"Compilation failed: {clean_error[:800]}",
                "stdout": stdout,
                "stderr": stderr,
                "findings": [],
                "raw_report": None,
                "duration_ms": duration_ms
            })

        # Check for unsupported compiler / imports
        if "Source file requires different compiler version" in combined_err or "Version constraint" in combined_err and "not supported" in combined_err:
            return with_versions({
                "status": "unsupported",
                "error_message": f"Unsupported compiler version: {combined_err[:400]}",
                "stdout": stdout,
                "stderr": stderr,
                "findings": [],
                "raw_report": None,
                "duration_ms": duration_ms
            })

        return with_versions({
            "status": "error",
            "error_message": f"Slither exited with code {proc.returncode}: {combined_err[:500]}",
            "stdout": stdout,
            "stderr": stderr,
            "findings": [],
            "raw_report": None,
            "duration_ms": duration_ms
        })

    except FileNotFoundError:
        return with_versions({
            "status": "error",
            "error_message": f"Slither executable '{SLITHER_BIN}' not found in environment.",
            "stdout": "",
            "stderr": "",
            "findings": [],
            "raw_report": None,
            "duration_ms": int((time.time() - start_time) * 1000)
        })
    except Exception as e:
        return with_versions({
            "status": "error",
            "error_message": f"Unexpected execution error: {str(e)}",
            "stdout": "",
            "stderr": "",
            "findings": [],
            "raw_report": None,
            "duration_ms": int((time.time() - start_time) * 1000)
        })

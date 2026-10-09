# Purpose: Expose Slither analysis adapter methods.
from pathlib import Path
from typing import Dict, Any
from app.analysis.runner import run_slither_analysis

def analyze_file(source_file: Path, filename: str, timeout: int = 60) -> Dict[str, Any]:
    return run_slither_analysis(source_file, filename, timeout=timeout)

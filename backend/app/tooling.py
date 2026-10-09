# Purpose: Observe local tool versions so reports distinguish configured expectations from actual executables.
import subprocess
from typing import Dict

from app.config import ANVIL_BIN, FORGE_BIN, PINNED_VERSIONS, SLITHER_BIN, SOLC_BIN


def _version(command: list[str], preferred_prefix: str | None = None) -> str:
    try:
        result = subprocess.run(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=10,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
        output = (result.stdout or result.stderr).strip()
        if result.returncode != 0 or not output:
            return "unavailable"
        lines = [line.strip() for line in output.splitlines() if line.strip()]
        if preferred_prefix:
            preferred = next((line for line in lines if line.startswith(preferred_prefix)), None)
            if preferred:
                return preferred
        return lines[0]
    except (OSError, subprocess.SubprocessError):
        return "unavailable"


def observed_tool_versions() -> Dict[str, str]:
    return {
        "solc": _version([SOLC_BIN, "--version"], preferred_prefix="Version:"),
        "slither": _version([SLITHER_BIN, "--version"]),
        "forge": _version([FORGE_BIN, "--version"]),
        "anvil": _version([ANVIL_BIN, "--version"]),
    }


def toolchain_status() -> Dict[str, object]:
    observed = observed_tool_versions()
    return {
        "expected": PINNED_VERSIONS,
        "observed": observed,
        "available": all(value != "unavailable" for value in observed.values()),
    }

# Purpose: Prevent clean-scan, hash-binding, and evidence-integrity regressions found during the audit.
import json
from pathlib import Path

from app.analysis import runner
from app.patches.validation import _prepare_workspace


def test_unsuccessful_slither_json_is_never_a_clean_scan(tmp_path, monkeypatch):
    source = tmp_path / "Example.sol"
    source.write_text("pragma solidity ^0.8.20; contract Example {}", encoding="utf-8")

    class FakeProcess:
        returncode = 0
        pid = 999999

        def __init__(self, command, **_kwargs):
            report_path = Path(command[command.index("--json") + 1])
            report_path.write_text(
                json.dumps({"success": False, "error": "compiler failed", "results": {}}),
                encoding="utf-8",
            )

        def wait(self, timeout):
            return 0

    monkeypatch.setattr(runner, "observed_tool_versions", lambda: {
        "solc": "test-solc", "slither": "test-slither", "forge": "n/a", "anvil": "n/a"
    })
    monkeypatch.setattr(runner.subprocess, "Popen", FakeProcess)

    result = runner.run_slither_analysis(source, source.name)
    assert result["status"] == "error"
    assert result["findings"] == []
    assert "unsuccessful analysis" in result["error_message"]


def test_candidate_hash_mismatch_is_refused_before_validation():
    workspace, error = _prepare_workspace(
        "val_hash_mismatch_regression",
        "pragma solidity ^0.8.20; contract Candidate {}",
        "0" * 64,
    )
    assert workspace is None
    assert "hash does not match" in error

# Purpose: Analyzer-adapter regression tests (P03.01, T03.02–T03.04).
import json
from pathlib import Path

from app.analysis import runner
from app.analysis.normalize import normalize_slither_json


def test_stale_report_from_failed_attempt_never_read(tmp_path, monkeypatch):
    source = tmp_path / "Example.sol"
    source.write_text("pragma solidity ^0.8.20; contract Example {}", encoding="utf-8")
    # Plant a stale successful report simulating a failed earlier attempt's leftover.
    (tmp_path / "slither_report.json").write_text(
        json.dumps({"success": True, "results": {"detectors": []}}), encoding="utf-8"
    )

    class MissingBinary:
        def __init__(self, *a, **k):
            raise FileNotFoundError("no such binary")

    monkeypatch.setattr(runner.subprocess, "Popen", MissingBinary)
    result = runner.run_slither_analysis(source, source.name)
    assert result["status"] == "error"  # stale success must not surface as complete
    assert result["findings"] == []


def test_unicode_multiline_ranges_preserved():
    raw = {
        "results": {
            "detectors": [
                {
                    "check": "reentrancy-eth",
                    "impact": "High",
                    "confidence": "Medium",
                    "description": "Reentrancy in Vault.withdraw (linecaf\u00e9 \u2614)",
                    "reference": "https://example.invalid/r",
                    "elements": [
                        {
                            "source_mapping": {
                                "lines": [18, 19, 20],
                                "starting_column": 5,
                                "ending_column": 42,
                                "filename_short": "Vault.sol",
                            }
                        }
                    ],
                }
            ]
        }
    }
    findings = normalize_slither_json(raw, "Vault.sol")
    assert len(findings) == 1
    f = findings[0]
    assert (f.start_line, f.end_line) == (18, 20)
    assert "caf\u00e9" in f.message  # Unicode display data retained, not mangled
    assert f.file == "Vault.sol"


def test_unknown_detector_gets_guidance_not_silence():
    raw = {
        "results": {
            "detectors": [
                {
                    "check": "some-future-detector",
                    "impact": "Low",
                    "confidence": "Low",
                    "description": "Something new.",
                    "elements": [],
                }
            ]
        }
    }
    findings = normalize_slither_json(raw, "X.sol")
    assert len(findings) == 1  # preserved, not dropped
    assert findings[0].recommendation  # unknown detector still carries guidance
    assert findings[0].start_line == 1  # missing location degrades to file top, stays listed

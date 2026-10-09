# Purpose: Normalize raw Slither JSON results into typed, consistent findings.
from typing import Dict, Any, List, Optional
from app.schemas import Finding

EXPLANATIONS = {
    "reentrancy-eth": {
        "explanation": "State variable is modified after an external call, allowing re-entrant execution to drain funds before accounting is finalized.",
        "recommendation": "Adopt the Checks-Effects-Interactions (CEI) pattern: update internal state before calling external addresses, or add a reentrancy guard."
    },
    "reentrancy-events": {
        "explanation": "Event emission occurs after external call, which can produce misordered event logs during reentrancy.",
        "recommendation": "Emit events before external calls alongside state mutations."
    },
    "low-level-calls": {
        "explanation": "Low-level .call() forwards arbitrary gas and execution flow to an untrusted recipient without compile-time interface checks.",
        "recommendation": "Always check the returned boolean and sanitize caller inputs."
    },
    "solc-version": {
        "explanation": "The solc pragma matches compiler versions with documented bugs or security advisories.",
        "recommendation": "Review known compiler issues or update pragma to an audited release."
    }
}

def normalize_slither_json(raw_data: Dict[str, Any], filename: str) -> List[Finding]:
    findings: List[Finding] = []
    
    results = raw_data.get("results", {})
    detectors = results.get("detectors", [])
    
    for idx, d in enumerate(detectors):
        check = d.get("check", "unknown")
        impact = d.get("impact", "Informational")
        confidence = d.get("confidence", "Medium")
        description = d.get("description", "").strip()
        ref_url = d.get("reference")
        
        # Determine source location
        elements = d.get("elements", [])
        start_line = 1
        end_line = 1
        start_col = None
        end_col = None
        target_file = filename
        
        for el in elements:
            src_map = el.get("source_mapping", {})
            if src_map:
                lines = src_map.get("lines", [])
                if lines:
                    start_line = min(lines)
                    end_line = max(lines)
                    start_col = src_map.get("starting_column")
                    end_col = src_map.get("ending_column")
                    target_file = src_map.get("filename_short", filename)
                    break
                    
        # Explanation & Recommendation
        preset = EXPLANATIONS.get(check)
        if preset:
            explanation = preset["explanation"]
            recommendation = preset["recommendation"]
        else:
            first_line = description.split("\n")[0] if description else f"Detector {check} triggered."
            explanation = first_line
            recommendation = f"Inspect {check} according to Crytic detector guidelines ({ref_url or 'crytic/slither'})."
            
        finding = Finding(
            id=f"{check}_{idx}_{start_line}",
            detector_id=check,
            impact=impact,
            confidence=confidence,
            message=description,
            file=target_file,
            start_line=start_line,
            end_line=end_line,
            start_col=start_col,
            end_col=end_col,
            explanation=explanation,
            recommendation=recommendation,
            reference_url=ref_url,
            raw_element=elements[0] if elements else None
        )
        findings.append(finding)
        
    return findings

# Purpose: Define validated API models for scans, findings, patch revisions, checks, and demo evidence.
from __future__ import annotations
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

class Finding(BaseModel):
    id: Optional[str] = None
    detector_id: str
    impact: str  # High, Medium, Low, Informational, Optimization
    confidence: str  # High, Medium, Low
    message: str
    file: str
    start_line: int
    end_line: int
    start_col: Optional[int] = None
    end_col: Optional[int] = None
    explanation: str
    recommendation: str
    reference_url: Optional[str] = None
    raw_element: Optional[Dict[str, Any]] = None

class CreateScanRequest(BaseModel):
    source_code: Optional[str] = None
    filename: Optional[str] = "contract.sol"
    fixture_id: Optional[str] = None

class ScanResponse(BaseModel):
    id: str
    filename: str
    source_hash: str
    source_code: str
    status: str  # queued, compiling, analyzing, complete, error, unsupported, timeout
    error_message: Optional[str] = None
    findings: List[Finding] = []
    compiler_version: Optional[str] = None
    analyzer_version: Optional[str] = None
    duration_ms: Optional[int] = None
    created_at: str
    updated_at: str

class ScanExport(BaseModel):
    export_version: str = "1.0.0"
    exported_at: str
    scan_id: str
    filename: str
    source_hash: str
    tool_versions: Dict[str, str]
    status: str
    findings_count: int
    findings: List[Finding]
    raw_diagnostics: Optional[Dict[str, Any]] = None

class PatchResponse(BaseModel):
    id: str
    scan_id: str
    original_hash: str
    candidate_hash: str
    candidate_code: str
    template_id: str
    template_name: str
    template_hash: Optional[str] = None
    template_version: Optional[str] = None
    explanation: str
    diff: str
    is_accepted: bool
    accepted_at: Optional[str] = None
    created_at: str

class ValidationCheck(BaseModel):
    check_type: str  # compile, rescan, attack_exploit, normal_behavior
    status: str      # passed, failed, skipped, unsupported, timeout
    duration_ms: int
    details: str
    log_output: Optional[str] = None

class ValidationResponse(BaseModel):
    id: str
    patch_id: str
    candidate_hash: str
    checks: List[ValidationCheck]
    all_passed: bool
    created_at: str

class TxReceipt(BaseModel):
    label: str
    tx_hash: str
    from_address: str
    to_address: Optional[str] = None
    status: str  # success, reverted
    gas_used: str
    fee_wei: Optional[str] = None  # actual fee paid; reverted txs still pay (R11)
    revert_reason: Optional[str] = None

class BalanceDelta(BaseModel):
    address: str
    label: str
    before_wei: str
    after_wei: str
    delta_wei: str

class IncidentAlert(BaseModel):
    severity: str  # high, medium, low, info
    title: str
    observation: str
    hypothesis: str
    suggested_action: str

class DemoRunResponse(BaseModel):
    id: str
    status: str  # running, complete, error, historical
    rpc_url: str
    chain_id: int
    original_vault: str
    protected_vault: str
    attacker: str
    normal_user: str
    transactions: List[TxReceipt]
    balances: List[BalanceDelta]
    alert: Optional[IncidentAlert] = None
    is_historical: bool = False
    created_at: str
    logs: Optional[str] = None

class FixtureInfo(BaseModel):
    id: str
    name: str
    hash: str
    description: str
    expected_detector: Optional[str] = None
    source_code: Optional[str] = None

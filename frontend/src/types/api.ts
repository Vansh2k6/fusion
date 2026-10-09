// Purpose: Define frontend request/response types matching backend schemas for scans, revisions, and demo evidence.

export type ScanStatus = 'queued' | 'compiling' | 'analyzing' | 'complete' | 'error' | 'unsupported' | 'timeout';
export type CheckStatus = 'passed' | 'failed' | 'skipped' | 'unsupported' | 'timeout';

export interface Finding {
  id?: string;
  detector_id: string;
  impact: 'High' | 'Medium' | 'Low' | 'Informational' | 'Optimization' | string;
  confidence: 'High' | 'Medium' | 'Low' | string;
  message: string;
  file: string;
  start_line: number;
  end_line: number;
  start_col?: number;
  end_col?: number;
  explanation: string;
  recommendation: string;
  reference_url?: string;
}

export interface ScanResponse {
  id: string;
  filename: string;
  source_hash: string;
  source_code: string;
  status: ScanStatus;
  error_message?: string;
  findings: Finding[];
  compiler_version?: string;
  analyzer_version?: string;
  duration_ms?: number;
  created_at: string;
  updated_at: string;
}

export interface ScanExport {
  export_version: string;
  exported_at: string;
  scan_id: string;
  filename: string;
  source_hash: string;
  tool_versions: Record<string, string>;
  status: string;
  findings_count: number;
  findings: Finding[];
  raw_diagnostics?: Record<string, unknown>;
}

export interface FixtureInfo {
  id: string;
  name: string;
  hash: string;
  description: string;
  expected_detector?: string;
  source_code?: string;
}

export interface PatchResponse {
  id: string;
  scan_id: string;
  original_hash: string;
  candidate_hash: string;
  candidate_code: string;
  template_id: string;
  template_name: string;
  template_hash?: string;
  template_version?: string;
  explanation: string;
  diff: string;
  is_accepted: boolean;
  accepted_at?: string;
  created_at: string;
}

export interface ValidationStatus {
  run_id: string | null;
  eligible: boolean;
  harness_matches: boolean;
  parent_harness_hash: string | null;
  current_harness_hash: string;
  fuzz_seed: number | null;
  fuzz_runs: number | null;
}

export interface ValidationCheck {
  check_type: 'compile' | 'rescan' | 'attack_exploit' | 'normal_behavior' | string;
  status: CheckStatus;
  duration_ms: number;
  details: string;
  log_output?: string;
}

export interface ValidationResponse {
  id: string;
  patch_id: string;
  candidate_hash: string;
  checks: ValidationCheck[];
  all_passed: boolean;
  created_at: string;
}

export interface TxReceipt {
  label: string;
  tx_hash: string;
  from_address: string;
  to_address?: string;
  status: 'success' | 'reverted' | string;
  gas_used: string;
  fee_wei?: string;
  revert_reason?: string;
}

export interface BalanceDelta {
  address: string;
  label: string;
  before_wei: string;
  after_wei: string;
  delta_wei: string;
}

export interface IncidentAlert {
  severity: 'high' | 'medium' | 'low' | 'info' | string;
  title: string;
  observation: string;
  hypothesis: string;
  suggested_action: string;
}

export interface DemoRunResponse {
  id: string;
  status: 'running' | 'complete' | 'error' | 'historical' | string;
  rpc_url: string;
  chain_id: number;
  original_vault: string;
  protected_vault: string;
  attacker: string;
  normal_user: string;
  transactions: TxReceipt[];
  balances: BalanceDelta[];
  alert?: IncidentAlert;
  is_historical: boolean;
  created_at: string;
  logs?: string;
}

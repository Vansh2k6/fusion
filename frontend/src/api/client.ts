// Purpose: Provide typed calls to the local FastAPI service, including polling and report downloads.
import {
  FixtureInfo,
  ScanResponse,
  ScanExport,
  PatchResponse,
  ValidationResponse,
  DemoRunResponse
} from '../types/api';

const API_BASE = '/api';

export async function fetchFixtures(): Promise<FixtureInfo[]> {
  const res = await fetch(`${API_BASE}/fixtures`);
  if (!res.ok) throw new Error(`Failed to load fixtures: ${res.statusText}`);
  return res.json();
}

export async function createScanWithFixture(fixture_id: string): Promise<ScanResponse> {
  const formData = new FormData();
  formData.append('fixture_id', fixture_id);
  const res = await fetch(`${API_BASE}/scans`, {
    method: 'POST',
    body: formData
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(err.detail || 'Scan creation failed');
  }
  return res.json();
}

export async function createScanWithCode(filename: string, source_code: string): Promise<ScanResponse> {
  const formData = new FormData();
  formData.append('filename', filename);
  formData.append('source_code', source_code);
  const res = await fetch(`${API_BASE}/scans`, {
    method: 'POST',
    body: formData
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(err.detail || 'Scan creation failed');
  }
  return res.json();
}

export async function createScanWithFile(file: File): Promise<ScanResponse> {
  const formData = new FormData();
  formData.append('file', file);
  const res = await fetch(`${API_BASE}/scans`, {
    method: 'POST',
    body: formData
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(err.detail || 'Upload scan creation failed');
  }
  return res.json();
}

export async function getScan(scanId: string): Promise<ScanResponse> {
  const res = await fetch(`${API_BASE}/scans/${scanId}`);
  if (!res.ok) throw new Error(`Failed to get scan: ${res.statusText}`);
  return res.json();
}

export async function listScans(limit = 20, offset = 0): Promise<ScanResponse[]> {
  const res = await fetch(`${API_BASE}/scans?limit=${limit}&offset=${offset}`);
  if (!res.ok) throw new Error(`Failed to list scans: ${res.statusText}`);
  return res.json();
}

export async function exportScan(scanId: string): Promise<ScanExport> {
  const res = await fetch(`${API_BASE}/scans/${scanId}/export`);
  if (!res.ok) throw new Error(`Failed to export scan: ${res.statusText}`);
  return res.json();
}

export async function proposePatch(scanId: string): Promise<PatchResponse> {
  const res = await fetch(`${API_BASE}/scans/${scanId}/patches`, {
    method: 'POST'
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(err.detail || 'Patch proposal unavailable');
  }
  return res.json();
}

export async function getPatch(patchId: string): Promise<PatchResponse> {
  const res = await fetch(`${API_BASE}/patches/${patchId}`);
  if (!res.ok) throw new Error(`Failed to get patch: ${res.statusText}`);
  return res.json();
}

export async function validatePatch(patchId: string): Promise<ValidationResponse> {
  const res = await fetch(`${API_BASE}/patches/${patchId}/validate`, {
    method: 'POST'
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(err.detail || 'Patch validation failed');
  }
  return res.json();
}

export async function acceptPatch(patchId: string, acknowledgedUnvalidated = false): Promise<PatchResponse> {
  const res = await fetch(`${API_BASE}/patches/${patchId}/accept?acknowledged_unvalidated=${acknowledgedUnvalidated}`, {
    method: 'POST'
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(err.detail || 'Failed to accept patch');
  }
  return res.json();
}

export async function revokePatch(patchId: string): Promise<PatchResponse> {
  const res = await fetch(`${API_BASE}/patches/${patchId}/revoke`, {
    method: 'POST'
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(err.detail || 'Failed to revoke patch');
  }
  return res.json();
}

export async function exportPatch(patchId: string): Promise<unknown> {
  const res = await fetch(`${API_BASE}/patches/${patchId}/export`);
  if (!res.ok) throw new Error(`Failed to export patch: ${res.statusText}`);
  return res.json();
}

export async function runDemo(): Promise<DemoRunResponse> {
  const res = await fetch(`${API_BASE}/demo/runs`, {
    method: 'POST'
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(err.detail || 'Demo simulation failed');
  }
  return res.json();
}

export async function getDemoRun(runId: string): Promise<DemoRunResponse> {
  const res = await fetch(`${API_BASE}/demo/runs/${runId}`);
  if (!res.ok) throw new Error(`Failed to fetch demo run: ${res.statusText}`);
  return res.json();
}

export async function listDemoRuns(): Promise<DemoRunResponse[]> {
  const res = await fetch(`${API_BASE}/demo/runs`);
  if (!res.ok) throw new Error(`Failed to list demo runs: ${res.statusText}`);
  return res.json();
}

export async function resetDemo(): Promise<{ status: string; message: string }> {
  const res = await fetch(`${API_BASE}/demo/reset`, {
    method: 'POST'
  });
  if (!res.ok) throw new Error(`Failed to reset demo: ${res.statusText}`);
  return res.json();
}

export async function getValidationStatus(patchId: string): Promise<import('../types/api').ValidationStatus> {
  const res = await fetch(`${API_BASE}/patches/${patchId}/validation-status`);
  if (!res.ok) throw new Error(`Failed to get validation status: ${res.statusText}`);
  return res.json();
}

export interface Review {
  scan_id: string;
  finding_key: string;
  state: 'open' | 'triaged' | 'in_progress' | 'resolved' | 'canceled' | string;
  reason: string;
  reviewer?: string;
  review_date?: string;
  version: number;
  updated_at: string;
}

export interface DashboardData {
  open_review_findings: { value: number | null; scope: string };
  recorded_incidents: { value: number | null; scope: string };
  required_checks: { passed: number; required: number; profile: string; scope: string };
  validation_duration_ms: { value: number | null; scope: string };
  activity: { id: string; kind: string; title: string; ref: string; created_at: string }[];
}

export async function getReviews(scanId: string): Promise<Review[]> {
  const res = await fetch(`${API_BASE}/scans/${scanId}/reviews`);
  if (!res.ok) throw new Error(`Failed to load reviews: ${res.statusText}`);
  return res.json();
}

export async function updateReview(scanId: string, key: string, body: { state: string; reason?: string; reviewer?: string; review_date?: string; version: number }): Promise<Review> {
  const res = await fetch(`${API_BASE}/scans/${scanId}/reviews/${encodeURIComponent(key)}`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body)
  });
  if (res.status === 409) throw new Error('This review changed elsewhere. Reload and retry.');
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(err.detail || 'Review update failed');
  }
  return res.json();
}

export async function fetchDashboard(): Promise<DashboardData> {
  const res = await fetch(`${API_BASE}/dashboard`);
  if (!res.ok) throw new Error(`Dashboard unavailable: ${res.statusText}`);
  return res.json();
}

export interface Capabilities {
  ready: boolean;
  observed_tool_versions: Record<string, string>;
  worker_mode: string;
  arbitrary_upload_available: boolean;
  [k: string]: unknown;
}

export async function fetchCapabilities(): Promise<Capabilities> {
  const res = await fetch(`${API_BASE}/capabilities`);
  if (!res.ok) throw new Error(`Capabilities unavailable: ${res.statusText}`);
  return res.json();
}

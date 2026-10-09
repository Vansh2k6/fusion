// Purpose: Patch proposal review (P06.01/P06.03): hash-bound diff, validation results,
// independent selection with explicit unvalidated acknowledgment, eligibility-gated replay.
import React, { useState, useEffect } from 'react';
import { ScanResponse, PatchResponse, ValidationResponse, ValidationStatus } from '../types/api';
import { proposePatch, validatePatch, acceptPatch, revokePatch, exportPatch, getValidationStatus } from '../api/client';
import {
  GitCommit,
  CheckCircle2,
  ShieldCheck,
  Download,
  ArrowRight,
  RotateCcw,
  Check,
  AlertTriangle,
  FileDiff
} from 'lucide-react';

interface PatchReviewProps {
  scan: ScanResponse | null;
  onNavigateToDemo: () => void;
}

export const PatchReview: React.FC<PatchReviewProps> = ({ scan, onNavigateToDemo }) => {
  const [patch, setPatch] = useState<PatchResponse | null>(null);
  const [validation, setValidation] = useState<ValidationResponse | null>(null);
  const [status, setStatus] = useState<ValidationStatus | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [isValidating, setIsValidating] = useState<boolean>(false);
  const [isAccepting, setIsAccepting] = useState<boolean>(false);
  const [ackUnvalidated, setAckUnvalidated] = useState<boolean>(false);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);
  const [actionMsg, setActionMsg] = useState<string | null>(null);

  useEffect(() => {
    setPatch(null);
    setValidation(null);
    setStatus(null);
    setAckUnvalidated(false);
    if (scan && scan.status === 'complete') {
      loadPatch();
    }
  }, [scan?.id]); // eslint-disable-line react-hooks/exhaustive-deps

  const loadPatch = async () => {
    if (!scan) return;
    setIsLoading(true);
    setErrorMsg(null);
    try {
      const p = await proposePatch(scan.id);
      setPatch(p);
      try {
        setStatus(await getValidationStatus(p.id));
      } catch {
        setStatus(null);
      }
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : 'No patch template available';
      setErrorMsg(msg);
      setPatch(null);
    } finally {
      setIsLoading(false);
    }
  };

  const handleValidate = async () => {
    if (!patch) return;
    setIsValidating(true);
    setActionMsg(null);
    try {
      const v = await validatePatch(patch.id);
      setValidation(v);
      setStatus(await getValidationStatus(patch.id));
    } catch (err: unknown) {
      setActionMsg(err instanceof Error ? err.message : 'Validation failed');
    } finally {
      setIsValidating(false);
    }
  };

  const handleAccept = async () => {
    if (!patch) return;
    setIsAccepting(true);
    setActionMsg(null);
    try {
      const updated = await acceptPatch(patch.id, ackUnvalidated);
      setPatch(updated);
      if (ackUnvalidated && !(status?.eligible)) {
        setActionMsg('Candidate selected without passing validation. Validated replay stays disabled.');
      }
    } catch (err: unknown) {
      setActionMsg(err instanceof Error ? err.message : 'Accept failed');
    } finally {
      setIsAccepting(false);
    }
  };

  const handleRevoke = async () => {
    if (!patch) return;
    try {
      const updated = await revokePatch(patch.id);
      setPatch(updated);
      setAckUnvalidated(false);
      setActionMsg(null);
    } catch (err: unknown) {
      setActionMsg(err instanceof Error ? err.message : 'Revoke failed');
    }
  };

  const handleExportPatch = async () => {
    if (!patch) return;
    try {
      const data = await exportPatch(patch.id);
      const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `candidate-patch-${patch.id}.json`;
      a.click();
      URL.revokeObjectURL(url);
    } catch (err: unknown) {
      setActionMsg(err instanceof Error ? err.message : 'Export failed');
    }
  };

  if (!scan) {
    return (
      <div className="card" style={{ textAlign: 'center', padding: '3.5rem 2rem' }}>
        <GitCommit size={40} style={{ color: 'var(--text-muted)', marginBottom: '1rem', strokeWidth: 1.5 }} />
        <h3 style={{ color: 'var(--text-primary)', fontSize: '1.1rem', fontWeight: 700 }}>No Active Scan Selected</h3>
        <p style={{ color: 'var(--text-secondary)', marginTop: '0.5rem', fontSize: '0.88rem' }}>
          Please scan a contract first to review applicable candidate patches.
        </p>
      </div>
    );
  }

  if (isLoading) {
    return (
      <div className="card" style={{ textAlign: 'center', padding: '3.5rem 2rem' }}>
        <p className="animate-pulse" style={{ color: 'var(--color-accent-primary)', fontWeight: 600 }}>
          Checking candidate patch template preconditions and hashes...
        </p>
      </div>
    );
  }

  if (errorMsg || !patch) {
    return (
      <div className="card">
        <div className="card-header">
          <div>
            <h2 className="card-title">
              <ShieldCheck size={18} style={{ color: 'var(--color-info)' }} />
              Reviewed Mitigation Patch
            </h2>
            <p className="card-subtitle">Template Verification Boundary</p>
          </div>
          <span className="badge badge-info">
            <span className="badge-dot" />
            Guidance Only
          </span>
        </div>
        <div className="alert-box warning">
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', fontWeight: 700 }}>
            <AlertTriangle size={16} /> Automatic patch template unavailable
          </div>
          <p style={{ marginTop: '0.35rem', fontSize: '0.85rem' }}>
            {errorMsg || 'The scanned contract does not match our reviewed vault template hash. In accordance with Rule R05, arbitrary contracts receive scanner findings and guidance only rather than unverified auto-patches.'}
          </p>
        </div>
        <p style={{ fontSize: '0.85rem', color: 'var(--text-secondary)' }}>
          To demonstrate the complete patch review and validation workflow, select the curated <code>VulnerableVault.sol</code> fixture in New scan.
        </p>
      </div>
    );
  }

  const eligible = status?.eligible === true;

  return (
    <div>
      {/* Overview Card */}
      <div className="card">
        <div className="card-header">
          <div>
            <h2 className="card-title">
              <ShieldCheck size={18} style={{ color: 'var(--color-accent-primary)' }} />
              Reviewed Candidate Patch &amp; Validation
            </h2>
            <p className="card-subtitle">{patch.template_name}</p>
          </div>
          <div style={{ display: 'flex', gap: '0.75rem', alignItems: 'center', flexWrap: 'wrap' }}>
            {patch.is_accepted ? (
              <span className="badge badge-success" style={{ padding: '0.35rem 0.75rem', fontSize: '0.78rem' }}>
                <span className="badge-dot" />
                Candidate selected {patch.accepted_at ? `(${new Date(patch.accepted_at).toLocaleTimeString()})` : ''}
              </span>
            ) : (
              <span className="badge badge-info" style={{ padding: '0.35rem 0.75rem', fontSize: '0.78rem' }}>
                <span className="badge-dot" />
                Original selected
              </span>
            )}
            <span className={`badge ${eligible ? 'badge-success' : 'badge-high'}`}>
              <span className="badge-dot" />
              {eligible ? 'Validation eligible' : 'Not validated'}
            </span>
            <button
              className="btn btn-secondary"
              onClick={handleExportPatch}
            >
              <Download size={14} /> Export Patch Package
            </button>
            <button
              className="btn btn-primary"
              onClick={onNavigateToDemo}
              disabled={!eligible}
              title={eligible ? 'Open the local replay for this validated candidate' : 'Validated replay needs every required check passed for these exact bytes'}
            >
              Replay Attack on Local Chain <ArrowRight size={14} />
            </button>
          </div>
        </div>

        <div className="metadata-strip" style={{ fontSize: '0.78rem', marginBottom: '1rem' }}>
          <div><strong>Template:</strong> {patch.template_id} v{patch.template_version || 'unknown'}</div>
          <div><strong>Original:</strong> <span style={{ fontFamily: 'var(--font-mono)' }}>{patch.original_hash.slice(0, 16)}…</span></div>
          <div><strong>Candidate:</strong> <span style={{ fontFamily: 'var(--font-mono)' }}>{patch.candidate_hash.slice(0, 16)}…</span></div>
          {status && <div><strong>Fuzz:</strong> {status.fuzz_runs} runs · seed {status.fuzz_seed}</div>}
        </div>

        {actionMsg && (
          <div className="alert-box warning" role="status" style={{ marginBottom: '1rem' }}>{actionMsg}</div>
        )}

        {/* Accept / Revoke Controls */}
        <div style={{ display: 'flex', gap: '1rem', alignItems: 'center', flexWrap: 'wrap' }}>
          {!patch.is_accepted ? (
            <>
              <button
                className="btn btn-accent"
                onClick={handleAccept}
                disabled={isAccepting || (!eligible && !ackUnvalidated)}
              >
                <Check size={14} /> {isAccepting ? 'Selecting…' : 'Select Candidate Revision'}
              </button>
              {!eligible && (
                <label style={{ fontSize: '0.82rem', color: 'var(--text-secondary)', display: 'flex', gap: '0.4rem', alignItems: 'center' }}>
                  <input type="checkbox" checked={ackUnvalidated} onChange={e => setAckUnvalidated(e.target.checked)} />
                  Select without passing validation (replay stays disabled)
                </label>
              )}
            </>
          ) : (
            <button
              className="btn btn-danger"
              onClick={handleRevoke}
            >
              <RotateCcw size={14} /> Revoke Candidate (Restore Original)
            </button>
          )}

          <button
            className="btn btn-primary"
            onClick={handleValidate}
            disabled={isValidating}
          >
            <ShieldCheck size={14} />
            {isValidating ? 'Running Validation Suite...' : 'Run Candidate Validation'}
          </button>
        </div>
        <p style={{ fontSize: '0.78rem', color: 'var(--text-muted)', marginTop: '0.5rem' }}>
          Selection and validation are independent: selecting never turns a failed or unrun check green.
        </p>
      </div>

      {/* Validation Results Card */}
      {validation && (
        <div className="card">
          <div className="card-header">
            <h3 className="card-title">
              <CheckCircle2 size={18} style={{ color: validation.all_passed ? 'var(--color-success)' : 'var(--color-danger)' }} />
              Validation results
            </h3>
            <span className={`badge ${validation.all_passed ? 'badge-success' : 'badge-high'}`}>
              <span className="badge-dot" />
              {validation.all_passed ? 'ALL REQUIRED CHECKS PASSED' : 'CHECK FAILURE DETECTED'}
            </span>
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))', gap: '1rem', marginBottom: '1rem' }}>
            {validation.checks.map((chk, idx) => (
              <div
                key={idx}
                style={{
                  background: 'var(--bg-tertiary)',
                  border: `1px solid ${chk.status === 'passed' ? 'rgba(22, 163, 74, 0.4)' : chk.status === 'skipped' ? 'rgba(150, 149, 145, 0.4)' : 'rgba(232, 70, 26, 0.4)'}`,
                  borderRadius: 'var(--radius-sm)',
                  padding: '1rem'
                }}
              >
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.4rem' }}>
                  <span style={{ fontWeight: 700, fontSize: '0.85rem', textTransform: 'capitalize', color: 'var(--text-primary)' }}>
                    {chk.check_type.replace('_', ' ')}
                  </span>
                  <span className={`badge ${chk.status === 'passed' ? 'badge-success' : 'badge-high'}`}>
                    <span className="badge-dot" />
                    {chk.status}
                  </span>
                </div>
                <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginBottom: '0.5rem', fontFamily: 'var(--font-mono)' }}>
                  Duration: {chk.duration_ms} ms
                </div>
                <p style={{ fontSize: '0.82rem', color: 'var(--text-secondary)', lineHeight: 1.45 }}>
                  {chk.details}
                </p>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Unified Diff View */}
      <div className="card">
        <div className="card-header">
          <h3 className="card-title">
            <FileDiff size={18} style={{ color: 'var(--color-accent-primary)' }} />
            Proposed Changes (Unified Diff)
          </h3>
          <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
            Reordering state updates before msg.sender.call
          </span>
        </div>

        <div className="diff-viewer" role="region" aria-label="Candidate diff" tabIndex={0}>
          {patch.diff.split('\n').map((dLine, idx) => {
            let className = '';
            if (dLine.startsWith('+') && !dLine.startsWith('+++')) className = 'diff-add';
            else if (dLine.startsWith('-') && !dLine.startsWith('---')) className = 'diff-del';
            else if (dLine.startsWith('@@') || dLine.startsWith('---') || dLine.startsWith('+++')) className = 'diff-header';
            return (
              <div key={idx} className={className}>
                {dLine || ' '}
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
};

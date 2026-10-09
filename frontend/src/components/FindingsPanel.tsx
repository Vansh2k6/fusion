import React, { useState } from 'react';
import { ScanResponse, Finding } from '../types/api';
import { exportScan } from '../api/client';
import {
  ShieldAlert,
  Download,
  ArrowRight,
  ExternalLink,
  Code2,
  CheckCircle2,
  AlertCircle,
  FileCode2,
  Sparkles
} from 'lucide-react';

interface FindingsPanelProps {
  scan: ScanResponse | null;
  onNavigateToPatch: () => void;
}

export const FindingsPanel: React.FC<FindingsPanelProps> = ({ scan, onNavigateToPatch }) => {
  const [selectedFinding, setSelectedFinding] = useState<Finding | null>(null);
  const [isExporting, setIsExporting] = useState<boolean>(false);

  React.useEffect(() => {
    if (scan && scan.findings.length > 0 && !selectedFinding) {
      setSelectedFinding(scan.findings[0]);
    }
  }, [scan, selectedFinding]);

  if (!scan) {
    return (
      <div className="card" style={{ textAlign: 'center', padding: '3.5rem 2rem' }}>
        <FileCode2 size={40} style={{ color: 'var(--text-muted)', marginBottom: '1rem', strokeWidth: 1.5 }} />
        <h3 style={{ color: 'var(--text-primary)', fontSize: '1.1rem', fontWeight: 700 }}>No Active Scan Selected</h3>
        <p style={{ color: 'var(--text-secondary)', marginTop: '0.5rem', fontSize: '0.88rem' }}>
          Select or ingest a Solidity contract in the Ingestion tab to run verified Slither static analysis.
        </p>
      </div>
    );
  }

  if (scan.status !== 'complete') {
    return (
      <div className="card">
        <div className="alert-box danger">
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', fontWeight: 700 }}>
            <AlertCircle size={16} /> Analysis did not complete ({scan.status})
          </div>
          <p style={{ marginTop: '0.35rem', fontSize: '0.85rem' }}>
            {scan.error_message || 'No completed Slither report is available for this scan.'}
          </p>
        </div>
      </div>
    );
  }

  const handleExport = async () => {
    setIsExporting(true);
    try {
      const data = await exportScan(scan.id);
      const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `fusion-scan-${scan.id}.json`;
      a.click();
      URL.revokeObjectURL(url);
    } catch (err: unknown) {
      alert(err instanceof Error ? err.message : 'Export failed');
    } finally {
      setIsExporting(false);
    }
  };

  const lines = scan.source_code.split('\n');
  const highlightedStart = selectedFinding?.start_line ?? -1;
  const highlightedEnd = selectedFinding?.end_line ?? -1;

  const renderImpactBadge = (impact: string) => {
    switch (impact.toLowerCase()) {
      case 'high':
        return (
          <span className="badge badge-high">
            <span className="badge-dot" />
            {impact}
          </span>
        );
      case 'medium':
        return (
          <span className="badge badge-medium">
            <span className="badge-dot" />
            {impact}
          </span>
        );
      case 'low':
        return (
          <span className="badge badge-low">
            <span className="badge-dot" />
            {impact}
          </span>
        );
      default:
        return (
          <span className="badge badge-info">
            <span className="badge-dot" />
            {impact}
          </span>
        );
    }
  };

  return (
    <div>
      {/* Top Banner */}
      <div className="card">
        <div className="card-header">
          <div>
            <h2 className="card-title">
              <ShieldAlert size={18} style={{ color: 'var(--color-accent-primary)' }} />
              2. Static Analysis Findings
            </h2>
            <p className="card-subtitle">
              Interactive vulnerability inspection and immutable source review
            </p>
          </div>
          <div style={{ display: 'flex', gap: '0.75rem', alignItems: 'center', flexWrap: 'wrap' }}>
            <button
              className="btn btn-secondary"
              onClick={handleExport}
              disabled={isExporting}
            >
              <Download size={14} /> Export JSON Report
            </button>
            <button
              className="btn btn-primary"
              onClick={onNavigateToPatch}
            >
              Review Mitigation Patch <ArrowRight size={14} />
            </button>
          </div>
        </div>

        <div className="metadata-strip">
          <div><strong>Contract:</strong> {scan.filename}</div>
          <div><strong>Detected Findings:</strong> {scan.findings.length}</div>
        </div>
      </div>

      {scan.findings.length === 0 ? (
        <div className="card">
          <div className="alert-box success">
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', fontWeight: 700 }}>
              <CheckCircle2 size={16} /> No static findings detected by this run.
            </div>
            <p style={{ marginTop: '0.35rem', fontSize: '0.85rem' }}>
              Note (Rule R03): A zero-findings result does not prove contract safety or absence of logical flaws.
            </p>
          </div>
        </div>
      ) : (
        <div className="grid-2">
          {/* Left: Findings List */}
          <div>
            <h3 style={{ fontSize: '0.95rem', fontWeight: 700, marginBottom: '0.75rem', color: 'var(--text-secondary)', textTransform: 'uppercase', letterSpacing: '0.5px' }}>
              Detected Issues ({scan.findings.length})
            </h3>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
              {scan.findings.map((f, idx) => {
                const isSelected =
                  selectedFinding?.detector_id === f.detector_id &&
                  selectedFinding?.start_line === f.start_line;
                return (
                  <div
                    key={idx}
                    role="button"
                    tabIndex={0}
                    onClick={() => setSelectedFinding(f)}
                    onKeyDown={(e) => {
                      if (e.key === 'Enter' || e.key === ' ') {
                        e.preventDefault();
                        setSelectedFinding(f);
                      }
                    }}
                    style={{
                      background: isSelected ? 'rgba(232, 70, 26, 0.12)' : 'var(--bg-card)',
                      border: `1px solid ${isSelected ? 'var(--color-accent-primary)' : 'var(--border-subtle)'}`,
                      borderLeft: isSelected ? '3px solid var(--color-accent-primary)' : undefined,
                      borderRadius: 'var(--radius-sm)',
                      padding: '1rem',
                      cursor: 'pointer',
                      transition: 'all 0.15s ease',
                      outline: 'none'
                    }}
                  >
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.4rem' }}>
                      <span style={{ fontFamily: 'var(--font-mono)', fontWeight: 700, color: 'var(--text-primary)', fontSize: '0.9rem' }}>
                        {f.detector_id}
                      </span>
                      <div style={{ display: 'flex', gap: '0.4rem' }}>
                        {renderImpactBadge(f.impact)}
                        <span className="badge badge-info">
                          <span className="badge-dot" />
                          {f.confidence}
                        </span>
                      </div>
                    </div>
                    <div style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', marginBottom: '0.45rem', fontFamily: 'var(--font-mono)' }}>
                      Lines {f.start_line} – {f.end_line}
                    </div>
                    <p style={{ fontSize: '0.82rem', color: 'var(--text-secondary)', lineHeight: 1.45 }}>
                      {f.explanation}
                    </p>
                  </div>
                );
              })}
            </div>

            {selectedFinding && (
              <div className="card" style={{ marginTop: '1.25rem', borderLeft: '3px solid var(--color-info)' }}>
                <h4 style={{ fontSize: '0.9rem', fontWeight: 700, color: 'var(--color-accent-primary)', marginBottom: '0.5rem', display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
                  <Sparkles size={15} />
                  Actionable Recommendation
                </h4>
                <p style={{ fontSize: '0.85rem', color: 'var(--text-primary)', marginBottom: '0.75rem', lineHeight: 1.45 }}>
                  {selectedFinding.recommendation}
                </p>
                {selectedFinding.reference_url && (
                  <div style={{ fontSize: '0.78rem' }}>
                    <a
                      href={selectedFinding.reference_url}
                      target="_blank"
                      rel="noopener noreferrer"
                      style={{ color: 'var(--color-accent-primary)', textDecoration: 'none', display: 'inline-flex', alignItems: 'center', gap: '0.35rem', fontWeight: 600 }}
                    >
                      View Crytic Slither Detector Reference <ExternalLink size={12} />
                    </a>
                  </div>
                )}
              </div>
            )}
          </div>

          {/* Right: Immutable Source Viewer */}
          <div>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.75rem' }}>
              <h3 style={{ fontSize: '0.95rem', fontWeight: 700, color: 'var(--text-secondary)', textTransform: 'uppercase', letterSpacing: '0.5px', display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
                <Code2 size={16} /> Immutable Source View
              </h3>
              <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                Rule R04: Source is display-only; never mutated
              </span>
            </div>

            <div className="code-viewer">
              {lines.map((codeLine, idx) => {
                const lineNum = idx + 1;
                const isTarget = lineNum >= highlightedStart && lineNum <= highlightedEnd;
                return (
                  <div key={idx} className={`code-line ${isTarget ? 'highlighted' : ''}`}>
                    <span className="line-number">{lineNum}</span>
                    <span className="line-content">{codeLine || ' '}</span>
                  </div>
                );
              })}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

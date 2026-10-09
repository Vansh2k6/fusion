import React, { useState } from 'react';
import { FixtureInfo, ScanResponse } from '../types/api';
import { createScanWithFixture, createScanWithCode, createScanWithFile } from '../api/client';
import { FileCode2, Shield, AlertTriangle, Play, Lock, Info, AlertOctagon } from 'lucide-react';

interface UploadPanelProps {
  fixtures: FixtureInfo[];
  activeScan: ScanResponse | null;
  onScanCreated: (scan: ScanResponse) => void;
  isScanning: boolean;
}

export const UploadPanel: React.FC<UploadPanelProps> = ({
  fixtures,
  activeScan,
  onScanCreated,
  isScanning
}) => {
  const [selectedFixtureId, setSelectedFixtureId] = useState<string>('vulnerable_vault');
  const [customCode, setCustomCode] = useState<string>('');
  const [customFilename, setCustomFilename] = useState<string>('Vault.sol');
  const [mode, setMode] = useState<'fixture' | 'custom' | 'file'>('fixture');
  const [errorMsg, setErrorMsg] = useState<string | null>(null);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const submittingRef = React.useRef(false); // duplicate-click guard ahead of parent state (T03.07)

  // Sync fixture code when selection changes
  React.useEffect(() => {
    const f = fixtures.find(item => item.id === selectedFixtureId);
    if (f && f.source_code) {
      setCustomCode(f.source_code);
      setCustomFilename(f.name);
    }
  }, [selectedFixtureId, fixtures]);

  const handleStartScan = async () => {
    if (submittingRef.current || isScanning) return; // second rapid click is ignored (T03.07)
    submittingRef.current = true;
    setErrorMsg(null);
    try {
      let scan: ScanResponse;
      if (mode === 'fixture') {
        scan = await createScanWithFixture(selectedFixtureId);
      } else if (mode === 'file' && selectedFile) {
        scan = await createScanWithFile(selectedFile);
      } else {
        if (!customCode.trim()) {
          setErrorMsg('Please enter Solidity source code.');
          return;
        }
        scan = await createScanWithCode(customFilename, customCode);
      }
      onScanCreated(scan);
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : 'Scan request failed';
      setErrorMsg(msg);
    } finally {
      submittingRef.current = false;
    }
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      const file = e.target.files[0];
      if (file.size > 256 * 1024) {
        setErrorMsg('File size exceeds the 256 KiB limit.');
        return;
      }
      setSelectedFile(file);
      setCustomFilename(file.name);
      const reader = new FileReader();
      reader.onload = () => {
        setCustomCode(reader.result as string);
      };
      reader.readAsText(file);
    }
  };

  return (
    <div>
      <div className="card">
        <div className="card-header">
          <div>
            <h2 className="card-title">
              <FileCode2 size={18} style={{ color: 'var(--color-accent-primary)' }} />
              1. Contract Ingestion & Analysis
            </h2>
            <p className="card-subtitle">
              Select an educational fixture or provide a Solidity contract (max 256 KiB) to run verified Slither static analysis.
            </p>
          </div>
          {activeScan && (
            <div className={`status-pill ${activeScan.status}`}>
              <span className={`badge-dot ${activeScan.status === 'analyzing' || activeScan.status === 'compiling' ? 'animate-pulse' : ''}`} style={{ background: 'currentColor' }} />
              {activeScan.status.toUpperCase()}
            </div>
          )}
        </div>

        {errorMsg && (
          <div className="alert-box danger">
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', fontWeight: 700 }}>
              <AlertOctagon size={16} /> Error:
            </div>
            <p style={{ marginTop: '0.25rem', fontSize: '0.85rem' }}>{errorMsg}</p>
          </div>
        )}

        <div style={{ display: 'flex', gap: '0.75rem', marginBottom: '1.25rem', flexWrap: 'wrap' }}>
          <button
            className={`btn ${mode === 'fixture' ? 'btn-primary' : 'btn-secondary'}`}
            onClick={() => setMode('fixture')}
          >
            <Shield size={14} /> Curated Fixture
          </button>
          <button
            className={`btn ${mode === 'custom' ? 'btn-primary' : 'btn-secondary'}`}
            onClick={() => setMode('custom')}
            disabled
            title="Unavailable until the isolated analysis worker is configured"
          >
            <Lock size={14} /> Direct Editor (Isolation Required)
          </button>
          <button
            className={`btn ${mode === 'file' ? 'btn-primary' : 'btn-secondary'}`}
            onClick={() => setMode('file')}
            disabled
            title="Unavailable until the isolated analysis worker is configured"
          >
            <Lock size={14} /> Upload File (Isolation Required)
          </button>
        </div>

        {mode === 'fixture' && (
          <div style={{ marginBottom: '1.25rem' }}>
            <label style={{ display: 'block', fontSize: '0.85rem', color: 'var(--text-secondary)', marginBottom: '0.5rem', fontWeight: 600 }}>
              Select Approved Educational Fixture:
            </label>
            <select
              className="form-select"
              value={selectedFixtureId}
              onChange={(e) => setSelectedFixtureId(e.target.value)}
            >
              {fixtures.map(f => (
                <option key={f.id} value={f.id}>
                  {f.name} — {f.description}
                </option>
              ))}
            </select>

            {/* Clean fixture selector */}
          </div>
        )}

        {mode === 'file' && (
          <div style={{ marginBottom: '1.25rem' }}>
            <label style={{ display: 'block', fontSize: '0.85rem', color: 'var(--text-secondary)', marginBottom: '0.5rem', fontWeight: 600 }}>
              Upload .sol File (Max 256 KiB):
            </label>
            <input
              type="file"
              accept=".sol"
              className="form-input"
              onChange={handleFileChange}
            />
          </div>
        )}

        {mode === 'custom' && (
          <div style={{ marginBottom: '1.25rem' }}>
            <label style={{ display: 'block', fontSize: '0.85rem', color: 'var(--text-secondary)', marginBottom: '0.5rem', fontWeight: 600 }}>
              Contract Filename:
            </label>
            <input
              type="text"
              className="form-input"
              value={customFilename}
              onChange={(e) => setCustomFilename(e.target.value)}
            />
          </div>
        )}

        <div style={{ marginBottom: '1.25rem' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.5rem' }}>
            <label style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', fontWeight: 600 }}>
              Source Preview ({customFilename}):
            </label>
            <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)', fontFamily: 'var(--font-mono)' }}>
              {new Blob([customCode]).size} bytes
            </span>
          </div>
          <textarea
            className="form-textarea"
            rows={12}
            value={customCode}
            onChange={(e) => setCustomCode(e.target.value)}
            placeholder="// Paste Solidity code here..."
          />
        </div>

        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '1rem' }}>
          <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)', display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
            <Info size={14} style={{ color: 'var(--color-info)' }} />
            Safety boundary: only exact approved fixture hashes execute until the isolated worker is available.
          </div>
          <button
            className="btn btn-primary"
            onClick={handleStartScan}
            disabled={isScanning}
          >
            <Play size={14} />
            {isScanning ? 'Running Slither Scan...' : 'Analyze with Slither'}
          </button>
        </div>
      </div>

      {activeScan && ['error', 'unsupported', 'timeout'].includes(activeScan.status) && (
        <div className="card" style={{ borderColor: 'rgba(232, 70, 26, 0.4)' }}>
          <div className="card-header">
            <h3 className="card-title" style={{ color: 'var(--color-danger)' }}>
              <AlertTriangle size={18} />
              Analysis Execution Diagnostic
            </h3>
            <span className="badge badge-high">
              <span className="badge-dot" />
              Analysis Did Not Complete
            </span>
          </div>
          <div className="alert-box danger">
            <p><strong>Status:</strong> {activeScan.status.toUpperCase()}</p>
            <pre style={{ marginTop: '0.5rem', whiteSpace: 'pre-wrap', fontFamily: 'var(--font-mono)', fontSize: '0.82rem' }}>
              {activeScan.error_message || 'Compilation or static analyzer failure occurred.'}
            </pre>
          </div>
          <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
            Rule R02: A compilation error is an explicit diagnostic, never an empty clean scan.
          </p>
        </div>
      )}
    </div>
  );
};

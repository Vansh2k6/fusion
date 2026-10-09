import React, { useState, useEffect } from 'react';
import { DemoRunResponse } from '../types/api';
import { runDemo, listDemoRuns, resetDemo } from '../api/client';
import {
  Activity,
  RotateCcw,
  Play,
  AlertTriangle,
  Flame,
  Cpu,
  Receipt,
  FileSpreadsheet,
  AlertOctagon
} from 'lucide-react';

export const DemoEvidence: React.FC = () => {
  const [activeRun, setActiveRun] = useState<DemoRunResponse | null>(null);
  const [history, setHistory] = useState<DemoRunResponse[]>([]);
  const [isRunning, setIsRunning] = useState<boolean>(false);
  const [isResetting, setIsResetting] = useState<boolean>(false);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  useEffect(() => {
    loadRuns();
  }, []);

  const loadRuns = async () => {
    try {
      const runs = await listDemoRuns();
      setHistory(runs);
      if (runs.length > 0 && !activeRun) {
        setActiveRun(runs[0]);
      }
    } catch {
      // ignore
    }
  };

  const handleExecuteDemo = async () => {
    setIsRunning(true);
    setErrorMsg(null);
    try {
      const run = await runDemo();
      setActiveRun(run);
      await loadRuns();
    } catch (err: unknown) {
      setErrorMsg(err instanceof Error ? err.message : 'Demo run failed');
    } finally {
      setIsRunning(false);
    }
  };

  const handleReset = async () => {
    setIsResetting(true);
    try {
      await resetDemo();
      await loadRuns();
      if (activeRun) {
        setActiveRun({ ...activeRun, is_historical: true });
      }
    } catch (err: unknown) {
      alert(err instanceof Error ? err.message : 'Reset failed');
    } finally {
      setIsResetting(false);
    }
  };

  const formatEth = (weiStr: string) => {
    try {
      const wei = BigInt(weiStr);
      const isNeg = wei < 0n;
      const absWei = isNeg ? -wei : wei;
      const ethWhole = absWei / 1000000000000000000n;
      const remainder = absWei % 1000000000000000000n;
      const remStr = remainder.toString().padStart(18, '0').slice(0, 4);
      return `${isNeg ? '-' : ''}${ethWhole}.${remStr} ETH`;
    } catch {
      return `${weiStr} wei`;
    }
  };

  return (
    <div>
      {/* Header card */}
      <div className="card">
        <div className="card-header">
          <div>
            <h2 className="card-title">
              <Activity size={18} style={{ color: 'var(--color-accent-primary)' }} />
              4. Live Local EVM Attack / Defense Evidence
            </h2>
            <p className="card-subtitle">
              Local Anvil Node (127.0.0.1:8545, Chain ID 31337) with disposable test accounts.
            </p>
          </div>
          <div style={{ display: 'flex', gap: '0.75rem', alignItems: 'center', flexWrap: 'wrap' }}>
            <button
              className="btn btn-secondary"
              onClick={handleReset}
              disabled={isResetting}
            >
              <RotateCcw size={14} />
              {isResetting ? 'Resetting Chain...' : 'Reset Local Chain'}
            </button>
            <button
              className="btn btn-primary"
              onClick={handleExecuteDemo}
              disabled={isRunning}
            >
              <Play size={14} />
              {isRunning ? 'Executing Real Anvil Scenario...' : 'Execute Live Attack/Defense Scenario'}
            </button>
          </div>
        </div>

        {errorMsg && (
          <div className="alert-box danger">
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', fontWeight: 700 }}>
              <AlertOctagon size={16} /> Error:
            </div>
            <p style={{ marginTop: '0.25rem', fontSize: '0.85rem' }}>{errorMsg}</p>
          </div>
        )}

        {history.length > 1 && (
          <div style={{ marginBottom: '1rem', display: 'flex', alignItems: 'center', gap: '0.75rem', flexWrap: 'wrap' }}>
            <label style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', fontWeight: 600 }}>Select Recorded Run:</label>
            <select
              className="form-select"
              style={{ width: 'auto' }}
              value={activeRun?.id || ''}
              onChange={(e) => {
                const found = history.find(r => r.id === e.target.value);
                if (found) setActiveRun(found);
              }}
            >
              {history.map((r, i) => (
                <option key={r.id} value={r.id}>
                  Run #{history.length - i}: {r.id} ({r.is_historical ? 'Historical' : 'Latest'}) - {new Date(r.created_at).toLocaleTimeString()}
                </option>
              ))}
            </select>
          </div>
        )}

        <div className="metadata-strip" style={{ color: 'var(--text-secondary)', fontSize: '0.78rem' }}>
          Rule R09 & R11: Disposable local Anvil accounts only. The smart contract enforces protection during EVM execution; the workbench dashboard observes and reports evidence afterward.
        </div>
      </div>

      {!activeRun ? (
        <div className="card" style={{ textAlign: 'center', padding: '3.5rem 2rem' }}>
          <Cpu size={40} style={{ color: 'var(--text-muted)', marginBottom: '1rem', strokeWidth: 1.5 }} />
          <h3 style={{ color: 'var(--text-primary)', fontSize: '1.1rem', fontWeight: 700 }}>No Demo Run Executed Yet</h3>
          <p style={{ color: 'var(--text-secondary)', marginTop: '0.5rem', fontSize: '0.88rem' }}>
            Click "Execute Live Attack/Defense Scenario" above to deploy VulnerableVault and ProtectedVault onto local Anvil, execute attacks, and observe real transactions.
          </p>
        </div>
      ) : (
        <div>
          {/* Active Run Status & Incident Alert */}
          {activeRun.is_historical && (
            <div className="alert-box warning">
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', fontWeight: 700 }}>
                <AlertTriangle size={16} /> Historical Run
              </div>
              <p style={{ marginTop: '0.25rem', fontSize: '0.85rem' }}>
                The local chain has been reset since this scenario ran. Contract handles and balances reflect historical evidence.
              </p>
            </div>
          )}

          {activeRun.alert && (
            <div className="card" style={{ borderColor: 'rgba(232, 70, 26, 0.4)' }}>
              <div className="card-header">
                <div>
                  <h3 className="card-title" style={{ color: 'var(--color-danger)' }}>
                    <Flame size={18} />
                    Incident Analysis: {activeRun.alert.title}
                  </h3>
                  <div style={{ marginTop: '0.35rem' }}>
                    <span className="badge badge-high">
                      <span className="badge-dot" />
                      Severity: {activeRun.alert.severity.toUpperCase()}
                    </span>
                  </div>
                </div>
                <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                  Rule R03: Separating Empirical Observation from Theoretical Hypothesis
                </span>
              </div>

              <div className="incident-card">
                <div className="incident-section">
                  <div className="incident-label" style={{ color: 'var(--color-accent-primary)' }}>
                    Empirical Observation (What Happened):
                  </div>
                  <div className="incident-text">
                    {activeRun.alert.observation}
                  </div>
                </div>

                <div className="incident-section">
                  <div className="incident-label" style={{ color: 'var(--color-warning)' }}>
                    Security Hypothesis (Root Cause):
                  </div>
                  <div className="incident-text">
                    {activeRun.alert.hypothesis}
                  </div>
                </div>

                <div className="incident-section" style={{ marginBottom: 0 }}>
                  <div className="incident-label" style={{ color: 'var(--color-success)' }}>
                    Recommended Action:
                  </div>
                  <div className="incident-text">
                    {activeRun.alert.suggested_action}
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Balance Deltas Table */}
          <div className="card">
            <div className="card-header">
              <h3 className="card-title">
                <FileSpreadsheet size={18} style={{ color: 'var(--color-accent-primary)' }} />
                Real Balance Deltas (Before vs After Exploits)
              </h3>
              <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                Exact wei integers represented as decimal strings
              </span>
            </div>

            <table className="balance-table">
              <thead>
                <tr>
                  <th>Entity / Account</th>
                  <th>Contract / EOA Address</th>
                  <th>Pre-Attack Balance</th>
                  <th>Post-Attack Balance</th>
                  <th>Net Delta</th>
                </tr>
              </thead>
              <tbody>
                {activeRun.balances.map((b, idx) => {
                  const isNeg = b.delta_wei.startsWith('-');
                  const isZero = b.delta_wei === '0';
                  return (
                    <tr key={idx}>
                      <td style={{ fontWeight: 600, color: 'var(--text-primary)' }}>{b.label}</td>
                      <td style={{ color: 'var(--text-secondary)', fontFamily: 'var(--font-mono)' }}>
                        {b.address.slice(0, 10)}...{b.address.slice(-8)}
                      </td>
                      <td>{formatEth(b.before_wei)}</td>
                      <td>{formatEth(b.after_wei)}</td>
                      <td className={isZero ? 'delta-zero' : isNeg ? 'delta-neg' : 'delta-pos'}>
                        {formatEth(b.delta_wei)}
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>

          {/* Transactions Stream */}
          <div className="card">
            <div className="card-header">
              <h3 className="card-title">
                <Receipt size={18} style={{ color: 'var(--color-accent-primary)' }} />
                Recorded EVM Transactions & Receipts
              </h3>
              <span className="badge badge-info">
                <span className="badge-dot" />
                {activeRun.transactions.length} Transactions
              </span>
            </div>

            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
              {activeRun.transactions.map((tx, idx) => (
                <div
                  key={idx}
                  style={{
                    background: 'var(--bg-tertiary)',
                    border: `1px solid ${tx.status === 'success' ? 'rgba(22, 163, 74, 0.3)' : 'rgba(232, 70, 26, 0.35)'}`,
                    borderRadius: 'var(--radius-sm)',
                    padding: '0.85rem 1rem',
                    fontFamily: 'var(--font-mono)',
                    fontSize: '0.82rem'
                  }}
                >
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.4rem' }}>
                    <span style={{ fontWeight: 700, color: 'var(--text-primary)', fontFamily: 'var(--font-sans)', fontSize: '0.88rem' }}>
                      #{idx + 1}: {tx.label}
                    </span>
                    <span className={`badge ${tx.status === 'success' ? 'badge-success' : 'badge-high'}`}>
                      <span className="badge-dot" />
                      {tx.status.toUpperCase()}
                    </span>
                  </div>
                  <div style={{ color: 'var(--text-secondary)', display: 'flex', gap: '1.5rem', flexWrap: 'wrap' }}>
                    <div>
                      <strong>Tx Hash:</strong>{' '}
                      <span style={{ color: 'var(--color-accent-primary)' }}>{tx.tx_hash.slice(0, 14)}...</span>
                    </div>
                    <div><strong>From:</strong> {tx.from_address.slice(0, 8)}...</div>
                    {tx.to_address && <div><strong>To:</strong> {tx.to_address.slice(0, 8)}...</div>}
                    <div><strong>Gas Used:</strong> {tx.gas_used}</div>
                  </div>
                  {tx.revert_reason && (
                    <div style={{ marginTop: '0.45rem', color: '#fca5a5', fontSize: '0.8rem', background: 'rgba(232, 70, 26, 0.1)', padding: '0.4rem 0.6rem', borderRadius: 'var(--radius-sm)', border: '1px solid rgba(232, 70, 26, 0.25)' }}>
                      <strong>Revert Diagnostic:</strong> {tx.revert_reason}
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

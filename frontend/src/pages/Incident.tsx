// Purpose: Incident detail page (P07.03, R5): metadata band, tabs, info card,
// scenario-dimension charts (observed 0/1 and wei magnitudes, never risk scores),
// entities table, export, and local review controls.
import React from 'react';
import { DemoRunResponse } from '../types/api';
import { getDemoRun } from '../api/client';
import { Download } from 'lucide-react';

type Tab = 'overview' | 'detections' | 'notes' | 'logs' | 'respond';
const TABS: { id: Tab; label: string }[] = [
  { id: 'overview', label: 'Overview' },
  { id: 'detections', label: 'Detections' },
  { id: 'notes', label: 'Notes' },
  { id: 'logs', label: 'Logs' },
  { id: 'respond', label: 'Respond' },
];

// Six observed scenario dimensions (1 = observed, 0 = not observed). These are
// execution facts from this run, not residual-risk scores.
function scenarioDimensions(run: DemoRunResponse): { label: string; value: number }[] {
  const tx = run.transactions;
  const has = (s: string) => tx.some(t => t.label.includes(s) && t.status === 'success') ? 1 : 0;
  const blocked = tx.some(t => t.label.includes('Blocked by CEI') && t.status === 'reverted') ? 1 : 0;
  const drained = run.balances.some(b => b.label.includes('VulnerableVault') && b.after_wei === '0') ? 1 : 0;
  return [
    { label: 'Deployed', value: has('Deploy VulnerableVault') },
    { label: 'Funded', value: has('Victim deposit') },
    { label: 'Exploited', value: drained },
    { label: 'Blocked', value: blocked },
    { label: 'Round-trip', value: has('Normal user withdrawal') },
    { label: 'Receipts', value: tx.length >= 10 ? 1 : 0 },
  ];
}

function polarPath(cx: number, cy: number, r: number, a0: number, a1: number): string {
  const p = (r: number, a: number) => `${cx + r * Math.cos(a)},${cy + r * Math.sin(a)}`;
  return `M${cx},${cy} L${p(r, a0)} A${r},${r} 0 0 1 ${p(r, a1)} Z`;
}

export const Incident: React.FC<{ runId: string; onBack: () => void }> = ({ runId, onBack }) => {
  const [run, setRun] = React.useState<DemoRunResponse | null>(null);
  const [error, setError] = React.useState<string | null>(null);
  const [tab, setTab] = React.useState<Tab>('overview');
  const [note, setNote] = React.useState(() => localStorage.getItem(`fusion.incident.note.${runId}`) || '');
  const [review, setReview] = React.useState(() => localStorage.getItem(`fusion.incident.review.${runId}`) || 'open');

  React.useEffect(() => {
    let live = true;
    setRun(null);
    setError(null);
    getDemoRun(runId).then(r => live && setRun(r)).catch(e => live && setError(e instanceof Error ? e.message : 'Failed to load run'));
    return () => { live = false; };
  }, [runId]);

  React.useEffect(() => { localStorage.setItem(`fusion.incident.note.${runId}`, note); }, [note, runId]);
  React.useEffect(() => { localStorage.setItem(`fusion.incident.review.${runId}`, review); }, [review, runId]);

  if (error) return <div className="card"><div className="alert-box danger" role="alert">{error} <button className="btn btn-secondary" onClick={onBack}>Back to Incidents</button></div></div>;
  if (!run) return <div className="card"><div className="skeleton" style={{ height: '200px' }} /></div>;

  const dims = scenarioDimensions(run);
  const maxDelta = Math.max(1, ...run.balances.map(b => {
    try { const v = BigInt(b.delta_wei); return Number(v < 0 ? -v : v); } catch { return 0; }
  }));

  const doExport = () => {
    const blob = new Blob([JSON.stringify(run, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `fusion-incident-${run.id}.json`;
    a.click();
    URL.revokeObjectURL(url);
  };

  const copy = (v: string) => { navigator.clipboard?.writeText(v).catch(() => undefined); };

  return (
    <div>
      {/* Metadata band */}
      <div className="card" style={{ borderColor: 'var(--line-warm)' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', gap: '12px', flexWrap: 'wrap', alignItems: 'flex-start' }}>
          <div>
            <h2 className="card-title">Incident · {run.id.slice(0, 12)}</h2>
            <div className="metadata-strip" style={{ marginTop: '8px' }}>
              <div><strong>Reviewer:</strong> local workspace</div>
              <div><strong>Created:</strong> {new Date(run.created_at).toLocaleString()}</div>
              <div><strong>Session:</strong> {run.rpc_url} · chain {run.chain_id}{run.is_historical ? ' · historical' : ''}</div>
            </div>
          </div>
          <div style={{ display: 'flex', gap: '8px', alignItems: 'center', flexWrap: 'wrap' }}>
            <label style={{ fontSize: '12px' }}>Status
              <select className="form-select" style={{ width: 'auto', marginLeft: '6px' }} value={review} onChange={e => setReview(e.target.value)} aria-label="Local review status">
                {['open', 'triaged', 'in_progress', 'resolved', 'canceled'].map(s => <option key={s} value={s}>{s}</option>)}
              </select>
            </label>
            <span className="chip">Severity: {run.alert?.severity || 'unavailable'}</span>
            <button className="btn btn-secondary" onClick={doExport}><Download size={14} /> Download report</button>
          </div>
        </div>
        <div role="tablist" aria-label="Incident sections" style={{ display: 'flex', gap: '4px', marginTop: '12px', borderTop: '1px solid var(--line-subtle)', paddingTop: '8px' }}>
          {TABS.map(t => (
            <button key={t.id} role="tab" aria-selected={tab === t.id} className={`btn ${tab === t.id ? 'btn-primary' : 'btn-secondary'}`} onClick={() => setTab(t.id)}>{t.label}</button>
          ))}
        </div>
      </div>

      {tab === 'overview' && (
        <div style={{ display: 'grid', gridTemplateColumns: '35% 65%', gap: '10px' }} className="incident-grid">
          <div>
            <div className="card">
              <h3 className="card-title">Information</h3>
              <div className="metadata-strip" style={{ marginTop: '8px' }}>
                <div><strong>Incident type:</strong> local reentrancy replay</div>
                <div><strong>Status:</strong> {review} (local review marker)</div>
                <div><strong>Origin:</strong> app-owned Anvil session</div>
                <div><strong>Detections:</strong> {run.transactions.filter(t => t.status === 'reverted').length} reverted · {run.transactions.length} total receipts</div>
              </div>
            </div>
            <div className="card">
              <h3 className="card-title">Balance movement (wei magnitude)</h3>
              <svg viewBox="0 0 200 200" role="img" aria-label="Polar chart of absolute balance movement per entity" style={{ width: '100%', maxWidth: '280px' }}>
                {[40, 70, 95].map(r => <circle key={r} cx="100" cy="100" r={r} fill="none" stroke="var(--line-subtle)" strokeWidth="1" />)}
                {run.balances.map((b, i) => {
                  let v = 0;
                  try { const x = BigInt(b.delta_wei); v = Number(x < 0 ? -x : x); } catch { v = 0; }
                  const r = 20 + 75 * (maxDelta ? v / maxDelta : 0);
                  const a0 = (i / run.balances.length) * Math.PI * 2 - Math.PI / 2;
                  const a1 = ((i + 0.85) / run.balances.length) * Math.PI * 2 - Math.PI / 2;
                  return <path key={i} d={polarPath(100, 100, r, a0, a1)} fill="rgba(241,59,8,0.45)" stroke="var(--accent-hot)" strokeWidth="1"><title>{`${b.label}: ${b.delta_wei} wei`}</title></path>;
                })}
              </svg>
              <table className="findings-table"><caption>Balance movement values</caption>
                <thead><tr><th scope="col">Entity</th><th scope="col">Delta (wei)</th></tr></thead>
                <tbody>{run.balances.map((b, i) => <tr key={i}><td>{b.label}</td><td>{b.delta_wei}</td></tr>)}</tbody>
              </table>
            </div>
          </div>
          <div>
            <div className="card">
              <h3 className="card-title">Observed scenario dimensions</h3>
              <p className="card-subtitle">Execution facts (0/1) from this run — not risk scores.</p>
              <svg viewBox="0 0 260 200" role="img" aria-label="Radar chart of observed scenario dimensions" style={{ width: '100%', maxWidth: '360px' }}>
                {[0.33, 0.66, 1].map(f => (
                  <polygon key={f} points={dims.map((_, i) => {
                    const a = (i / dims.length) * Math.PI * 2 - Math.PI / 2;
                    return `${130 + 80 * f * Math.cos(a)},${100 + 80 * f * Math.sin(a)}`;
                  }).join(' ')} fill="none" stroke="var(--line-subtle)" strokeWidth="1" />
                ))}
                <polygon points={dims.map((d, i) => {
                  const a = (i / dims.length) * Math.PI * 2 - Math.PI / 2;
                  return `${130 + 80 * d.value * Math.cos(a)},${100 + 80 * d.value * Math.sin(a)}`;
                }).join(' ')} fill="rgba(241,59,8,0.3)" stroke="var(--accent-hot)" strokeWidth="1.5" />
                {dims.map((d, i) => {
                  const a = (i / dims.length) * Math.PI * 2 - Math.PI / 2;
                  return <text key={i} x={130 + 95 * Math.cos(a)} y={100 + 95 * Math.sin(a)} fill="var(--text-secondary)" fontSize="9" textAnchor="middle">{d.label}</text>;
                })}
              </svg>
              <table className="findings-table"><caption>Scenario dimension values</caption>
                <thead><tr><th scope="col">Dimension</th><th scope="col">Observed</th></tr></thead>
                <tbody>{dims.map(d => <tr key={d.label}><td>{d.label}</td><td>{d.value}</td></tr>)}</tbody>
              </table>
            </div>
            <div className="card">
              <h3 className="card-title">Entities</h3>
              <div className="findings-table-wrap" role="region" aria-label="Involved entities" tabIndex={0}>
                <table className="findings-table">
                  <thead><tr><th scope="col">Role</th><th scope="col">Address</th><th scope="col">Balance delta</th></tr></thead>
                  <tbody>
                    {[
                      { role: 'Vulnerable vault', addr: run.original_vault },
                      { role: 'Protected vault', addr: run.protected_vault },
                      { role: 'Attacker', addr: run.attacker },
                      { role: 'Normal user', addr: run.normal_user },
                    ].map(e => {
                      const bal = run.balances.find(b => b.address.toLowerCase() === e.addr.toLowerCase());
                      return (
                        <tr key={e.role}>
                          <td>{e.role}</td>
                          <td><span style={{ fontFamily: 'var(--font-mono)', fontSize: '11px' }}>{e.addr.slice(0, 10)}…{e.addr.slice(-6)}</span>
                            <button className="btn btn-secondary" style={{ marginLeft: '6px' }} onClick={() => copy(e.addr)} aria-label={`Copy ${e.role} address`}>Copy</button>
                          </td>
                          <td>{bal ? `${bal.delta_wei} wei` : 'unavailable'}</td>
                        </tr>
                      );
                    })}
                  </tbody>
                </table>
              </div>
              {run.is_historical && <div className="alert-box warning" style={{ marginTop: '8px' }}>Historical run: chain reset since execution; addresses are not live handles.</div>}
            </div>
          </div>
        </div>
      )}

      {tab === 'detections' && (
        <div className="card">
          <h3 className="card-title">Detections</h3>
          {run.alert ? (
            <div className="metadata-strip" style={{ marginTop: '8px' }}>
              <div><strong>Title:</strong> {run.alert.title}</div>
              <div><strong>Observation:</strong> {run.alert.observation}</div>
              <div><strong>Hypothesis:</strong> {run.alert.hypothesis}</div>
              <div><strong>Suggested action:</strong> {run.alert.suggested_action}</div>
            </div>
          ) : <div className="empty-state">No detections recorded for this run.</div>}
        </div>
      )}

      {tab === 'notes' && (
        <div className="card">
          <h3 className="card-title">Notes</h3>
          <p className="card-subtitle">Local-only annotations; stored in this browser, never on chain.</p>
          <textarea className="form-input" style={{ width: '100%', minHeight: '120px', marginTop: '8px' }} value={note} onChange={e => setNote(e.target.value)} aria-label="Incident notes" placeholder="Observation vs hypothesis…" />
        </div>
      )}

      {tab === 'logs' && (
        <div className="card">
          <h3 className="card-title">Logs</h3>
          <p className="card-subtitle">{run.logs || 'No run log message.'}</p>
          <div className="findings-table-wrap" role="region" aria-label="Transaction receipts" tabIndex={0} style={{ marginTop: '8px' }}>
            <table className="findings-table">
              <thead><tr><th scope="col">#</th><th scope="col">Step</th><th scope="col">Tx hash</th><th scope="col">Status</th><th scope="col">Gas</th><th scope="col">Fee (wei)</th></tr></thead>
              <tbody>
                {run.transactions.map((t, i) => (
                  <tr key={i}>
                    <td>{i + 1}</td><td>{t.label}</td>
                    <td><span style={{ fontFamily: 'var(--font-mono)', fontSize: '11px' }}>0x{t.tx_hash.slice(0, 10)}…</span>
                      <button className="btn btn-secondary" style={{ marginLeft: '6px' }} onClick={() => copy(`0x${t.tx_hash}`)} aria-label={`Copy transaction ${i + 1} hash`}>Copy</button>
                    </td>
                    <td>{t.status}{t.revert_reason ? ` — ${t.revert_reason}` : ''}</td>
                    <td>{t.gas_used}</td><td>{t.fee_wei || 'unavailable'}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          <p style={{ fontSize: '12px', color: 'var(--text-muted)', marginTop: '8px' }}>Call traces are unavailable from Anvil receipts in this build; receipt status and balances are the evidence.</p>
        </div>
      )}

      {tab === 'respond' && (
        <div className="card">
          <h3 className="card-title">Respond</h3>
          <div style={{ fontSize: '13px', color: 'var(--text-secondary)', display: 'flex', flexDirection: 'column', gap: '8px', marginTop: '8px' }}>
            <p>1. Review the CEI candidate in Patch review; selection never rewrites chain history.</p>
            <p>2. Re-run candidate validation before any new replay; unresolved findings need manual review.</p>
            <p>3. No auto-pause exists in this build: pausing would require existing contract support, authorization, and a separate transaction.</p>
          </div>
        </div>
      )}
    </div>
  );
};

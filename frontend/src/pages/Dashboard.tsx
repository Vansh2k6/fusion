// Purpose: Dashboard page (P08.01–P08.03): single batched aggregate read, metrics
// linked to filtered work, labeled contract/call topology in the map slot, live
// severity bars with table equivalents. No invented geography, trends, or sparklines.
import React from 'react';
import { ScanResponse } from '../types/api';
import { fetchDashboard, listScans, DashboardData } from '../api/client';

interface Props {
  onOpenScan: (id: string) => void;
  onOpenIncident: (id: string) => void;
}

export const Dashboard: React.FC<Props> = ({ onOpenScan, onOpenIncident }) => {
  const [data, setData] = React.useState<DashboardData | null>(null);
  const [scans, setScans] = React.useState<ScanResponse[] | null>(null);
  const [error, setError] = React.useState<string | null>(null);
  const [sortNewest, setSortNewest] = React.useState(true);
  const [windowN, setWindowN] = React.useState(25);

  React.useEffect(() => {
    let live = true;
    // One batched aggregate read plus one bounded scan page (no per-chart polling).
    Promise.all([fetchDashboard(), listScans(20, 0)])
      .then(([d, s]) => {
        if (!live) return;
        setData(d);
        setScans(s);
      })
      .catch(e => live && setError(e instanceof Error ? e.message : 'Failed to load dashboard'));
    return () => { live = false; };
  }, []);

  const openActivity = (kind: string, ref: string) => {
    if (kind === 'scan') onOpenScan(ref);
    else if (kind === 'incident') onOpenIncident(ref);
    else if (kind === 'validation' || kind === 'selection') window.location.hash = '#/patch';
  };

  if (error) return <div className="card"><div className="alert-box danger" role="alert">{error} — showing no cached values because none were verified this session.</div></div>;
  if (!data || !scans) return <div className="card"><div className="skeleton" style={{ height: '120px' }} /></div>;

  const byImpact = new Map<string, number>();
  scans.forEach(s => s.findings.forEach(f => byImpact.set(f.impact, (byImpact.get(f.impact) || 0) + 1)));
  const maxBar = Math.max(1, ...byImpact.values());
  const activity = [...data.activity].sort((a, b) => sortNewest
    ? b.created_at.localeCompare(a.created_at)
    : a.created_at.localeCompare(b.created_at)).slice(0, windowN);

  const kpi = (label: string, value: string, scope: string, action?: () => void, actionLabel?: string) => (
    <div className="kpi-card" style={{ minHeight: '96px' }}>
      <div className="kpi-label">{label}</div>
      <div className="kpi-value" style={value.length > 8 ? { fontSize: '16px', paddingTop: '6px' } : undefined}>{value}</div>
      <div style={{ fontSize: '11px', color: 'var(--text-muted)', marginTop: '4px' }}>{scope}</div>
      {action && <button className="btn btn-secondary" style={{ marginTop: '6px' }} onClick={action}>{actionLabel}</button>}
    </div>
  );

  return (
    <div>
      <div className="kpi-grid">
        {kpi('Open review findings', String(data.open_review_findings.value), data.open_review_findings.scope,
          () => { window.location.hash = '#/findings'; }, 'Open findings')}
        {kpi('Recorded local incidents', String(data.recorded_incidents.value), data.recorded_incidents.scope,
          () => { window.location.hash = '#/incidents'; }, 'Open incidents')}
        {kpi('Required checks passed / required',
          `${data.required_checks.passed} / ${data.required_checks.required}`, data.required_checks.scope)}
        {kpi('Measured validation duration',
          data.validation_duration_ms.value === null ? 'Unavailable' : `${(data.validation_duration_ms.value / 1000).toFixed(1)}s`,
          data.validation_duration_ms.scope)}
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '55% 45%', gap: '10px' }} className="incident-grid">
        <div>
          <div className="card" style={{ minHeight: '220px' }}>
            <div className="card-header"><div>
              <h3 className="card-title">Contract / call topology</h3>
              <p className="card-subtitle">Live local call graph. No geographic threat data exists, so no map is shown.</p>
            </div></div>
            <svg viewBox="0 0 400 160" role="img" aria-label="Local contract and call topology" style={{ width: '100%' }}>
              {[
                { x: 60, y: 80, label: 'Scanner' },
                { x: 180, y: 40, label: `VulnerableVault · ${scans.length} scans` },
                { x: 180, y: 120, label: 'ProtectedVault' },
                { x: 300, y: 80, label: `Attacker · ${data.recorded_incidents.value} replays` },
              ].map((n, i) => (
                <g key={i}>
                  <circle cx={n.x} cy={n.y} r="26" fill="rgba(241,59,8,0.12)" stroke="var(--accent-hot)" strokeWidth="1.5" />
                  <text x={n.x} y={n.y + 42} fill="var(--text-secondary)" fontSize="10" textAnchor="middle">{n.label}</text>
                </g>
              ))}
              <line x1="86" y1="80" x2="154" y2="40" stroke="var(--line-warm)" strokeWidth="1.5" />
              <line x1="86" y1="80" x2="154" y2="120" stroke="var(--line-warm)" strokeWidth="1.5" />
              <line x1="206" y1="40" x2="274" y2="80" stroke="var(--line-warm)" strokeWidth="1.5" />
              <line x1="206" y1="120" x2="274" y2="80" stroke="var(--line-warm)" strokeWidth="1.5" />
            </svg>
          </div>
          <div className="card" style={{ minHeight: '160px' }}>
            <h3 className="card-title">Findings by severity · last 20 scans</h3>
            {byImpact.size === 0 ? <div className="empty-state">No findings in this window.</div> : (
              <div>
                {[...byImpact.entries()].map(([impact, n]) => (
                  <div key={impact} style={{ display: 'flex', alignItems: 'center', gap: '8px', marginTop: '6px' }}>
                    <span style={{ width: '110px', fontSize: '12px' }}>{impact}</span>
                    <div style={{ flex: 1, background: 'var(--surface-raised)', borderRadius: '3px' }}>
                      <div style={{ width: `${(n / maxBar) * 100}%`, height: '8px', background: 'var(--accent-primary)', borderRadius: '3px' }} />
                    </div>
                    <span style={{ fontSize: '12px', fontVariantNumeric: 'tabular-nums' }}>{n}</span>
                  </div>
                ))}
                <table className="findings-table" style={{ marginTop: '8px' }}><caption>Findings by severity values</caption>
                  <thead><tr><th scope="col">Severity</th><th scope="col">Count</th></tr></thead>
                  <tbody>{[...byImpact.entries()].map(([k, v]) => <tr key={k}><td>{k}</td><td>{v}</td></tr>)}</tbody>
                </table>
              </div>
            )}
          </div>
        </div>
        <div className="card" style={{ minHeight: '380px' }}>
          <div className="card-header"><div>
            <h3 className="card-title">Recent activity</h3>
            <p className="card-subtitle">Immutable scans, validations, selections, and replays.</p>
          </div>
            <div style={{ display: 'flex', gap: '6px', alignItems: 'center' }}>
              <button className="btn btn-secondary" onClick={() => setSortNewest(!sortNewest)} aria-label="Toggle activity sort order">
                {sortNewest ? 'Newest first' : 'Oldest first'}
              </button>
              <select className="form-select" style={{ width: 'auto' }} value={windowN} onChange={e => setWindowN(Number(e.target.value))} aria-label="Activity window size">
                {[10, 25, 50].map(n => <option key={n} value={n}>Last {n}</option>)}
              </select>
            </div>
          </div>
          {activity.length === 0 ? <div className="empty-state">No events yet. Run a scan to start the trail.</div> : (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
              {activity.map(e => (
                <button key={`${e.kind}-${e.id}`} className="menu-item" style={{ border: '1px solid var(--line-subtle)', borderRadius: '4px' }} onClick={() => openActivity(e.kind, e.ref)}>
                  <span className="chip">{e.kind}</span>
                  {e.title} · {new Date(e.created_at).toLocaleString()}
                </button>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

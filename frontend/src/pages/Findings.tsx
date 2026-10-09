// Purpose: Findings review page (P05.01–P05.03): dense table, five-column board,
// nested filters, finding detail with immutable source and persisted review state.
import React from 'react';
import { ScanResponse, Finding } from '../types/api';
import { exportScan, getReviews, updateReview, Review } from '../api/client';
import { Download, List, LayoutGrid, SlidersHorizontal, ChevronDown } from 'lucide-react';

export type ReviewState = 'open' | 'triaged' | 'in_progress' | 'resolved' | 'canceled';
const STATES: ReviewState[] = ['open', 'triaged', 'in_progress', 'resolved', 'canceled'];
const STATE_LABEL: Record<string, string> = {
  open: 'Open', triaged: 'Triaged', in_progress: 'In Progress', resolved: 'Resolved', canceled: 'Canceled',
};

export function findingKey(f: Finding): string {
  return f.id || `${f.detector_id}_${f.start_line}`;
}

function sevColor(impact: string): string {
  switch (impact.toLowerCase()) {
    case 'high': return '#ff613b';
    case 'medium': return '#efbc57';
    case 'low': return '#b5c65d';
    default: return '#969591';
  }
}

interface Props {
  scans: ScanResponse[];
  activeScan: ScanResponse | null;
  onSelectScan: (id: string) => void;
  onOpenPatch: () => void;
}

export const Findings: React.FC<Props> = ({ scans, activeScan, onSelectScan, onOpenPatch }) => {
  const [view, setView] = React.useState<'table' | 'board'>(() => (localStorage.getItem('fusion.findings.view') as 'table' | 'board') || 'table');
  const [sevFilter, setSevFilter] = React.useState<string[]>(() => JSON.parse(localStorage.getItem('fusion.findings.sev') || '[]'));
  const [stateFilter, setStateFilter] = React.useState<string[]>(() => JSON.parse(localStorage.getItem('fusion.findings.state') || '[]'));
  const [detFilter, setDetFilter] = React.useState('');
  const [menuOpen, setMenuOpen] = React.useState(false);
  const [subMenu, setSubMenu] = React.useState<string | null>(null);
  const [selectedKey, setSelectedKey] = React.useState<string | null>(null);
  const [reviews, setReviews] = React.useState<Record<string, Review>>({});
  const [reviewError, setReviewError] = React.useState<string | null>(null);
  const [reason, setReason] = React.useState('');
  const menuRef = React.useRef<HTMLDivElement>(null);

  React.useEffect(() => { localStorage.setItem('fusion.findings.view', view); }, [view]);
  React.useEffect(() => { localStorage.setItem('fusion.findings.sev', JSON.stringify(sevFilter)); }, [sevFilter]);
  React.useEffect(() => { localStorage.setItem('fusion.findings.state', JSON.stringify(stateFilter)); }, [stateFilter]);
  React.useEffect(() => { setSelectedKey(null); setReviews({}); }, [activeScan?.id]);

  React.useEffect(() => {
    if (activeScan && activeScan.status === 'complete') {
      getReviews(activeScan.id).then(rs => {
        const map: Record<string, Review> = {};
        rs.forEach(r => { map[r.finding_key] = r; });
        setReviews(map);
      }).catch(() => undefined);
    }
  }, [activeScan]);

  // Focus return + outside dismissal for the filter menu (T05.13).
  React.useEffect(() => {
    if (!menuOpen) return;
    const onKey = (e: KeyboardEvent) => { if (e.key === 'Escape') { setMenuOpen(false); setSubMenu(null); } };
    const onClick = (e: MouseEvent) => { if (menuRef.current && !menuRef.current.contains(e.target as Node)) { setMenuOpen(false); setSubMenu(null); } };
    document.addEventListener('keydown', onKey);
    document.addEventListener('mousedown', onClick);
    return () => { document.removeEventListener('keydown', onKey); document.removeEventListener('mousedown', onClick); };
  }, [menuOpen]);

  const stateOf = (f: Finding): ReviewState => (reviews[findingKey(f)]?.state as ReviewState) || 'open';

  const filtered = React.useMemo(() => {
    if (!activeScan) return [];
    return activeScan.findings.filter(f => {
      if (sevFilter.length && !sevFilter.includes(f.impact)) return false;
      if (stateFilter.length && !stateFilter.includes(stateOf(f))) return false;
      if (detFilter && !f.detector_id.toLowerCase().includes(detFilter.toLowerCase())) return false;
      return true;
    });
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [activeScan, sevFilter, stateFilter, detFilter, reviews]);

  const selected: Finding | null = filtered.find(f => findingKey(f) === selectedKey) || null;

  const toggle = (list: string[], v: string, set: (l: string[]) => void) =>
    set(list.includes(v) ? list.filter(x => x !== v) : [...list, v]);

  const chips: { label: string; clear: () => void }[] = [
    ...sevFilter.map(s => ({ label: `Severity: ${s}`, clear: () => toggle(sevFilter, s, setSevFilter) })),
    ...stateFilter.map(s => ({ label: `Status: ${STATE_LABEL[s] || s}`, clear: () => toggle(stateFilter, s, setStateFilter) })),
    ...(detFilter ? [{ label: `Detector: ${detFilter}`, clear: () => setDetFilter('') }] : []),
  ];

  const doExport = async () => {
    if (!activeScan) return;
    const data = await exportScan(activeScan.id);
    const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `fusion-scan-${activeScan.id}.json`;
    a.click();
    URL.revokeObjectURL(url);
  };

  const setReviewState = async (f: Finding, state: ReviewState) => {
    if (!activeScan) return;
    setReviewError(null);
    const key = findingKey(f);
    const current = reviews[key];
    try {
      const updated = await updateReview(activeScan.id, key, {
        state, reason, version: current ? current.version : 0,
      });
      setReviews({ ...reviews, [key]: updated });
      setReason('');
    } catch (e) {
      setReviewError(e instanceof Error ? e.message : 'Review update failed');
    }
  };

  if (!activeScan) {
    return (
      <div className="card"><div className="empty-state">
        <h3>No scan history yet</h3>
        <p>Run your first curated scan to populate findings.</p>
      </div></div>
    );
  }
  if (activeScan.status !== 'complete') {
    return (
      <div className="card"><div className="alert-box danger" role="alert">
        Analysis did not complete ({activeScan.status}): {activeScan.error_message || 'no report available.'}
      </div></div>
    );
  }

  const allSev = Array.from(new Set(activeScan.findings.map(f => f.impact)));

  return (
    <div>
      <div style={{ display: 'flex', gap: '8px', alignItems: 'center', flexWrap: 'wrap', marginBottom: '10px' }}>
        <label htmlFor="scan-select" style={{ fontSize: '12px', color: 'var(--text-secondary)' }}>Scan</label>
        <select id="scan-select" className="form-select" style={{ width: 'auto' }} value={activeScan.id} onChange={e => onSelectScan(e.target.value)}>
          {scans.map(s => <option key={s.id} value={s.id}>{s.filename} · {s.id.slice(0, 12)}</option>)}
        </select>
        <div style={{ position: 'relative' }} ref={menuRef}>
          <button className="btn btn-secondary" aria-haspopup="menu" aria-expanded={menuOpen} onClick={() => { setMenuOpen(!menuOpen); setSubMenu(null); }}>
            <SlidersHorizontal size={14} /> Filter <ChevronDown size={12} />
          </button>
          {menuOpen && (
            <div className="menu" role="menu">
              {['Severity', 'Status', 'Detector'].map(field => (
                <button key={field} className="menu-item" role="menuitem"
                  onMouseEnter={() => setSubMenu(field)} onFocus={() => setSubMenu(field)}
                  onClick={() => setSubMenu(subMenu === field ? null : field)}>
                  {field}
                </button>
              ))}
              {subMenu === 'Severity' && (
                <div className="menu-sub" role="menu">
                  {allSev.map(s => (
                    <label key={s} className="menu-item"><input type="checkbox" checked={sevFilter.includes(s)} onChange={() => toggle(sevFilter, s, setSevFilter)} /> {s}</label>
                  ))}
                </div>
              )}
              {subMenu === 'Status' && (
                <div className="menu-sub" role="menu">
                  {STATES.map(s => (
                    <label key={s} className="menu-item"><input type="checkbox" checked={stateFilter.includes(s)} onChange={() => toggle(stateFilter, s, setStateFilter)} /> {STATE_LABEL[s]}</label>
                  ))}
                </div>
              )}
              {subMenu === 'Detector' && (
                <div className="menu-sub" role="menu">
                  <input className="form-input" placeholder="Detector contains…" value={detFilter} onChange={e => setDetFilter(e.target.value)} aria-label="Detector contains" />
                </div>
              )}
            </div>
          )}
        </div>
        {chips.map(c => (
          <span key={c.label} className="chip">{c.label}<button onClick={c.clear} aria-label={`Clear ${c.label}`}>×</button></span>
        ))}
        {chips.length > 0 && <button className="btn btn-secondary" onClick={() => { setSevFilter([]); setStateFilter([]); setDetFilter(''); }}>Clear all</button>}
        <span style={{ flex: 1 }} />
        <button className="btn btn-secondary" aria-label="Table view" onClick={() => setView('table')} disabled={view === 'table'}><List size={14} /></button>
        <button className="btn btn-secondary" aria-label="Board view" onClick={() => setView('board')} disabled={view === 'board'}><LayoutGrid size={14} /></button>
        <button className="btn btn-secondary" onClick={doExport}><Download size={14} /> Export</button>
      </div>

      {activeScan.findings.length === 0 && (
        <div className="card"><div className="alert-box success" role="status">No findings detected by this run. Scoped wording: this run's detectors reported nothing; it is not a safety claim.</div></div>
      )}
      {activeScan.findings.length > 0 && filtered.length === 0 && (
        <div className="card"><div className="empty-state" role="status">
          <h3>No findings match these filters</h3>
          <p>Adjust or clear the filters to restore the full set.</p>
        </div></div>
      )}

      {reviewError && <div className="alert-box danger" role="alert">{reviewError}</div>}

      {filtered.length > 0 && view === 'table' && (
        <div className="findings-table-wrap" role="region" aria-label="Findings table" tabIndex={0}>
          <table className="findings-table">
            <thead><tr>
              <th scope="col">ID</th><th scope="col">Severity</th><th scope="col">Asset / Source</th>
              <th scope="col">Confidence</th><th scope="col">Review status</th><th scope="col">Reviewer</th><th scope="col">Review date</th>
            </tr></thead>
            <tbody>
              {filtered.map(f => {
                const k = findingKey(f);
                const r = reviews[k];
                return (
                  <tr key={k} className={selectedKey === k ? 'selected' : ''} onClick={() => setSelectedKey(k)}
                    onKeyDown={e => { if (e.key === 'Enter') setSelectedKey(k); }} tabIndex={0}>
                    <td>{f.detector_id}</td>
                    <td><span className="sev"><span className="sev-sq" style={{ background: sevColor(f.impact) }} />{f.impact}</span></td>
                    <td title={`${f.file}:${f.start_line}`}>{f.file}:{f.start_line}</td>
                    <td>{f.confidence}</td>
                    <td>{STATE_LABEL[stateOf(f)]}</td>
                    <td>{r?.reviewer || '—'}</td>
                    <td>{r?.review_date || '—'}</td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      )}

      {filtered.length > 0 && view === 'board' && (
        <div className="board" role="region" aria-label="Findings board" tabIndex={0}>
          {STATES.map(st => {
            const cards = filtered.filter(f => stateOf(f) === st);
            return (
              <div key={st} className="board-col" aria-label={`${STATE_LABEL[st]} column`}>
                <div className="board-col-head"><span className="sev-sq" style={{ background: st === 'resolved' ? '#25b87b' : st === 'canceled' ? '#969591' : '#efbc57' }} />{STATE_LABEL[st]} ({cards.length})</div>
                {cards.map(f => {
                  const k = findingKey(f);
                  return (
                    <div key={k} className="board-card">
                      <div className="board-card-id"><span>{f.detector_id}</span>
                        <select aria-label={`Move ${f.detector_id} to status`} value={stateOf(f)}
                          onChange={e => setReviewState(f, e.target.value as ReviewState)}>
                          {STATES.map(s => <option key={s} value={s}>{STATE_LABEL[s]}</option>)}
                        </select>
                      </div>
                      <div className="board-card-sub">{f.file}:{f.start_line} · {f.confidence} confidence</div>
                      <div className="board-card-foot">
                        <button className="btn btn-secondary" onClick={() => { setSelectedKey(k); setView('table'); }}>Open</button>
                      </div>
                    </div>
                  );
                })}
              </div>
            );
          })}
        </div>
      )}

      {selected && (
        <div className="card" style={{ marginTop: '12px' }}>
          <div className="card-header">
            <div>
              <h3 className="card-title">{selected.detector_id} <span className="sev"><span className="sev-sq" style={{ background: sevColor(selected.impact) }} />{selected.impact}</span></h3>
              <p className="card-subtitle">{selected.file} lines {selected.start_line}–{selected.end_line} · {selected.confidence} confidence</p>
            </div>
            <button className="btn btn-primary" onClick={onOpenPatch}>Review supported patch</button>
          </div>
          <p style={{ fontSize: '13px', marginBottom: '8px' }}>{selected.explanation}</p>
          <p style={{ fontSize: '13px', color: 'var(--text-secondary)', marginBottom: '12px' }}>{selected.recommendation}</p>
          <div className="code-viewer" role="region" aria-label="Immutable source" tabIndex={0}>
            {activeScan.source_code.split('\n').map((line, i) => {
              const n = i + 1;
              const hot = n >= selected.start_line && n <= selected.end_line;
              return <div key={i} className={`code-line${hot ? ' highlighted' : ''}`}><span className="line-number">{n}</span><span className="line-content">{line || ' '}</span></div>;
            })}
          </div>
          <div style={{ display: 'flex', gap: '8px', marginTop: '12px', flexWrap: 'wrap', alignItems: 'center' }}>
            <label htmlFor="review-state" style={{ fontSize: '12px' }}>Review state</label>
            <select id="review-state" className="form-select" style={{ width: 'auto' }} value={stateOf(selected)}
              onChange={e => setReviewState(selected, e.target.value as ReviewState)}>
              {STATES.map(s => <option key={s} value={s}>{STATE_LABEL[s]}</option>)}
            </select>
            <input className="form-input" style={{ width: '220px' }} placeholder="Reason (required to resolve)" value={reason}
              onChange={e => setReason(e.target.value)} aria-label="Review reason" />
          </div>
        </div>
      )}
    </div>
  );
};

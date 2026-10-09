// Purpose: Reference shell (P04.02): sidebar, split CTA, breadcrumb row, durable hash
// routes, drawer nav. Server owns execution state; the URL owns route/filter/view.
import React from 'react';
import { FixtureInfo, ScanResponse, DemoRunResponse } from './types/api';
import { fetchFixtures, getScan, listScans, listDemoRuns, fetchCapabilities, Capabilities } from './api/client';
import { UploadPanel } from './components/UploadPanel';
import { PatchReview } from './components/PatchReview';
import { DemoEvidence } from './components/DemoEvidence';
import { Findings } from './pages/Findings';
import { Dashboard } from './pages/Dashboard';
import { Incident } from './pages/Incident';
import { Incidents, Compliance, Vault, Integrations, Help } from './pages/States';
import {
  LayoutGrid, Crosshair, FileText, BookOpenCheck, FolderOpen, Plug, CircleHelp, Menu,
} from 'lucide-react';

type Page = 'dashboard' | 'findings' | 'newscan' | 'patch' | 'incidents' | 'compliance' | 'vault' | 'integrations' | 'help';

const NAV: { id: Page; label: string; icon: React.ReactNode }[] = [
  { id: 'dashboard', label: 'Dashboard', icon: <LayoutGrid size={15} /> },
  { id: 'findings', label: 'Findings', icon: <Crosshair size={15} /> },
  { id: 'incidents', label: 'Incidents', icon: <FileText size={15} /> },
  { id: 'compliance', label: 'Compliance', icon: <BookOpenCheck size={15} /> },
  { id: 'vault', label: 'Vault', icon: <FolderOpen size={15} /> },
  { id: 'integrations', label: 'Integrations', icon: <Plug size={15} /> },
];

function parseHash(): { page: Page | 'notfound' | 'incident'; scanId: string | null; incidentId: string | null } {
  const h = window.location.hash.replace(/^#\/?/, '');
  if (!h) return { page: 'dashboard', scanId: null, incidentId: null };
  const [path, id] = h.split('/');
  if (path === 'findings' && id) return { page: 'findings', scanId: id, incidentId: null };
  if (path === 'findings') return { page: 'findings', scanId: null, incidentId: null };
  if (path === 'incidents' && id) return { page: 'incident', scanId: null, incidentId: id };
  if ((NAV.map(n => n.id) as string[]).includes(path)) return { page: path as Page, scanId: null, incidentId: null };
  if (path === 'scans' && id === 'new') return { page: 'newscan', scanId: null, incidentId: null };
  if (path === 'patch') return { page: 'patch', scanId: null, incidentId: null };
  return { page: 'notfound', scanId: null, incidentId: null }; // unknown route: explicit recovery, not silent redirect
}

export const App: React.FC = () => {
  const [route, setRoute] = React.useState(parseHash);
  const [fixtures, setFixtures] = React.useState<FixtureInfo[]>([]);
  const [scans, setScans] = React.useState<ScanResponse[]>([]);
  const [activeScan, setActiveScan] = React.useState<ScanResponse | null>(null);
  const [isScanning, setIsScanning] = React.useState<boolean>(false);
  const [pollError, setPollError] = React.useState<string | null>(null);
  const [demoRuns, setDemoRuns] = React.useState<DemoRunResponse[] | null>(null);
  const [caps, setCaps] = React.useState<Capabilities | null>(null);
  const [drawer, setDrawer] = React.useState(false);
  const drawerBtnRef = React.useRef<HTMLButtonElement>(null);
  // Drawer: Escape closes and focus returns to the trigger (T04.10).
  React.useEffect(() => {
    if (!drawer) return;
    const onKey = (e: KeyboardEvent) => {
      if (e.key === 'Escape') {
        setDrawer(false);
        drawerBtnRef.current?.focus();
      }
    };
    document.addEventListener('keydown', onKey);
    return () => document.removeEventListener('keydown', onKey);
  }, [drawer]);
  const [scanMissing, setScanMissing] = React.useState(false); // bad findings id -> explicit recovery (T04.11)
  const pollSeq = React.useRef(0);

  React.useEffect(() => {
    const onHash = () => { setRoute(parseHash()); };
    window.addEventListener('hashchange', onHash);
    return () => window.removeEventListener('hashchange', onHash);
  }, []);

  // Re-evaluate id matches on every route/scan-list change (back/forward-safe).
  React.useEffect(() => {
    if (route.page === 'findings' && route.scanId && scans.length > 0) {
      setScanMissing(!scans.some(s => s.id === route.scanId));
    } else if (route.page === 'findings' && !route.scanId) {
      setScanMissing(false);
    }
  }, [route.page, route.scanId, scans]);

  const go = (hash: string) => { window.location.hash = hash; setDrawer(false); };

  React.useEffect(() => {
    fetchFixtures().then(setFixtures).catch(() => undefined);
    listScans(20, 0).then(s => {
      setScans(s);
      const { page, scanId } = parseHash();
      if (page === 'findings') {
        // A findings route without an id opens the most recent scan (T04.08/T04.12).
        // An id that matches nothing shows an explicit not-found recovery (T04.11).
        const match = scanId ? s.find(x => x.id === scanId) : undefined;
        setScanMissing(!!scanId && !match && s.length > 0);
        setActiveScan(match || s[0] || null);
      } else if (scanId) {
        getScan(scanId).then(setActiveScan).catch(() => undefined);
      }
    }).catch(() => undefined);
    listDemoRuns().then(setDemoRuns).catch(() => setDemoRuns([]));
    fetchCapabilities().then(setCaps).catch(() => undefined);
  }, []);

  // Poll the active scan until a terminal state; ignore stale responses (T03.09).
  React.useEffect(() => {
    if (!activeScan) return;
    if (['complete', 'error', 'unsupported', 'timeout'].includes(activeScan.status)) {
      setIsScanning(false);
      return;
    }
    setIsScanning(true);
    setPollError(null);
    const seq = ++pollSeq.current;
    const interval = setInterval(async () => {
      try {
        const updated = await getScan(activeScan.id);
        if (seq !== pollSeq.current) return;
        setPollError(null);
        setActiveScan(updated);
        setScans(prev => {
          const rest = prev.filter(s => s.id !== updated.id);
          return [updated, ...rest];
        });
        if (['complete', 'error', 'unsupported', 'timeout'].includes(updated.status)) {
          setIsScanning(false);
          clearInterval(interval);
          if (updated.status === 'complete') go(`#/findings/${updated.id}`);
        }
      } catch (err) {
        if (seq !== pollSeq.current) return;
        setPollError(err instanceof Error ? err.message : 'Polling failed');
      }
    }, 1000);
    return () => clearInterval(interval);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [activeScan?.id, activeScan?.status]);

  const retryPoll = async () => {
    if (!activeScan) return;
    setPollError(null);
    try {
      setActiveScan(await getScan(activeScan.id));
    } catch (err) {
      setPollError(err instanceof Error ? err.message : 'Polling failed');
    }
  };

  const handleScanCreated = (scan: ScanResponse) => {
    setScans(prev => [scan, ...prev.filter(s => s.id !== scan.id)]);
    setActiveScan(scan);
  };

  const openScan = (id: string) => {
    const found = scans.find(s => s.id === id);
    setScanMissing(!found && scans.length > 0);
    if (found) setActiveScan(found);
    else if (scans.length > 0) setActiveScan(scans[0]);
    else getScan(id).then(setActiveScan).catch(() => setScanMissing(true));
    go(`#/findings/${id}`);
  };

  const titles: Record<Page | 'notfound' | 'incident', string> = {
    dashboard: 'Dashboard', findings: 'Findings', newscan: 'New scan', patch: 'Patch review',
    incidents: 'Incidents', compliance: 'Compliance / Check coverage', vault: 'Vault',
    integrations: 'Integrations', help: 'Help & Docs', notfound: 'Not found', incident: 'Incident detail',
  };

  return (
    <div className="app-shell">
      <a className="skip-link" href="#main">Skip to content</a>
      {drawer && <button className="sidebar-scrim" aria-label="Close navigation" onClick={() => setDrawer(false)} />}
      <aside className={`sidebar${drawer ? ' open' : ''}`} aria-label="Primary">
        <div className="sidebar-brand">FUSION</div>
        <div className="split-cta">
          <button className="split-cta-main" onClick={() => go('#/scans/new')}>New scan</button>
          <button className="split-cta-plus" aria-label="More scan modes" title="Fixture, file, and paste modes" onClick={() => go('#/scans/new')}>+</button>
        </div>
        <nav className="sidebar-nav">
          {NAV.map(n => {
            const active = route.page === n.id || (route.page === 'incident' && n.id === 'incidents');
            return (
              <button key={n.id} className={`sidebar-link${active ? ' active' : ''}`}
                aria-current={active ? 'page' : undefined}
                onClick={() => go(`#/${n.id}`)}>
                {n.icon} {n.label}
              </button>
            );
          })}
        </nav>
        <div className="sidebar-foot">
          <button className={`sidebar-link${route.page === 'help' ? ' active' : ''}`} onClick={() => go('#/help')}>
            <CircleHelp size={15} /> Help &amp; Docs
          </button>
          <div style={{ fontSize: '11px', color: 'var(--text-muted)' }} title="Workspace label, not a login">Local workspace</div>
        </div>
      </aside>

      <div className="shell-main">
        <div className="crumb-row">
          <span>
            <button ref={drawerBtnRef} className="btn btn-secondary drawer-btn" aria-label="Open navigation" aria-expanded={drawer} onClick={() => setDrawer(true)}><Menu size={14} /></button>
            <a href="#/dashboard">Fusion</a> › {titles[route.page]}
          </span>
          <span>{isScanning ? 'Scan running…' : caps ? (caps.ready ? 'Toolchain ready' : 'Toolchain degraded') : ''}</span>
        </div>
        <h1 className="page-title">{titles[route.page]}</h1>

        {pollError && activeScan && (
          <div className="alert-box danger" role="alert">
            <div style={{ display: 'flex', gap: '8px', justifyContent: 'space-between', flexWrap: 'wrap', alignItems: 'center' }}>
              <span>Scan status updates interrupted: {pollError}. The scan continues on the server.</span>
              <button className="btn btn-secondary" onClick={retryPoll}>Retry</button>
            </div>
          </div>
        )}

        <main id="main">
          {route.page === 'dashboard' && <Dashboard onOpenScan={openScan} onOpenIncident={id => go(`#/incidents/${id}`)} />}
          {route.page === 'findings' && !scanMissing && (
            <Findings scans={scans} activeScan={activeScan} onSelectScan={openScan} onOpenPatch={() => go('#/patch')} />
          )}
          {route.page === 'findings' && scanMissing && (
            <div className="card"><div className="empty-state" role="alert">
              <h3>Scan record not found</h3>
              <p>This link does not match a stored scan. The latest scan is shown below once selected.</p>
              <div style={{ display: 'flex', gap: '8px', justifyContent: 'center', marginTop: '8px' }}>
                <button className="btn btn-primary" onClick={() => { setScanMissing(false); if (scans[0]) openScan(scans[0].id); }}>Open latest scan</button>
                <button className="btn btn-secondary" onClick={() => go('#/scans/new')}>New scan</button>
              </div>
            </div></div>
          )}
          {route.page === 'newscan' && (
            <UploadPanel fixtures={fixtures} activeScan={activeScan} onScanCreated={handleScanCreated} isScanning={isScanning} />
          )}
          {route.page === 'patch' && (
            <PatchReview scan={activeScan} onNavigateToDemo={() => go('#/incidents')} />
          )}
          {route.page === 'incidents' && (
            <div>
              <DemoEvidence />
              <Incidents runs={demoRuns} onOpen={id => go(`#/incidents/${id}`)} />
            </div>
          )}
          {route.page === 'incident' && route.incidentId && (
            <Incident runId={route.incidentId} onBack={() => go('#/incidents')} />
          )}
          {route.page === 'compliance' && <Compliance />}
          {route.page === 'vault' && <Vault />}
          {route.page === 'integrations' && <Integrations caps={caps} />}
          {route.page === 'help' && <Help />}
          {route.page === 'notfound' && (
            <div className="card"><div className="empty-state" role="alert">
              <h3>Unknown destination</h3>
              <p>This link does not match a workbench page.</p>
              <button className="btn btn-primary" onClick={() => go('#/dashboard')}>Back to Dashboard</button>
            </div></div>
          )}
        </main>
      </div>
    </div>
  );
};

export default App;

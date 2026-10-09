// Purpose: Honest destination states for pages whose full function lands in later phases.
import React from 'react';
import { Capabilities } from '../api/client';

export const PageNote: React.FC<{ title: string; children: React.ReactNode }> = ({ title, children }) => (
  <div className="card">
    <div className="card-header"><div><h3 className="card-title">{title}</h3></div></div>
    <div style={{ fontSize: '13px', color: 'var(--text-secondary)' }}>{children}</div>
  </div>
);

export const Incidents: React.FC<{ runs: import('../types/api').DemoRunResponse[] | null; onOpen: (id: string) => void }> = ({ runs, onOpen }) => (
  <div className="card">
    <div className="card-header"><div>
      <h3 className="card-title">Incidents</h3>
      <p className="card-subtitle">Local replay runs on the app-owned Anvil session. Select a run for detail.</p>
    </div></div>
    {runs === null ? <div className="skeleton" style={{ height: '60px' }} /> :
      runs.length === 0 ? <div className="empty-state">No local runs recorded yet.</div> : (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
          {runs.map(r => (
            <button key={r.id} className="menu-item" style={{ border: '1px solid var(--line-subtle)', borderRadius: '4px' }} onClick={() => onOpen(r.id)}>
              <span className="sev-sq" style={{ background: r.status === 'complete' ? '#25b87b' : '#f65c66' }} />
              {r.id.slice(0, 12)} · {r.status}{r.is_historical ? ' · historical' : ''}
            </button>
          ))}
        </div>
      )}
  </div>
);

export const Compliance: React.FC = () => (
  <PageNote title="Compliance / Check coverage">
    Local check coverage lands in P09. No regulatory certification is claimed. Required check
    profiles, evidence attachments, and the heatmap will appear here.
  </PageNote>
);

export const Vault: React.FC = () => (
  <PageNote title="Vault">
    The source and evidence vault lands in P09: searchable immutable artifacts with hash-bound
    downloads. Nothing here is a wallet or key store.
  </PageNote>
);

export const Integrations: React.FC<{ caps: Capabilities | null }> = ({ caps }) => (
  <div className="card">
    <div className="card-header"><div>
      <h3 className="card-title">Integrations</h3>
      <p className="card-subtitle">Local tool capabilities. Refresh is read-only; nothing here installs software.</p>
    </div></div>
    {caps === null ? <div className="skeleton" style={{ height: '60px' }} /> : (
      <div className="metadata-strip">
        <div><strong>Mode:</strong> {String(caps.worker_mode)}</div>
        <div><strong>Ready:</strong> {caps.ready ? 'yes' : 'degraded'}</div>
        <div><strong>Arbitrary upload:</strong> {caps.arbitrary_upload_available ? 'available' : 'unavailable — curated only'}</div>
        {Object.entries(caps.observed_tool_versions || {}).map(([k, v]) => (
          <div key={k}><strong>{k}:</strong> {String(v).slice(0, 60)}</div>
        ))}
      </div>
    )}
  </div>
);

export const Help: React.FC = () => (
  <PageNote title="Help & Docs">
    <p>1. Pick a curated fixture in New scan and run Slither analysis.</p>
    <p>2. Review findings in the table or board; change review states with reasons.</p>
    <p>3. Propose the supported patch for the exact vault, validate, then accept or revoke.</p>
    <p>4. Arbitrary uploads stay disabled until the isolated worker passes its gates.</p>
    <p style={{ marginTop: '8px' }}>Statuses: queued → compiling → analyzing → complete; error, unsupported, and timeout are terminal failures, never clean scans. Works offline once dependencies are installed.</p>
  </PageNote>
);

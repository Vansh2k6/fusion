<!-- Purpose: Explain current frontend ownership, startup, planned reference UI migration, state rules, and verification. -->
# Frontend

React 18, TypeScript, Vite and Lucide form the existing UI. Exact resolved versions are in package-lock.json; package.json currently declares dev/build/preview scripts. Do not describe a browser-test command as available until implemented.

## Run and build

From frontend:
```powershell
npm ci
npm run dev -- --host 127.0.0.1 --port 5173
npm run build
```

Vite proxies /api to the loopback backend at port 8000. Prepare dependencies before offline use. A build runs TypeScript and Vite bundling; it does not test interactions or reference fidelity.

## Existing files

| File | Ownership |
|---|---|
| src/main.tsx | React entry point |
| src/App.tsx | Current four-tab navigation and scan polling |
| src/api/client.ts | Fixture/scan/patch/demo requests and exports |
| src/types/api.ts | Typed response models |
| src/styles.css | Current palette/layout; migration to reference tokens required |
| src/components/UploadPanel.tsx | Fixture/file/paste controls and scan status |
| src/components/FindingsPanel.tsx | Finding selection and source rendering |
| src/components/PatchReview.tsx | Candidate diff, checks, selection, export |
| src/components/DemoEvidence.tsx | Local chain run and evidence display |
| vite.config.ts | Loopback dev server and local API proxy |

## Target migration

[Design](../CONTEXT/design.md) replaces top tabs with the exact reference sidebar and page shell. P04 establishes tokens/primitives/routing; P05 findings table/board/filters; P06 patch flow; P07 incidents; P08 dashboard; P09 coverage/vault/integrations; P10 3D and presentation. Preserve the working scan while moving components into routes.

Group reusable primitives, route pages, findings components, evidence charts and lazy 3D scenes by responsibility. Add dependencies only when needed and lock compatible versions. Do not build a second disconnected demo UI.

Backend owns run state, capability status, review/selection history and hashes. Route/query state owns current record/filter/view. Component state owns temporary controls/forms. Abort or ignore stale responses; immediately prevent duplicate submissions. Refresh must restore the exact selected record/revision.

## Rendering and interaction rules

Render source/report text safely. Use integer-safe wei formatting, not Number conversion. Keep failed/unsupported/pending/completed-zero/filtered-empty states distinct. Capabilities come from API, not hardcoded green status pills.

All enabled controls work, with keyboard paths and accessible names. Chart values link to actual evidence. Reference showcase has separate deterministic sample data and no mutating live client. Globes/device decorations do not intercept input or block scanner loading; provide motion/WebGL fallbacks.

## Verification

Add and run component behavior, real-browser journey and visual tests under the phase plan. Cover delayed/out-of-order responses, backend loss, duplicate clicks, refresh/back navigation, source safety, large integers, table/board parity and focus restoration. Inspect captures for all six references at 375/768/1024/1440 widths, plus keyboard/200% zoom/reduced motion.

Do not claim these tests already exist merely because this README specifies them. Record actual scripts, outcomes and screenshot paths in [progress](../CONTEXT/progress.md).

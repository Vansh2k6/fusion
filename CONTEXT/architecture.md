<!-- Purpose: Define current components, target interfaces, state ownership, persistence, execution boundaries, and migration strategy. -->
# Fusion architecture

## 1. Status and topology

This is the target architecture for the expanded product. The existing app has scan/patch/demo routes, SQLite tables, a native curated worker, and four React panels. Capabilities, normalized revision/run models, isolation, expanded pages, and 3D scenes below are planned until verified in [progress.md](progress.md). Existing filenames are entry points, not a mandate to preserve every implementation detail.

```text
React routes / typed API client
  -> loopback FastAPI / policy + capability checks
     -> SQLite metadata and event history
     -> immutable source / report / trace artifacts
     -> bounded job queue
        -> curated native adapter OR verified isolated worker
        -> solc + Slither
     -> reviewed-template service -> candidate revision
        -> isolated approved validation harness -> Foundry + Slither
     -> owned local Anvil session -> hash-bound deploy/replay
        -> receipts / optional traces -> incidents / dashboard
```

No external AI or network service is necessary at runtime. SQLite and local files are sufficient; use polling and one active analysis slot. The API remains responsive while tools execute. UI navigation and decorative scenes never own execution state.

## 2. Current module ownership

| Existing file/module | Responsibility and required direction |
|---|---|
| backend/app/main.py | App lifespan, route wiring, local request boundary; separate liveness/readiness |
| config.py | Roots, limits, expected versions, approved fixture/tool profiles |
| tooling.py | Bounded observed-version/capability probes; never substitute expected pins |
| database.py | Connection lifecycle and migrations; avoid hidden destructive initialization |
| storage.py | Immutable byte storage, hashes, atomic writes, resolved containment |
| schemas.py | Typed requests/responses/errors; explicit states and large integer strings |
| jobs.py | Bounded queue, worker lifecycle, terminal errors, restart recovery |
| analysis/runner.py | Safe execution, limits, fresh reports, actual tool result |
| analysis/slither.py and normalize.py | Detector/result adaptation, locations, severity/confidence |
| patches/service.py | Exact-template eligibility, candidates, diff, selection history |
| patches/validation.py | Fresh candidate/harness runs and check evidence |
| monitoring/observer.py | Managed chain identity, serialized replay/reset, receipt correlation |
| routes/scans.py | Ingestion, history, status, reports and fixture metadata |
| routes/patches.py | Proposal, retrieval, validation, acceptance/revocation, export |
| routes/demo.py | Curated local run history/details and controlled reset |
| frontend/src/api/client.ts | Typed transport, errors, cancellation and downloads |
| frontend/src/types/api.ts | UI-facing API types aligned with backend schema |
| frontend/src/App.tsx | Current four-tab root; migrate to reference route shell |
| components/UploadPanel.tsx | Existing scan entry/status, migrate into new-scan flow |
| components/FindingsPanel.tsx | Current findings/source presentation |
| components/PatchReview.tsx | Current diff/check/selection presentation |
| components/DemoEvidence.tsx | Current local-run presentation |
| frontend/src/styles.css | Existing warm palette; replace layout/tokens per design |

Target frontend modules may include shell/Sidebar, common primitives, route pages, findings table/board/filter components, source/diff views, evidence charts, and lazy scenes. Reuse sound existing logic; do not create duplicate parallel apps. Tests and READMEs follow ownership.

## 3. Source and execution boundary

Ingestion accepts exactly one of fixture ID, one .sol upload, or UTF-8 pasted source. Default byte limit is 256 KiB; enforce during read. Client filename is display-only. No ZIP/repository import in this plan.

Save bytes atomically with server-generated IDs; compute SHA-256 before any display transformations. Decode for preview after encoding validation. Record encoding/BOM policy without silently modifying input. Fixture selection must read bytes and verify approved hash. Every executor checks policy itself; route checks alone are insufficient.

Compiler selection uses installed approved compatible profiles. Imports resolve only under explicitly approved job/dependency roots, using syntax-aware discovery and resolved filesystem checks. Reject remote/absolute/unapproved imports, traversal, reparse escapes, uploaded configuration and scripts. No compiler/library downloads during scans. A compiler mismatch is unsupported, not permission to rewrite pragma.

Curated native execution remains limited to approved exact bytes. Arbitrary execution needs the verified worker launch profile: non-root, no network, read-only root, restricted capabilities, no home/socket/secrets mounts, input read-only, bounded output/temp. Initial policy defaults: 60-second analysis/validation wall-clock budgets, 1 MiB retained log output, 5 MiB raw report, one active job. P02 must add and measure CPU/memory/PID/disk/queue limits; configuration alone does not prove enforcement.

Read output incrementally and limit disk while writing, not after reading an enormous file into memory. Kill the process tree/container on timeout or limit breach. Fresh workspace/report path per attempt; never reuse stale JSON. Preserve bounded diagnostics and terminal reason.

## 4. Data model and migrations

Existing schema contains scans, findings, patches, per-check validation_runs, and demo_runs. It is not yet the fully normalized target below. Introduce versioned non-destructive migrations, retain legacy evidence with provenance limitations, and test upgrades on a DB copy.

| Target record | Key fields / invariant |
|---|---|
| SourceRevision | id, parent_id, kind, byte_sha256, byte_size, artifact_id, display_name, encoding, created_at; bytes immutable |
| Scan | id, revision_id, status, stage/timestamps, observed tools, expected profile, exit/result metadata, error code, raw artifact; one explicit attempt identity |
| Finding | id, scan_id, detector_id, impact, confidence, message/guidance, source range, raw evidence; detector output immutable |
| FindingReview | finding_id, state, reason, optional local reviewer/date, version, updated_at; separate from detector |
| PatchProposal | id, scan_id, original_revision_id, candidate_revision_id, template_id/version/hash, preconditions, diff artifact |
| RevisionSelection | scan/context id, selected_revision_id, version; exactly one selected revision per context |
| SelectionEvent | action, previous/new revision, timestamp, explicit unvalidated acknowledgment if applicable |
| ValidationRun | id, candidate_hash, original_hash, harness/config hashes, observed tools, seed/settings, parent state/times |
| ValidationCheck | run_id, check_id/type, outcome, duration, detail, log artifact; unique per run/check |
| ChainSession | id, endpoint, chain_id, managed process/start identity, session nonce, lifecycle, reset timestamp |
| DemoRun | id, session_id, revision/bytecode hashes, harness/tool metadata, scenario, addresses, step outcomes |
| TransactionEvidence | run_id, role/step, tx hash, receipt, status, gas/fee strings, balance snapshots, trace availability/artifact |
| Incident | run_id, observed outcome, evidence refs, separate hypothesis, review state, timestamp |
| Artifact | id, parent/run/revision, kind, internal relative path, sha256, size, content type, retention/historical state |
| ActivityEvent | id, entity/type, immutable action/time, references; powers actual activity feed |
| CheckProfile | id/version and required check IDs; defines coverage denominator |

UTC timestamps at rest; local timezone formatting in UI with explicit absolute-time access. Wei, gas-related large integers, and balances are decimal strings. Use integers/BigInt for calculations; never JS Number for wei. Database unique constraints and transactions enforce idempotency. Close connections in success and failure paths.

Artifacts are managed within configured roots. Download by artifact ID, not caller path. Validate containment/hash before read. Original/candidate source is never overwritten. Migrations do not reinterpret absent historical metadata as trustworthy current values.

## 5. State machines

Scan: queued -> compiling -> analyzing -> complete. Terminal alternatives: error, unsupported, timeout. Interruption/resource limits can use a stable error_code under error, avoiding undocumented status proliferation. Stages reflect actual execution; combined compiler/analyzer operation may expose a documented combined message without fake percentages.

Validation parent: queued -> running -> complete or error/timeout. Checks: passed, failed, skipped, unsupported, timeout. Parent completion does not mean all checks passed. Aggregate eligible=true only if every required check for the profile passed in the same hash/tool/harness-bound run. A failed prerequisite creates explicit skipped dependent checks.

Selection: original or an exact candidate revision. It is independent of validation. New edits create new revisions; old evidence remains historical for old bytes. Accepted does not mean deployed. Explicit unvalidated selection is permitted with acknowledgment; validated replay remains disabled.

Review: open, triaged, in_progress, resolved, canceled. Review changes never mutate detector output. Resolved requires reason/evidence. Optimistic concurrency uses a version/ETag or equivalent; stale writes return conflict.

Demo: queued/running -> complete or error. Persist completed transaction steps even if a later step fails. Chain session reset makes all prior runs historical; old addresses cannot be reused as live deployment handles.

## 6. API inventory and target extensions

Existing endpoints observed in source:

| Method/path | Purpose |
|---|---|
| GET /api/health | Current process/tool status; readiness semantics need hardening |
| GET /api/fixtures | Curated metadata and preview |
| POST /api/scans | Multipart fixture/file/source submission |
| GET /api/scans | Current recent history |
| GET /api/scans/{id} | Source/status/findings |
| GET /api/scans/{id}/export | Scan JSON export |
| POST /api/scans/{id}/patches | Supported proposal |
| GET /api/patches/{id} | Candidate/diff/selection |
| POST /api/patches/{id}/validate | Current synchronous validation request |
| POST /api/patches/{id}/accept | Select candidate |
| POST /api/patches/{id}/revoke | Select original |
| GET /api/patches/{id}/export | Candidate plus validation metadata |
| POST /api/demo/runs | Current curated replay |
| GET /api/demo/runs | Run history |
| GET /api/demo/runs/{id} | Evidence |
| POST /api/demo/reset | Controlled reset |

Planned extensions, not yet implemented:
- GET /api/capabilities: readiness, observed/expected tools, worker modes, compiler/import profiles, chain ownership status and check time.
- Stable cursor pagination/filter parameters for scan/finding/run history; deterministic secondary ordering.
- GET /api/findings and PATCH /api/findings/{id}/review: cross-scan filtered review and versioned mutations.
- GET /api/validation-runs/{id}: poll a queued validation parent; POST validation eventually returns accepted job identity.
- GET /api/dashboard and GET /api/activity: defined scoped aggregates/events.
- GET /api/check-profiles and GET /api/checks: coverage and evidence, no regulatory certification.
- GET /api/artifacts, GET /api/artifacts/{id}, GET /api/artifacts/{id}/download: controlled inventory/preview/download.
- POST bounded evidence attachments and local note/reviewer mutations with explicit schema.
- Incident list/detail derived from real demo records with notes/review state.

Prefer additive migrations and compatibility responses until the frontend changes together. Document final request/response examples in tests/OpenAPI. Stable errors include code, message, operation/entity ID where available, retryable flag, and safe details. Use 400 for invalid input, 404 missing ID, 409 state/integrity conflict, 413 size, 422 schema errors, 429 queue overload, and 503 unavailable required capability. Do not leak stack traces/host paths.

Mutating requests need server-side input/capability checks regardless of disabled UI. Loopback binding alone is not a complete browser request boundary; validate host/origin and use an appropriate local mutation token/origin strategy without inventing a login product.

## 7. Validation and chain evidence flow

Proposal checks approved original/template bytes. Validation copies exact candidate into a fresh controlled project with approved tests/configuration; records all hashes. Compile failure prevents dependent runtime tests. Real rescan checks target detector while preserving other findings. Original exploit establishes the baseline; candidate attack and normal behavior establish bounded mitigation evidence. Fuzz inputs must exercise the permitted domain.

Replay uses the exact eligible candidate artifacts, not whatever happens to be in a shared contracts directory. Verify bytecode/source relationships and record compiler settings. Confirm managed Anvil ownership before transactions. Serial run/reset lock prevents interleaving. Each transaction has expected step, real hash, receipt status, and snapshots. Missing receipt/trace yields explicit error/unavailable state, never invented data.

After successful reset, change session identity, invalidate deployment handles, and mark prior records historical. If reset succeeds but persistence fails, block new replay until reconciliation; do not silently continue with stale history.

## 8. Frontend state and design boundary

Server state is fetched/polled through typed client code and keyed by record ID. Abort or ignore stale responses after navigation. Local state holds forms/open menus; URL holds route/filter/view; DB holds review/selection/evidence. A request starts busy state before awaiting the response. Retry must not accidentally repeat deployment.

Reference showcase uses separate deterministic fixture data and explicit mode identity. It cannot access mutating live transport. Shared visual components accept typed live/sample models and preserve a visible mode marker. Live charts derive from actual scoped records; unavailable values do not become sample values.

Three.js is lazy-loaded for decorative scenes only; SVG charts expose table equivalents. Scene errors never crash the scanner route. Dispose resources and stop hidden rendering. See [design.md](design.md) for geometry and states.

## 9. Testability, observability, and recovery

Inject clock, artifact root, DB path, execution adapter, and RPC transport for tests. Test doubles are limited to failure/unit tests. Real-tool suites have explicit markers and isolated data. Log operation/job IDs and safe diagnostics; keep sources local and avoid secrets.

Structured evidence should make a bug reproducible: input hash, tool version, operation state, bounded stderr, run/harness identity. On startup, reconcile interrupted jobs and chain session; never leave unbounded queued/running spinners. Preserve partial evidence with incomplete status.

The detailed acceptance matrix is in [phases.md](phases.md). No architecture diagram, dependency installation, or endpoint returning 200 independently proves the product works.

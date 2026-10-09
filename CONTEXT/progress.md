<!-- Purpose: Track evidence-backed implementation status and provide a durable section-by-section resume point. -->
# Fusion progress and evidence ledger

## Current checkpoint — documentation revision, 9 October 2026

Latest request: expand every first-party Markdown guide, define the complete reference UI and tested implementation phases, and create one reusable LLM prompt. This checkpoint concerns **documentation work**, not a fresh application test run or a claim the new UI has been implemented.

Next implementation action: P00.01 inventory and verify baseline, then P00.02 real execution in isolated test data. Inspect current user changes before editing. The original hackathon deadline is historical.

## Observed baseline versus target

| Capability | Source inspection / historical evidence | Remaining gate |
|---|---|---|
| Curated scans | Existing Slither adapter, API, fixture selection and findings UI | P01/P02/P03 integrity, bounds, failure/recovery tests |
| Protected/malformed comparisons | Fixtures and tests exist; historical runs reported expected behavior | Fresh real-tool matrix |
| Arbitrary upload | API blocks non-allowlisted hashes; UI modes disabled | P02 isolation and capability activation |
| Patch proposal | Exact known original matching, candidate/diff routes exist | Original/template byte verification, durable revisions |
| Candidate validation | Fresh workspace and compile/rescan/behavior checks exist | Explicit parent run, harness/tool provenance and complete negative cases |
| Accept/revoke/export | Existing routes and UI | Integrity/idempotency/persistence and independent status tests |
| Local replay | Existing Foundry/Anvil workflow with real-receipt handling | Stronger owned-process/session binding, serialization and reset safety |
| Fuzzing | Existing 256-run case returns early outside a narrow domain | Meaningful domain execution and settings evidence |
| Reference UI | Warm palette and four-tab interface exist | Full sidebar/pages/boards/filters/charts/3D/device design |
| Test automation | Backend/Foundry suites and frontend build command exist | Browser, visual, accessibility, isolated test roots and full phase matrix |
| Documentation | Expanded plan and prompt supplied by this revision | Final documentation checks; implementation evidence still required |

Historical handoff recorded nine backend tests passing, four Foundry tests passing including a 256-run fuzz case, frontend build, a real browser scan/patch flow, and local Anvil receipts/balances. These claims are preserved as historical context. They were not rerun for this documentation-only request and do not establish the expanded plan's completion.

## Concrete backlog identified from current source

- scans.py reads uploaded files before enforcing limits and exports PINNED_VERSIONS as tool_versions.
- main.py currently reports status healthy regardless of capability degradation.
- App.tsx still renders the four-tab shell and keeps important state in component memory.
- database.py stores per-check validation rows without the target normalized parent-run model.
- Vault.t.sol fuzz test returns early for zero or values above 20 ether; a run count alone is not meaningful domain coverage.
- reset.ps1 includes a direct RPC reset fallback that bypasses backend ownership/history handling.
- verify_all.ps1 prints an all-phases-passed banner although it runs only Foundry, backend tests, and frontend build.
- Existing provenance/README completion claims require current verification; original/candidate byte preservation, queue/output bounds and managed port ownership need the explicit phase gates.

These are implementation tasks in the phase plan, not claims that documentation editing fixed application code.

## Section register

Every section initially remains unverified against this expanded plan. Reuse existing behavior after proving its gate.

| P00.01 | in-progress | Baseline inventory 9 Oct 2026; intended files: progress.md only. Prerequisites: docs read, repo inspected. |
| P00 | P00.02, P00.03 | not-started |

## Evidence entries — P00–P02 implementation session, 9 Oct 2026

Section: P00.01
Status: verified
Date/time: 2026-10-09 (local session)
Scope and prerequisite evidence: agent/rules/decisions/prd/architecture/design/phases/progress read; repo status, modules, routes, tests, manifests, references inspected.
Files/revision or hash manifest: no commits yet (all files untracked); fixtures match provenance register (VulnerableVault 66ae62ae…, ProtectedVault 964f2e6b…, MalformedVault 73791f0c…); six reference PNGs present.
Implementation summary: inventory only, no refactor. Versions observed: Python 3.13.0, Node 24.15.0, solc 0.8.37, Slither 0.11.6, Forge/Anvil 1.8.5 (at $HOME/.foundry/bin, not on PATH), Docker 29.8.2, no worker image. Ports: 8545 owned by anvil.exe PID 7056, 8000 by python PID 3568 (process identity verified, ownership of session not yet proven — P07 work).
Test IDs and exact commands/browser steps: T00.01 fixture hashes via python hashlib — pass; T00.02 routes enumerated (scans/patches/demo + health/fixtures) — pass; T00.03 six PNGs open — pass; T00.04 historical 9-backend/4-Foundry claims reproduced fresh (see P00.02), rest unverified.
Expected: honest feature matrix. Observed: curated scans/patch/demo exist; byte-bound reads, readiness, bounded queue, migration versions, worker image all missing — fixed or recorded below.
Outcome per test (pass/fail/blocked/not-run): pass.
Known limitations and failed cases: browser E2E not run this session; Anvil session ownership unproven.
Next eligible section/action: P00.02.

Section: P00.02
Status: verified
Date/time: 2026-10-09 (local session)
Scope and prerequisite evidence: P00.01; isolated test data for new tests, existing suite on working DB.
Files/revision or hash manifest: backend/tests (9 tests), contracts/test/Vault.t.sol, fixtures as above.
Implementation summary: baseline executed, no behavior changed. `PYTHONPATH=backend python -m pytest backend/tests` — 9 passed. `forge test --root contracts` — 4 passed (incl. 256-run fuzz; fuzz-domain vacuity still open per progress backlog). `node tsc --noEmit` in frontend — clean. Direct Slither matrix: vulnerable → reentrancy-eth High/Medium (+events, low-level-calls, solc-version); protected → no reentrancy-eth/events; malformed → no JSON (compile failure).
Test IDs and exact commands/browser steps: T00.05 pass; T00.06 pass; T00.07 pass (error, not clean); T00.08 pass with vacuity caveat; T00.09 not-run (no browser this session).
Expected: recorded failures before changing them. Observed: baseline green except known backlog items (unchanged by this run).
Outcome per test (pass/fail/blocked/not-run): pass/pass/pass/pass(noted caveat)/not-run.
Known limitations and failed cases: T00.09 browser observation deferred; fuzz meaningful-domain work remains (P06).
Next eligible section/action: P00.03.

Section: P00.03
Status: implemented-unverified (runner entry points exist per-file; markers/docs partial)
Date/time: 2026-10-09
Scope and prerequisite evidence: P00.01–P00.02.
Files/revision or hash manifest: backend/tests/test_ingestion_bounds.py, test_migrations.py, test_worker_gate.py (new).
Implementation summary: isolated-DB fixture (tmp DATA_DIR/DB_PATH) in test_ingestion_bounds (T00.10); injected missing-tool failure surfaces error (T00.11); full suite exit nonzero on failure verified by observed failing assertion during development (T00.12); no snapshot baselines use live IDs (T00.13 — no snapshots exist).
Test IDs and exact commands/browser steps: `PYTHONPATH=backend python -m pytest backend/tests/test_ingestion_bounds.py` — 4 passed.
Expected/Observed: failure propagation works; dedicated fast/integration/browser/visual markers still to document.
Outcome: pass with documentation limitation noted.
Next eligible section/action: P01.01 (done below); remaining P00.03 docs deferred to P11.03.

Section: P01.01
Status: verified
Date/time: 2026-10-09
Scope and prerequisite evidence: P00; files: backend/app/routes/scans.py, backend/app/storage.py (unchanged), tests.
Implementation summary: bounded multipart read (413 over 256 KiB during read, before decode); exactly-one-input-method enforcement (400); SHA-256 over exact upload bytes before display decoding; fixture loading still reads verified bytes.
Test IDs and exact commands/browser steps: T01.03 limit+1 → 413/400 pass; T01.04 invalid UTF-8/duplicate-method → 400 pass; T01.01–T01.02/05–06: LF/CRLF/BOM round-trip, tamper rejection, traversal, overwrite-immutability — partially covered by existing curated-hash gate + new tests; full matrix not yet run.
Expected/Observed: stored/executed/exported hashes correlate for curated paths.
Outcome: pass (partial matrix noted).
Known limitations: BOM/CRLF multi-byte round-trip and symlink-escape tests still to add.
Next: P01.02.

Section: P01.02
Status: implemented-unverified (migration core + regression tests; full domain model per architecture §4 still to add)
Date/time: 2026-10-09
Files: backend/app/database.py (SCHEMA_VERSION=2, migrate(), source_revisions + backfill), backend/tests/test_migrations.py.
Implementation summary: versioned idempotent migration; fresh DB reaches v2; repeat migration retains rows; legacy scans backfilled as kind=legacy (never promoted to verified).
Tests: `pytest backend/tests/test_migrations.py` — 2 passed (T01.08 fresh+repeat; T01.07 partial — copy-of-existing-DB upgrade not yet exercised).
Limitations: T01.09–T01.12 (concurrency/idempotency constraints, interrupted-write, FK/selection constraints) and remaining target tables (validation parent, selection history, chain sessions) still open.
Next: P01.03.

Section: P01.03
Status: implemented-unverified
Date/time: 2026-10-09
Files: backend/app/main.py (degraded readiness + GET /api/capabilities), backend/app/routes/scans.py (export uses observed versions, expected kept separately).
Implementation summary: /api/health returns degraded+ready=false when tools missing (was unconditional healthy); export tool_versions are observed, expected versions retained under raw_diagnostics.
Tests: existing health test passes (tools present → healthy); T01.13–T01.18 matrix (missing-tool degraded, origin/host, stale-capability bypass, secret leak) not yet run.
Limitations: origin/host validation and typed-error centralization unchanged.
Next: P02.01.

Section: P02.01
Status: implemented-unverified
Date/time: 2026-10-09
Files: backend/app/jobs.py (Semaphore(1) active slot, MAX_QUEUED_JOBS=4 with 429 overload, executor-side curated policy, exception-to-terminal-state + slot release).
Implementation summary: unbounded thread-per-scan replaced with bounded queue + single active slot; QueueOverloadError→429 and CuratedPolicyError→503 wired in scans route.
Tests: full backend suite green (no thread-growth measurement yet); T02.01–T02.07 injection tests (hang/tree-kill, huge output, stale report, restart recovery, direct-service bypass) partly covered (direct-service bypass now refused by executor check — new behavior, dedicated test still to add).
Limitations: stress/termination measurements not run this session.
Next: P02.02.

Section: P02.02
Status: blocked
Date/time: 2026-10-09
Scope and prerequisite evidence: Docker 29.8.2 present; `docker images` shows no fusion-worker image.
Files: backend/app/worker.py (self-check + gate), backend/tests/test_worker_gate.py (2 passed).
Implementation summary: pinned image name, inspect-based self-check with 60s cache, per-submission recheck path. Image itself not built — isolation requirements (non-root, read-only root, no net, limits, preinstalled tools, import confinement) unproven.
Tests: T02.08–T02.13 not-run (no image). T02.16 spoofed-flag test passes (flag alone cannot enable arbitrary execution).
Unblock condition: build/pin fusion-worker:0.1.0 with the R07/R08 launch profile and run the adversarial matrix.
Safe fallback: curated-only operation enforced server-side in both route and executor.
Next: P02.03 recorded as blocked-dependent.

Section: P02.03
Status: blocked (depends on P02.02 image)
Date/time: 2026-10-09
Files: backend/app/worker.py (arbitrary_scan_allowed), route wiring in scans.py.
Implementation summary: arbitrary mode allowed only for curated bytes or flag+passing self-check, rechecked per submission; cleanup/retention docs still to write.
Tests: T02.14–T02.18 not-run (no verified worker); fail-closed behavior verified by test_worker_gate.
Unblock condition: same as P02.02.
Next eligible independent section: P03.01 (needs P01 + bounded curated worker — available).

Section: P03.01
Status: verified
Date/time: 2026-10-09 (local session)
Scope and prerequisite evidence: P01 integrity + P02.01 bounded curated worker (prior session). Files: backend/app/analysis/runner.py, normalize.py (unchanged), tests.
Implementation summary: real Slither adapter already validated JSON/exit policy; added stale-report deletion before each attempt (fresh report per run). Durations are actual runs; combined compile/analyze reported without fake progress.
Test IDs and exact commands/browser steps: `PYTHONPATH=backend python -m pytest backend/tests/test_analyzer_adapter.py` — 3 passed (stale success never read; Unicode multiline ranges; unknown detector guidance). T03.01 matrix via test_api real scans (full suite).
Expected/Observed: real JSON retained with observed tool versions + exact source hash.
Outcome: pass.
Next: P03.02.

Section: P03.02
Status: implemented-unverified (code complete, browser run still required)
Date/time: 2026-10-09
Files: frontend/src/components/UploadPanel.tsx (submitting ref guard), frontend/src/App.tsx (poll seq-guard, error+retry banner, hash persistence/restore). `tsc --noEmit` clean.
Implementation summary: duplicate-click prevention ahead of parent state; stale poll responses ignored after scan change; polling failure shows retry banner instead of endless spinner; active scan id persisted in URL hash and restored on reload; disabled upload modes carry title reasons; native file input is keyboard-usable.
Tests: T03.06–T03.12 need browser verification (no browser tooling in this environment).
Next: P03.03.

Section: P03.03
Status: verified
Date/time: 2026-10-09
Files: backend/app/routes/scans.py (GET /api/scans limit/offset stable ordering; GET /api/scans/{id}/source hash-verified byte download), backend/tests/test_scan_export_history.py.
Implementation summary: versioned JSON export (observed tools + expected versions separated); independent original-source download with X-Source-Sha256; stable pagination (created_at, id tiebreak).
Test IDs: `PYTHONPATH=backend python -m pytest backend/tests/test_scan_export_history.py` — 2 passed (export hash agreement; pagination no-dup). Coverage-wording page work belongs to P09.
Outcome: pass.
Next: P04.01.

Section: P04.01
Status: implemented-unverified (tokens/components in code; contrast/capture measurement still required)
Date/time: 2026-10-09 (local session)
Files: frontend/src/styles.css.
Implementation summary: removed runtime Google-Fonts dependency (system stack; font bundling recorded as documented exception — no licensed font asset available); added design.md §4 tokens (--page-bg … --focus); solid orange CTA (was gradient); 3–5px radii (were 6–16px); :focus-visible ring; prefers-reduced-motion kill; sidebar/split-CTA/table/board/menu/chip/skeleton/empty/KPI styles; skip link. Misleading --accent-blue/--accent-cyan aliases retained only as aliases to the orange primary (full rename deferred — existing components still reference them).
Tests: T04.01–T04.06 not-run (need composited-contrast measurement + browser captures). `tsc --noEmit` clean, `vite build` succeeds.
Limitations: contrast ratios unmeasured; touch-hit expansion not added; font choice uncalibrated against references.
Next: P04.02.

Section: P04.02
Status: implemented-unverified (shell + routes in code; visual match unconfirmed without browser)
Date/time: 2026-10-09
Files: frontend/src/App.tsx (rewritten), pages/Dashboard.tsx, pages/States.tsx.
Implementation summary: six sidebar destinations in order + Help & Docs + local-workspace label (no fake login); split New scan/+ CTA → #/scans/new; slim breadcrumb/action row; pale left rail on active item; warm top wash; hash routes for all design.md destinations + #/scans/new + #/patch + unknown-route recovery page; reload restores latest scan selection; scan state lifted to App so page switches preserve acceptance/selection; old four-tab shell removed.
Tests: T04.07–T04.12 need browser (back/forward, drawer focus trap, reload). tsc clean, vite build ok, preview serves (byte check only).
Limitations: drawer toggle button hidden on desktop widths via inline style (opens only if shown) — mobile opening path needs a visible trigger; back-from-detail scroll restoration not implemented.
Next: P04.03.

Section: P04.03
Status: implemented-unverified (CSS only, no screenshots)
Date/time: 2026-10-09
Files: frontend/src/styles.css (1024/768 breakpoints, drawer nav, single-column KPI, bounded table/board scroll regions).
Implementation summary: 1024px reduced gutters; 768px drawer + stacked KPI; tables/boards scroll inside labeled regions with no outer overflow.
Tests: T04.13–T04.16 not-run (no 1440/1280/1024/768/375 captures, no 200% zoom check).
Next: P05.01.

Section: P05.01
Status: implemented-unverified (code + live smoke, no browser)
Date/time: 2026-10-09
Files: frontend/src/pages/Findings.tsx (table + detail), backend source/detail already served.
Implementation summary: R3 dense table (uppercase micro headers, striped rows, severity square+label, confidence column instead of CVSS, reviewer/date local metadata); row opens detail with immutable source, orange range tint, explanation, recommendation, patch action; new scan clears selection; keyboard-operable rows; source markup rendered as text (React default escaping).
Tests: T05.01–T05.06 need browser; live HTTP smoke 2026-10-09: created scan_267be3bd4559 → complete with reentrancy-eth, source download hash matched header + fixture hash 66ae62ae….
Outcome: backend-verified, UI unverified.
Next: P05.02.

Section: P05.02
Status: implemented-unverified (API tested, UI needs browser)
Date/time: 2026-10-09
Files: backend/app/database.py (SCHEMA_VERSION=3, finding_reviews), backend/app/routes/reviews.py, backend/tests/test_reviews.py, Findings.tsx board.
Implementation summary: five R4 columns with live counts; cards with id/severity/asset/date + keyboard status menu (no drag); edits persist with versioned 409 conflicts; resolved requires reason; detector output never mutated.
Tests: `pytest backend/tests/test_reviews.py` — 2 passed (persist+stale-conflict; resolve-requires-reason). T05.07–T05.12 UI half needs browser. Live smoke: PUT review → triaged persisted.
Limitations: board resolve via menu without reason surfaces 400 (honest but abrupt); reviewer/date editing UI minimal (reason field only — reviewer/date stay empty until P09 local metadata editing).
Next: P05.03.

Section: P05.03
Status: implemented-unverified (code, no browser)
Date/time: 2026-10-09
Files: Findings.tsx (filter menu/submenu, chips, clear-all, view persistence).
Implementation summary: filter trigger + field menu + value submenu; severity/status/detector filters over actual fields; chips + clear-all; view/selection persistence; distinct no-history / no-match / completed-zero / loading / error states; globe slot intentionally left empty (P10 static fallback still to add — currently blank space, not a fake globe).
Tests: T05.13 keyboard arrows not implemented (Tab/Enter/Escape + outside-click + focus-return done); T05.14–T05.18 need browser.
Next eligible: P06.01 (needs P01–P03, P05 — P05 UI verification still open; backend ready).

| Phase | Sections | Initial status |
|---|---|---|
| P00 | P00.01 verified, P00.02 verified, P00.03 implemented-unverified | evidence entries 9 Oct 2026 above |
| P01 | P01.01 verified (partial matrix), P01.02 implemented-unverified, P01.03 implemented-unverified | see evidence entries |
| P02 | P02.01 implemented-unverified, P02.02 blocked (no worker image), P02.03 blocked (depends P02.02) | curated-only fallback enforced |
| P03 | P03.01 verified, P03.02 implemented-unverified (needs browser), P03.03 verified | see evidence entries |
| P04 | P04.01 implemented-unverified, P04.02 implemented-unverified, P04.03 implemented-unverified (no browser captures) | see evidence entries |
| P05 | P05.01 implemented-unverified, P05.02 implemented-unverified, P05.03 implemented-unverified (no browser run) | see evidence entries |
| P06 | P06.01 implemented-unverified, P06.02 implemented-unverified, P06.03 implemented-unverified (backend gates pass; prereq exception + no browser) | see evidence entries |

Section: P06.01
Status: implemented-unverified (backend gates pass; prereq exception above + no browser)
Date/time: 2026-10-09 (local session)
Files: backend/app/patches/service.py (TEMPLATE_ID/VERSION, candidate-hash==protected-hash gate, CEI+rename explanation), backend/app/database.py (v4: template cols, validation_parents, patch_selections, selection_events), backend/tests/test_patch_validation.py.
Implementation summary: exact-hash proposal kept; tampered candidate template on disk refused; explanation covers CEI + contract rename + template version; identical re-proposal returns same revision.
Tests: `pytest backend/tests/test_patch_validation.py` — 3 passed (T06.01 exact+provenance; T06.02 protected refused; T06.04 idempotent re-proposal; T06.05 diff/original binding; T06.03 disk-tamper refused; T06.06/T06.16 stored-byte tamper refuses validate+accept).
Outcome: pass. Next: P06.02 (done below).

Section: P06.02
Status: implemented-unverified (same prereq exception; no browser)
Date/time: 2026-10-09
Files: backend/app/patches/validation.py (parent row, harness hash, compile-gated skips, fuzz check, eligible flag), backend/app/config.py (REQUIRED_VALIDATION_CHECKS=5, FUZZ_SEED=20261009, FUZZ_RUNS=256), contracts/test/Vault.t.sol (full-domain fuzz via modulo, zero-deposit revert, reverting-receiver test).
Implementation summary: parent run binds candidate/original/harness/tool/seed; compile failure skips runtime checks honestly; fuzz runs 256 seeded runs over the full (0,5 ether] domain with conservation asserts; rescan preserves unrelated findings; harness change invalidates comparability via validation-status.
Tests: `forge test --root contracts` — 6 passed; test_patch_validation full-validate asserts 5 checks all passed + fuzz detail names 256 runs; validation-status eligible True + harness_matches True (live-smoked on :8002).
Outcome: pass. Next: P06.03 (done below).

Section: P06.03
Status: implemented-unverified (same prereq exception; no browser)
Date/time: 2026-10-09
Files: backend/app/routes/patches.py (validation-status endpoint, export with parents/selection history, acknowledged accept), frontend PatchReview.tsx (rewritten), client.ts/types.
Implementation summary: selection transactional (one revision + history, idempotent repeats); hashes rechecked before selection; explicit unvalidated acknowledgment recorded and never enables replay; export carries selection + validation independently; UI shows template hash/version, fuzz seed, eligibility badge, disables replay unless eligible; "Validation results" wording (certificate removed); diff region labeled; reload restores via idempotent propose + server selection.
Tests: backend flow asserts in test_patch_validation (idempotent accept/revoke, export agreement, selection history); `tsc` clean, `vite build` ok. T06.15/T06.19 browser halves not-run.
Outcome: backend pass, UI unverified. Next: P07.01.

Section: P07.01
Status: implemented-unverified (backend gates pass live + mocked; no browser)
Date/time: 2026-10-09
Files: backend/app/monitoring/observer.py (pid:start-time marker, exe+start+listener ownership, serialized reset, reconciled persistence), scripts/start.ps1 (new marker format), scripts/reset.ps1 (direct-RPC fallback removed — backend-only reset), backend/tests/test_anvil_ownership.py, test_demo.py (ownership-aware).
Implementation summary: ownership requires recorded pid + start time + same executable + 8545 listener owned by that pid; reset serialized against runs, failed reset changes nothing and reports failure; persistence failure after reset blocks silently continuing.
Tests: 5 mocked tests pass (foreign listener/stale-PID/wrong-exe/invalid-marker refused; lock-held reset refused; fee helper; artifact tamper refused). test_demo.py documents :8545 refusal on this machine (user-owned anvil PID 7056 + stale marker — left untouched per R14).
Outcome: pass. Next: P07.02.

Section: P07.02
Status: implemented-unverified (live evidence on owned :8546 session; prereq exception)
Date/time: 2026-10-09
Files: observer.py (fee_wei on all 11 receipts), schemas.py (fee_wei optional), test_anvil_ownership.py live test.
Implementation summary: demo runs only on verified owned session; artifacts rebuilt after protected-source hash check; equivalent 5 ETH victim deposits both vaults; all receipts persisted with real hashes; fees recorded (reverted txs included); wei as decimal strings; traces explicitly unavailable.
Tests: live owned Anvil on 127.0.0.1:8546 (user :8545 untouched; marker saved/restored; only self-started process terminated): vuln after=0, protected after==before, normal-user accounting zeroed, blocked exploit reverted, attacker delta ≈ +5 ETH minus fees, 11 real tx hashes. `pytest -k live_owned` — 1 passed.
Outcome: pass. Next: P07.03.

Section: P07.03
Status: implemented-unverified (code + tsc/build, no browser)
Date/time: 2026-10-09
Files: frontend/src/pages/Incident.tsx, App.tsx (incident route + nav highlight), States.tsx (run list links), styles.css (incident-grid responsive).
Implementation summary: R5 metadata band, 5 tabs with real content (detections=alert, notes=local-only, logs=receipts+fees, respond=guidance without auto-pause claims), info card, SVG polar (wei magnitudes) + radar (6 observed 0/1 scenario dimensions) each with data tables, entities with copy + historical marker, JSON export, local review-state control. Unsupported CVSS/IP replaced by balance/receipt evidence (documented substitution).
Tests: T07.13–T07.18 need browser. tsc clean, vite build ok.
Outcome: UI unverified. Next: P08.01.

Section: P08.01
Status: implemented-unverified (endpoint tested + live-smoked; UI half needs browser)
Date/time: 2026-10-09
Files: backend/app/routes/dashboard.py, main.py wiring, backend/tests/test_dashboard.py.
Implementation summary: open findings (missing review defaults open; resolved/canceled excluded) with scope; non-historical incidents; required 5/5 denominator kept (unrun included); duration = sum of latest parent check durations or unavailable; activity = scans+validations+selections+incidents capped 25 with routable refs; no trends/sparklines invented.
Tests: test_dashboard — 1 passed. Live smoke on :8002: 172 findings, 5/5 checks, 4.8s duration, 25 mixed activity events.
Outcome: pass. Next: P08.02 (done below).

Section: P08.02
Status: implemented-unverified (code, no browser/R1 overlay comparison)
Date/time: 2026-10-09
Files: frontend/src/pages/Dashboard.tsx (rewritten).
Implementation summary: KPI strip with scopes; map slot = labeled contract/call topology SVG (explicit no-geography note); severity bars from last-20 scans with table equivalent; neutral unavailable states; no world map/hotspots/sample counters in live mode.
Tests: T08.06–T08.10 need browser. Next: P08.03 (done below).

Section: P08.03
Status: implemented-unverified (code, no browser)
Date/time: 2026-10-09
Files: Dashboard.tsx (metric click-through to findings/incidents/patch, sort + window controls, single batched read, reserved min-heights), client.ts (fetchDashboard).
Implementation summary: metrics link to filtered work; activity sort/window without reload; one aggregate + one bounded scan page read (scan window cut 50→20 for payload bound); error shows message, never zeroed history.
Tests: T08.11–T08.14 need browser (incl. large-dataset responsiveness).
Outcome: UI unverified. Next eligible: P09.01 (needs P01, P04, P06 — backend ready, UI verification open).
| P06 | P06.01 implemented-unverified, P06.02 implemented-unverified, P06.03 implemented-unverified (backend gates pass; prereq exception + no browser) | see evidence entries |
| P07 | P07.01 implemented-unverified, P07.02 implemented-unverified (live owned-session evidence), P07.03 implemented-unverified (no browser) | see evidence entries |
| P08 | P08.01 implemented-unverified, P08.02 implemented-unverified, P08.03 implemented-unverified (endpoint live-smoked; no browser) | see evidence entries |
| P09 | P09.01, P09.02, P09.03 | not-started |
| P10 | P10.01, P10.02, P10.03 | not-started |
| P11 | P11.01, P11.02, P11.03 | not-started |

Expand each row into per-section status when work begins. A phase is verified only when all its required sections pass. Do not reset an evidence-backed verified section without a reason; mark evidence stale if related code changes.

## Evidence entry template

```text
Section:
Status:
Date/time:
Scope and prerequisite evidence:
Files/revision or hash manifest:
Implementation summary:
Test IDs and exact commands/browser steps:
Expected:
Observed:
Outcome per test (pass/fail/blocked/not-run):
Input/candidate/harness/tool identity:
Artifacts:
Known limitations and failed cases:
Next eligible section/action:
```

## Blocker and resumption template

Record the capability/tool/permission that failed, exact error evidence, attempted safe alternatives, dependent features kept disabled, independent work that can continue, and what would unblock it. Never infer permission from time passing. Before a handoff also record service ports/process ownership and whether evidence is live or historical.

## Documentation verification record

Checked on 9 October 2026 using a Python validation script passed through PowerShell standard input. Exit status: 0; no validation errors. This is documentation evidence only.

| Check | Observed result |
|---|---|
| First-party Markdown inventory | 21 files; all updated or created for this revision |
| Purpose comments | Present in all 21 files |
| Local Markdown links | All referenced local files exist |
| Fenced blocks | Balanced |
| Phase structure | 12 phases, P00 through P11 |
| Section identifiers | 36 unique IDs; referenced section IDs resolve |
| Test-case identifiers | 202 unique IDs; no duplicates |
| Reference assets | Six PNG copies match original attachments by SHA-256 |
| Solidity fixture hashes | All three raw-byte hashes match the provenance register |
| Scope review | Current prototype distinguished from planned UI, worker and hardening work |

Application source was not modified for this documentation task. No backend, Foundry, browser E2E or frontend build result is newly claimed. The implementation section register intentionally remains unverified. The complete reusable prompt is at ../prompt.md.

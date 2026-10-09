<!-- Purpose: Define the full implementation sequence, section deliverables, tests, evidence, and completion gates. -->
# Fusion implementation phases

## How to execute this plan

Read [agent.md](agent.md) first. This plan replaces the old clock-based five-phase hackathon checklist. The current request expands the interface and hardens the existing prototype; this document does not claim those features are already built. Baseline and current evidence belong in [progress.md](progress.md).

Work **section by section**, not one giant rewrite and not one prompt per phase. Each section has a stable ID. Finish implementation, relevant tests, evidence, and documentation before marking it verified. Continue to the next eligible section without requesting routine approval. Existing code can satisfy a requirement after verification; do not rebuild it merely because it appears later here.

Status vocabulary: `not-started | in-progress | implemented-unverified | verified | blocked | deferred`. Deferred is allowed only for the explicit future-scope list or a user-approved scope change. A blocked required feature remains incomplete. Test outcomes independently use `pass | fail | not-run | blocked`.

For every test below retain: test ID, setup/input hash, relevant code revision or file hash manifest, expected result, observed result, date, command/browser steps, artifact location, tool versions, and limitations. A section gate is the conjunction of its tests, not whichever test was easiest.

## Dependency map and milestones

| Phase | Purpose | Prerequisites | Observable milestone |
|---|---|---|---|
| P00 | Establish actual baseline and test harness | Read project docs | Reproducible evidence and scoped backlog |
| P01 | Integrity, persistence, and API contracts | P00 | Trustworthy bytes and recoverable state |
| P02 | Bounded workers and arbitrary-upload isolation | P01 | Verified execution boundary |
| P03 | Complete scan workflow | P01, bounded curated worker from P02.01 | Real scanner E2E; arbitrary mode also requires P02.02–03 |
| P04 | Reference shell and design foundation | P00; P01 contracts for live states | Sidebar/navigation and tokens match references |
| P05 | Findings table, board, source, filters | P03, P04 | Persistent review workflow |
| P06 | Patch review and exact-revision validation | P01–03, P05 | Traceable candidate selection and checks |
| P07 | Managed local replay and incident detail | P06 | Actual receipts and balance evidence |
| P08 | Evidence dashboard and charts | P05, P07 | Live dashboard without invented metrics |
| P09 | Check coverage, artifacts, local integrations | P01, P04, P06; P02 for worker capability | Every sidebar destination useful |
| P10 | 3D scenes, presentation, visual matching | P04–05, P08–09 | All six reference compositions covered |
| P11 | Full regression, offline rehearsal, handoff | All required sections | Tested local release with explicit scope |

P04 can progress while isolation tooling is externally blocked. P03 can verify curated mode without claiming arbitrary upload complete. No final “full implementation complete” claim is allowed while required P02 upload isolation is blocked; deliver a labeled curated-only milestone with the remaining work listed.

## P00 — Baseline, contracts, and reproducibility

### P00.01 — Inventory and honest status
**Work:** Inspect repository status, all first-party modules, routes, test files, manifests, lockfiles, artifacts, and reference assets. Separate existing implementation from verified behavior and planned features. Preserve user edits. Record actual runtime versions, compiler compatibility, local port owners, and Docker capability results. Do not equate permission denial with missing software.

**Files:** progress.md, component READMEs, configuration inventory; no broad refactor.

**Tests:** T00.01 compare fixture byte hashes to the provenance register; T00.02 enumerate actual routes and frontend commands; T00.03 check all six reference images open and match the supplied assets; T00.04 each baseline completion claim has evidence or an unverified label.

**Exit/evidence:** version inventory, fixture manifest, current feature matrix, and actionable first section. Existing historical nine-backend/four-contract results are not fresh test results.

### P00.02 — Baseline execution
**Work:** Use isolated test data; run existing backend tests, Foundry tests, and frontend typecheck/build. Exercise vulnerable, protected, and malformed scans through the browser. Record failures before changing them. Save original source/report hashes.

**Tests:** T00.05 actual Slither target appears on vulnerable input; T00.06 target is absent on the protected comparison while unrelated findings remain; T00.07 malformed input fails visibly; T00.08 record Foundry assertions and whether fuzz iterations perform useful work; T00.09 refresh/navigation behavior is observed, not inferred from compilation.

**Exit:** baseline report with commands, outputs, browser observations, and known defects. Environment-blocked checks remain blocked. Do not mark a broken baseline green merely to advance.

### P00.03 — Test and evidence scaffolding
**Work:** Add separate fast, integration, browser, and visual test entry points where missing. Configure temporary DB/artifact roots, deterministic sample records, stable clock/IDs for visual fixtures, and real-tool test markers. Pin compatible browser/test dependencies and document installation separately from runtime.

**Tests:** T00.10 tests cannot reset ordinary user/demo data; T00.11 injected tool failure is surfaced; T00.12 one intentional failing test yields a nonzero command result; T00.13 snapshots cannot use live random transaction IDs as a deterministic baseline.

**Exit:** documented commands with meaningful failure propagation. No claim that adding a test runner covers the product.

## P01 — Source integrity, persistence, and capabilities

### P01.01 — Byte-preserving storage
**Work:** Move authoritative sources to immutable byte artifacts; store metadata separately. Hash uploaded bytes before display decoding. Use bounded multipart reads; require exactly one input method. Server-generate storage names and enforce resolved path/reparse containment. Treat fixture selection as loading verified bytes, not trusted text. Export the same bytes.

**Files:** storage.py, routes/scans.py, schemas.py, config.py, fixture registry, tests.

**Tests:** T01.01 LF, CRLF, BOM policy, and multi-byte source round-trip with the original SHA-256; T01.02 changed fixture/template bytes are rejected; T01.03 limit−1/limit/limit+1 bytes and oversized streaming bodies; T01.04 empty, invalid UTF-8, duplicate input methods, extension mismatch; T01.05 sibling-prefix path, traversal, absolute filename, symlink/reparse escape; T01.06 original artifacts cannot be overwritten through a second request.

**Exit:** stored, executed, displayed-source reference, and exported hashes correlate. Display normalization never changes the execution artifact.

### P01.02 — Durable domain models and migrations
**Work:** Introduce explicit source revisions, validation parent runs/check rows, acceptance history, finding review state, artifact metadata, and chain sessions as specified in architecture. Migrate existing SQLite data without deleting it. Legacy validation records lacking provenance remain legacy/unverified. Wrap related mutations in transactions; add uniqueness/idempotency constraints.

**Tests:** T01.07 migration from a copy of the existing DB retains scans/patches/demo history; T01.08 fresh DB and repeated migration both succeed; T01.09 concurrent proposal/accept/revoke cannot create contradictory active revisions; T01.10 interrupted write leaves a consistent state; T01.11 old validation is never promoted into complete current evidence; T01.12 foreign-key and per-scan selection constraints hold.

**Exit:** migration version, backup/restore procedure, and regression evidence. Test connections close on every error path.

### P01.03 — Truthful capabilities and transport
**Work:** Separate API liveness from readiness. Expose observed/expected tool versions, worker mode/reason, available compiler/import profiles, patch support, managed chain status, and capability check timestamp. Validate origins/hosts and mutation requests. Centralize typed errors and frontend response parsing. Bound capability probe time and cache results for a short documented interval.

**Tests:** T01.13 missing/mismatched tools produce degraded readiness; T01.14 unavailable Docker cannot enable upload; T01.15 unexpected Origin/Host mutation is refused while the intended local UI works; T01.16 no secrets/absolute host paths leak to UI diagnostics; T01.17 stale capability UI cannot bypass server policy; T01.18 expected versions are not exported as observed versions.

**Exit:** UI can explain which feature is unavailable and why; health is not unconditionally healthy.

## P02 — Worker lifecycle and isolated uploads

### P02.01 — Bounded curated execution
**Work:** Replace unlimited job threads with a bounded queue and one active execution slot. Use fresh job/run directories, safe environments, argument arrays, bounded continuous log capture, report limits, process-tree termination, and exception-to-terminal-state handling. Enforce curated hash policy inside the execution service as well as at the API boundary. Recover interrupted jobs after restart.

**Tests:** T02.01 flood beyond queue capacity gets explicit overload without thread growth; T02.02 child that hangs/spawns a child is fully terminated; T02.03 huge stdout/stderr/report terminates or truncates within stated disk/memory bounds; T02.04 missing executable/permission/parse/unexpected exception reaches a terminal state; T02.05 stale report from a failed earlier attempt is never read; T02.06 restart marks interrupted work accurately; T02.07 direct service calls cannot bypass curated policy.

**Exit:** bounded real curated scans and failure-injection evidence. Partial logs remain available with a truncated marker.

### P02.02 — Container worker and compiler/import policy
**Work:** Build/pin the worker image, non-root user, read-only root filesystem, no network, capability restrictions, process/memory/CPU limits, bounded writable job output, no host home/socket/secrets. Preinstall approved tools and dependencies. Add an installed-compiler matrix; never download compilers from an upload. Resolve imports within explicit approved roots using parser/compiler evidence plus filesystem confinement; line-based regex alone is insufficient.

**Tests:** T02.08 worker cannot read a host sentinel outside mounts or connect to network; T02.09 CPU/memory/PID/disk stress hits limits without harming API responsiveness; T02.10 absolute/remote/multiline/comment-disguised imports and symlink escapes fail; T02.11 uploaded Foundry config/FFI/build scripts cannot run; T02.12 allowed local import and supported compiler succeed without network; T02.13 compiler mismatch yields unsupported rather than an arbitrary upgrade.

**Exit:** retain launch settings and adversarial-test evidence. If Docker is unavailable, mark blocked and keep curated-only operation. Do not lower isolation requirements to unlock the file picker.

### P02.03 — Capability activation and recovery
**Work:** Enable arbitrary mode only after the worker self-check and pinned image validation pass. Recheck worker availability per submission and fail closed if it disappears. Document limits, supported single-file format, imports, compiler profiles, and cleanup retention.

**Tests:** T02.14 a non-allowlisted benign contract runs through the verified worker; T02.15 stop worker between health check and submission, assert safe refusal; T02.16 spoofing a flag cannot enable native arbitrary execution; T02.17 job input/output mounts cannot affect another job; T02.18 cleanup preserves retained evidence and only removes verified disposable paths.

**Exit:** arbitrary upload is actually available end to end or explicitly blocked. This is mandatory for the expanded upload release.

## P03 — Scanner journey and reports

### P03.01 — Real analyzer adapter
**Work:** Run compile/analyze stages with truthful timestamps; if Slither performs combined compilation, report that without fake progress percentages. Pin and document its exit policy. Validate complete JSON structure, success, detector schema, and path references. Normalize detector, impact, confidence, Unicode-safe ranges, concise explanation, guidance, and raw evidence linkage.

**Tests:** T03.01 real vulnerable/protected/malformed matrix; T03.02 success:false, null/missing detectors, malformed JSON, incompatible exit status, stale output, empty output; T03.03 multi-line and Unicode location highlighting; T03.04 preserve unrelated informational findings and unknown detector guidance; T03.05 no partial parsing is presented as complete.

**Exit:** real JSON retained with observed tool versions and exact source hash.

### P03.02 — New scan UI and resilient polling
**Work:** Implement split New scan/+ entry points, fixture/file/paste modes, size/encoding help, submitted source preview, async duplicate-click prevention, queued/running/terminal state, retry, and navigation to result. Controls use backend capabilities. Cancel stale requests when scan/route changes; prevent out-of-order response overwrites. Preserve active scan in the route and reload it.

**Tests:** T03.06 fixture and verified arbitrary file/paste paths; T03.07 two rapid clicks create one intended job; T03.08 offline API, polling error, retry, and reconnect show useful state without spinner forever; T03.09 switch scans during a delayed response; T03.10 reload pending/completed/error scan; T03.11 keyboard-only upload mode and status announcement; T03.12 disabled upload gives a visible reason.

**Exit:** user can obtain and recover a scan without developer-console intervention.

### P03.03 — Export, history, and coverage wording
**Work:** Download versioned JSON with run ID, status, byte hash, observed tools, findings, diagnostics, limits, and timestamps. Offer original source export independently. Add stable paginated history. Mark legacy/missing evidence and recorded fixture reports. Coverage notes for unchecked/old-compiler/access/oracle areas distinguish available detector evidence from manual-review suggestions.

**Tests:** T03.13 download parses and hash matches original; T03.14 error report remains error with diagnostics; T03.15 versions are observed values; T03.16 pagination has no duplicate/missing rows under documented ordering; T03.17 completed zero findings, filtered empty, no scans, and error have different messages.

**Exit:** scanner E2E report is reproducible and usable outside the app.

## P04 — Reference design foundation and navigation

### P04.01 — Tokens, fonts, icons, and primitives
**Work:** Implement design.md tokens; inspect locally available/licensed font options and bundle the chosen font with its license. Match screenshot stroke weight, compact radii, density, orange buttons, warm top wash, and dark surfaces. Build button, badge, field, tooltip, dropdown, tab, dialog, table, card, skeleton, and empty/error primitives with state contracts.

**Tests:** T04.01 text/control contrast on actual composited backgrounds; T04.02 keyboard focus/disabled/busy states; T04.03 icon labels and consistent SVG strokes; T04.04 offline fonts load and fallback does not break layout; T04.05 no residual blue/cyan theme or old gradient CTA substitutes; T04.06 touch hit areas are adequate without inflating desktop visual geometry.

**Exit:** deterministic component gallery/captures with tokens and all interactive states.

### P04.02 — Sidebar shell and durable routes
**Work:** Implement the six reference sidebar destinations in order, bottom help/local-profile area, split CTA, slim breadcrumb/action row, active pale left rail, and warm angular sidebar top. Replace old primary top tabs. Keep patch/source flow accessible as findings detail routes. Implement direct navigation, back/forward, reload, invalid route, and selected scan/run restoration.

**Tests:** T04.07 each nav item routes correctly and highlights one active item; T04.08 deep links survive refresh; T04.09 back from detail restores list filters/scroll; T04.10 mobile drawer traps focus, closes on Escape, returns focus; T04.11 missing record shows not-found with a recovery action; T04.12 switching pages preserves stored acceptance.

**Exit:** shell structure visually matches the references and all destinations have honest live/empty states.

### P04.03 — Responsive composition
**Work:** Build 1440/1280/1024 desktop layouts, 768 tablet, and 375 mobile. Keep content readable at 200% zoom. Tables and boards may scroll inside labeled regions; the page must not overflow. Hide decorative device packaging at narrow widths. Preserve dense desktop typography while using readable mobile body text.

**Tests:** T04.13 screenshots at the specified widths; T04.14 long hashes, filenames, errors, and translated-length labels do not escape cells; T04.15 browser zoom and keyboard scroll regions; T04.16 popovers reposition within viewport.

**Exit:** responsive screenshots and documented intentional mobile rearrangements.

## P05 — Findings review system

### P05.01 — Dense table and source detail
**Work:** Match reference 03: heading, breadcrumb, filter chips, view toggle/export, fine uppercase headers, alternating low-contrast rows, small severity squares, compact metadata. Use actual detector/asset/confidence/review data. Preserve geometry where replacing unsupported CVSS with confidence. Open finding detail with immutable source, highlighted range, explanation, raw evidence, and supported patch action.

**Tests:** T05.01 correct source/file/range for each row; T05.02 sort/filter operate on actual fields and stable IDs; T05.03 missing severity/confidence remains unknown; T05.04 source snippets containing markup render as text; T05.05 selecting a new scan clears stale detail; T05.06 table headers/row actions are keyboard and screen-reader usable.

**Exit:** every displayed finding can be traced to its original scan and bytes.

### P05.02 — Persistent board workflow
**Work:** Match reference 04 five columns and compact cards. Add review states Open/Triaged/In progress/Resolved/Canceled, counts, optional local owner/date metadata, and thumbnails only when real evidence exists. Persist edits with conflict handling. Provide a keyboard status menu even if drag/drop is added. Resolved requires a review reason/evidence link and never deletes the original scanner finding.

**Tests:** T05.07 table/board show identical filtered IDs/counts; T05.08 move/reload/reopen persists state; T05.09 failed mutation rolls back with retry; T05.10 keyboard move and optional drag produce same state; T05.11 concurrent stale edits give a conflict instead of silent overwrite; T05.12 “Resolved” never claims universal security.

**Exit:** functional board, not static reference cards.

### P05.03 — Nested filters and distinct empty states
**Work:** Match reference 06 filter trigger, first menu, right-hand submenu, selected chips, clear controls, and view persistence. Implement only supported fields; unavailable reference fields explain their status. Provide distinct no-history, no-match, completed-zero, loading, and error states. Reserve the globe slot for P10; use a designed static fallback meanwhile.

**Tests:** T05.13 nested menu keyboard arrows/Escape/outside click/focus return; T05.14 filter intersection and clear-all restore original set; T05.15 URL/view restoration; T05.16 no-match message never appears while loading/failed; T05.17 popover over canvas remains clickable; T05.18 default/advanced controls have defined filter-density behavior.

**Exit:** reference empty composition works for a real empty filtered result.

## P06 — Patch generation, validation, and selection

### P06.01 — Exact template proposal and diff
**Work:** Verify original and candidate template bytes, version, supported contract identity, and preconditions. Reuse an existing identical proposal idempotently. Store immutable candidate and real diff; explain CEI and contract-name changes. Unsupported sources remain guidance-only.

**Tests:** T06.01 exact fixture succeeds; T06.02 one-byte variant/name-only/detector-only match is refused; T06.03 tampered candidate template is refused; T06.04 repeated/concurrent proposal creates consistent revision; T06.05 diff reconstructs candidate and preserves original.

**Exit:** reviewable hash-bound proposal, no generic code rewrite.

### P06.02 — Validation parent run and behavior harness
**Work:** Materialize exact candidate bytes in fresh workspace with approved harness/config hashes. Run compile, real rescan, original exploit, candidate exploit resistance, normal behavior, and meaningful bounded fuzz checks. Persist each independent outcome and parent aggregation. Skip dependent tests honestly after compile failure. Record tool versions, arguments, seeds, durations, and bounded logs.

**Tests:** T06.06 candidate bytes/hash mismatch stops before execution; T06.07 modification after a pass cannot reuse that pass; T06.08 original excess proceeds and candidate preservation assertions; T06.09 normal/zero/double/over-withdrawal and reverting receiver; T06.10 bounded fuzz executes its intended domain including edges, records seed; T06.11 failed/skipped/timeout check prevents all-pass aggregation; T06.12 unrelated Slither warnings remain; T06.13 harness/tool changes invalidate comparability.

**Exit:** actual evidence addresses both protection and usability; four unrelated old check rows cannot impersonate one completed run.

### P06.03 — Accept, revoke, export, and navigation
**Work:** Separate selected revision from validation outcome. Present diff/check summary, normal accept/revoke, and explicit acknowledgment for unvalidated selection. Recheck hashes before selection/download. Persist history. Export source plus manifest/check report with honest status; retain logs and prior candidates. Restore state on navigation/reload.

**Tests:** T06.14 repeated accept/revoke is idempotent; T06.15 reload preserves selection; T06.16 stale/tampered bytes are refused; T06.17 selecting failed/unrun candidate never enables validated-demo action; T06.18 export bytes/manifest/check-run identity agree; T06.19 parallel requests cannot select two revisions.

**Exit:** user controls a revision without confusing selection, checks, and deployment.

## P07 — Managed local replay and incident detail

### P07.01 — Anvil ownership, sessions, and safe reset
**Work:** Manage process identity with executable/start time/listener/session verification. Serialize demo and reset operations. Validate loopback RPC and disposable-account context. Reject unrelated occupied ports and stale/PID-reused markers. Record chain session and invalidate deployments/history on confirmed reset. Remove direct unchecked reset fallbacks.

**Tests:** T07.01 unrelated service on 8545 is not reset; T07.02 wrong chain, stale PID, reused PID, wrong executable, and unowned listener are refused; T07.03 concurrent reset/run cannot interleave; T07.04 failed reset does not falsely mark success; T07.05 successful reset marks old evidence historical and forces redeploy; T07.06 shutdown affects only owned processes.

**Exit:** management evidence verifies more than chain ID or process-name presence.

### P07.02 — Hash-bound deployments and real transactions
**Work:** Deploy artifacts compiled from the selected validated fixture revision and recorded harness/tool settings. Give both scenarios equivalent initial balances/inputs. Persist all intended/observed transaction steps and receipt statuses; stop on unexpected evidence. Capture fees and integer-safe balances. Retrieve traces if supported, otherwise state unavailable.

**Tests:** T07.07 original vault loses victim funds and attacker excess proceeds are shown; T07.08 candidate preserves victim balance and normal withdrawal succeeds; T07.09 wrong artifact/candidate hash refuses replay; T07.10 failed receipt/timeout does not fabricate hash/gas; T07.11 values beyond JavaScript safe integers remain exact; T07.12 caught-subcall/top-level-revert semantics and missing traces display honestly.

**Exit:** real Anvil evidence, separated from Foundry test output and recorded samples.

### P07.03 — Incident page and evidence charts
**Work:** Match reference 05 metadata band, tabs, information card, polar/radar slots, entities table, export action, severity/status controls. Tabs expose actual detections, local notes, receipt/trace logs, and review response guidance. Replace unsupported security-domain scores with defined scenario/check dimensions or clearly labeled sample display. No decorative chart asserts unmeasured risk.

**Tests:** T07.13 each tab works with real run data; T07.14 evidence links open correct receipt/artifact; T07.15 observations and hypotheses are distinct; T07.16 no events claimed from reverted execution; T07.17 chart legend/table values match underlying data; T07.18 historical run clearly identified after reset.

**Exit:** incident detail matches reference composition and explains the actual local scenario.

## P08 — Dashboard and evidence visualization

### P08.01 — Aggregation and activity
**Work:** Define four metrics: open review findings, recorded local incidents, required checks passed/required checks, and measured validation duration. Include scope/time window/denominator. Unknown duration/trend is unavailable. Aggregate immutable events into recent activity; avoid counting resolved findings as erased scan history. Provide filters and links.

**Tests:** T08.01 aggregates match a controlled DB dataset; T08.02 empty/partial history yields correct unavailable states; T08.03 time-window boundaries/timezones/duplicate events; T08.04 required-check denominator includes skipped/unrun checks; T08.05 activity links route to records, missing records recover gracefully.

**Exit:** every dashboard value is traceable to stored evidence.

### P08.02 — Reference map, bars, and metric visuals
**Work:** Match reference 01 card strip, left map composition/hotspot glow, lower horizontal bars, right activity rows. Live mode uses a labeled contract/call topology in the map slot unless actual geographical data exists. Reference showcase retains the literal world map, sample hotspot positions, counters, and labels under an explicit sample marker. Metric arcs/sparklines require real series; otherwise show neutral unavailable graphics.

**Tests:** T08.06 visual geometry compared with reference 01; T08.07 live/sample data cannot mix in aggregates or exports; T08.08 chart tooltip and table are equivalent; T08.09 no locale/geography is inferred from an Ethereum address; T08.10 partial data cannot generate an invented trend.

**Exit:** faithful dashboard structure with honest functional semantics and a labeled literal showcase.

### P08.03 — Dashboard interaction and performance
**Work:** Link metrics to filtered findings/checks/incidents, allow activity sort/window selection, and update after completed scans/reviews. Batch API reads and avoid polling every chart independently. Reserve chart dimensions to prevent layout jumps.

**Tests:** T08.11 click-through filters match displayed counts; T08.12 new scan/review appears without full page reload; T08.13 API failure shows stale timestamp/error rather than zeroing history; T08.14 large fixture dataset stays responsive and has bounded payloads.

**Exit:** dashboard is an entry to work, not a disconnected visual page.

## P09 — Coverage, evidence vault, and integrations

### P09.01 — Check-coverage table
**Work:** Match reference 02 title/actions, percentage band, table, expandable row, upload well, square heatmap, and floating concern preview. Label the page Compliance / Check coverage with an explicit local-check scope. Define required check IDs, outcome, description, evidence, local reviewer, and last-run/next-review metadata. Evidence attachments are bounded inert text/JSON/images/PDF downloads, never executed source; no active HTML rendering. Preserve “not run” and “unsupported” in the denominator.

**Tests:** T09.01 coverage formula matches all required checks; T09.02 selected profile changes denominator explicitly; T09.03 expand/upload/preview/review actions persist; T09.04 dangerous attachment content is not executed; T09.05 heatmap has documented axes and table equivalent; T09.06 no ISO certification claim in live mode.

**Exit:** functional evidence checklist with the exact reference layout language.

### P09.02 — Source and evidence vault
**Work:** Build searchable artifact inventory by scan/revision/run/type/date, immutable source previews, manifest/hash details, parent links, and downloads. Distinguish original/candidate/recorded/sample/historical files. Bound file retrieval and sanitize download names. No wallet/private-key storage. Keep deletion outside the default workflow; if added, require scoped review and reference checks.

**Tests:** T09.07 search/filter results and parent relationships; T09.08 download hash/size/type match manifest; T09.09 path traversal and cross-root reads fail; T09.10 missing/corrupt artifact shows integrity error; T09.11 untrusted markup remains inert; T09.12 archived chain evidence remains readable.

**Exit:** users can locate and verify the evidence behind every displayed result.

### P09.03 — Local integrations and help
**Work:** Show Slither, solc, Foundry, Anvil, worker isolation, and API capability cards with observed/expected versions, status, last check, and remediation. Refresh is read-only; do not install software or execute arbitrary commands from the UI. Add local Help & Docs with scanning walkthrough, limitations, status semantics, and troubleshooting. Local profile is a workspace label, not a fake login.

**Tests:** T09.13 capability cards reflect backend failures and mismatches; T09.14 refresh cannot enable a failed worker; T09.15 unavailable tools link to useful instructions; T09.16 help works offline; T09.17 no credential request or fabricated integration appears.

**Exit:** all sidebar destinations and footer actions work with defined local behavior.

## P10 — 3D, presentation, and visual fidelity

### P10.01 — Orange globe and wireframe objects
**Work:** Implement lazy-loaded 3D triangulated globe matching reference 06, orange line network, sparse nodes, broken/dissolving upper cap, dark center, and restrained depth. Create exterior white geodesic spheres and warped grid/saddle objects for reference 01/06 strips. Use deterministic geometry/seed and a fixed capture pose. Include a locally bundled static/SVG fallback.

**Tests:** T10.01 reference silhouette, mesh density, color, position, and scale match annotated captures; T10.02 WebGL disabled/context lost still shows usable empty state; T10.03 reduced motion freezes decorative animation; T10.04 hidden tab/route stops frame loop and disposes GPU resources; T10.05 popovers and buttons remain above/nonblocked by canvas; T10.06 repeated mount/unmount does not accumulate canvases/listeners.

**Exit:** real reconstructed 3D objects, not an emoji, stock icon, or screenshot pasted over the application.

### P10.02 — Device frame and reference showcase
**Work:** Add optional presentation wrapper with black bezel, metallic rim, rounded screen mask, browser-chrome strip, warm exterior backdrop, controlled perspective presets, and repeating wireframe/logotype strip. Keep ordinary workbench flat and readable. Reference showcase uses deterministic labeled sample content and all six compositions; never submits fake backend records. Preserve reference brand text only within labeled reference presentation; default product identity is Fusion.

**Tests:** T10.07 straight/angled presets align to corresponding references; T10.08 showcase actions cannot create live evidence; T10.09 pointer/focus geometry remains usable under presentation transforms; T10.10 small screens drop wrapper without dropping content; T10.11 browser-like chrome cannot be mistaken for actual connection/security status.

**Exit:** all reference packaging is represented, with normal app workflow still practical.

### P10.03 — Visual comparison and accessibility pass
**Work:** Capture each page/state at a fixed viewport/DPR/font-ready state. Compare flat app crops independently from angled presentation. Overlay references and annotate deviations in shell bounds, sidebar width, baseline alignment, rows, radii, colors, charts, filters, and 3D silhouette. Fix major differences before accepting screenshots. Record inferred font/assets and intentional accessible-text/semantic differences.

**Tests:** T10.12 six-state reference checklist plus hover/focus/loading/error states; T10.13 375/768/1024/1440 and 200% zoom; T10.14 no serious/critical automated accessibility findings plus manual keyboard/screen-reader smoke; T10.15 local performance budgets in design.md measured on stated hardware; T10.16 reference UI cannot be replaced by screenshots as the functioning interface.

**Exit:** visual report with actual/baseline/diff images, approved documented exceptions, performance measurements, and manual inspection.

## P11 — Integration, reliability, and handoff

### P11.01 — Complete browser journeys
**Work:** Run real API/UI/tool journeys with isolated data: vulnerable scan -> finding -> patch -> validate -> select -> export -> revoke; protected comparison; malformed source; verified arbitrary upload; local replay -> incident -> export -> reset -> historical view; findings review -> coverage -> vault -> integrations. Keep real-tool and mocked failure tests separately identified.

**Tests:** T11.01 every journey asserts user-visible outcome and artifact hashes; T11.02 double-click, refresh, back/forward, API interruption, worker timeout, failed validation; T11.03 no stale selected finding/candidate/run leaks between records; T11.04 all enabled controls work; T11.05 live run never falls back silently to saved evidence; T11.06 current UI text contains no unsupported certificate/audit/safety claims.

**Exit:** complete E2E evidence, not just HTTP 200 or screenshot success.

### P11.02 — Safe scripts and offline rehearsal
**Work:** Harden setup/start/verify/reset scripts for exit codes, paths with spaces, idempotent startup, readiness waits, hidden background processes, owned-process cleanup, and accurate summaries. Separate dependency installation from offline start. Use approved backend reset only. Prepare a labeled recorded backup with source/tool metadata.

**Tests:** T11.07 fresh prepared checkout starts with no network; T11.08 second startup does not duplicate services; T11.09 missing tool/failed build causes nonzero setup/verification result; T11.10 occupied unrelated port is not killed/reset; T11.11 reset retains historical DB/artifacts; T11.12 two rehearsals reproduce the scenario without editing source; T11.13 script summary reports only checks it actually ran.

**Exit:** exact local commands, recoverable failures, and rehearsal evidence.

### P11.03 — Release inventory and continuation
**Work:** Update all first-party READMEs, progress, decisions, provenance, design differences, and manual walkthrough. Verify links and reference hashes. Produce implemented/verified/blocked/deferred matrix and point to evidence for every completed phase. Document known residual limitations and next actions.

**Tests:** T11.14 no contradictory completed claims or stale scaffold statements; T11.15 Markdown links and phase/test IDs resolve; T11.16 reports contain observed versions and hashes; T11.17 no secrets/runtime uploads unintentionally staged; T11.18 each required section has evidence or remains visibly incomplete.

**Exit:** a new developer can run, test, understand scope, and resume from the single root prompt.

## Explicitly deferred future projects

These are not hidden missing prototype features: multi-file/ZIP/repository imports beyond approved profiles; generalized patch synthesis; developer-authored runtime invariants on arbitrary contracts; oracle/economic protections; public/testnet monitoring; pending-transaction simulation; automated pause; governance/timelocks; proxy upgrades/migration; custody; hosting/auth/billing; production operational security and formal verification. Each needs a separate threat model, authority decision, data model, failure policy, and acceptance tests before entering implementation.

The earlier proposal to insert every kind of guard automatically is not revived by “full implementation.” Full implementation means the bounded product and reference UI above.

## Human team coordination

If four humans are available, ownership can be backend/worker, contracts/evidence, UI/design, and integration/testing. Agree schemas and section ownership before simultaneous edits. This is not an instruction to spawn autonomous agents. Shared files have one active editor, and integration gates remain mandatory regardless of contributor count.

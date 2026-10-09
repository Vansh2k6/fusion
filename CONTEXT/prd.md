<!-- Purpose: Define the expanded local product, user journeys, acceptance criteria, truth constraints, and exclusions. -->
# Fusion product requirements

## 1. Product and audience

Fusion is a local Solidity security workbench for developers reviewing contracts before deployment. It combines real Slither findings, source inspection, a narrowly supported reviewed patch, executable validation, and a controlled original-versus-candidate attack comparison.

Proposed value: move from warning to reviewable change and reproducible evidence in one workflow. This is a positioning hypothesis, not a verified market-uniqueness claim. The product reduces uncertainty about specified checks; it does not certify safety or guarantee reduced losses on arbitrary contracts.

The expanded interface follows all six user references: dashboard, findings table/board/empty state, incident detail, check coverage, evidence vault, local integrations, full left navigation, 3D objects, and presentation framing. See [design.md](design.md). Current implementation and verification are recorded separately in [progress.md](progress.md).

## 2. Users and constraints

Primary user: Solidity developer inspecting a local source file. Secondary user: hackathon reviewer following a reproducible demonstration. Local reviewer/assignee metadata does not require accounts or multi-tenant auth.

Four contributors were available for the original hackathon. Local execution only, no hosting or real funds. Existing Slither/Foundry tooling must be reused. Runtime remains usable offline after dependencies are prepared. Source is not sent to an external model/service.

The original 14:00 IST review on 9 October 2026 is historical. The full phase plan is the current target; no elapsed cutoff silently removes requirements.

## 3. Core journeys

### J1 — Scan and understand
Open New scan, choose approved fixture or permitted upload/paste, inspect the submitted source, start analysis, follow real status, and inspect detector/severity/confidence/location/guidance. Choose a finding to see its immutable source range. Export the original and a hash/tool-bound report.

If isolation is unavailable, arbitrary modes show why and server refuses them. Curated scanning remains available. Malformed source produces compilation error; unsupported compiler/import produces unsupported status. Zero findings appears only after completed analysis and carries scoped wording.

### J2 — Review findings
Use table or board, filter actual records, inspect source, change local review state with a reason, and restore the same view on reload. Resolved means a recorded review decision, not deletion of a detector finding. No-match, no-history, loading, error, and completed-zero states remain distinct.

### J3 — Review a supported patch
For the exact supported vault, propose a candidate, inspect the actual diff, run validation, inspect each check, and select or revoke the candidate. Original bytes never change. Unsupported contracts receive guidance without a fabricated patch.

The ordinary flow validates before selection. Explicitly acknowledged unvalidated selection remains possible but cannot claim passing checks or enable a validated replay. Exports disclose selection and validation independently.

### J4 — Replay the controlled scenario
With an eligible validated fixture, deploy exact original/candidate artifacts on the managed local Anvil session. Reproduce original excess withdrawal, test candidate behavior and normal use, inspect actual receipts/balances, and open incident detail. Reset only the owned local session; keep previous evidence as historical.

### J5 — Navigate evidence
Dashboard numbers link to filtered underlying records. Compliance shows defined required-check coverage. Vault lists immutable source/reports/receipts/attachments. Integrations reports actual local capabilities. Help explains these workflows offline.

### J6 — Present the reference UI
Toggle optional device presentation and deterministic reference showcase. Inspect all six reconstructed compositions, including 3D globe/exterior objects. Sample data remains visibly isolated from live evidence. Normal workflow continues to use the same complete visual system.

## 4. Functional requirements and acceptance

| ID | Requirement | Observable acceptance | Phase |
|---|---|---|---|
| FR01 | Source ingestion | Exactly one bounded input, unchanged bytes/hash, verified fixture loading | P01/P03 |
| FR02 | Worker safety | Curated gate or verified isolated arbitrary worker; fail closed when unavailable | P02 |
| FR03 | Real scanning | Vulnerable target appears, comparison lacks target, malformed input errors | P03 |
| FR04 | Findings | Detector, impact, confidence, source range, explanation and evidence retained | P03/P05 |
| FR05 | Scan recovery | Reload/retry and interrupted worker yield truthful state without duplicate job | P02/P03 |
| FR06 | Exports | Actual bytes, hash, status, observed versions and scope survive download | P03/P06 |
| FR07 | Finding review | Table/board/filter share IDs; review changes persist with history | P05 |
| FR08 | Patch support | Exact original/template matching and actual immutable diff | P06 |
| FR09 | Validation | Candidate-bound compile/rescan/exploit/normal/fuzz outcomes with reproducible provenance | P06 |
| FR10 | Selection | Idempotent accept/revoke, reload persistence, no false validation promotion | P06 |
| FR11 | Local replay | Managed session, exact artifacts, real receipts and balance outcomes | P07 |
| FR12 | Incident inspection | Tabs, observations, hypotheses, actual entities, trace availability and export | P07 |
| FR13 | Dashboard | Defined aggregates/time windows; activity links to real events | P08 |
| FR14 | Check coverage | Required denominator includes unrun/skipped; evidence table works | P09 |
| FR15 | Artifact vault | Safe searchable inventory, correct hash-bound downloads | P09 |
| FR16 | Integrations/help | Actual capabilities, useful availability explanations, offline instructions | P09 |
| FR17 | Reference fidelity | All six compositions, sidebar, fonts reconstruction, 3D and device stage | P04/P10 |
| FR18 | Reliable release | Full browser journeys, failure tests, offline startup/rehearsal and accurate docs | P11 |

## 5. Interface behavior

Sidebar order and appearance are fixed by design.md. Every enabled action performs a defined function. Unsupported reference fields can be disabled with explanations or exist within the labeled showcase; do not create inert clickable placeholders.

Live finding severity comes from scanner impact; confidence remains separate. Live CVSS is unavailable unless independently supplied with a documented method. Owner/date values are actual optional local metadata. Unknown timestamps and metrics display unavailable, not invented defaults.

The Compliance label is retained for reference navigation, with “Check coverage” scope visible in the page title/subtitle. No ISO certification claim. Vault is an evidence library, not a wallet. Integrations is a local tool-status page, not a credential collection screen.

Error states preserve diagnostic context and offer appropriate recovery. Empty result wording distinguishes filters from analyzer coverage. No “audited,” “certificate,” “safe,” or “fully protected” badges.

## 6. Nonfunctional requirements

- Integrity: source/candidate/harness/report hashes correlate; stale evidence cannot validate new bytes.
- Security boundary: arbitrary inputs isolated and bounded; local mutations protected; owned Anvil only.
- Reliability: bounded jobs/logs, interruption recovery, idempotency, transactional selection, honest partial outcomes.
- Usability: keyboard-accessible navigation, focus management, readable contrast, responsive 375–1440 layouts and 200% zoom.
- Performance: nonblocking tool jobs, lazy decorative 3D, measured budgets from design.md, bounded payload/history.
- Privacy: no source transmission, telemetry or remote-font requirement in default operation.
- Reproducibility: dependency locks, observed versions, fixture provenance, deterministic test settings and recorded seeds.
- Maintainability: explicit module responsibilities, typed interfaces, migration tests, one canonical document per topic.

## 7. Metrics with definitions

Measure fixture-specific target detection, not a general “security accuracy” percentage. Record actual scan and validation duration. Count open review findings within explicit filters, local incidents in a stated session/window, and passed required checks divided by all required checks in a chosen profile. Unrun/unsupported checks are not silently removed from the denominator.

A successful demo includes a real vulnerable scan, correct comparison/error handling, exact supported patch evidence, ordinary-use preservation, and real local receipt/balance correlation. Visual success additionally requires all reference states and accessibility/interaction checks. Do not equate one of these with the other.

## 8. Exclusions and future scope

Excluded: custom analyzer, arbitrary automatic guards/patches, formal verification claims, universal inferred invariants, generalized economic/oracle protection, public mempool simulation, production monitoring/auto-pause, escrow rollback, custody, mainnet/testnet deployment, proxy upgrades, hosting/auth/billing and remote AI analysis. Multi-file/ZIP/repository import is beyond the single-file/approved-import release.

Original proposed defenses remain research ideas requiring context-specific threat models. Per-address caps can be bypassed through many addresses; timelocks delay actions rather than undoing them; a clean scan cannot establish intended business logic.

## 9. Product completion

Full completion requires every required phase section verified with current evidence. A curated-only release can be a useful milestone but must list arbitrary upload as blocked until isolation passes. A reference showcase is visual evidence, not a substitute for live workflow tests. Use [progress.md](progress.md) as the implemented/verified/blocked/deferred register and [phases.md](phases.md) for test IDs.

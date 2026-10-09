<!-- Purpose: Record accepted product, technical, safety, and visual decisions with their rationale and historical limits. -->
# Fusion decision register

## How to use this register

These decisions supplement [agent.md](agent.md). Record material changes with date, rationale, affected sections, and evidence; do not silently rewrite scope. Accepted design decisions are not implementation completion claims. Current status lives in [progress.md](progress.md).

## D01 — Positioning and audience
Accepted: local pre-deployment Solidity review for developers. Proposed USP: “See the vulnerability, review the fix, and replay the attack against both versions.” Existing analysis becomes more useful when linked to a reviewable candidate and reproducible behavior. Market uniqueness remains an unverified hypothesis.

## D02 — Bounded scope
Accepted: real scanning for supported Solidity/compiler/import profiles; one educational vault/attacker family for patching and replay. Arbitrary uploads require verified isolation. Supported and unsupported operations must be visible.

Excluded from this delivery: public chain, custody, rollback escrow, public mempool simulation, generalized economic/oracle defenses, automatic pause, proxy upgrades, production governance, auth/billing/hosting. A request for complete implementation expands the defined workflow/UI, not every research idea from the original proposal.

## D03 — Stack and deployment model
Accepted: React/TypeScript/Vite, FastAPI/Python, SQLite, local files, Slither/solc, Foundry/Anvil. One bounded worker with polling. This superseded the provisional Next.js/PostgreSQL idea; local use needs neither SSR nor another DB service.

Extend the existing stack with route persistence, compatible test tooling, and lazy pinned Three.js for requested 3D. Use existing Lucide and CSS tokens. No runtime CDN/font/API dependency. Docker is the planned arbitrary-input boundary; WSL can host tools but is not by itself that boundary.

## D04 — Patch authority and acceptance
Accepted: exact-hash reviewed CEI template, real diff, immutable candidate, explicit preconditions. No regex guard insertion across arbitrary contracts. Selecting a candidate and validating it are independent facts. Revocation restores local source selection and retains history; it cannot revoke blockchain transactions.

Default UX validates before accepting. Explicit acknowledgment may select without passing checks, with status retained and validated replay disabled. This resolves the former design-guide implication that acceptance automatically represented successful validation.

## D05 — Evidence rather than proof
Accepted: record exact source/candidate/harness hashes, observed tools, check outcomes, logs, seeds, receipts and limitations. “Generate guards and prove them” becomes “propose changes and test them.” Require original exploit plus legitimate-use tests; a candidate that rejects all withdrawals is not successful.

## D06 — Audit hardening history, 9 October 2026
Earlier audit work restricted native analysis to curated hashes, required successful Slither JSON, added fresh candidate validation workspaces, and removed fabricated demo evidence fallbacks. Historical runs reported nine backend tests, four Foundry tests including a 256-run fuzz case, frontend build, a browser workflow and local Anvil evidence.

These are historical results, not a claim that the expanded architecture or all security controls are implemented. Current source still needs the P01/P02/P06/P07 hardening gates. In particular, run-level provenance, bounded capture, exact byte handling, meaningful fuzz-domain execution and process ownership need verification or fixes.

## D07 — Full reference UI supersedes the four-tab design
Accepted from the latest user request: reproduce all six supplied UI compositions. The sidebar is mandatory; so are table/board/filter states, dashboard, incident charts, coverage table, 3D globe, exterior meshes, and optional device stage. The earlier optional-sidebar/no-3D interpretation is superseded.

Use the screenshots as visual authority. Generic skill-generated blue/Fira/landing-page defaults are not adopted. Existing warm palette changes are only a starting point.

## D08 — Preserve appearance without inventing evidence
Accepted: default Fusion workbench with real records; optional device presentation; isolated labeled reference showcase for literal CY · FOCUS/sample map/ISO/CVSS/owner content. Live semantics map unsupported reference metrics to defined fields: confidence instead of inferred CVSS, local check coverage instead of certification, contract topology instead of fabricated geographic threats.

All modes use the complete visual design. Showcase cannot write fake records or drive live transactions. Reference screenshots are retained as user-supplied design inputs; no unsupported ownership/license assertion is made.

## D09 — Fonts and 3D reconstruction
Accepted: original font/model files are unavailable. Compare bundled font candidates visually, retain licenses, and reconstruct mesh/device geometry from references. Values in design.md are provisional calibrated targets, not recovered source values. Do not repeatedly block on missing assets or claim exact identity. Preserve readable contrast, keyboard access, reduced motion and static fallback.

## D10 — Section-driven autonomous implementation
Accepted: one reusable root prompt, stable phase/section/test IDs, persistent progress ledger, continue from the earliest unmet prerequisite. No separate prompt or approval for every phase. Mark blocked required work incomplete and continue independent eligible sections. Do not rewrite working code solely to match a preferred scaffold.

The original 14:00 IST hackathon deadline is historical; current work follows dependencies. Four human contributors do not alone authorize autonomous subagents.

## D11 — Domain integrity and source of truth
Accepted: immutable byte revisions, explicit validation parent/check model, independent selection history, durable review states, artifact inventory, and managed chain sessions. Expected pins and observed versions are distinct. Legacy data lacking evidence remains legacy, not upgraded into a passing result by migration.

## D12 — Release completeness
Accepted: real tool/API/browser tests plus reference visual/accessibility/performance checks. A successful build or old “ALL PHASES PASSED” script banner is insufficient. Full expanded release includes isolated arbitrary uploads; a curated-only milestone may be delivered honestly while isolation remains blocked.

## Technical corrections retained from the original proposal

1. Per-address limits are bypassable via multiple addresses; they do not alone establish total damage bounds.
2. Old compiler, unchecked blocks, and oracle use are review signals, not automatically exploitable findings. Slither cannot establish all authorization or economic intent.
3. Compiler upgrades alter semantics; SafeMath and sum-of-balances rules are contextual. On-chain mappings are not automatically enumerable.
4. Timelocks delay supported actions, not all admin power. TWAP/deviation caps are not universal oracle fixes and may reject legitimate market changes.
5. Function-exit checks are not universal transaction-wide invariants. A caller can catch a subcall revert; top-level reverted execution still pays fees.
6. Logs from reverted execution are discarded. Diagnose with actual receipt/revert/trace evidence.
7. Monitoring cannot undo an executed transfer. Pause is a separate authorized action and may race further harm.
8. A proxy cannot simply be added to an already deployed non-upgradeable contract to change it. Migration or an existing authorized upgrade path is required.
9. An anomaly is not a proven exploit; root-cause suggestions remain hypotheses absent evidence.
10. Avoid unsupported rankings of historical exploit losses; they are unnecessary to the product.

## Source pointers and provenance of research

Earlier planning recorded these primary sources on 9 October 2026; this documentation update does not claim fresh verification of each source:
- [Slither](https://github.com/crytic/slither)
- [Foundry invariant testing](https://getfoundry.sh/forge/invariant-testing)
- [Solidity control structures](https://docs.soliditylang.org/en/latest/control-structures.html)
- [OpenZeppelin utilities](https://docs.openzeppelin.com/contracts/5.x/api/utils)
- [OpenZeppelin access controls](https://docs.openzeppelin.com/contracts/5.x/access-control)

Accessibility guidance checked during this update is linked in [design.md](design.md). Any later external package/API choice must be verified against its actual installed version.

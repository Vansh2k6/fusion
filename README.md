<!-- Purpose: Orient users to the current local prototype, full implementation plan, setup, manual scan checks, and documentation. -->
# Fusion

A local Solidity security workbench: run Slither, inspect findings, review one supported patch, and compare attack/defense evidence on local Anvil.

## Start here

For an LLM implementation session, copy the single block in [prompt.md](prompt.md). It directs the model through [36 implementation sections](CONTEXT/phases.md), runs each section's tests, updates [progress](CONTEXT/progress.md), and continues automatically.

[CONTEXT/agent.md](CONTEXT/agent.md) is the authoritative project guide. The full [design specification](CONTEXT/design.md) covers all six preserved [UI references](CONTEXT/references/README.md), including sidebar, tables/board, filters, charts, 3D objects and device presentation.

## Current implementation versus expanded target

Existing source contains a curated Slither flow, source-linked findings, one CEI candidate, validation/accept/revoke/export, and a controlled Foundry/Anvil scenario. The current frontend remains a four-tab interface with a warm palette. Arbitrary-source execution is blocked pending verified isolation.

The expanded documentation is an implementation contract, not a claim that the new dashboard/sidebar/3D screens already exist. Historical test results and remaining integrity, worker, lifecycle and UI work are recorded in [progress.md](CONTEXT/progress.md). No fresh application test run is claimed by this documentation update.

## Local setup and run

Prerequisites: the compatible Node/Python/solc/Slither/Foundry tools described in [provenance](fixtures/provenance.md), with Foundry executables available under the configured path. Docker is needed for the planned arbitrary-input worker, not for approved native fixture scans. Prepare dependencies before the offline demonstration.

From the repository root in PowerShell:
```powershell
powershell -ExecutionPolicy Bypass -File scripts\setup.ps1
powershell -ExecutionPolicy Bypass -File scripts\start.ps1
```

Open http://127.0.0.1:5173. API is on http://127.0.0.1:8000; local Anvil uses 127.0.0.1:8545. Existing scripts still need the hardening described in [scripts/README.md](scripts/README.md), particularly exit handling, duplicate startup and reset ownership. Inspect actual errors rather than relying on a success banner.

For separate manual startup, see [backend](backend/README.md) and [frontend](frontend/README.md). Do not deploy the vulnerable contracts to a public chain.

## Check a scan manually in the current UI

1. Select VulnerableVault.sol under Ingestion & Scan.
2. Click Analyze with Slither and wait for a terminal state.
3. Open Static Findings & Source. Expect reentrancy-eth with source mapping around the withdraw function, historically lines 18–28 for this exact fixture.
4. Export the JSON report and compare its source hash with [provenance](fixtures/provenance.md). Observe versions/diagnostics, including known export-metadata hardening still planned.
5. Run ProtectedVault.sol. The target reentrancy-eth finding must be absent; informational findings can remain.
6. Run MalformedVault.sol. It must show a compilation error, never a successful zero-findings result.
7. For the supported vulnerable fixture, inspect the patch diff, run validation, inspect each outcome, accept then revoke and verify source selection. Never infer a security guarantee from a green check.

Future sidebar navigation changes are defined in the plan; the labels above describe the current source. A failed/missing tool is a real unavailable capability, not a reason to substitute saved reports.

## Verification commands

```powershell
powershell -ExecutionPolicy Bypass -File scripts\verify_all.ps1
```

This currently runs contract tests, backend tests, and frontend build. Its old all-phases-passed banner overstates coverage; browser, visual, accessibility, isolation and complete phase gates still require separate evidence. Backend tests include local demo mutations; use isolated test configuration/owned disposable services. See [test guidance](backend/tests/README.md).

## Repository map

| Folder | Purpose |
|---|---|
| CONTEXT/ | Agent contract, rules, decisions, PRD, architecture, design, phases, progress and visual references |
| frontend/ | React interface, typed API client, source/diff/demo components |
| backend/app/ | FastAPI, SQLite, jobs, analyzer, patches and local observer |
| backend/tests/ | API, integration and regression checks |
| contracts/ | Educational vaults, attacker and controlled Foundry harness |
| fixtures/ | Approved sources, recorded reference reports and provenance |
| scripts/ | Setup/start/verify/reset helpers |
| data/ | Ignored local runtime sources, DB, reports and evidence |

Source remains local by default. A completed scan/test provides evidence for specified checks; it does not certify contract safety.

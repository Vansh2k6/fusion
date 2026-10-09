<!-- Purpose: Document existing test scope, execution side effects, and the required layered regression and E2E strategy. -->
# Backend and cross-system tests

## Existing suites

| File | Current scope |
|---|---|
| test_api.py | Health/fixtures, curated-mode gate, real vulnerable/protected/malformed scans; supported patch flow within scan scenario |
| test_regressions.py | Failed Slither JSON handling and candidate-hash mismatch |
| test_demo.py | Actual local demo API run and reset |

Source inspection finds nine test functions. Historical handoff reported nine passing; this documentation revision does not rerun them. These tests are not a complete implementation of the phase test matrix.

## Execution

From backend:
```powershell
python -m pytest tests -v
```

Tests require native tools and loopback/socketpair support for applicable integrations. A blocked socket/process operation is an environment failure, not passing evidence. Use an isolated DB/artifact root and app-owned disposable Anvil session; current test configuration needs P00.03 improvements before assuming ordinary data is protected. The demo test mutates/resets chain state.

## Target layers

1. Pure tests: normalization, Unicode range mapping, integer formatting helpers, hash/path policy and aggregate formulas.
2. API/storage tests: bounded ingestion, schema/status/error behavior, migrations, concurrency/idempotency, selection history, downloads and capability enforcement.
3. Execution-adapter tests: controlled missing tool, exit/JSON mismatch, stale files, timeout/tree termination, output limits, interruption/restart.
4. Real integration: actual Slither fixture matrix, Foundry original/candidate/normal/fuzz checks, verified arbitrary worker and Anvil receipts.
5. Browser E2E: real user journeys, polling/reload/retry, filters/board, exports, selection/revocation, incident reset history.
6. Visual/accessibility: deterministic showcase captures, responsive/focus states, globe fallback and manual comparisons.

Separate fake adapters from real-tool tests using explicit markers/configuration. Never replay fixture JSON as a live scan. Tests assert content and hashes/outcomes, not just HTTP success.

## Essential regressions

LF/CRLF/Unicode preservation; streamed size bounds; traversal and reparse escape; fixture/template tampering; incompatible versions; noncurated direct-executor bypass; malformed/success:false/stale Slither report; unbounded output; job exception/restart; candidate/harness change after validation; concurrent accept/revoke; wrong Anvil port owner; reset race/failure; missing receipt/trace; large wei precision; vacuous fuzz inputs; stale frontend responses; sample/live separation.

Every detailed test ID and expected outcome is in [phases.md](../../CONTEXT/phases.md). Add tests where they own behavior rather than creating a giant all-purpose test file.

## Evidence and pass criteria

Record exact commands, tool versions, seeds, input/candidate/harness hashes, test-root configuration, exit status and artifact paths. Preserve failing logs. Mark not-run/blocked distinctly. Test counts alone do not establish coverage; a successful frontend build is not E2E evidence.

The full release requires the real browser journeys and isolation/visual gates, not the old verification script's broad completion banner.

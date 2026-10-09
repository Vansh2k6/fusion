<!-- Purpose: Explain helper scripts, current shortcomings, safe lifecycle requirements, and verification of script behavior. -->
# Local setup, startup, verification and reset

Run helpers from the repository root in PowerShell after reading their current behavior. They are convenience scripts, not proof that every phase is complete.

| Script | Current behavior | Required hardening |
|---|---|---|
| setup.ps1 | Probes tools, builds contracts, installs backend requirements and frontend lockfile | Check every native exit, validate compatibility, clear failure summary, paths with spaces |
| start.ps1 | Starts hidden Anvil/API helpers and foreground Vite | Owned-process/port verification, readiness waits, duplicate-start prevention and cleanup |
| verify_all.ps1 | Foundry tests, backend pytest, frontend build | Accurate per-suite summary; additional E2E/visual/isolation gates explicitly separate |
| reset.ps1 | Calls backend reset; falls back to direct Anvil RPC | Remove unchecked fallback; retain historical evidence and verify managed ownership |

## Commands

```powershell
powershell -ExecutionPolicy Bypass -File scripts\setup.ps1
powershell -ExecutionPolicy Bypass -File scripts\start.ps1
powershell -ExecutionPolicy Bypass -File scripts\verify_all.ps1
```

Setup may download/install dependencies and must finish before an offline demo. Startup must not install dependencies. Existing setup's success text is not enough: inspect failed native commands until P11 hardening is complete.

## Reset guidance

Do not use reset.ps1's direct fallback against an unverified occupied RPC port. The supported reset path is the backend's managed-session operation after ownership checks. Reset affects the disposable chain, not source/validation history. Confirmed reset marks previous run evidence historical; failed reset cannot report success. Ownership enforcement itself remains a P07 verification requirement.

## Target lifecycle contract

Resolve paths natively in PowerShell. Start background helpers with hidden windows. Record PID, start identity, executable and session; verify listening-port owner before reuse. A second start should reuse only verified owned services or report a conflict, never kill an unrelated process. Wait for readiness with bounded timeouts.

Return nonzero on any required failed command. Restore caller directory using structured cleanup. Never combine destructive path operations across shells. Recursive cleanup verifies final absolute paths and touches only disposable task-owned artifacts.

## Script tests

P11 requires missing-tool/build-failure tests, paths with spaces, duplicate startup, unrelated occupied ports, stop/restart, reset failure/history, two offline rehearsals and accurate completion summaries. The present “ALL VERIFICATION GATES PASSED (PHASES 0 - 4)” banner must not be used as evidence for the expanded twelve-phase plan.

<!-- Purpose: Explain API/runtime responsibilities, local startup, current limits, target hardening, and scanner verification. -->
# Backend

FastAPI/Python orchestrates Slither, supported Foundry validation, SQLite metadata, local artifacts and Anvil evidence. Direct Python dependencies are pinned in requirements.txt; native tool versions must be observed separately.

## Start locally

After installing the prepared requirements, run from backend:
```powershell
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

Interactive API docs are available at http://127.0.0.1:8000/docs. Existing health is /api/health; it currently reports healthy too broadly, so inspect toolchain fields and actual operations. Planned capability/readiness changes are P01.03.

## Ownership and interfaces

main.py wires lifespan/routes. config.py holds roots, policies and expected pins. database.py manages SQLite. storage.py owns artifacts/hashes. jobs.py schedules execution. analysis handles Slither execution and normalization. patches handles reviewed templates, validation and selection. monitoring/observer.py handles the controlled local scenario.

Routes under /api expose fixtures, scan history/status/export, proposal/validation/accept/revoke/export, and demo run/history/reset. The full observed inventory and target additions are in [architecture](../CONTEXT/architecture.md). New review/dashboard/artifact/capability models are planned, not already available.

## Current restrictions

Native scans accept exact allowlisted fixture hashes. Arbitrary-source execution is disabled until the verified isolated worker exists. Do not flip the configuration flag to bypass P02. Uploaded source staying local does not by itself isolate compiler/analyzer execution.

Single-file Solidity and approved compiler/import profiles are the intended format. No uploaded projects/config/scripts, FFI, remote dependencies or arbitrary commands. All source revisions must preserve exact bytes; hardening this throughout current text-oriented paths is part of P01.

## Scanner check

Use the frontend fixture flow or /api/scans multipart fixture_id. VulnerableVault must produce reentrancy-eth; ProtectedVault must omit that target while retaining other warnings; MalformedVault must terminate as a compilation failure. Inspect /api/scans/{id} and export. Compare byte hash with [provenance](../fixtures/provenance.md).

Reports must record observed versions. Current scans export code still uses configured PINNED_VERSIONS in the primary tool_versions field; P01/P03 must correct this rather than treating configured pins as execution evidence.

## Required hardening

Use bounded queue/process/output capture, terminal exception handling, immutable bytes, path-aware containment, strong worker policy, versioned migrations, explicit validation parent runs and managed chain ownership. Add negative cases for stale reports, changed templates/candidates, unexpected tool exits, unavailable worker, concurrent selection, and run/reset races.

Test roots should be injectable and isolated from ordinary data. Current tests can persist records and reset the local chain; do not point them at unrelated/user-managed RPC services. More guidance is in [tests/README.md](tests/README.md).

API errors should be stable, typed and useful without leaking host paths/secrets. Local binding must be supplemented by origin/host/mutation protections. Keep capability decisions server-side even when the frontend disables a control.

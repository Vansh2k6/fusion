<!-- Purpose: Explain approved Solidity fixtures, recorded reports, provenance, exact-hash policy, and fixture maintenance. -->
# Scanner and replay fixtures

Fixtures exist in this repository; the former “no vetted fixtures yet” statement is obsolete. Approval is narrow educational use under exact registered hashes, not a claim that a contract is safe.

| File | Purpose and expected outcome |
|---|---|
| VulnerableVault.sol | Real Slither scan should include reentrancy-eth; controlled original exploit |
| ProtectedVault.sol | CEI comparison should omit that target; informational warnings may remain |
| MalformedVault.sol | Deliberate syntax error; compilation fails, never a clean scan |
| vulnerable_vault_report.json | Recorded scanner output; not a substitute for a new live scan |
| protected_vault_report.json | Recorded comparison output with the same limitation |
| backup_demo_evidence.json | Recorded local-demo backup, never live receipt evidence |
| provenance.md | Origins, SPDX declarations, byte hashes, expectations and tool metadata |

## Exact-byte policy

The configured curated allowlist must match the bytes in [provenance](provenance.md). Reading a fixture through newline-normalizing text APIs can break byte identity; P01 requires exact byte storage throughout the pipeline. A filename or matching detector is not approval to execute changed source natively.

Until arbitrary isolation passes, only exact approved fixture hashes may execute. New public examples require source URL, immutable revision, license/redistribution review, modifications, expected outcome and deliberate approval. Do not automatically whitelist arbitrary uploaded bytes just to make a demo succeed.

## Maintenance process

1. Review purpose, license and expected behavior before adding/changing a fixture.
2. Preserve the old version where evidence depends on it; changed bytes mean a new revision.
3. Compute raw SHA-256 and update the approved registry intentionally.
4. Re-run real compiler/Slither behavior and applicable Foundry tests.
5. Bind any protected template, harness and replay artifacts to the new hashes.
6. Label recorded reports with original run/tool/input identity; never present them as freshly generated.

Source copies under contracts/src have separate build responsibilities. Verify agreement where required; do not assume matching filenames mean identical bytes. See [phases](../CONTEXT/phases.md) P00/P01/P03/P06 for tests.

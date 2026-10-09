<!-- Purpose: Register original educational fixture provenance, exact byte hashes, detector expectations, and historical tool versions. -->
# Fixture provenance register

## Provenance policy

These three Solidity fixtures are described by the project as original educational code and carry MIT SPDX declarations. Preserve their headers; retain/add the appropriate full license notice when packaging redistribution. No external public-source URL or upstream commit exists for this original material. Do not invent one.

Hashes below were checked against current file bytes during the documentation update on 9 October 2026. This confirms byte identity, not a fresh analyzer or behavioral test run. Detector expectations originate from earlier project runs and must be revalidated if source/tools change.

## Approved sources

### VulnerableVault.sol
- Origin: original Fusion educational vault.
- License declaration: SPDX MIT.
- SHA-256: `66ae62ae4832a0f60b34deeee7a207fb051659994de9ad7cdea52b41ee6fca96`.
- Purpose: illustrate external ETH call before clearing the caller balance.
- Expected target: reentrancy-eth, historically High impact / Medium confidence around lines 18–28; call around 23 and state write around 26.
- Historical additional findings: reentrancy-events, low-level-calls, solc-version.
- Approval scope: exact bytes for curated scanner and controlled local exploit demonstration. No production use or security endorsement.

### ProtectedVault.sol
- Origin: original Fusion educational CEI comparison.
- License declaration: SPDX MIT.
- SHA-256: `964f2e6bac7788c69b92adc041719aa49711aac3c9bd84b2817641ae0f109639`.
- Modification relative to the original concept: update accounting and emit event before external interaction; contract name differs and must be disclosed in diff/replay bindings.
- Expected targets: reentrancy-eth and reentrancy-events absent for the recorded tool profile; low-level-calls/solc-version can remain.
- Approval scope: reviewed template for the exact supported original, subject to byte checks and current validation. “Protected” in the filename is not a universal safety claim.

### MalformedVault.sol
- Origin: original Fusion compiler-error fixture.
- License declaration: SPDX MIT.
- SHA-256: `73791f0cb74c338f94ff92b9387970586b22ad5c729e77c38d929501294e8221`.
- Purpose: deliberately malformed condition `if (x > 10 {`.
- Expected result: compile/parser failure. Findings are unavailable because analysis did not complete; do not represent this as a successful empty list.
- Approval scope: curated failure-path test only.

## Historical compatible tool profile

| Tool | Recorded version |
|---|---|
| solc | 0.8.37; 0.8.37+commit.f401782d.Windows.msvc |
| Slither | 0.11.6 |
| Forge | 1.8.5; 51a52c59cffd940f76eddd0b4bb1791aa4b5ac7f |
| Anvil | 1.8.5; 51a52c59cffd940f76eddd0b4bb1791aa4b5ac7f |
| Python | 3.13.0 |
| Node.js | 24.15.0 |

These are earlier recorded values and current configuration expectations, not fresh observations for every machine. Each scan/validation/replay records its actual observed versions. Frontend resolved dependency versions come from package-lock.json; direct backend pins from requirements.txt. Unsupported combinations require verification, not silent assumption.

## Recorded evidence files

The two scanner JSON files and backup_demo_evidence.json are recorded examples. Before use, inspect their embedded source/run/tool metadata and disclose any missing provenance. Never use their presence to show a live completed scan or fabricate transaction receipts. They are acceptable labeled backups for presentation.

## Adding another fixture

Record unique ID, origin URL or original-authorship statement, immutable upstream revision if applicable, license, modifications, raw-byte hash, expected findings/failure, compiler/import profile, and test/harness relationship. Approve deliberately. A changed fixture requires new evidence, template compatibility checks and careful handling of old reports.

Byte hashes, detector output and tool versions have different meanings; do not interchange them as proof of security.

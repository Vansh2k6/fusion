<!-- Purpose: Explain educational contracts, controlled attack harness, legitimate behavior requirements, and local-only evidence. -->
# Controlled contracts and Foundry harness

This project contains deliberately vulnerable educational code. It is used only with disposable local funds to demonstrate a specified reentrancy scenario.

| File | Purpose |
|---|---|
| src/VulnerableVault.sol | Original vault whose external transfer precedes accounting update |
| src/ProtectedVault.sol | Reviewed CEI comparison with accounting update before interaction |
| src/Attacker.sol | Controlled recursive withdrawal attacker and proceeds collection |
| test/Vault.t.sol | Original exploit, candidate behavior, ordinary use and current fuzz case |
| script/DeployDemo.s.sol | Local chain-31337 deployment helper |
| foundry.toml | Approved project paths/compiler/EVM settings with FFI disabled |

The configured compiler is 0.8.37, auto-detection is disabled, and EVM version is cancun. Record observed compiler/Foundry versions rather than assuming installed tools match configuration. Fixture copies under fixtures are separately hash-registered; keep source/artifact bindings explicit.

## Run tests

From contracts:
```powershell
forge test -vv
```

Current deterministic tests check an original drain, candidate attack rejection, legitimate withdrawal and repeat-withdrawal rejection. The fuzz function currently returns early outside 0 < amount <= 20 ether, which can make many iterations vacuous. P06 must bound/generate meaningful values, cover edges and record seed/settings; a reported 256 runs alone is insufficient.

## Required behavioral evidence

Original scenario starts with victim funds and attacker deposit, then asserts excess attacker proceeds and drained vault. Candidate starts equivalently and preserves victim assets under the attack. Legitimate deposit/withdrawal still updates accounting and transfers funds correctly.

Extend with zero/double/over-withdrawal, reverting receiver, boundary amounts, meaningful fuzz/invariant sequences and harness provenance. Assertion failures are not fixed by replacing specific accounting checks with expectRevert alone.

Foundry test balances and live EOA balances have different fee contexts. Live Anvil evidence must account for transaction fees and receipt status. Do not label test traces as live monitoring.

## Validation and replay boundaries

A candidate is compiled from its exact immutable bytes inside a fresh approved harness workspace. Record source, template, harness/config and bytecode hashes plus observed tools. A successful check of shared source files does not validate different stored candidate bytes.

The deployment script's chain-ID check alone does not prove ownership of the RPC node. The backend must verify the managed local process/listener/session before deployments or reset. No public-chain deployment, real keys, uploaded FFI/configuration or arbitrary harness execution is part of this workflow.

See [P06/P07](../CONTEXT/phases.md) and [fixture provenance](../fixtures/provenance.md) for acceptance and hashes.

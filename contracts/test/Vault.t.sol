// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "../src/VulnerableVault.sol";
import "../src/ProtectedVault.sol";
import "../src/Attacker.sol";

// Minimal self-contained Foundry test base without external dependencies
abstract contract Vm {
    function deal(address who, uint256 newBalance) external virtual;
    function prank(address sender) external virtual;
    function startPrank(address sender) external virtual;
    function stopPrank() external virtual;
    function expectRevert(bytes calldata revertData) external virtual;
    function expectRevert() external virtual;
}

contract VaultTest {
    Vm constant vm = Vm(address(uint160(uint256(keccak256("hevm cheat code")))));

    VulnerableVault vulnerableVault;
    ProtectedVault protectedVault;

    address victim = address(0x1111);
    address attackerUser = address(0x2222);
    address normalUser = address(0x3333);

    function setUp() public {
        vulnerableVault = new VulnerableVault();
        protectedVault = new ProtectedVault();

        vm.deal(victim, 10 ether);
        vm.deal(attackerUser, 2 ether);
        vm.deal(normalUser, 5 ether);

        // Victim deposits 5 ETH in vulnerable vault
        vm.prank(victim);
        vulnerableVault.deposit{value: 5 ether}();

        // Victim deposits 5 ETH in protected vault
        vm.prank(victim);
        protectedVault.deposit{value: 5 ether}();
    }

    function test_vulnerable_vault_exploit() public {
        uint256 initialVaultBalance = address(vulnerableVault).balance;
        require(initialVaultBalance == 5 ether, "Initial vault balance mismatch");

        // Attacker deploys exploit contract
        vm.startPrank(attackerUser);
        Attacker attacker = new Attacker(address(vulnerableVault));

        // Attacker calls attack with 1 ETH
        attacker.attack{value: 1 ether}();
        attacker.withdrawProceeds();
        vm.stopPrank();

        // Attacker started with 2 ETH, spent 1 ETH on attack, and drained all 6 ETH (5 victim + 1 own)
        // Leaving vault empty and attacker balance at 7 ETH
        require(address(vulnerableVault).balance == 0, "Vault was not drained");
        require(attackerUser.balance == 7 ether, "Attacker did not extract excess funds");
    }

    function test_protected_vault_blocks_attack() public {
        uint256 initialVaultBalance = address(protectedVault).balance;
        require(initialVaultBalance == 5 ether, "Initial protected vault balance mismatch");

        vm.startPrank(attackerUser);
        Attacker attacker = new Attacker(address(protectedVault));

        // Attack must revert because balance is zeroed before external call
        vm.expectRevert();
        attacker.attack{value: 1 ether}();
        vm.stopPrank();

        // Protected vault balance must still be 5 ETH intact
        require(address(protectedVault).balance == 5 ether, "Protected vault balance compromised");
        require(attackerUser.balance == 2 ether, "Attacker balance changed unexpectedly");
    }

    function test_protected_vault_legitimate_use() public {
        // Normal user deposits 2 ETH
        vm.startPrank(normalUser);
        protectedVault.deposit{value: 2 ether}();
        require(protectedVault.balances(normalUser) == 2 ether, "Deposit accounting error");
        require(address(protectedVault).balance == 7 ether, "Total vault balance error");

        // Normal user withdraws 2 ETH
        protectedVault.withdraw();
        require(protectedVault.balances(normalUser) == 0, "Balance not zeroed after withdrawal");
        require(normalUser.balance == 5 ether, "Normal user did not receive withdrawn ETH");
        require(address(protectedVault).balance == 5 ether, "Remaining vault balance error");

        // Normal user attempting another withdrawal must revert
        vm.expectRevert();
        protectedVault.withdraw();
        vm.stopPrank();
    }

    /// @notice Bounded fuzz test verifying accounting conservation for legitimate transactions.
    /// The raw uint96 input is folded into (0, 5 ether] so every run executes the
    /// deposit/withdraw path; nothing returns early (fuzz-domain vacuity fix).
    function testFuzz_protected_vault_deposit_and_withdraw(uint96 amount) public {
        uint256 bounded = (uint256(amount) % 5 ether) + 1;

        address fuzzedUser = address(0x5555);
        vm.deal(fuzzedUser, bounded);

        uint256 vaultInitial = address(protectedVault).balance;

        vm.startPrank(fuzzedUser);
        protectedVault.deposit{value: bounded}();
        require(protectedVault.balances(fuzzedUser) == bounded, "Fuzz deposit accounting failed");
        require(address(protectedVault).balance == vaultInitial + bounded, "Vault balance invariant failed");

        protectedVault.withdraw();
        require(protectedVault.balances(fuzzedUser) == 0, "Fuzz balance not zeroed");
        require(fuzzedUser.balance == bounded, "User funds not restored");
        require(address(protectedVault).balance == vaultInitial, "Vault balance not restored");
        vm.stopPrank();
    }

    function test_protected_vault_zero_deposit_reverts() public {
        vm.startPrank(normalUser);
        vm.expectRevert();
        protectedVault.deposit{value: 0}();
        require(protectedVault.balances(normalUser) == 0, "Failed zero deposit must not credit balance");
        vm.stopPrank();
    }

    function test_protected_vault_reverting_receiver_keeps_funds() public {
        RevertingReceiver receiver = new RevertingReceiver();
        vm.deal(address(receiver), 1 ether);
        vm.startPrank(address(receiver));
        protectedVault.deposit{value: 1 ether}();
        // The external call to a reverting receiver reverts the whole withdrawal;
        // accounting must be unchanged afterward (top-level revert undoes effects).
        vm.expectRevert();
        protectedVault.withdraw();
        require(protectedVault.balances(address(receiver)) == 1 ether, "Reverted withdrawal must not alter accounting");
        require(address(protectedVault).balance == 6 ether, "Vault balance must be intact after revert");
        vm.stopPrank();
    }
}

contract RevertingReceiver {
    receive() external payable {
        revert("receiver refuses funds");
    }
}

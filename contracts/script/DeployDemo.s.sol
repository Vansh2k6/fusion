// Purpose: Deploy the controlled vault pair only when Foundry is connected to local Anvil chain 31337.
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "../src/VulnerableVault.sol";
import "../src/ProtectedVault.sol";

interface Vm {
    function startBroadcast() external;
    function stopBroadcast() external;
}

contract DeployDemo {
    Vm private constant vm = Vm(address(uint160(uint256(keccak256("hevm cheat code")))));

    event DemoContractsDeployed(address vulnerableVault, address protectedVault);

    function run() external returns (VulnerableVault vulnerable, ProtectedVault protected) {
        require(block.chainid == 31337, "Fusion demo requires local Anvil chain 31337");

        vm.startBroadcast();
        vulnerable = new VulnerableVault();
        protected = new ProtectedVault();
        vm.stopBroadcast();

        emit DemoContractsDeployed(address(vulnerable), address(protected));
    }
}

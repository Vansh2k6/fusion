// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

contract MalformedVault {
    // Syntax error intentionally introduced
    function broken(uint256 x) public {
        if (x > 10 {
            revert();
        }
    }
}

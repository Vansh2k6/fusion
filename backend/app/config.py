# Purpose: Centralize loopback endpoints, upload limits, job timeouts, approved tools, and artifact paths.
import os
from pathlib import Path

# Base paths
BASE_DIR = Path(__file__).resolve().parent.parent.parent
DATA_DIR = BASE_DIR / "data"
FIXTURES_DIR = BASE_DIR / "fixtures"
CONTRACTS_DIR = BASE_DIR / "contracts"

# Ensure data directories exist
DATA_DIR.mkdir(parents=True, exist_ok=True)
(DATA_DIR / "scans").mkdir(parents=True, exist_ok=True)
(DATA_DIR / "patches").mkdir(parents=True, exist_ok=True)
(DATA_DIR / "demo").mkdir(parents=True, exist_ok=True)

# Database
DB_PATH = DATA_DIR / "fusion.db"

# Server configuration
HOST = "127.0.0.1"
PORT = 8000
ALLOWED_ORIGINS = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]

# Security limits
MAX_UPLOAD_SIZE = 256 * 1024  # 256 KiB limit
ANALYSIS_TIMEOUT_SECONDS = 60
VALIDATION_TIMEOUT_SECONDS = 60
MAX_TOOL_OUTPUT_BYTES = 1024 * 1024
MAX_REPORT_BYTES = 5 * 1024 * 1024

# Arbitrary source execution stays disabled until a verified container worker
# enforces the isolation requirements in CONTEXT/agent.md R07/R08.
ARBITRARY_SCAN_ISOLATION_ENABLED = False

# Local toolchain discovery
user_home = Path.home()
foundry_bin = user_home / ".foundry" / "bin"

FORGE_BIN = str(foundry_bin / "forge.exe") if (foundry_bin / "forge.exe").exists() else "forge"
ANVIL_BIN = str(foundry_bin / "anvil.exe") if (foundry_bin / "anvil.exe").exists() else "anvil"
SOLC_BIN = "solc"
SLITHER_BIN = "slither"

# Anvil local demo RPC configuration
ANVIL_HOST = "127.0.0.1"
ANVIL_PORT = 8545
ANVIL_RPC_URL = f"http://{ANVIL_HOST}:{ANVIL_PORT}"
ANVIL_CHAIN_ID = 31337
ANVIL_PID_PATH = DATA_DIR / "anvil.pid"

# Pinned tool versions for verification metadata
PINNED_VERSIONS = {
    "solc": "0.8.37",
    "slither": "0.11.6",
    "forge": "1.8.5",
    "anvil": "1.8.5",
    "python": "3.13.0",
    "node": "24.15.0"
}

# Validation profile (P06.02/P08.01): required check IDs, deterministic fuzz settings.
REQUIRED_VALIDATION_CHECKS = ("compile", "rescan", "attack_exploit", "normal_behavior", "fuzz")
FUZZ_SEED = 20261009
FUZZ_RUNS = 256

# Curated Fixture Hashes (all lowercase)
CURATED_FIXTURES = {
    "vulnerable_vault": {
        "id": "vulnerable_vault",
        "name": "VulnerableVault.sol",
        "hash": "66ae62ae4832a0f60b34deeee7a207fb051659994de9ad7cdea52b41ee6fca96",
        "rel_path": "fixtures/VulnerableVault.sol",
        "description": "Educational vault exhibiting reentrancy in withdraw() (reentrancy-eth)",
        "expected_detector": "reentrancy-eth"
    },
    "protected_vault": {
        "id": "protected_vault",
        "name": "ProtectedVault.sol",
        "hash": "964f2e6bac7788c69b92adc041719aa49711aac3c9bd84b2817641ae0f109639",
        "rel_path": "fixtures/ProtectedVault.sol",
        "description": "Educational vault with Checks-Effects-Interactions (CEI) mitigation",
        "expected_detector": None
    },
    "malformed_vault": {
        "id": "malformed_vault",
        "name": "MalformedVault.sol",
        "hash": "73791f0cb74c338f94ff92b9387970586b22ad5c729e77c38d929501294e8221",
        "rel_path": "fixtures/MalformedVault.sol",
        "description": "Solidity file with syntax error to test compile failure diagnostics",
        "expected_detector": None
    }
}

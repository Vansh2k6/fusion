# Purpose: Verify prerequisites, pin toolchains, build contracts, and install frontend dependencies.
$ErrorActionPreference = "Stop"

Write-Host "=== Fusion Security Workbench: Setup ===" -ForegroundColor Cyan

# 1. Check Python
$pythonVer = python --version 2>&1
Write-Host "[✓] Python: $pythonVer" -ForegroundColor Green

# 2. Check Solc
$solcVer = solc --version 2>&1 | Select-String "Version:"
Write-Host "[✓] Solc: $solcVer" -ForegroundColor Green

# 3. Check Slither
$slitherVer = slither --version 2>&1
Write-Host "[✓] Slither: $slitherVer" -ForegroundColor Green

# 4. Check Foundry (forge / anvil)
$foundryBin = "$HOME\.foundry\bin"
if (Test-Path "$foundryBin\forge.exe") {
    $forgeVer = & "$foundryBin\forge.exe" --version
    Write-Host "[✓] Forge: $forgeVer" -ForegroundColor Green
} else {
    Write-Host "[!] Forge not found in $foundryBin" -ForegroundColor Yellow
}

# 5. Build Smart Contracts
Write-Host "`nBuilding Solidity contracts with forge..." -ForegroundColor Cyan
Set-Location -Path "$PSScriptRoot\..\contracts"
& "$foundryBin\forge.exe" build
Set-Location -Path "$PSScriptRoot\.."

# 6. Install pinned backend dependencies
Write-Host "`nInstalling pinned backend dependencies..." -ForegroundColor Cyan
python -m pip install -r "$PSScriptRoot\..\backend\requirements.txt"

# 7. Install Frontend Dependencies from lockfile
Write-Host "`nInstalling frontend npm dependencies..." -ForegroundColor Cyan
Set-Location -Path "$PSScriptRoot\..\frontend"
cmd.exe /c npm ci
Set-Location -Path "$PSScriptRoot\.."

Write-Host "`n[✓] Fusion environment setup complete!" -ForegroundColor Green

# Purpose: Run all automated unit, integration, invariant, and build verification checks across the repository.
$ErrorActionPreference = "Stop"

Write-Host "=== Running Complete Fusion Verification Suite ===" -ForegroundColor Cyan
$root = Resolve-Path "$PSScriptRoot\.."
$foundryBin = "$HOME\.foundry\bin"

# 1. Forge Contract Suite (Exploit test, mitigation test, legitimate use, bounded fuzz)
Write-Host "`n[1/3] Running Forge test suite..." -ForegroundColor Yellow
Set-Location -Path "$root\contracts"
& "$foundryBin\forge.exe" test -vv
if ($LASTEXITCODE -ne 0) { throw "Forge tests failed!" }

# 2. Backend Pytest Suite (M1 scanner, Slither normalization, M2 patch validation, M3 live demo API)
Write-Host "`n[2/3] Running Backend pytest suite..." -ForegroundColor Yellow
Set-Location -Path "$root\backend"
python -m pytest tests/ -v --basetemp "$root\data\pytest-verify"
if ($LASTEXITCODE -ne 0) { throw "Backend tests failed!" }

# 3. Frontend TypeScript & Production Build
Write-Host "`n[3/3] Running Frontend typecheck & Vite build..." -ForegroundColor Yellow
Set-Location -Path "$root\frontend"
cmd.exe /c npm run build
if ($LASTEXITCODE -ne 0) { throw "Frontend build failed!" }

Set-Location -Path "$root"
Write-Host "`n=======================================================" -ForegroundColor Green
Write-Host "  ALL VERIFICATION GATES PASSED (PHASES 0 - 4)" -ForegroundColor Green
Write-Host "=======================================================" -ForegroundColor Green

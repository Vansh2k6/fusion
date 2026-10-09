# Purpose: Reset local chain state and mark prior demo runs as historical.
# Only the backend performs the reset so ownership verification and history
# marking cannot be bypassed (P07.01: no direct unchecked RPC fallback).
$ErrorActionPreference = "Continue"

Write-Host "=== Resetting Fusion Demo State ===" -ForegroundColor Cyan

try {
    $res = Invoke-RestMethod -Uri "http://127.0.0.1:8000/api/demo/reset" -Method Post
    Write-Host "[OK] Server response: $($res.message)" -ForegroundColor Green
} catch {
    Write-Host "[!] Backend reset refused or unreachable: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host "    Start the backend, verify Anvil ownership (scripts/start.ps1), then retry." -ForegroundColor Yellow
    Write-Host "    Direct anvil_reset RPC calls are intentionally unsupported: they would skip ownership checks and history marking." -ForegroundColor Yellow
    exit 1
}

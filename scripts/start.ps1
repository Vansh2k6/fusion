# Purpose: Start local Anvil, FastAPI backend, and Vite frontend with loopback binding.
$ErrorActionPreference = "Stop"

Write-Host "Fusion Security Workbench - local startup" -ForegroundColor Cyan

$foundryBin = Join-Path $env:USERPROFILE ".foundry\bin"
$projectRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path

$anvilConnection = Test-NetConnection -ComputerName 127.0.0.1 -Port 8545 -WarningAction SilentlyContinue
if (-not $anvilConnection.TcpTestSucceeded) {
    Write-Host "Starting Anvil on 127.0.0.1:8545 (chain 31337)..." -ForegroundColor Yellow
    $anvilProcess = Start-Process `
        -FilePath (Join-Path $foundryBin "anvil.exe") `
        -ArgumentList @("--host", "127.0.0.1", "--port", "8545", "--chain-id", "31337", "--silent") `
        -WindowStyle Hidden `
        -PassThru
    # Ownership marker is pid:start-time so the backend can reject stale/PID-reused markers.
    $startedEpoch = [long]([datetimeoffset]((Get-Process -Id $anvilProcess.Id).StartTime.ToUniversalTime())).ToUnixTimeSeconds()
    Set-Content -LiteralPath (Join-Path $projectRoot "data\anvil.pid") -Value "$($anvilProcess.Id):$startedEpoch" -Encoding Ascii -NoNewline
    Start-Sleep -Seconds 2
} else {
    Write-Host "Anvil port is already in use; the API will verify its identity before transactions." -ForegroundColor Green
}

Write-Host "Starting API on http://127.0.0.1:8000..." -ForegroundColor Yellow
Start-Process `
    -FilePath "python" `
    -ArgumentList @("-m", "uvicorn", "app.main:app", "--host", "127.0.0.1", "--port", "8000") `
    -WorkingDirectory (Join-Path $projectRoot "backend") `
    -WindowStyle Hidden
Start-Sleep -Seconds 2

Write-Host "Starting UI on http://127.0.0.1:5173..." -ForegroundColor Yellow
Set-Location -Path (Join-Path $projectRoot "frontend")
cmd.exe /c npm run dev -- --host 127.0.0.1 --port 5173

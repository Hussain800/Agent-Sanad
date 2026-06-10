# Agent Sanad — one-command local launch (Windows PowerShell).
# Starts the API + UI on http://127.0.0.1:8000 in offline mock mode.
# If an older server is already bound to the port, it tells you instead of
# silently serving stale routes (the classic "new UI, old API" failure).

$ErrorActionPreference = "Stop"
Set-Location -Path $PSScriptRoot

# Refuse to start on top of an existing (possibly stale) server.
$existing = Get-NetTCPConnection -LocalPort 8000 -State Listen -ErrorAction SilentlyContinue
if ($existing) {
    $owners = $existing | Select-Object -ExpandProperty OwningProcess -Unique
    Write-Host "Port 8000 is already in use by process id(s): $($owners -join ', ')." -ForegroundColor Yellow
    Write-Host "That server may be an OLDER build (routes load at startup)." -ForegroundColor Yellow
    Write-Host "Stop it first:  Stop-Process -Id $($owners -join ',') -Force" -ForegroundColor Yellow
    exit 1
}

$env:PYTHONPATH = "."
$env:LOCAL_MOCK_MODE = "true"
$env:SANAD_LIVE_EXTRACTION = "1"   # live synthetic GOLDEN certificate parse (cached fallback)

Write-Host "Agent Sanad starting on http://127.0.0.1:8000  (offline mock mode)" -ForegroundColor Green
python -B -m uvicorn backend.app:app --host 127.0.0.1 --port 8000

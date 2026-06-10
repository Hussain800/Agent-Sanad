# Agent Sanad - one-command local launch (Windows PowerShell).
# Starts the API + UI on http://127.0.0.1:8000 in offline mock mode.
# If an older server is already bound to the port, it tells you instead of
# silently serving stale routes (the classic "new UI, old API" failure).

$ErrorActionPreference = "Stop"
Set-Location -Path $PSScriptRoot

$Port = 8000

function Get-ListeningPortOwners {
    param([int]$Port)

    $owners = @()

    try {
        $connections = Get-NetTCPConnection -LocalPort $Port -State Listen -ErrorAction Stop
        $owners += $connections | ForEach-Object { [int]$_.OwningProcess }
    } catch {
        # Some managed Windows environments deny CIM access for
        # Get-NetTCPConnection. netstat still exposes the listener PID.
    }

    if ($owners.Count -eq 0) {
        $pattern = "^\s*TCP\s+\S+:$Port\s+\S+\s+LISTENING\s+(\d+)\s*$"
        $lines = & netstat -ano -p tcp 2>$null
        foreach ($line in $lines) {
            if ($line -match $pattern) {
                $owners += [int]$Matches[1]
            }
        }
    }

    return $owners | Where-Object { $_ -gt 0 } | Sort-Object -Unique
}

# Refuse to start on top of an existing (possibly stale) server.
$owners = @(Get-ListeningPortOwners -Port $Port)
if ($owners.Count -gt 0) {
    Write-Host "Port 8000 is already in use by process id(s): $($owners -join ', ')." -ForegroundColor Yellow
    Write-Host "That server may be an OLDER build (routes load at startup)." -ForegroundColor Yellow
    Write-Host "Stop it first:  Stop-Process -Id $($owners -join ',') -Force" -ForegroundColor Yellow
    exit 1
}

$env:PYTHONPATH = "."
$env:LOCAL_MOCK_MODE = "true"
$env:SANAD_LIVE_EXTRACTION = "1"   # live synthetic GOLDEN certificate parse (cached fallback)

Write-Host "Agent Sanad starting on http://127.0.0.1:8000  (offline mock mode)" -ForegroundColor Green
python -B -m uvicorn backend.app:app --host 127.0.0.1 --port $Port
exit $LASTEXITCODE

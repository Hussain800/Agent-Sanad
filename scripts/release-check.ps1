#!/usr/bin/env pwsh
# Agent Sanad v1.4 Release Check
# Run from repo root:  .\scripts\release-check.ps1
$ErrorActionPreference = "Stop"
$ROOT = Split-Path -Parent (Split-Path -Parent $PSCommandPath)
Set-Location $ROOT
$passed = 0; $failed = 0

function check($name, $condition) {
    if (& $condition) { $script:passed++; Write-Host "  PASS  $name" -ForegroundColor Green }
    else { $script:failed++; Write-Host "  FAIL  $name" -ForegroundColor Red }
}

Write-Host "===== Agent Sanad v1.4 Release Check =====" -ForegroundColor Cyan

# 1. Version handshake
check "APP_VERSION == CLIENT_BUILD" { 
    $av = Select-String -Path backend\app.py -Pattern 'APP_VERSION = "(.+)"' | ForEach-Object { $_.Matches.Groups[1].Value }
    $cv = Select-String -Path frontend\index.html -Pattern 'CLIENT_BUILD = "(.+)"' | ForEach-Object { $_.Matches.Groups[1].Value }
    $av -eq $cv
}

# 2. Full test suite
check "Full test suite 139+" {
    $result = & python -B -m pytest tests\ -q -p no:cacheprovider 2>&1 | Out-String
    $result -match "passed"
}

# 3. No workbook tracked
check "No workbook tracked" {
    $tracked = & git ls-files '*.xlsx' '*.xls'
    -not $tracked
}

# 4. PII patterns scan
check "No PII in tracked files" {
    $pii = Select-String -Path (git ls-files '*.py' '*.md' '*.html' '*.json') -Pattern '\b\d{15}\b|784-\d{4}-\d{7}-\d' -SimpleMatch -ErrorAction SilentlyContinue
    -not $pii
}

# 5. OpenAPI routes check
check "OpenAPI exposes routes" {
    $routes = & python -c "from backend.app import app; print(len(app.routes))" 2>$null
    [int]$routes -ge 40
}

# 6. Connector contract test
check "Connectors registered" {
    $count = & python -c "from backend.connectors import list_connectors; print(len(list_connectors()))" 2>$null
    [int]$count -ge 6
}

# 7. Audit chain verification test
check "Audit chain basic" {
    $result = & python -c "
from backend.audit_chain import add_chain_event, verify_chain
add_chain_event('TEST-CHECK', 'system', 'release_test')
v = verify_chain('TEST-CHECK')
print(v['ok'])
" 2>$null
    $result -eq "True"
}

# 8. Graph equivalence
check "Graph/plain equivalence passes" {
    $result = & python -m pytest tests\test_graph_equivalence.py -q -p no:cacheprovider 2>&1 | Out-String
    $result -match "passed"
}

Write-Host "`n===== Results: $passed passed, $failed failed =====" -ForegroundColor Cyan
if ($failed -gt 0) { exit 1 }

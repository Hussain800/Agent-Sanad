#!/usr/bin/env pwsh
# Agent Sanad v1.8 Release Check
# Run from repo root:  .\scripts\release-check.ps1
$ErrorActionPreference = "Stop"
$ROOT = Split-Path -Parent (Split-Path -Parent $PSCommandPath)
Set-Location $ROOT
$passed = 0; $failed = 0

function check($name, $condition) {
    if (& $condition) { $script:passed++; Write-Host "  PASS  $name" -ForegroundColor Green }
    else { $script:failed++; Write-Host "  FAIL  $name" -ForegroundColor Red }
}

Write-Host "===== Agent Sanad v1.8 Release Check =====" -ForegroundColor Cyan

# 1. Version handshake
check "APP_VERSION == CLIENT_BUILD == 1.8.0" { 
    $av = Select-String -Path backend\app.py -Pattern 'APP_VERSION = "(.+)"' | ForEach-Object { $_.Matches.Groups[1].Value }
    $cv = Select-String -Path frontend\index.html -Pattern 'CLIENT_BUILD = "(.+)"' | ForEach-Object { $_.Matches.Groups[1].Value }
    ($av -eq $cv) -and ($av -eq "1.8.0")
}

# 2. Full test suite
check "Full test suite 420+" {
    $result = & python -B -m pytest tests\ -q -p no:cacheprovider 2>&1 | Out-String
    ($result -match "passed") -and ($result -match "(\d+) passed") -and ([int]$matches[1] -ge 420)
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
    [int]$routes -ge 108
}

# 6. Connector contract test (7 connectors)
check "Connectors registered (7+)" {
    $count = & python -c "from backend.connectors import list_connectors; print(len(list_connectors()))" 2>$null
    [int]$count -ge 7
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

# 9. Consent guard tests
check "Consent guard tests pass" {
    $result = & python -B -m pytest tests\test_consent_guard.py -q -p no:cacheprovider 2>&1 | Out-String
    $result -match "passed"
}

# 10. ABAC tests
check "ABAC tests pass" {
    $result = & python -B -m pytest tests\test_abac.py -q -p no:cacheprovider 2>&1 | Out-String
    $result -match "passed"
}

# 11. Signature integrity tests
check "Signature integrity tests pass" {
    $result = & python -B -m pytest tests\test_signature_integrity.py -q -p no:cacheprovider 2>&1 | Out-String
    $result -match "passed"
}

# 12. Connector contract tests
check "Connector contract tests pass" {
    $result = & python -B -m pytest tests\test_connector_contracts.py -q -p no:cacheprovider 2>&1 | Out-String
    $result -match "passed"
}

# 13. OpenAPI generated
check "OpenAPI JSON generated" {
    Test-Path docs\api\openapi.json
}

# 14. Postman collection generated
check "Postman collection generated" {
    Test-Path docs\POSTMAN_COLLECTION.json
}

# 15. Release notes exist
check "Release notes exist" {
    Test-Path docs\RELEASE_NOTES_V1_8.md
}

# 16. Arabic key coverage
check "Arabic i18n coverage" {
    $result = & python -B -m pytest tests\test_accessibility_i18n.py -q -p no:cacheprovider 2>&1 | Out-String
    $result -match "passed"
}

# 17. Docs current
check "Docs version references current" {
    $readme = Get-Content README.md -Raw
    ($readme -match "1\.8\.0") -and ($readme -match "431")
}

# 18. Docs drift check
check "Docs drift check" {
    $result = & python -B -m pytest tests\test_docs_drift.py -q -p no:cacheprovider 2>&1 | Out-String
    $result -match "passed"
}

# 19. Lifecycle tests
check "Lifecycle tests" {
    $result = & python -B -m pytest tests\test_case_lifecycle.py -q -p no:cacheprovider 2>&1 | Out-String
    $result -match "passed"
}

# 20. Evidence graph / audit export tests
check "Evidence graph + audit tests" {
    $result = & python -B -m pytest tests\test_evidence_graph.py tests\test_audit_export.py -q -p no:cacheprovider 2>&1 | Out-String
    $result -match "passed"
}

# 21. Reliability lab tests
check "Reliability lab tests" {
    $result = & python -B -m pytest tests\test_connector_reliability_lab.py -q -p no:cacheprovider 2>&1 | Out-String
    $result -match "passed"
}

# 22. API contract tests
check "API contract tests" {
    $result = & python -B -m pytest tests\test_api_contract_models.py -q -p no:cacheprovider 2>&1 | Out-String
    $result -match "passed"
}

# 23. ABAC v2 tests
check "ABAC v2 tests" {
    $result = & python -B -m pytest tests\test_abac_v2.py -q -p no:cacheprovider 2>&1 | Out-String
    $result -match "passed"
}

# 24. UAE PASS / signature v4 tests
check "UAE PASS/signature v4 tests" {
    $result = & python -B -m pytest tests\test_uaepass_signature_v4.py -q -p no:cacheprovider 2>&1 | Out-String
    $result -match "passed"
}

# 25. Fairness analytics tests
check "Fairness analytics tests" {
    $result = & python -B -m pytest tests\test_fairness_analytics.py -q -p no:cacheprovider 2>&1 | Out-String
    $result -match "passed"
}

# 26. Evidence graph v2
check "Evidence graph v2 tests" {
    $result = & python -B -m pytest tests\test_evidence_graph_v2.py -q -p no:cacheprovider 2>&1 | Out-String
    $result -match "passed"
}

# 27. Ops observability
check "Ops observability tests" {
    $result = & python -B -m pytest tests\test_ops_observability.py -q -p no:cacheprovider 2>&1 | Out-String
    $result -match "passed"
}

# 28. Security drills
check "Security drills tests" {
    $result = & python -B -m pytest tests\test_security_drills.py -q -p no:cacheprovider 2>&1 | Out-String
    $result -match "passed"
}

# 29. Fairness impact v3
check "Fairness impact v3 tests" {
    $result = & python -B -m pytest tests\test_fairness_impact_v3.py -q -p no:cacheprovider 2>&1 | Out-String
    $result -match "passed"
}

# 30. Materials v1.7/v1.8
check "Materials tests" {
    $result = & python -B -m pytest tests\test_materials_v1_7.py -q -p no:cacheprovider 2>&1 | Out-String
    $result -match "passed"
}

# 31. Lifecycle enforcement
check "Lifecycle enforcement" {
    $result = & python -B -m pytest tests\test_lifecycle_enforcement_v17.py -q -p no:cacheprovider 2>&1 | Out-String
    $result -match "passed"
}

# 32. No raw dict routes
check "No raw dict routes" {
    $result = & python -B -m pytest tests\test_no_raw_dict_routes.py -q -p no:cacheprovider 2>&1 | Out-String
    $result -match "passed"
}

# 33. Zero warnings check
check "Zero stale test counts" {
    $result = & python -B -m pytest tests\test_zero_warnings_v17.py -q -p no:cacheprovider 2>&1 | Out-String
    $result -match "passed"
}

# 34. Pilot docs exist
check "Pilot docs exist" {
    $result = & python -B -m pytest tests\test_pilot_docs_v17.py -q -p no:cacheprovider 2>&1 | Out-String
    $result -match "passed"
}

# 35. Version consistency
check "Version consistency" {
    $result = & python -B -m pytest tests\test_version_consistency_v17.py -q -p no:cacheprovider 2>&1 | Out-String
    $result -match "passed"
}

# 36. v1.8 module smoke tests
check "v1.8 module tests" {
    $result = & python -B -m pytest tests\test_v18_modules.py -q -p no:cacheprovider 2>&1 | Out-String
    $result -match "passed"
}

# 37. v1.8 release facts
check "v1.8 release facts" {
    $result = & python -B -m pytest tests\test_release_facts_v18.py tests\test_v18_gates.py -q -p no:cacheprovider 2>&1 | Out-String
    $result -match "passed"
}

# 38. v1.8 copilot and interop
check "v1.8 copilot and interop tests" {
    $result = & python -B -m pytest tests\test_v18_copilot_interop.py -q -p no:cacheprovider 2>&1 | Out-String
    $result -match "passed"
}

# 39. v1.8 material routes
check "v1.8 material routes" {
    $result = & python -B -m pytest tests\test_v18_materials.py -q -p no:cacheprovider 2>&1 | Out-String
    $result -match "passed"
}

# 40. v1.8 backend modules exist
check "v1.8 backend modules exist" {
    (Test-Path backend\release_brain.py) -and
    (Test-Path backend\rescue_radar.py) -and
    (Test-Path backend\policy_digital_twin.py) -and
    (Test-Path backend\evidence_vault.py) -and
    (Test-Path backend\interop_certification.py) -and
    (Test-Path backend\service_copilot.py) -and
    (Test-Path backend\mission_control.py) -and
    (Test-Path backend\redteam_lab.py)
}

# 41. v1.8 OpenAPI routes
check "v1.8 OpenAPI routes" {
    $openapi = Get-Content docs\api\openapi.json -Raw
    ($openapi -match "/rescue/radar") -and
    ($openapi -match "/digital-twin/run") -and
    ($openapi -match "/evidence-vault") -and
    ($openapi -match "/interop/certification") -and
    ($openapi -match "/copilot/session/start") -and
    ($openapi -match "/mission-control") -and
    ($openapi -match "/redteam/run")
}

# 42. Release provenance current
check "Release provenance current" {
    $prov = Get-Content docs\RELEASE_PROVENANCE.md -Raw
    ($prov -match "1\.8\.0") -and ($prov -match "431 passing tests") -and ($prov -match "45/45 release gates")
}

# 43. Runtime release facts current
check "Runtime release facts current" {
    $result = & python -c "from backend.observability.service_metrics import get_release_check_latest; r=get_release_check_latest(); print(r['version'], r['tests'], r['gates'])" 2>$null
    $result -match "1\.8\.0 431 45"
}

# 44. Current release doc current
check "Current release doc current" {
    $current = Get-Content docs\CURRENT_RELEASE.md -Raw
    ($current -match "1\.8\.0") -and ($current -match "431") -and ($current -match "45\+")
}

# 45. v1.8 release notes current
check "v1.8 release notes current" {
    $notes = Get-Content docs\RELEASE_NOTES_V1_8.md -Raw
    ($notes -match "1\.8\.0") -and ($notes -match "431") -and ($notes -match "45\+")
}

Write-Host "`n===== Results: $passed passed, $failed failed =====" -ForegroundColor Cyan
if ($failed -gt 0) { exit 1 }

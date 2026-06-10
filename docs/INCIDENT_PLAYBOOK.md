# Agent Sanad v1.5 Incident Playbook

## Incident Classification

| Severity | Definition | Response |
|----------|-----------|----------|
| P1 - Critical | Service completely unavailable | Immediate escalation |
| P2 - High | Key feature broken (consent, decisions, UAE PASS) | Address within 1 hour |
| P3 - Medium | Non-critical feature degraded (supervisor metrics, appeals) | Address within 4 hours |
| P4 - Low | Cosmetic issues | Next release |

## Common Incidents

### 1. Port Already Bound
**Symptom**: `run.ps1` refuses to start  
**Cause**: Stale uvicorn process on port 8000  
**Resolution**: `Get-Process -Name python | Stop-Process` then relaunch

### 2. Build Version Mismatch
**Symptom**: Yellow banner on frontend  
**Cause**: Server running older code than frontend  
**Resolution**: Kill uvicorn, pull latest main, relaunch

### 3. Connector Health Degraded
**Symptom**: Connector returns error/timeout  
**Cause**: Simulated failure mode set  
**Resolution**: `POST /connectors/{name}/reset` or restart server

### 4. Audit Chain Broken
**Symptom**: `POST /audit/verify` returns `ok: false`  
**Cause**: Event tampering or corruption  
**Resolution**: Reset DB (`data/agent_sanad.db`) and restart

### 5. Consent Denials Spike
**Symptom**: High consent denial rate  
**Cause**: Consent scope/purpose mismatch in requests  
**Resolution**: Check consent records match required purpose_codes

### 6. UAE PASS Session Failures
**Symptom**: Callback returns "wrong nonce" or "replay rejected"  
**Cause**: Stale session state  
**Resolution**: Start new session, verify nonce matches

### 7. Test Suite Failures
**Symptom**: Tests failing after code changes  
**Cause**: Backward compatibility break  
**Resolution**: 
- Check `APP_VERSION == CLIENT_BUILD`
- Ensure policy/engine.py unchanged unless intentional
- Verify all 13 sample cases still produce correct recommendations
- Check no PII patterns in tracked files

## Recovery Procedures

### Full Reset
```powershell
Remove-Item data/agent_sanad.db -ErrorAction SilentlyContinue
.\run.ps1
```

### Verify Integrity
```powershell
$env:PYTHONPATH="."
python -B -m pytest tests\ -q -p no:cacheprovider
powershell -ExecutionPolicy Bypass -File scripts\release-check.ps1
```

## Escalation Path

1. First: Run release-check.ps1 (17 automated checks)
2. Second: Run full test suite
3. Third: Check git status for uncommitted changes
4. Fourth: Inspect `data/agent_sanad.db` via SQLite
5. Fifth: Consult `docs/` for architecture reference

# Agent Sanad v1.6 Sandbox Onboarding

## Prerequisites
- Windows PowerShell 5.1+ or macOS/Linux bash
- Python 3.11+
- Git
- Port 8000 free

## Quick Start
```powershell
git clone https://github.com/Hussain800/Agent-Sanad.git
cd Agent-Sanad
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
.\run.ps1
```
Open http://127.0.0.1:8000/

## Verify Installation
```powershell
$env:PYTHONPATH="."
python -B -m pytest tests\ -q -p no:cacheprovider
powershell -ExecutionPolicy Bypass -File scripts\release-check.ps1
```
Expected: 287 passed, 25/25 release gates.

## Connector Setup
All connectors are mock. No external API keys needed. Set `LOCAL_MOCK_MODE=true` (default).

## Database
SQLite at `data/agent_sanad.db` (auto-created). Delete to reset.

## Demo Flows
1. Beneficiary: UAE PASS → Consent → Application → Processing → Result
2. Officer: Queue → Case Review → Evidence Trace → Action
3. Supervisor: Metrics → Backlog → SLA Risk → Fairness
4. Auditor: Audit Export → Evidence Graph → Package Verification
5. Admin: Connector Simulator → Reliability Lab → Materials

## Environment Variables
| Variable | Default | Purpose |
|----------|---------|---------|
| LOCAL_MOCK_MODE | true | Offline mock mode |
| SANAD_ORCHESTRATOR | plain | plain/graph |
| SANAD_DB_PATH | data/agent_sanad.db | SQLite path |

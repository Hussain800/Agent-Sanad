# Agent Sanad v1.5 Pilot Runbook

## Prerequisites

- Python 3.11+
- Git
- PowerShell 5.1+ (Windows)
- Port 8000 available

## Quick Start

```powershell
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
.\run.ps1
```

Open http://127.0.0.1:8000/

## Running Tests

```powershell
$env:PYTHONPATH="."
python -B -m pytest tests\ -q -p no:cacheprovider
```

Expected: 231+ passed

## Release Check

```powershell
powershell -ExecutionPolicy Bypass -File scripts\release-check.ps1
```

Expected: 17/17 passed

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `LOCAL_MOCK_MODE` | `true` | Offline mock mode |
| `SANAD_LIVE_EXTRACTION` | `0` | Live salary cert parsing |
| `SANAD_ORCHESTRATOR` | `plain` | Orchestrator (plain/graph) |
| `LANGSMITH_TRACING` | `false` | LangSmith tracing |
| `SANAD_DB_PATH` | `data/agent_sanad.db` | SQLite path |

## Demo Flow

1. **Landing** → Click "Continue with UAE PASS"
2. **UAE PASS** → Click "Verify identity" (mock)
3. **Consent** → Grant consent
4. **Application** → Select sample case → Review → Submit
5. **Processing** → Watch animated timeline
6. **Result** → View recommendation + next steps
7. **Officer Portal** → Review case, view evidence trace, take action

## Health Check

```
curl http://127.0.0.1:8000/healthz
```

Response:
```json
{
  "ok": true,
  "mock_mode": true,
  "app_version": "1.5.0",
  "orchestrator": "plain",
  "graph_available": true
}
```

## Knowing When Things Are Wrong

- **Build mismatch banner**: Server version != frontend version. Restart uvicorn.
- **404 on new routes**: Server running old code. Kill and restart.
- **Tests failing**: Check PYTHONPATH, run from repo root.
- **DB errors**: Delete `data/agent_sanad.db` to reset.

## Security Notes

- No real data in fixtures (APP-*, AGR-*, masked names)
- No credentials stored
- SQLite is demo-only (not production)
- All connectors are mock

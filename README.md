# Agent Sanad

Agentera — MOEI × 42 Abu Dhabi Hackathon · Sheikh Zayed Housing Programme.

Agent Sanad is a governed casework agent for housing-loan **arrears
rescheduling**: a deterministic policy engine validated against 1,960 real
historical decisions, contract-true integration adapters, a full
citizen application flow (UAE PASS mock → application → recommendation), and an
officer workbench with an evidence-linked audit trail.

> **Doctrine:** the LLM reads and explains · deterministic code decides ·
> a human officer owns exceptions.

## Quick start (one command)

```powershell
# Windows
.\run.ps1
```
```bash
# macOS / Linux / Git-Bash
./run.sh
```

Then open **http://127.0.0.1:8000/** — you land on the branded service page.

> If the page shows a yellow "older build" banner, an old server process is
> still bound to port 8000. The launcher refuses to double-start; stop the old
> process and re-run.

First-time setup:

```powershell
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
$env:PYTHONPATH="."
python -B -m pytest tests\ -q -p no:cacheprovider    # full suite must be green
```

## The app

| Surface | What you see |
|---|---|
| **Beneficiary flow** | Landing → UAE PASS verification (mock) → application stepper (Programme data → financial details → documents → review) → animated agent processing → plain-language result |
| **Officer portal** (`#/officer`) | Case queue (13 samples + your last submitted application), official Section-8 recommendation, 6-section evidence trace, raw audit feed, benchmark panel, approve/adjust/escalate |
| **Custom applications** | Enter any values — they are Pydantic-validated, mapped to a synthetic case, and decided by the same engine. The demo is not hard-coded. |

### API (14 endpoints)

`GET /healthz` · `GET /` · `GET /architecture` · `GET /cases` · `GET /benchmark`
· `GET /cases/{id}` · `GET /cases/{id}/audit` · `POST /demo/run/{id}` ·
`POST /demo/run-graph/{id}` · `GET /demo/compare/{id}` ·
`POST /cases/{id}/decide` · `POST /cases/{id}/officer-action` ·
`POST /applications/mock` · `POST /applications/mock/decide`

All errors return `{error_code, message, path, app_version}`.

### Tooling (addendum, governed)

- **LangGraph** orchestrates the same workflow as the plain route; the
  deterministic engine still makes every financial decision. Equivalence on
  all 13 cases is test-enforced; `GET /demo/compare/{id}` proves it live.
  Toggle per-case in the officer portal, or set `SANAD_ORCHESTRATOR=graph`
  (plain stays the default; graph failures fall back to plain automatically).
- **Tracing is off by default** (`LANGSMITH_TRACING=false`). If enabled, every
  payload passes mandatory PII redaction (allow-list + Emirates-ID/Arabic/
  document-text scrubbing); disabling redaction makes the adapter refuse to
  emit. Verify: `python -B -m pytest tests/test_observability.py -q`.
- LlamaIndex / LangChain / CrewAI / AutoGen / Semantic Kernel / DSPy / MCP
  servers: intentionally **not** implemented — rationale in
  [docs/TOOLING_IMPLEMENTATION_SUMMARY.md](docs/TOOLING_IMPLEMENTATION_SUMMARY.md).

## Benchmark (honest claim)

```bash
# Workbook contains real beneficiary data — benchmark/data is gitignored.
python benchmark/run.py benchmark/data/RescheduleArrears.xlsx
```

> Agent Sanad matches the officers' rescheduling **path 94.6%** of the time on
> held-out 2025 cases and every UPDATE plan it sets is within the 20% cap. It
> does **not** claim exact reproduction of every premium or duration.

## Guardrails

Protected files — do not modify without rerunning the full suite and manually
reviewing the 20% cap, period logic, and rule IDs:
`backend/policy/engine.py` · `backend/policy/period.py` ·
`backend/policy/config.yaml` · `backend/policy/rules.py` ·
`benchmark/replay.py` · `benchmark/score.py`

## Documentation

- [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) — system design + IBM 7-skills mapping
- [docs/PRODUCTION_READINESS.md](docs/PRODUCTION_READINESS.md) — honest pilot-gap assessment
- [docs/V1_1_COMPLETION_SUMMARY.md](docs/V1_1_COMPLETION_SUMMARY.md) — full v1.1 delivery record
- [docs/DEMO_SCRIPTS.md](docs/DEMO_SCRIPTS.md) · [docs/JUDGE_QA.md](docs/JUDGE_QA.md)
- [CODING_HANDOFF.md](CODING_HANDOFF.md) — for the next engineer

## Layout

- `backend/` — schemas, policy engine (protected), adapters, applications, extraction, audit, API
- `benchmark/` — normalize / replay / score / run (protected scoring)
- `frontend/index.html` — the multi-screen application (single offline file)
- `tests/` — policy, API-contract, application-flow, and governance suites
- `seeds/` — human-facing case index

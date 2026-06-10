# Agent Sanad — AGENTS.md

**Do not summon subagents.** No delegates, no explore/librarian/oracle agents, no background tasks. Gather context yourself with direct tools (grep, read, glob) and make changes directly. This repo is compact enough that subagents add overhead and lose context.

FastAPI hackathon MVP: deterministic policy engine for Sheikh Zayed Housing Programme arrears rescheduling. 13 demo cases, fixture-backed offline mode.

**125 tests passing** across 9 test files.

## Core doctrine

> LLM reads and explains. Deterministic code decides. Human owns the exception.

SQLite persistence for custom apps and officer actions. Single-file frontend served by FastAPI. LangGraph is optional (import-guarded, falls back to plain orchestrator). Arabic/English i18n with language toggle.

## Run & test

```powershell
# Launch (port 8000; refuses if port is already bound)
.\run.ps1                                          # or ./run.sh

# Manual
$env:PYTHONPATH="."; uvicorn backend.app:app --host 127.0.0.1 --port 8000

# Full test suite (125 expected)
$env:PYTHONPATH="."; python -B -m pytest tests\ -q -p no:cacheprovider

# Single test
$env:PYTHONPATH="."; python -B -m pytest tests\test_policy.py::test_golden_update_approve -q -p no:cacheprovider

# Observability subset
$env:PYTHONPATH="."; python -B -m pytest tests\test_observability.py -q -p no:cacheprovider

# Check live health
Invoke-RestMethod http://127.0.0.1:8000/healthz    # ok=true, mock_mode=true, app_version=1.1.0, orchestrator=plain
```

## Env flags (`.env.example`)

| Flag | Default | Note |
|---|---|---|
| `LOCAL_MOCK_MODE` | `true` | Demo-safe offline mode |
| `SANAD_LIVE_EXTRACTION` | `0` | Set `1` to parse synthetic GOLDEN cert from disk |
| `SANAD_ORCHESTRATOR` | `plain` | `plain` / `graph` |
| `LANGSMITH_TRACING` | `false` | Off by default |
| `TRACE_REDACTION` | `true` | Refuses to emit if tracing on + redaction off |
| `SANAD_LLM` | `0` | Optional LLM reasoning (cached fallback always present) |
| `SANAD_DB_PATH` | `data/agent_sanad.db` | Override SQLite database path |

## API endpoints (17 routes)

| Method | Path | Purpose |
|---|---|---|
| GET | `/healthz` | Liveness + mock_mode + policy_version |
| GET | `/` | Single-page demo UI |
| GET | `/architecture` | IBM 7-skills mapping (USP surface) |
| GET | `/cases` | List 13 seeded case IDs + picker metadata |
| GET | `/benchmark` | Benchmark metrics + honest claim |
| GET | `/cases/{id}` | Assembled Case snapshot (no policy run) |
| GET | `/cases/{id}/audit` | Audit trail for the case |
| POST | `/demo/run/{id}` | Main demo path — full retrieve→decide→report |
| POST | `/demo/run-graph/{id}` | LangGraph route (falls back to plain) |
| GET | `/demo/compare/{id}` | Plain vs Graph equivalence proof |
| POST | `/cases/{id}/decide` | Same as /demo/run (v1.1 route name) |
| POST | `/cases/{id}/officer-action` | Human-in-the-loop: approve/adjust/escalate |
| POST | `/applications/mock` | Validate + assemble custom application (no decide) |
| POST | `/applications/mock/decide` | Full custom application flow |
| GET | `/applications` | List persisted custom applications |
| GET | `/applications/{id}` | Retrieve persisted application + report + audit |
| GET | `/officer-actions` | List persisted officer actions |

## Architecture

```
backend/
  app.py              — FastAPI app (17 routes, JSON logger, error envelope, store integration)
  store.py            — SQLite persistence layer (applications, recommendations, audit, officer actions)
  adapters/__init__.py — 5 mock adapters (UAE PASS, Loan, Arrears, Salary Verify, Doc Validate) + 13 fixtures
  applications.py     — Custom application form → synthetic Case
  schemas.py          — Pydantic v2 schemas (extra="forbid" on ALL payloads)
  policy/engine.py    — THE deterministic decide() money path. 3 gates + 2-path decision
  policy/config.yaml  — Externalized policy config (20% cap, thresholds)
  policy/rules.py     — 14 rule IDs (ACTIVE-01, ELIG-01, DOC-01/02, INC-01, OBL-01, FAM-01, HARD-01/02, CAP-01/02, AFF-01, TEN-01, RSK-01, OFF-01)
  policy/period.py    — Rule 2 period compliance helpers
  audit.py            — Append-only audit trail with 8-state machine transitions
  confidence.py       — Confidence band + risk level scoring
  extraction.py       — Salary certificate parsing with cached fallback
  reasoning.py        — Deterministic cached reasoning text (optional LLM hook)
  graph/              — Optional LangGraph wrapper (import-guarded, never required)
  observability/      — PII redaction + LangSmith-ready adapter (refuse-to-emit interlock)
frontend/
  index.html          — Single-file hash-routed SPA (~1576 lines, vanilla HTML/CSS/JS, zero deps)
  i18n.json           — Arabic/English translation strings (95 keys)
tests/                — 9 test files (125 passing)
  test_policy.py      — 13 case assertions + endpoint contract tests
  test_demo_api.py    — API contract + CLIENT_BUILD handshake test
  test_governance.py  — No workbook tracked, no PII, risky cases routed to human
  test_graph_equivalence.py  — Plain vs LangGraph same output for all 13 cases
  test_observability.py      — Tracing off by default, redaction safety
  test_applications.py       — Custom application flow
  test_benchmark_replay.py   — Benchmark replay logic (18 tests, 7 scenarios)
  test_store.py              — SQLite persistence (12 tests)
  test_security.py           — Security, PII, XSS, error envelope (11 tests)
benchmark/            — Historical replay + scoring (94.6% path-match on held-out 2025)
seeds/cases_v1.json   — Human-facing demo case index (13 cases)
```

## Critical constraints

- **`APP_VERSION` in `app.py` MUST equal `CLIENT_BUILD` in `index.html`** — a test enforces this. Bump both together on every release.
- **Never commit `RescheduleArrears*.xlsx`** — gitignored, contains real beneficiary data.
- **Never change `backend/policy/engine.py` without**: full test suite re-run + manual review of GOLDEN new EMI (~AED 3,342) and additional months (120), NOHEAD stays TRANSFER_ARREARS, ACTIVE rejects before computation, CONTRA keeps RSK-01+INC-01, and all 13 case outputs.
- Fixtures use synthetic identifiers only (APP-\*, AGR-\*, masked names). No Emirates-ID numbers, no real personal data.
- Port 8000 must be free at launch — stale servers serve new UI with old API routes. The launchers refuse to start if bound.
- LangGraph is optional and tested for output equivalence. The demo must never depend on it.
- The LLM (if used) is read-only: explains results, never decides numbers. Template fallback on any error.
- All API errors follow `{error_code, message, path, app_version}` envelope.
- Allocation rounding: premium = floor, months = ceil (configurable in config.yaml).
- The 20% salary cap is the hard policy rule. Monthly deduction must not exceed it. Never relax this.
- **SQLite persistence** is in `backend/store.py`. DB lives at `data/agent_sanad.db` (gitignored). Gracefully degrades if DB can't be created. Three new endpoints: `GET /applications`, `GET /applications/{id}`, `GET /officer-actions`.
- **Arabic localization** is in `frontend/i18n.json` (95 keys). Language toggle in the top bar loads translations client-side. RTL direction support. Key static text and beneficiary result strings are translated.
- **New test files**: `test_benchmark_replay.py` (18 tests), `test_store.py` (12), `test_security.py` (11). Run full suite to verify 125 tests pass.

## 13 demo cases

All fixture values live in `backend/adapters/__init__.py`. Each fixture was hand-traced through `decide()` before its test was written. Expected recommendations:

| Case | Recommendation | Path | Key rules |
|---|---|---|---|
| GOLDEN | Approve | UPDATE_INSTALLMENT | CAP-02, AFF-01 |
| NOHEAD | Refer | TRANSFER_ARREARS | HARD-01, CAP-01 |
| MISSING | Request docs | NONE | DOC-01 |
| ACTIVE | Reject | NONE | ACTIVE-01 |
| CONTRA | Refer | TRANSFER_ARREARS | INC-01, RSK-01 |
| HIGH_OBLIGATIONS | Refer | UPDATE_INSTALLMENT | OBL-01 |
| PERIOD_BREACH | Refer | UPDATE_INSTALLMENT | TEN-01 |
| HARDSHIP | Approve | TRANSFER_ARREARS | HARD-02 |
| ZERO_OR_MISSING_INCOME | Request docs | NONE | DOC-02 |
| LOW_INCOME_PER_MEMBER | Approve | UPDATE_INSTALLMENT | FAM-01 |
| UNVERIFIED_HARDSHIP | Refer | TRANSFER_ARREARS | HARD-01 |
| PROMPT_INJECTION_ONLY | Approve | UPDATE_INSTALLMENT | RSK-01 (logged, policy unchanged) |
| HIGH_CAPACITY_UPDATE | Approve | UPDATE_INSTALLMENT | CAP-02, AFF-01 |

## Policy engine flow

1. **Gate 1** — ACTIVE-01: if active request exists → Reject
2. **Gate 2** — ELIG-01: if not UAE national → Refer
3. **Gate 3** — DOC-01: if salary certificate missing → Request docs
4. **RSK-01**: injection flags logged as content only, engine continues
5. **DOC-02**: if verified income is None → Request docs
6. **Two-path decision**: headroom = (20% × salary) − current EMI
   - headroom <= `min_headroom_aed` (50) → TRANSFER_ARREARS
   - headroom > 50 → UPDATE_INSTALLMENT (raise installment, clear arrears)
7. **Risk signals**: INC-01 (contradiction → immediate refer), OBL-01 (obligations > 60% → refer), FAM-01 (low per-member income → lowers confidence only)
8. **Hardship**: HARD-01 (unemployed/no income) / HARD-02 (verified temporary circumstance)
9. **Period check** (Rule 2): proposed schedule must not exceed original loan term → TEN-01

## Policy config (`backend/policy/config.yaml`)

Checks the config file on startup via PyYAML (falls back to defaults silently). All prototype thresholds that need MOEI validation are in this single file. Safe to adjust thresholds without touching engine.py.

## Test writing conventions

- Every fixture case has an exact expected output hand-traced through `decide()` before its test is written.
- Policy tests use direct `decide()` calls (no HTTP).
- Endpoint tests use `TestClient(app)` to guard adapter+endpoint wiring.
- All 13 cases must route through `POST /demo/run/{id}` with correct recommendations.
- Governance tests enforce: no `.xlsx` tracked, no PII in fixtures, risky cases never auto-approve, referred cases carry fired rules.
- Graph equivalence tests assert same report fields (recommendation, path, fired_rules, 20%/period compliance) for every case. Never relax — fix the wrapper.
- `LOCAL_MOCK_MODE=true` is the default test environment.

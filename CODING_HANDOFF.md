# Agent Sanad Coding Handoff

Last updated: 2026-06-09 (v1.1 functional expansion)

This file is a working handoff for continuing Agent Sanad in another coding tool such as Claude Code. Read this before changing code.

## Repository State

- Local path: `C:\Hussain new\Agent-Sanad`
- GitHub repo: `https://github.com/Hussain800/Agent-Sanad`
- Active branch: `v1.1-functional-expansion` (NOT merged; awaiting manual QA per the v1.1 brief)
- Stable trunk: `main` (clean v0.8 — the LangGraph tooling branch was deleted)
- Tooling addendum (LangGraph / LangSmith / LlamaIndex etc.) is **paused** — see `Agent_Sanad_PRD_v1.1_Tooling_Addendum.md` for the future plan.
- Working tree at handoff: clean except intentionally ignored local files:
  - `.claude/`
  - `RescheduleArrears (1).xlsx`

The real workbook contains beneficiary data and must not be committed. `.gitignore` excludes `RescheduleArrears*.xlsx`, `RescheduleArrears*.xls`, and `benchmark/data/*.xlsx`.

## Product Context

Agent Sanad is the Agentera / MOEI Track 1 prototype for rescheduling Sheikh Zayed Housing Programme housing-loan arrears.

The MVP follows `Agent_Sanad_PRD_v0.8_MVP.md`, with `Agent_Sanad_PRD_v1.1.md` as the north-star PRD.

Core framing:

- LLM/extraction can read and explain.
- Deterministic Python code decides the financial recommendation.
- Human officers handle exceptions.
- The demo must run offline/cached.

Hard policy rules:

- Monthly deduction must not exceed 20% of beneficiary income.
- Repayment schedule must not exceed the original approved loan period.
- Existing active request may auto-reject.

## What Has Been Built

### Backend Spine

- `backend/policy/engine.py`
  - Deterministic `decide()` money path.
  - Handles active request, eligibility, document completeness, 20% headroom math, hardship/no-headroom path, risk flags, period compliance, and recommendation.
  - Do not modify without re-running all tests and reviewing the 20% cap logic manually.

- `backend/policy/period.py`
  - Rule 2 period compliance helpers.

- `backend/policy/rules.py`
  - Rule ID catalog and `load_policy()`.

- `backend/policy/config.yaml`
  - Externalized policy configuration.

- `backend/schemas.py`
  - Pydantic v2 schemas, including official Section 8 `RecommendationReport`.

### Mock Adapters And Cases

- `backend/adapters/__init__.py`
  - Fixture-backed UAE PASS, loan, arrears, document validation, salary extraction, and salary verification flow.
  - Assembles `Case` objects and append-only audit logs.

- Five v0.8 demo cases:
  - `GOLDEN`: approve, `UPDATE_INSTALLMENT`
  - `NOHEAD`: refer, `TRANSFER_ARREARS`
  - `MISSING`: request documents
  - `ACTIVE`: reject at active-request gate
  - `CONTRA`: refer for contradiction + injected text
- Three v1.1 functional-expansion cases:
  - `HIGH_OBLIGATIONS`: refer (OBL-01); plan computed inside the cap
  - `PERIOD_BREACH`: refer (TEN-01); period compliance Fail
  - `HARDSHIP`: approve via TRANSFER_ARREARS; HARD-02 branch
- Five v1.1 completion cases (on `v1.1-functional-expansion`):
  - `ZERO_OR_MISSING_INCOME`: request documents (DOC-02); cert received but income unverifiable
  - `LOW_INCOME_PER_MEMBER`: approve (FAM-01 lowers confidence); plan still within cap
  - `UNVERIFIED_HARDSHIP`: refer (HARD-01 + unverified); arrears transferred
  - `PROMPT_INJECTION_ONLY`: approve with RSK-01 logged; policy unchanged by injected text
  - `HIGH_CAPACITY_UPDATE`: approve via UPDATE; engine uses real headroom (AED 4,000)
- **13 demo cases total.** Each expected output is hand-traced through `decide()` before its test is written. See `docs/V1_1_COMPLETION_SUMMARY.md`.

### v1.1 state machine + safe endpoints

- `backend/audit.py` — `AuditEvent` now carries optional `state_from`/`state_to`; `AuditLog.transition()` helper. The **full canonical 8-state journey** (Submitted → IdentityLinked → DataRetrieved → Extracting → Validating → PolicyRun → terminal → Closed) is emitted across `build_case` + `app.py`. The UI timeline is reconstructed from these real audit events.
- Endpoints (do not replace `/demo/run/{case_id}`, the main demo path): `GET /benchmark`, `GET /cases/{id}`, `GET /cases/{id}/audit`, `POST /cases/{id}/decide` (same envelope as `/demo/run`), `POST /cases/{id}/officer-action` (stateless `OfficerAction` validation + OFF-01 audit; adjust/escalate require a reason code).
- `backend/schemas.py` — added `OfficerAction` (v1.1 §6) with the reason-code validator.
- Audit drawer has 6 trace sections: state timeline, adapter source map, rule trace, calculation trace, period trace, security trace, plus the raw audit feed.
- NONE-path cases (gated/rejected/incomplete) render "Not generated" / "Not applicable" in the Section-8 table — no misleading zeroes.
- Tests: **44 passing** across `tests/test_policy.py`, `tests/test_demo_api.py`, `tests/test_governance.py`.

### Live/Cached Salary Extraction

- `backend/extraction.py`
  - Offline-safe salary-certificate extraction layer.
  - Default mode is cached fixture value.
  - Set `SANAD_LIVE_EXTRACTION=1` to parse the synthetic golden-case salary certificate from disk.
  - Any extraction failure falls back to cached fixture value.

- `backend/fixtures/salary_certificates/GOLDEN.txt`
  - Synthetic demo salary certificate.
  - Contains no real beneficiary identifiers.

### API

- `backend/app.py`
  - FastAPI app.
  - `GET /healthz`
  - `GET /cases`
  - `POST /demo/run/{case_id}`
  - Serves `frontend/index.html` at `/`.
  - `/demo/run` returns:
    - `case`
    - `report`
    - `audit`
    - `impact`
  - `impact` includes benchmark metrics and `mock_mode`.

### Frontend

- `frontend/index.html`
  - Single-file federal-service style demo UI.
  - Case selector.
  - Distinct exception-state banners.
  - Thin beneficiary journey.
  - Officer Section 8 recommendation output table.
  - 20%/period/risk/confidence chips.
  - Retrieved/extracted facts panel.
  - Extraction source display.
  - "Why this plan?" audit drawer.
  - Zero-bureaucracy benchmark panel.
  - Loading state, disabled controls while running, runtime error banner, and retry button.
  - Dynamic backend strings are escaped before rendering into HTML.

### Reasoning

- `backend/reasoning.py`
  - Deterministic cached reasoning for all five demo cases.
  - Keeps demo offline-safe and stable.
  - Optional `SANAD_LLM=1` hook exists but is intentionally not relied on.

### Benchmark

- `benchmark/normalize.py`
- `benchmark/replay.py`
- `benchmark/score.py`
- `benchmark/run.py`

Verified benchmark claim using the local workbook:

- Held-out 2025 `n=522`
- Path-match accuracy: `94.6%`
- UPDATE 20% compliance: `100%`
- Premium deviation median: `AED 557`
- Months deviation median: `10`

Important claim wording:

> Agent Sanad matches the officers' rescheduling path 94.6% of the time on held-out 2025 cases and every UPDATE plan it sets is within the 20% cap. It does not claim exact reproduction of every premium or duration.

## Tests And Verification

Current test files:

- `tests/test_policy.py`
  - Policy regression tests for the five demo cases.
  - Cached extraction default test.
  - Live extraction switch test.

- `tests/test_demo_api.py`
  - FastAPI contract tests.
  - Static UI smoke checks.
  - Benchmark block and audit event checks.

Latest verification performed:

```text
python -B -m pytest tests\ -q -p no:cacheprovider
11 passed
```

Live extraction check:

```text
SANAD_LIVE_EXTRACTION=1
GOLDEN parsed AED 16,711 from GOLDEN.txt
```

HTTP smoke check:

```text
GET /healthz passed
GET / passed static UI checks
POST /demo/run/GOLDEN passed
POST /demo/run/NOHEAD passed
POST /demo/run/MISSING passed
POST /demo/run/ACTIVE passed
POST /demo/run/CONTRA passed
```

Benchmark check:

```text
python -B benchmark\run.py "RescheduleArrears (1).xlsx"
held_out_2025.path_match_accuracy = 0.946
held_out_2025.twenty_pct_compliance_update_plans = 1.0
```

## Running The App

Recommended local demo mode with live golden extraction:

```powershell
$env:PYTHONPATH="."
$env:LOCAL_MOCK_MODE="true"
$env:SANAD_LIVE_EXTRACTION="1"
python -B -m uvicorn backend.app:app --host 127.0.0.1 --port 8000
```

Open:

```text
http://127.0.0.1:8000/
```

Current server at handoff was running as:

```text
process id 37560
python
http://127.0.0.1:8000/
```

If the process is gone, restart with the command above.

## Environment Flags

`.env.example` includes:

```text
LOCAL_MOCK_MODE=true
DETERMINISTIC_SEED=42
DISABLE_EXTERNAL_WRITES=true
SANAD_LLM=0
SANAD_LIVE_EXTRACTION=0
SANAD_CERT_PATH=
```

Use `SANAD_LIVE_EXTRACTION=1` for the judging/demo run if you want the audit drawer to show live parsing of the synthetic golden salary certificate.

## Git History From This Work

Recent commits:

- `10f0140 Complete final demo hardening`
  - Added live salary extraction + fallback.
  - Added synthetic golden certificate.
  - Hardened UI runtime behavior.
  - Added API/demo contract tests.
  - Updated docs/env.

- `3db141a Polish demo exception flows`
  - Made exception cases visually distinct.
  - Added beneficiary journey.
  - Added cached reasoning and extraction/source UI foundations.

- `081d5e8 Merge existing GitHub history`
  - Preserved old GitHub README history and merged local MVP spine.

- `b3b2ccd Initial Agent Sanad MVP spine`
  - Initial backend/frontend/benchmark/test scaffold.

## Known Tooling Blocker

The Codex in-app Browser plugin blocked `http://127.0.0.1:8000/` with a local-browser security policy. Because of that, visual QA was completed through local HTTP/static/API verification rather than Browser screenshots.

Do not attempt to bypass that policy from Codex. If using another tool, do a normal manual browser pass:

1. Open `http://127.0.0.1:8000/`.
2. Click all five case buttons.
3. Confirm the case title, recommendation banner, beneficiary journey, Section 8 table, extraction source, audit drawer, and benchmark panel update.
4. Check one mobile viewport.
5. Record screenshots/video for Block 6.

## Remaining Non-Code PRD Work

All core coding/app items from the v0.8 MVP are complete.

Remaining work is Block 6/hackathon packaging:

- Manual visual QA in a browser.
- 8 labeled screenshots.
- 1080p backup screen recording.
- 90-second and 3-minute demo script rehearsal.
- Optional slide deck / single benchmark slide.
- Rehearse the live sequence at least 5 times.

## Guardrails For The Next Coding Tool

- Do not commit `RescheduleArrears (1).xlsx`.
- Do not display raw workbook IDs, applicant names, or Arabic narratives.
- Do not rewrite `backend/policy/engine.py` unless absolutely necessary.
- If `engine.py` changes, run all tests and re-check:
  - `GOLDEN` new EMI around AED 3,342
  - `GOLDEN` additional months `120`
  - `NOHEAD` remains `TRANSFER_ARREARS`
  - `ACTIVE` rejects before computation
  - `CONTRA` keeps `RSK-01` and `INC-01`
- Benchmark claims must stay honest: path-match and compliant terms, not exact reproduction.
- Keep the demo offline-safe. Live extraction/LLM must never be required for a successful run.

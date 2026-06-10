# Agent Sanad

Agent Sanad is a governed decision-support agent for Sheikh Zayed Housing
Programme arrears rescheduling cases. It validates applicant inputs, retrieves
mock Programme data, applies the official policy constraints, and produces an
officer-ready Section 8 recommendation with a traceable audit trail.

The core design rule is simple:

> LLMs and orchestration frameworks may explain or coordinate. Deterministic
> policy code makes the financial decision. A human officer owns exceptions.

## What Judges Can Try

- Beneficiary journey: UAE PASS mock verification, application stepper,
  document status, agent processing timeline, and plain-language result.
- Officer portal: case queue, official Section 8 recommendation, policy chips,
  evidence trace, audit feed, benchmark panel, and officer action controls.
- Custom applications: enter new values and submit them through the same
  Pydantic schemas and policy engine used by the seeded demo cases.
- LangGraph comparison: run the optional graph route and prove that it returns
  the same recommendation report as the plain deterministic route.

The app is intentionally offline-first. UAE PASS, Programme systems, salary
verification, document validation, and loan/arrears retrieval are represented by
contract-shaped mock adapters so the demo can run reliably without external
services or beneficiary data.

## Quick Start

```powershell
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
.\run.ps1
```

Open:

```text
http://127.0.0.1:8000/
```

For macOS, Linux, or Git Bash:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
./run.sh
```

The launchers set safe demo defaults:

```text
PYTHONPATH=.
LOCAL_MOCK_MODE=true
SANAD_LIVE_EXTRACTION=1
LANGSMITH_TRACING=false
```

If port 8000 is already occupied, the launcher refuses to start so an older
server cannot silently serve stale routes.

## Verification

Run the full test suite:

```powershell
$env:PYTHONPATH="."
python -B -m pytest tests\ -q -p no:cacheprovider
```

Expected result on the verified main build:

```text
84 passed
```

Run the dedicated observability safety tests:

```powershell
python -B -m pytest tests\test_observability.py -q -p no:cacheprovider
```

Expected result:

```text
6 passed
```

Check the live health endpoint:

```powershell
Invoke-RestMethod http://127.0.0.1:8000/healthz
```

Expected properties include:

```text
ok=true
mock_mode=true
app_version=1.1.0
orchestrator=plain
```

## API Surface

The demo exposes 14 routes:

```text
GET  /healthz
GET  /
GET  /architecture
GET  /cases
GET  /benchmark
GET  /cases/{id}
GET  /cases/{id}/audit
GET  /demo/compare/{id}
POST /demo/run/{id}
POST /demo/run-graph/{id}
POST /cases/{id}/decide
POST /cases/{id}/officer-action
POST /applications/mock
POST /applications/mock/decide
```

All API errors use the same contract:

```json
{
  "error_code": "VALIDATION_ERROR",
  "message": "Human-readable error",
  "path": "/request/path",
  "app_version": "1.1.0"
}
```

## Demo Cases

The repository includes 13 synthetic cases that exercise the policy matrix and
governance gates:

```text
GOLDEN
NOHEAD
MISSING
ACTIVE
CONTRA
HIGH_OBLIGATIONS
PERIOD_BREACH
HARDSHIP
ZERO_OR_MISSING_INCOME
LOW_INCOME_PER_MEMBER
UNVERIFIED_HARDSHIP
PROMPT_INJECTION_ONLY
HIGH_CAPACITY_UPDATE
```

They cover approval, document requests, active-request rejection, hardship
handling, high-obligation referral, period-breach referral, zero-income
validation, low-income-per-family-member confidence reduction, and prompt
injection logging without policy override.

## Policy And Governance

The protected policy path is:

```text
backend/policy/engine.py
backend/policy/period.py
backend/policy/config.yaml
backend/policy/rules.py
benchmark/replay.py
benchmark/score.py
```

These files should not change without rerunning the full test suite and manually
reviewing the 20 percent cap, period compliance, fired rule IDs, and benchmark
wording.

Key safeguards:

- Rule gates are deterministic and test-covered.
- The 20 percent salary cap is enforced in the policy engine.
- Proposed schedules must not exceed the original loan term.
- Active existing rescheduling requests are rejected.
- Missing or unverifiable documents request documents instead of deciding.
- Risky or contradictory cases route to a human officer.
- Prompt injection text is logged as risk but cannot alter the policy result.
- LangGraph is optional and equivalence-tested against the plain route.
- LangSmith tracing is off by default and refuses to emit if redaction is
  disabled while tracing is enabled.

## Benchmark

The historical benchmark runner is included, but the real workbook is never
committed:

```powershell
python benchmark/run.py benchmark/data/RescheduleArrears.xlsx
```

The project claim is intentionally narrow:

```text
Agent Sanad matches the officer rescheduling path 94.6 percent of the time on
the held-out 2025 workbook, and every generated UPDATE plan respects the 20
percent cap.
```

The app does not claim exact reproduction of every historical premium or
duration.

## Repository Layout

```text
backend/       FastAPI app, schemas, adapters, extraction, audit, policy calls
backend/policy Deterministic decision engine and policy configuration
backend/graph  Optional LangGraph wrapper and equivalence helpers
benchmark/     Historical replay, normalization, and scoring scripts
frontend/      Single-file offline UI served by FastAPI
tests/         Policy, API, application-flow, governance, graph, tracing tests
docs/          Architecture, readiness, demo scripts, judge Q&A, screenshots
seeds/         Human-facing demo case index
```

## Useful Documentation

- `docs/ARCHITECTURE.md` - system design and IBM skills mapping.
- `docs/PRODUCTION_READINESS.md` - pilot gaps and production-readiness truth.
- `docs/TOOLING_IMPLEMENTATION_SUMMARY.md` - LangGraph/LangSmith addendum.
- `docs/V1_1_COMPLETION_SUMMARY.md` - v1.1 delivery record.
- `docs/DEMO_SCRIPTS.md` - 3-minute and backup demo scripts.
- `docs/JUDGE_QA.md` - expected judge questions and answers.
- `docs/SCREENSHOTS.md` - required demo capture checklist.
- `CODING_HANDOFF.md` - handoff notes for another coding agent.

## Production Boundary

This is a hackathon MVP, not a live government production deployment. The
financial decision logic, schemas, test coverage, error contracts, audit trail,
and governance posture are production-shaped. Real deployment still requires
approved UAE PASS integration, authenticated Programme-system adapters,
persistent storage, secrets management, infrastructure, compliance review, and
operational monitoring.

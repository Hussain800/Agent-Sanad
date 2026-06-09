# Agent Sanad — MVP backend spine (v0.8)

Deterministic arrears-rescheduling engine + 5 mock adapters + one demo endpoint + benchmark.
The money path is tested and green; the benchmark reproduces 94.6% path-match on held-out 2025.

## Run
```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
PYTHONPATH=. python -m pytest tests/ -q          # 6 passing — money path
PYTHONPATH=. uvicorn backend.app:app --reload    # open http://127.0.0.1:8000
```
Open `/` for the demo UI (case selector → recommendation card → "Why this plan?" → impact panel).
Endpoint: `POST /demo/run/{case_id}` where case_id ∈ GOLDEN, NOHEAD, MISSING, ACTIVE, CONTRA.

## Benchmark (already validated)
```bash
# put the workbook at benchmark/data/RescheduleArrears.xlsx (gitignored — real data)
PYTHONPATH=. python benchmark/run.py benchmark/data/RescheduleArrears.xlsx
```
→ held-out 2025: path-match 94.6%, 20% compliance 100% (UPDATE), premium dev AED 557, months dev 10.

## What to build next (Claude Code), per the PRD
Polish the frontend, add loading/exception styling, wire the optional live salary-cert extraction
(golden case only, cached fallback). DO NOT change `backend/policy/engine.py` without re-running tests.
You personally review: decide(), the 20% cap, period.py, rule IDs, recommendation wording.

## Layout
backend/ (schemas, policy/engine+period+rules+config, adapters, app, confidence, reasoning, audit)
benchmark/ (normalize, replay, score, run)  ·  frontend/index.html  ·  tests/test_policy.py

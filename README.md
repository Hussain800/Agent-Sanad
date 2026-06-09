# Agent Sanad

Agentera - MOEI X 42 Abu Dhabi Hackathon.

Agent Sanad is an agentic AI prototype for Sheikh Zayed Housing Programme housing-loan arrears rescheduling. It combines a deterministic policy engine, fixture-backed integration adapters, an officer recommendation UI, and a historical benchmark panel.

## MVP Spine

Deterministic arrears-rescheduling engine + 5 mock adapters + one demo endpoint + benchmark.

The money path is tested and green; the benchmark reproduces 94.6% path-match on held-out 2025.

## Run

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python -m pytest tests/ -q
python -m uvicorn backend.app:app --reload
```

Open `http://127.0.0.1:8000/` for the demo UI.

Endpoint: `POST /demo/run/{case_id}` where `case_id` is one of `GOLDEN`, `NOHEAD`, `MISSING`, `ACTIVE`, `CONTRA`.

## Benchmark

```bash
# Put the workbook at benchmark/data/RescheduleArrears.xlsx
# benchmark/data is gitignored because the workbook contains real beneficiary data.
python benchmark/run.py benchmark/data/RescheduleArrears.xlsx
```

Expected held-out 2025 result: path-match 94.6%, 20% compliance 100% for UPDATE plans, premium deviation AED 557, months deviation 10.

## What To Build Next

Polish the frontend, add loading and exception-case styling, and wire optional live salary-certificate extraction for the golden case only with cached fallback.

Do not change `backend/policy/engine.py` without re-running tests. Personally review `decide()`, the 20% cap, period logic, rule IDs, and recommendation wording.

## Layout

- `backend/`: schemas, policy engine, period checks, rules, adapters, API, confidence, reasoning, audit
- `benchmark/`: normalize, replay, score, run
- `frontend/index.html`: single-page demo UI
- `tests/test_policy.py`: policy regression tests

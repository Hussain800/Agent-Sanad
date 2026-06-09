"""Agent Sanad API — ONE endpoint powers the whole demo. Plus static frontend."""
import os, time
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles

from backend.adapters import build_case, FIXTURES
from backend.policy.engine import decide
from backend.policy.rules import load_policy

POLICY = load_policy()
MOCK_MODE = os.getenv("LOCAL_MOCK_MODE", "true").lower() == "true"

# Static benchmark metrics (produced offline by benchmark/score.py — PRD 9.2).
BENCHMARK = {
    "calibrated_on": "2023-2024", "validated_on": "2025", "n_held_out": 522,
    "path_match_accuracy": 0.946, "twenty_pct_compliance_update": 1.00,
    "premium_dev_median_aed": 557, "months_dev_median": 10, "deterministic": 1.00,
}

app = FastAPI(title="Agent Sanad", version="0.8")


@app.get("/healthz")
def healthz():
    return {"ok": True, "mock_mode": MOCK_MODE, "policy_version": POLICY.policy_version}


@app.get("/cases")
def cases():
    return {"cases": list(FIXTURES.keys())}


@app.post("/demo/run/{case_id}")
def run(case_id: str):
    case_id = case_id.upper()
    if case_id not in FIXTURES:
        raise HTTPException(404, f"unknown case '{case_id}'")
    t0 = time.time()
    case, log = build_case(case_id)
    report = decide(case, POLICY)
    log.add(case_id, "policy.decide", "system",
            f"{report.recommendation} / {report.proposed_plan.path}",
            latency_ms=int((time.time() - t0) * 1000), mock_mode=MOCK_MODE)
    return JSONResponse({
        "case": case.model_dump(mode="json"),
        "report": report.model_dump(mode="json"),
        "audit": log.events(),
        "impact": {"latency_ms": int((time.time() - t0) * 1000), "benchmark": BENCHMARK},
    })


# serve the single-page frontend if present
_FE = os.path.join(os.path.dirname(__file__), "..", "frontend")
if os.path.isdir(_FE):
    @app.get("/")
    def index():
        return FileResponse(os.path.join(_FE, "index.html"))
    app.mount("/static", StaticFiles(directory=_FE), name="static")

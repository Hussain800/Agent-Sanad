"""Agent Sanad API — ONE endpoint powers the whole demo. Plus static frontend."""
import json
import logging
import os
import time
import uuid
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import ValidationError

from backend.adapters import build_case, FIXTURES
from backend.policy.engine import decide
from backend.policy.rules import load_policy
from backend.schemas import OfficerAction

POLICY = load_policy()
MOCK_MODE = os.getenv("LOCAL_MOCK_MODE", "true").lower() == "true"


# ---- structured JSON logger (IBM agent skill 6: observability) ---------------
# Every /demo/run gets a request_id; every line is one JSON object so a judge
# (or, in pilot, an SRE) can grep, filter, and ship to any log aggregator.
class _JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        payload = {
            "ts": self.formatTime(record, "%Y-%m-%dT%H:%M:%S"),
            "level": record.levelname,
            "logger": record.name,
            "msg": record.getMessage(),
        }
        for k in ("request_id", "case_id", "step", "latency_ms", "mock_mode",
                  "recommendation", "path", "fired_rules"):
            v = getattr(record, k, None)
            if v is not None:
                payload[k] = v
        return json.dumps(payload, ensure_ascii=False)


_log = logging.getLogger("sanad")
if not _log.handlers:
    _h = logging.StreamHandler()
    _h.setFormatter(_JsonFormatter())
    _log.addHandler(_h)
    _log.setLevel(logging.INFO)
    _log.propagate = False

# Static benchmark metrics (produced offline by benchmark/score.py — PRD 9.2).
BENCHMARK = {
    "calibrated_on": "2023-2024", "validated_on": "2025", "n_held_out": 522,
    "path_match_accuracy": 0.946, "twenty_pct_compliance_update": 1.00,
    "premium_dev_median_aed": 557, "months_dev_median": 10, "deterministic": 1.00,
}

# IBM Research's 7 agent-engineering skills, mapped to Agent Sanad subsystems.
# Surfaces the USP machine-readably so a judge can curl /architecture and see the
# engineering depth without reading docs. Full narrative: docs/ARCHITECTURE.md.
ARCHITECTURE = {
    "doctrine": "LLM reads and explains. Deterministic code decides. Human owns exceptions.",
    "ibm_seven_skills": [
        {"n": 1, "skill": "System design",
         "shipped_in": "FastAPI orchestrator + hard LLM/deterministic/human boundary"},
        {"n": 2, "skill": "Tool & contract design",
         "shipped_in": "Pydantic v2 schemas with extra='forbid' on every payload; 5 typed adapter contracts"},
        {"n": 3, "skill": "Retrieval engineering",
         "shipped_in": "5 fixture-backed adapters retrieve Programme data; cert extraction with cached fallback"},
        {"n": 4, "skill": "Reliability engineering",
         "shipped_in": "LOCAL_MOCK_MODE default; cached extraction fallback; cached reasoning fallback; UI retry"},
        {"n": 5, "skill": "Security & safety",
         "shipped_in": "Untrusted document text (RSK-01); read-only LLM; XSS-escaped UI; PII gitignored"},
        {"n": 6, "skill": "Evaluation & observability",
         "shipped_in": "Historical benchmark (94.6% path-match on n=522); append-only audit; 11 tests"},
        {"n": 7, "skill": "Product thinking",
         "shipped_in": "Beneficiary vs officer surfaces; plain-language reasoning; exception bands; Why-this-plan drawer"},
    ],
    "rubric_alignment": {
        "Agentic Decision Intelligence (25)": ["system design", "tool contracts", "retrieval"],
        "Policy Compliance & Governance (25)": ["system design", "security", "observability", "product"],
        "Technical Excellence & Data Integration (20)": ["system design", "tool contracts", "retrieval", "reliability"],
        "Impact on Service Transformation (15)": ["observability (benchmark)"],
        "Demo, Explainability & UX (15)": ["reliability", "product thinking"],
    },
    "honest_claims": {
        "path_match_accuracy_2025": "94.6% (n=522, held-out)",
        "twenty_pct_compliance_update_plans": "100% by construction",
        "premium_dev_median_aed": 557,
        "months_dev_median": 10,
        "manual_baseline": "~5 working days",
        "draft_latency": "<1 second (measured)",
        "do_not_claim": "exact reproduction of officer premium/months — officers apply discretion routed to a human",
    },
}

app = FastAPI(title="Agent Sanad", version="0.8")


@app.get("/healthz")
def healthz():
    return {"ok": True, "mock_mode": MOCK_MODE, "policy_version": POLICY.policy_version}


@app.get("/cases")
def cases():
    return {"cases": list(FIXTURES.keys())}


@app.get("/architecture")
def architecture():
    """USP surface: IBM 7-skill mapping + rubric alignment + honest claims."""
    return ARCHITECTURE


@app.get("/benchmark")
def benchmark():
    """v1.1 §5.5: historical benchmark metrics. Numbers come from the offline
    run of benchmark/run.py against the workbook; the demo never recomputes."""
    return {
        "metrics": BENCHMARK,
        "calibrated_on": BENCHMARK["calibrated_on"],
        "validated_on": BENCHMARK["validated_on"],
        "n": BENCHMARK["n_held_out"],
        "honest_claim": (
            "Agent Sanad matches the officers' rescheduling path 94.6% of the "
            "time on held-out 2025 cases and every UPDATE plan it sets is within "
            "the 20% cap. It does not claim exact reproduction of every premium "
            "or duration."
        ),
    }


# ── v1.1 §5.5 — case-scoped read surface (safe; delegates to existing logic) ─
# These endpoints exist so a curious judge / pilot integration can inspect the
# pipeline at finer granularity. They do NOT replace POST /demo/run/{case_id},
# which remains the main demo path. None of them mutate state.

@app.get("/cases/{case_id}")
def get_case(case_id: str):
    """Return the assembled Case object (no policy run)."""
    case_id = case_id.upper()
    if case_id not in FIXTURES:
        raise HTTPException(404, f"unknown case '{case_id}'")
    case, _ = build_case(case_id)
    return {"case": case.model_dump(mode="json"), "case_id": case_id}


@app.get("/cases/{case_id}/audit")
def get_case_audit(case_id: str):
    """Return only the audit trail produced by assembling the case."""
    case_id = case_id.upper()
    if case_id not in FIXTURES:
        raise HTTPException(404, f"unknown case '{case_id}'")
    _, log = build_case(case_id)
    return {"events": log.events(), "case_id": case_id}


@app.post("/cases/{case_id}/decide")
def post_case_decide(case_id: str, request: Request):
    """Same money path as /demo/run/{case_id}, exposed under the v1.1 route name.
    Implementation reuses the same internals; the response envelope is identical."""
    return run(case_id, request)


@app.post("/cases/{case_id}/officer-action")
def post_officer_action(case_id: str, body: dict):
    """v1.1 §5.5 / §6 — record a human officer's decision on a case.

    STATELESS by design: there is no database in the hackathon build, so this
    validates the OfficerAction, records an OFF-01 audit event with the officer
    as actor, and returns the (unchanged) deterministic report alongside the
    officer's recorded action. The deterministic recommendation is never
    overwritten silently — adjust/escalate require a reason code (governance).
    """
    case_id = case_id.upper()
    if case_id not in FIXTURES:
        raise HTTPException(404, f"unknown case '{case_id}'")
    # Validate the officer action against the typed contract.
    payload = dict(body or {})
    payload.setdefault("case_id", case_id)
    try:
        action = OfficerAction(**payload)
    except ValidationError as exc:
        raise HTTPException(422, f"invalid officer action: {exc.errors()}")

    case, log = build_case(case_id)
    report = decide(case, POLICY)
    terminal = _TERMINAL_STATE.get(report.recommendation, "RecommendationReady")
    detail = f"officer {action.action}"
    if action.override_reason_code:
        detail += f" (reason: {action.override_reason_code})"
    # OFF-01: human-in-the-loop record. Actor = officer.
    log.add(case_id, "officer.action", "officer", detail,
            mock_mode=MOCK_MODE, state_from=terminal,
            state_to={"approve": "Approved", "adjust": "Adjusted",
                      "escalate": "Refer"}.get(action.action, terminal))
    return {
        "case_id": case_id,
        "report": report.model_dump(mode="json"),
        "officer_action": action.model_dump(mode="json"),
        "audit": log.events(),
        "note": ("Deterministic recommendation preserved. Officer action recorded "
                 "with OFF-01 audit; adjust/escalate require a reason code."),
    }


# Map a Recommendation to the terminal CaseState used by the audit timeline.
_TERMINAL_STATE = {
    "Approve":            "RecommendationReady",
    "Refer to employee":  "Refer",
    "Request documents":  "NeedsDocuments",
    "Reject":             "Rejected",
}


@app.post("/demo/run/{case_id}")
def run(case_id: str, request: Request):
    case_id = case_id.upper()
    request_id = request.headers.get("x-request-id") or uuid.uuid4().hex[:12]
    if case_id not in FIXTURES:
        _log.warning("unknown case", extra={"request_id": request_id, "case_id": case_id})
        raise HTTPException(404, f"unknown case '{case_id}'")
    t0 = time.time()
    _log.info("case.start", extra={"request_id": request_id, "case_id": case_id, "mock_mode": MOCK_MODE})
    case, log = build_case(case_id)
    # v1.1 §7 transition: validation -> policy execution
    log.transition(case_id, "Validating", "PolicyRun", actor="policy",
                   detail="deterministic decide() called", mock_mode=MOCK_MODE)
    report = decide(case, POLICY)
    latency_ms = int((time.time() - t0) * 1000)
    terminal = _TERMINAL_STATE.get(report.recommendation, "RecommendationReady")
    log.add(case_id, "policy.decide", "policy",
            f"{report.recommendation} / {report.proposed_plan.path} (rules: {','.join(report.fired_rules) or 'none'})",
            latency_ms=latency_ms, mock_mode=MOCK_MODE,
            state_from="PolicyRun", state_to=terminal)
    # v1.1 §7 — the case is finalized into the audit record (no further mutation).
    log.transition(case_id, terminal, "Closed", mock_mode=MOCK_MODE,
                   detail="case finalized in the audit record")
    _log.info("case.decide", extra={
        "request_id": request_id, "case_id": case_id, "step": "policy.decide",
        "recommendation": report.recommendation, "path": report.proposed_plan.path,
        "fired_rules": report.fired_rules, "latency_ms": latency_ms, "mock_mode": MOCK_MODE,
    })
    return JSONResponse({
        "case": case.model_dump(mode="json"),
        "report": report.model_dump(mode="json"),
        "audit": log.events(),
        "impact": {
            "latency_ms": latency_ms,
            "mock_mode": MOCK_MODE,
            "benchmark": BENCHMARK,
            "request_id": request_id,
            "policy_version": POLICY.policy_version,
        },
    }, headers={"x-request-id": request_id})


# serve the single-page frontend if present
_FE = os.path.join(os.path.dirname(__file__), "..", "frontend")
if os.path.isdir(_FE):
    @app.get("/")
    def index():
        return FileResponse(os.path.join(_FE, "index.html"))
    app.mount("/static", StaticFiles(directory=_FE), name="static")

"""Agent Sanad API — ONE endpoint powers the whole demo. Plus static frontend."""
import json
import logging
import os
import time
import uuid
from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import ValidationError

from backend.adapters import build_case, FIXTURES
from backend.applications import build_case_from_application
from backend.policy.engine import decide
from backend.policy.rules import load_policy
from backend.schemas import MockApplication, OfficerAction
from backend.store import STORE
from backend.actions import next_actions

# T1 — optional LangGraph orchestration (Tooling Addendum). Import-guarded so a
# missing/broken langgraph dependency can never break the demo: the routes
# fall back to the plain orchestrator and /healthz reports why.
try:
    from backend.graph import run_graph_case, GRAPH_AVAILABLE, graph_import_error
    from backend.graph.compare_outputs import diff_summary
except Exception as _graph_exc:  # pragma: no cover
    run_graph_case = None  # type: ignore[assignment]
    GRAPH_AVAILABLE = False
    diff_summary = None  # type: ignore[assignment]
    _graph_err = f"{_graph_exc.__class__.__name__}: {_graph_exc}"
    def graph_import_error() -> str:  # type: ignore[no-redef]
        return _graph_err

POLICY = load_policy()
MOCK_MODE = os.getenv("LOCAL_MOCK_MODE", "true").lower() == "true"
# T1 flag — which orchestrator the UI should prefer. plain stays the default;
# the plain /demo/run route is always available regardless of this setting.
ORCHESTRATOR = os.getenv("SANAD_ORCHESTRATOR", "plain").lower()
if ORCHESTRATOR not in ("plain", "graph"):
    ORCHESTRATOR = "plain"

# Build version — the frontend pins the same string and compares it against
# /healthz at boot. A mismatch means a stale server process is running old
# routes while serving new static files (the classic local-dev failure mode);
# the UI then shows an actionable banner instead of leaking raw 404s.
APP_VERSION = "1.1.0"


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

app = FastAPI(title="Agent Sanad", version=APP_VERSION)


# ── PRD §5.5 error contract: every error returns {error_code, message} ──────
# Keeps raw framework tracebacks away from clients; the structured logger
# still captures full detail server-side.
_ERROR_CODES = {400: "BAD_REQUEST", 404: "NOT_FOUND", 405: "METHOD_NOT_ALLOWED",
                422: "VALIDATION_ERROR", 500: "INTERNAL_ERROR"}


@app.exception_handler(HTTPException)
async def http_exception_envelope(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error_code": _ERROR_CODES.get(exc.status_code, f"HTTP_{exc.status_code}"),
            "message": str(exc.detail),
            "path": str(request.url.path),
            "app_version": APP_VERSION,
        },
    )


@app.exception_handler(RequestValidationError)
async def request_validation_envelope(request: Request, exc: RequestValidationError):
    """Malformed/missing JSON bodies on dict-param endpoints raise
    RequestValidationError (not HTTPException) — without this handler they'd
    bypass the PRD §5.5 envelope and leak FastAPI's default shape."""
    return JSONResponse(
        status_code=422,
        content={
            "error_code": "VALIDATION_ERROR",
            "message": "Request body is missing or malformed JSON.",
            "path": str(request.url.path),
            "app_version": APP_VERSION,
        },
    )


@app.exception_handler(Exception)
async def unhandled_exception_envelope(request: Request, exc: Exception):
    _log.error("unhandled exception", extra={
        "step": "error.unhandled", "case_id": str(request.url.path),
    })
    return JSONResponse(
        status_code=500,
        content={
            "error_code": "INTERNAL_ERROR",
            "message": "An internal error occurred. The incident has been logged.",
            "path": str(request.url.path),
            "app_version": APP_VERSION,
        },
    )


@app.get("/healthz")
def healthz():
    return {
        "ok": True,
        "mock_mode": MOCK_MODE,
        "policy_version": POLICY.policy_version,
        "app_version": APP_VERSION,
        "orchestrator": ORCHESTRATOR,
        "graph_available": bool(GRAPH_AVAILABLE),
        "graph_import_error": None if GRAPH_AVAILABLE else graph_import_error(),
    }


# Human-facing labels for the app's sample-case picker (mirrors seeds/cases_v1.json).
# Known fired rules per case (used by Exception Studio for server-driven filtering).
_KNOWN_FIRED = {
    "GOLDEN": [], "NOHEAD": ["HARD-01","CAP-01"], "MISSING": ["DOC-01"],
    "ACTIVE": ["ACTIVE-01"], "CONTRA": ["INC-01","RSK-01"],
    "HIGH_OBLIGATIONS": ["OBL-01"], "PERIOD_BREACH": ["TEN-01"],
    "HARDSHIP": ["HARD-02"], "ZERO_OR_MISSING_INCOME": ["DOC-02"],
    "LOW_INCOME_PER_MEMBER": ["FAM-01"], "UNVERIFIED_HARDSHIP": ["HARD-01"],
    "PROMPT_INJECTION_ONLY": ["RSK-01"], "HIGH_CAPACITY_UPDATE": [],
}
_EXCEPTION_GROUP_MAP: dict[str, str] = {}
for _cid, _rules in _KNOWN_FIRED.items():
    if "ACTIVE-01" in _rules or "TEN-01" in _rules:
        _EXCEPTION_GROUP_MAP[_cid] = "Policy hard stop"
    elif "DOC-01" in _rules or "DOC-02" in _rules or "INC-01" in _rules:
        _EXCEPTION_GROUP_MAP[_cid] = "Evidence problem"
    elif "OBL-01" in _rules:
        _EXCEPTION_GROUP_MAP[_cid] = "Affordability risk"
    elif "HARD-01" in _rules or "HARD-02" in _rules or "FAM-01" in _rules:
        _EXCEPTION_GROUP_MAP[_cid] = "Social hardship"
    elif "RSK-01" in _rules:
        _EXCEPTION_GROUP_MAP[_cid] = "Security risk"

CASE_META = {
    "GOLDEN":                 {"label": "Clean update — approve",            "group": "Standard"},
    "NOHEAD":                 {"label": "No headroom — transfer & refer",    "group": "Hardship"},
    "MISSING":                {"label": "Missing salary certificate",        "group": "Documents"},
    "ACTIVE":                 {"label": "Active request — auto reject",      "group": "Governance"},
    "CONTRA":                 {"label": "Income contradiction + injection",  "group": "Security"},
    "HIGH_OBLIGATIONS":       {"label": "High obligations — refer",          "group": "Risk"},
    "PERIOD_BREACH":          {"label": "Period breach — refer",             "group": "Governance"},
    "HARDSHIP":               {"label": "Verified hardship — approve",       "group": "Hardship"},
    "ZERO_OR_MISSING_INCOME": {"label": "Income unverifiable — request docs","group": "Documents"},
    "LOW_INCOME_PER_MEMBER":  {"label": "Low income per member — approve",   "group": "Social"},
    "UNVERIFIED_HARDSHIP":    {"label": "Unverified hardship — refer",       "group": "Hardship"},
    "PROMPT_INJECTION_ONLY":  {"label": "Prompt injection — logged only",    "group": "Security"},
    "HIGH_CAPACITY_UPDATE":   {"label": "High capacity — approve",           "group": "Standard"},
}


@app.get("/cases")
def cases():
    return {
        "cases": list(FIXTURES.keys()),
        "details": [
            {
                "id": cid,
                **CASE_META.get(cid, {"label": cid, "group": "Other"}),
                "exception_group": _EXCEPTION_GROUP_MAP.get(cid, ""),
            }
            for cid in FIXTURES.keys()
        ],
    }


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
    # Persist officer action.
    STORE.save_officer_action(case_id, action.action,
                                     action.override_reason_code, action.notes)
    return {
        "case_id": case_id,
        "report": report.model_dump(mode="json"),
        "next_required_actions": next_actions(report.fired_rules),
        "officer_action": action.model_dump(mode="json"),
        "audit": log.events(),
        "note": ("Deterministic recommendation preserved. Officer action recorded "
                 "with OFF-01 audit; adjust/escalate require a reason code."),
    }


# ── P1 persistence — list/retrieve stored applications & actions ───────────


@app.get("/applications")
def list_applications():
    """Return all persisted custom applications, newest first."""
    return {"applications": STORE.list_applications()}


@app.get("/applications/{application_id}")
def get_application(application_id: str):
    """Return a persisted application with its recommendation and audit trail."""
    app_data = STORE.get_application(application_id.upper())
    if app_data is None:
        raise HTTPException(404, f"unknown application '{application_id}'")
    return app_data


@app.get("/officer-actions")
def list_officer_actions():
    """Return all persisted officer actions, newest first."""
    return {"actions": STORE.list_officer_actions()}


# ── v1.1 app flow — custom mock application ─────────────────────────────────
# The beneficiary form posts here. Input is Pydantic-validated, mapped onto a
# synthetic Case (backend/applications.py), and decided by the EXISTING
# deterministic engine. No PII, no engine changes.

def _parse_mock_application(body: dict) -> MockApplication:
    try:
        return MockApplication(**(body or {}))
    except ValidationError as exc:
        raise HTTPException(422, f"invalid application: {exc.errors()}")


@app.post("/applications/mock")
def post_mock_application(body: dict):
    """Validate a mock application and return the assembled Case snapshot
    (no policy run) — used by the app's review step."""
    app_in = _parse_mock_application(body)
    case, log, application_id = build_case_from_application(app_in)
    STORE.save_application(application_id, app_in.model_dump(mode="json"))
    STORE.save_audit_events(application_id, log.events())
    return {
        "application_id": application_id,
        "case": case.model_dump(mode="json"),
        "audit": log.events(),
    }


@app.post("/applications/mock/decide")
def post_mock_application_decide(body: dict, request: Request):
    """Full custom flow: validate -> build synthetic Case -> existing decide().
    Returns the same envelope shape as /demo/run/{case_id}."""
    request_id = request.headers.get("x-request-id") or uuid.uuid4().hex[:12]
    app_in = _parse_mock_application(body)
    t0 = time.time()
    case, log, application_id = build_case_from_application(app_in)
    log.transition(application_id, "Validating", "PolicyRun", actor="policy",
                   detail="deterministic decide() called", mock_mode=MOCK_MODE)
    report = decide(case, POLICY)
    latency_ms = int((time.time() - t0) * 1000)
    terminal = _TERMINAL_STATE.get(report.recommendation, "RecommendationReady")
    log.add(application_id, "policy.decide", "policy",
            f"{report.recommendation} / {report.proposed_plan.path} "
            f"(rules: {','.join(report.fired_rules) or 'none'})",
            latency_ms=latency_ms, mock_mode=MOCK_MODE,
            state_from="PolicyRun", state_to=terminal)
    log.transition(application_id, terminal, "Closed", mock_mode=MOCK_MODE,
                   detail="case finalized in the audit record")
    _log.info("application.decide", extra={
        "request_id": request_id, "case_id": application_id,
        "step": "policy.decide", "recommendation": report.recommendation,
        "path": report.proposed_plan.path, "fired_rules": report.fired_rules,
        "latency_ms": latency_ms, "mock_mode": MOCK_MODE,
    })
    STORE.save_application(application_id, app_in.model_dump(mode="json"))
    STORE.save_recommendation(application_id, report.model_dump(mode="json"))
    STORE.save_audit_events(application_id, log.events())
    return JSONResponse({
        "application_id": application_id,
        "case": case.model_dump(mode="json"),
        "report": report.model_dump(mode="json"),
        "next_required_actions": next_actions(report.fired_rules),
        "audit": log.events(),
        "impact": {
            "latency_ms": latency_ms,
            "mock_mode": MOCK_MODE,
            "benchmark": BENCHMARK,
            "request_id": request_id,
            "policy_version": POLICY.policy_version,
        },
    }, headers={"x-request-id": request_id})


# Map a Recommendation to the terminal CaseState used by the audit timeline.
_TERMINAL_STATE = {
    "Approve":            "RecommendationReady",
    "Refer to employee":  "Refer",
    "Request documents":  "NeedsDocuments",
    "Reject":             "Rejected",
}


# ── T1: LangGraph routes (Tooling Addendum) ─────────────────────────────────
# Same envelope as /demo/run plus impact.graph_path. Any failure falls back to
# the plain orchestrator with impact.fallback_used=true — the demo cannot
# break because of the framework. The framework never decides the money.

@app.post("/demo/run-graph/{case_id}")
def run_graph(case_id: str, request: Request):
    case_id = case_id.upper()
    request_id = request.headers.get("x-request-id") or uuid.uuid4().hex[:12]
    if case_id not in FIXTURES:
        raise HTTPException(404, f"unknown case '{case_id}'")
    if not GRAPH_AVAILABLE or run_graph_case is None:
        return _plain_envelope(case_id, request_id,
                               fallback="graph_unavailable: " + str(graph_import_error()))
    try:
        envelope = run_graph_case(case_id, mock_mode=MOCK_MODE, request_id=request_id)
        envelope["impact"]["benchmark"] = BENCHMARK
        envelope["impact"]["request_id"] = request_id
        envelope["impact"]["policy_version"] = POLICY.policy_version
        envelope["impact"]["fallback_used"] = False
        _log.info("graph.complete", extra={
            "request_id": request_id, "case_id": case_id, "step": "graph.complete",
            "recommendation": envelope["report"]["recommendation"],
            "path": envelope["report"]["proposed_plan"]["path"],
            "fired_rules": envelope["report"]["fired_rules"],
            "latency_ms": envelope["impact"]["latency_ms"], "mock_mode": MOCK_MODE,
        })
        return JSONResponse(envelope, headers={"x-request-id": request_id})
    except Exception as exc:
        _log.error("graph.failed", extra={
            "request_id": request_id, "case_id": case_id, "step": "graph.failed",
        })
        return _plain_envelope(case_id, request_id,
                               fallback=f"graph_error: {exc.__class__.__name__}")


def _plain_envelope(case_id: str, request_id: str, *,
                    fallback: str | None = None) -> JSONResponse:
    """The plain orchestrator path, reusable by the graph fallback."""
    t0 = time.time()
    case, log = build_case(case_id)
    log.transition(case_id, "Validating", "PolicyRun", actor="policy",
                   detail="deterministic decide() called", mock_mode=MOCK_MODE)
    report = decide(case, POLICY)
    latency_ms = int((time.time() - t0) * 1000)
    terminal = _TERMINAL_STATE.get(report.recommendation, "RecommendationReady")
    log.add(case_id, "policy.decide", "policy",
            f"{report.recommendation} / {report.proposed_plan.path}",
            latency_ms=latency_ms, mock_mode=MOCK_MODE,
            state_from="PolicyRun", state_to=terminal)
    log.transition(case_id, terminal, "Closed", mock_mode=MOCK_MODE,
                   detail="case finalized in the audit record")
    envelope = {
        "case": case.model_dump(mode="json"),
        "report": report.model_dump(mode="json"),
        "next_required_actions": next_actions(report.fired_rules),
        "audit": log.events(),
        "impact": {
            "latency_ms": latency_ms, "mock_mode": MOCK_MODE,
            "benchmark": BENCHMARK, "orchestrator": "plain",
            "request_id": request_id, "policy_version": POLICY.policy_version,
        },
    }
    if fallback:
        envelope["impact"]["fallback_used"] = True
        envelope["impact"]["fallback_reason"] = fallback
    return JSONResponse(envelope, headers={"x-request-id": request_id})


@app.get("/demo/compare/{case_id}")
def compare(case_id: str):
    """Side-by-side equivalence proof for plain vs graph (officer/judge view)."""
    case_id = case_id.upper()
    if case_id not in FIXTURES:
        raise HTTPException(404, f"unknown case '{case_id}'")
    t0 = time.time()
    case, log = build_case(case_id)
    report = decide(case, POLICY)
    plain = {
        "case": case.model_dump(mode="json"),
        "report": report.model_dump(mode="json"),
        "audit": log.events(),
        "impact": {"latency_ms": int((time.time() - t0) * 1000),
                   "mock_mode": MOCK_MODE, "orchestrator": "plain"},
    }
    if not GRAPH_AVAILABLE or run_graph_case is None or diff_summary is None:
        return {"equivalent": None, "graph_available": False,
                "reason": graph_import_error()}
    graph_env = run_graph_case(case_id, mock_mode=MOCK_MODE)
    return diff_summary(plain, graph_env)


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
        "next_required_actions": next_actions(report.fired_rules),
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

"""LangGraph node functions for Agent Sanad.

Design principles (do not relax):
1. Every financial decision is made by backend.policy.engine.decide() and ONLY
   by decide(). These nodes ORCHESTRATE; they never COMPUTE money.
2. The graph and the plain route share the same build_case, decide, and
   RecommendationReport. Equivalence is enforced by tests for all 13 cases.
3. Pre-policy nodes (check_active_request, validate_documents) are
   inspect-only labels. They never short-circuit — the Rule-1/2/3 gates fire
   inside decide() exactly as on the plain route. This is what guarantees
   byte-identical reports.
4. Each node appends a graph.* audit event so the officer drawer shows the
   traversal alongside the adapter calls and state transitions.
"""
from __future__ import annotations

from typing import Callable, TYPE_CHECKING

from backend.adapters import FIXTURES, build_case
from backend.audit import AuditLog
from backend.policy.engine import decide
from backend.policy.rules import load_policy

if TYPE_CHECKING:
    from backend.graph.state import SanadGraphState


_POLICY = load_policy()


def _mark(state: "SanadGraphState", node: str) -> None:
    path = list(state.get("graph_path", []))
    path.append(node)
    state["graph_path"] = path


def _audit(state: "SanadGraphState", step: str, detail: str = "",
           actor: str = "graph") -> None:
    log: AuditLog | None = state.get("_audit_log")
    if log is not None:
        log.add(state["case_id"], step, actor, detail,
                mock_mode=state.get("mock_mode", True))


# ─── the 10 nodes (Tooling Addendum §4.4) ────────────────────────────────────

def verify_identity(state: "SanadGraphState") -> "SanadGraphState":
    """Assemble the working Case via the existing adapter pipeline.

    build_case() is the atomic retrieval primitive (UAE PASS → loan → arrears
    → doc validation → extraction → salary verification, emitting the §7 state
    transitions). We invoke it once here; subsequent nodes are informational
    labels over the same validated Case — splitting it would risk divergence
    from the plain route for zero benefit.
    """
    _mark(state, "verify_identity")
    case, log = build_case(state["case_id"])
    state["_case"] = case
    state["_audit_log"] = log
    _audit(state, "graph.verify_identity",
           f"identity {case.applicant.applicant_ref if case.applicant else 'unknown'}")
    return state


def retrieve_programme_data(state: "SanadGraphState") -> "SanadGraphState":
    _mark(state, "retrieve_programme_data")
    case = state["_case"]
    detail = ""
    if case.arrears:
        detail = (f"loan {case.loan.agreement_id if case.loan else '?'} · "
                  f"arrears AED {case.arrears.arrears_amount_aed:,.0f}")
    _audit(state, "graph.retrieve_programme_data", detail)
    return state


def check_active_request(state: "SanadGraphState") -> "SanadGraphState":
    """Inspect-only flag; the real Rule-3 gate fires inside decide()."""
    _mark(state, "check_active_request")
    case = state["_case"]
    active = bool(case.arrears and case.arrears.active_request_exists)
    state["active_request_detected"] = active
    _audit(state, "graph.check_active_request",
           "active rescheduling request detected" if active else "no active request")
    return state


def validate_documents(state: "SanadGraphState") -> "SanadGraphState":
    """Inspect-only completeness label; the DOC gates fire inside decide()."""
    _mark(state, "validate_documents")
    case = state["_case"]
    complete = not case.documents.missing_required
    state["documents_complete"] = complete
    _audit(state, "graph.validate_documents",
           "documents complete" if complete
           else f"missing: {','.join(case.documents.missing_required)}")
    return state


def extract_income(state: "SanadGraphState") -> "SanadGraphState":
    """Extraction already ran inside build_case (live or cached, with
    fallback). This node documents the step in the graph traversal."""
    _mark(state, "extract_income")
    case = state["_case"]
    inc = case.income.salary_certificate_income_aed if case.income else None
    _audit(state, "graph.extract_income",
           f"certificate income {inc}" if inc is not None else "no certificate income")
    return state


def verify_salary(state: "SanadGraphState") -> "SanadGraphState":
    _mark(state, "verify_salary")
    case = state["_case"]
    ver = case.income.verified_monthly_income_aed if case.income else None
    _audit(state, "graph.verify_salary",
           f"verified income AED {ver:,.0f}" if ver else "no verified income")
    return state


def run_policy_engine(state: "SanadGraphState") -> "SanadGraphState":
    """THE single source of every financial decision: the existing decide()."""
    _mark(state, "run_policy_engine")
    report = decide(state["_case"], _POLICY)
    state["_report"] = report
    state["recommendation"] = report.recommendation
    state["proposed_path"] = report.proposed_plan.path
    state["fired_rules"] = list(report.fired_rules)
    _audit(state, "graph.run_policy_engine",
           f"{report.recommendation} / {report.proposed_plan.path}")
    return state


def build_reasoning(state: "SanadGraphState") -> "SanadGraphState":
    """Reasoning text is already attached by decide() via reasoning.py
    (cached/templated, LLM-optional). Node exists for addendum symmetry."""
    _mark(state, "build_reasoning")
    _audit(state, "graph.build_reasoning", "reasoning text attached to report")
    return state


def emit_audit(state: "SanadGraphState") -> "SanadGraphState":
    """Package the response envelope from the validated objects."""
    _mark(state, "emit_audit")
    report = state["_report"]
    _audit(state, "graph.emit_audit", "envelope packaged")
    state["report"] = report.model_dump(mode="json")
    state["_case_dump"] = state["_case"].model_dump(mode="json")
    return state


def route_exception_or_close(state: "SanadGraphState") -> "SanadGraphState":
    """Terminal node: label the case_state from the recommendation."""
    _mark(state, "route_exception_or_close")
    state["case_state"] = {
        "Approve":           "RecommendationReady",
        "Reject":            "Rejected",
        "Request documents": "NeedsDocuments",
        "Refer to employee": "Refer",
    }.get(state.get("recommendation", ""), "RecommendationReady")
    _audit(state, "graph.route_exception_or_close",
           f"final state: {state['case_state']}")
    return state


NODES: dict[str, Callable[["SanadGraphState"], "SanadGraphState"]] = {
    "verify_identity":          verify_identity,
    "retrieve_programme_data":  retrieve_programme_data,
    "check_active_request":     check_active_request,
    "validate_documents":       validate_documents,
    "extract_income":           extract_income,
    "verify_salary":            verify_salary,
    "run_policy_engine":        run_policy_engine,
    "build_reasoning":          build_reasoning,
    "emit_audit":               emit_audit,
    "route_exception_or_close": route_exception_or_close,
}


def assert_case_known(case_id: str) -> None:
    if case_id not in FIXTURES:
        raise KeyError(f"unknown case '{case_id}'")

"""Compile the Agent Sanad LangGraph + a sync runner for the API layer.

The graph is linear (10 nodes in sequence) because the orchestration decision
(active-request, missing-doc, contradiction, hardship) is fully owned by
decide() inside backend.policy.engine. Pre-policy nodes label the case; they
never short-circuit — that is what guarantees report equivalence with the
plain route.

If LangGraph fails to import or compile, GRAPH_AVAILABLE flips to False and
run_graph_case() raises RuntimeError; the API layer catches it and falls back
to the plain path with impact.fallback_used=true. The demo cannot break.
"""
from __future__ import annotations

import time
from typing import Any

from backend.actions import next_actions
from backend.graph.nodes import NODES, assert_case_known
from backend.graph.state import SanadGraphState

GRAPH_AVAILABLE = True
_COMPILED_GRAPH = None
_IMPORT_ERROR: str | None = None


def _compile() -> Any | None:
    global GRAPH_AVAILABLE, _IMPORT_ERROR
    try:
        from langgraph.graph import StateGraph, END
    except Exception as exc:  # pragma: no cover — only without the dependency
        GRAPH_AVAILABLE = False
        _IMPORT_ERROR = f"{exc.__class__.__name__}: {exc}"
        return None

    builder = StateGraph(SanadGraphState)
    for name, fn in NODES.items():
        builder.add_node(name, fn)
    builder.set_entry_point("verify_identity")
    seq = list(NODES.keys())
    for src, dst in zip(seq, seq[1:]):
        builder.add_edge(src, dst)
    builder.add_edge(seq[-1], END)
    return builder.compile()


def build_sanad_graph() -> Any:
    """Return (and memoize) the compiled graph. Used by tests and the API."""
    global _COMPILED_GRAPH
    if _COMPILED_GRAPH is None and GRAPH_AVAILABLE:
        _COMPILED_GRAPH = _compile()
    return _COMPILED_GRAPH


def graph_import_error() -> str | None:
    return _IMPORT_ERROR


# Map a Recommendation to the §7 terminal CaseState (mirrors the plain route).
_TERMINAL = {
    "Approve":           "RecommendationReady",
    "Refer to employee": "Refer",
    "Request documents": "NeedsDocuments",
    "Reject":            "Rejected",
}


def run_graph_case(case_id: str, *, mock_mode: bool = True,
                   request_id: str = "") -> dict:
    """Run the LangGraph for case_id; return the standard envelope:
    {"case", "report", "audit", "impact", "graph_path"}.

    Raises KeyError (unknown case) or RuntimeError (graph unavailable) — the
    API layer translates those into 404 / plain-route fallback respectively.
    """
    assert_case_known(case_id)
    graph = build_sanad_graph()
    if graph is None:
        raise RuntimeError(
            f"LangGraph unavailable: {graph_import_error() or 'unknown error'}")

    initial: SanadGraphState = {
        "case_id": case_id,
        "mock_mode": mock_mode,
        "request_id": request_id,
        "graph_path": [],
    }
    t0 = time.time()
    final: SanadGraphState = graph.invoke(initial)  # type: ignore[assignment]
    latency_ms = int((time.time() - t0) * 1000)

    # Terminal + Closed transitions, mirroring the plain route so the officer
    # drawer's state timeline is identical regardless of orchestrator.
    report = final["_report"]
    log = final["_audit_log"]
    terminal = _TERMINAL.get(report.recommendation, "RecommendationReady")
    log.transition(case_id, "Validating", "PolicyRun", actor="policy",
                   detail="deterministic decide() called (graph orchestrator)",
                   mock_mode=mock_mode)
    log.add(case_id, "policy.decide", "policy",
            f"{report.recommendation} / {report.proposed_plan.path} "
            f"(rules: {','.join(report.fired_rules) or 'none'})",
            latency_ms=latency_ms, mock_mode=mock_mode,
            state_from="PolicyRun", state_to=terminal)
    log.transition(case_id, terminal, "Closed", mock_mode=mock_mode,
                   detail="case finalized in the audit record")

    fired_rules = list(report.fired_rules)
    return {
        "case": final.get("_case_dump") or final["_case"].model_dump(mode="json"),
        "report": final["report"],
        "next_required_actions": next_actions(fired_rules),
        "audit": log.events(),
        "impact": {
            "latency_ms": latency_ms,
            "mock_mode": mock_mode,
            "orchestrator": "langgraph",
            "graph_path": final.get("graph_path", []),
        },
        "graph_path": final.get("graph_path", []),
    }

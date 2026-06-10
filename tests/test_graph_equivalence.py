"""T1 acceptance (Tooling Addendum §4.6 / §11.1).

For EVERY sample case, the plain route and the LangGraph route must produce
the same RecommendationReport: recommendation, path, fired rules, 20% and
period compliance, plan numbers. Audit events and latency are per-run and are
excluded from equivalence.

If any assertion here fails, the framework has altered the money path — fix
the graph wrapper; never relax the assertion.
"""
from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from backend.app import app
from backend.graph import GRAPH_AVAILABLE
from backend.graph.compare_outputs import equivalent_report

ALL_CASES = [
    "GOLDEN", "NOHEAD", "MISSING", "ACTIVE", "CONTRA",
    "HIGH_OBLIGATIONS", "PERIOD_BREACH", "HARDSHIP",
    "ZERO_OR_MISSING_INCOME", "LOW_INCOME_PER_MEMBER",
    "UNVERIFIED_HARDSHIP", "PROMPT_INJECTION_ONLY", "HIGH_CAPACITY_UPDATE",
]

client = TestClient(app)


def _both(case_id: str) -> tuple[dict, dict]:
    plain = client.post(f"/demo/run/{case_id}")
    graph = client.post(f"/demo/run-graph/{case_id}")
    assert plain.status_code == 200, plain.text
    assert graph.status_code == 200, graph.text
    return plain.json(), graph.json()


@pytest.mark.skipif(not GRAPH_AVAILABLE, reason="LangGraph not installed")
@pytest.mark.parametrize("case_id", ALL_CASES)
def test_graph_report_equivalent_to_plain(case_id: str) -> None:
    plain, graph = _both(case_id)
    ok, diffs = equivalent_report(plain, graph)
    assert ok, f"{case_id}: {diffs}"
    # Explicit spell-out of the addendum's named fields.
    pr, gr = plain["report"], graph["report"]
    assert pr["recommendation"] == gr["recommendation"]
    assert pr["proposed_plan"]["path"] == gr["proposed_plan"]["path"]
    assert set(pr["fired_rules"]) == set(gr["fired_rules"])
    assert pr["twenty_pct_compliance"] == gr["twenty_pct_compliance"]
    assert pr["period_compliance"] == gr["period_compliance"]


@pytest.mark.skipif(not GRAPH_AVAILABLE, reason="LangGraph not installed")
def test_graph_route_exposes_node_sequence_and_full_state_timeline() -> None:
    d = client.post("/demo/run-graph/GOLDEN").json()
    impact = d["impact"]
    assert impact["orchestrator"] == "langgraph"
    assert impact["fallback_used"] is False
    nodes = impact["graph_path"]
    assert nodes[0] == "verify_identity"
    assert "run_policy_engine" in nodes
    assert nodes[-1] == "route_exception_or_close"
    assert len(nodes) == 10
    # The §7 state timeline must be identical to the plain route's.
    states = [e["state_to"] for e in d["audit"] if e.get("state_to")]
    assert states == ["Submitted", "IdentityLinked", "DataRetrieved",
                      "Extracting", "Validating", "PolicyRun",
                      "RecommendationReady", "Closed"]


@pytest.mark.skipif(not GRAPH_AVAILABLE, reason="LangGraph not installed")
def test_compare_endpoint_proves_equivalence() -> None:
    body = client.get("/demo/compare/GOLDEN").json()
    assert body["equivalent"] is True, body
    assert body["plain"]["recommendation"] == body["graph"]["recommendation"]


@pytest.mark.skipif(not GRAPH_AVAILABLE, reason="LangGraph not installed")
@pytest.mark.parametrize("case_id", ALL_CASES)
def test_graph_route_returns_same_actions_as_plain(case_id: str) -> None:
    """v1.3 P1 fix: graph route must include next_required_actions matching
    the plain route. Guards the Evidence Repair Loop parity."""
    plain = client.post(f"/demo/run/{case_id}").json()
    graph = client.post(f"/demo/run-graph/{case_id}").json()
    assert plain.get("next_required_actions") == graph.get("next_required_actions"), (
        f"{case_id}: plain actions {plain.get('next_required_actions')} != "
        f"graph actions {graph.get('next_required_actions')}"
    )


def test_graph_route_falls_back_to_plain_on_failure(monkeypatch) -> None:
    """If graph execution raises, the route must return the plain envelope
    with fallback_used=true — never a 500 to the demo."""
    import backend.app as app_module
    def boom(*a, **k):
        raise RuntimeError("forced graph failure")
    monkeypatch.setattr(app_module, "run_graph_case", boom)
    r = client.post("/demo/run-graph/GOLDEN")
    assert r.status_code == 200
    body = r.json()
    assert body["impact"]["orchestrator"] == "plain"
    assert body["impact"]["fallback_used"] is True
    assert "graph_error" in body["impact"]["fallback_reason"]
    assert body["report"]["recommendation"] == "Approve"


def test_healthz_advertises_orchestrator() -> None:
    h = client.get("/healthz").json()
    assert h["orchestrator"] in ("plain", "graph")
    assert isinstance(h["graph_available"], bool)


def test_graph_unknown_case_404() -> None:
    r = client.post("/demo/run-graph/NOPE")
    assert r.status_code == 404
    assert r.json()["error_code"] == "NOT_FOUND"

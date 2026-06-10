"""SanadGraphState — typed state flowing through the LangGraph nodes.

Per the Tooling Addendum §4.3. All fields optional (total=False): each node
fills its own slice; the final node packages the response envelope.

The AUTHORITATIVE Case / RecommendationReport / AuditLog remain the validated
objects from backend.schemas + backend.audit — carried under private keys so
the graph state stays serializable while the engine operates only on typed
objects. The graph is glue; it never re-types or rewrites engine output.
"""
from __future__ import annotations

from typing import Any, Optional, TypedDict


class SanadGraphState(TypedDict, total=False):
    # Inputs
    case_id: str
    mock_mode: bool
    request_id: str

    # Workflow labels (informational; gates still fire inside decide())
    case_state: str
    active_request_detected: bool
    documents_complete: bool

    # Live objects carried between nodes (private to the graph layer)
    _case: Any                      # backend.schemas.Case
    _report: Any                    # backend.schemas.RecommendationReport
    _audit_log: Any                 # backend.audit.AuditLog
    _case_dump: dict

    # Outputs (mirrors the /demo/run envelope)
    report: dict
    audit_events: list[dict]

    # Observability
    graph_path: list[str]           # ordered node names that executed
    fired_rules: list[str]
    recommendation: str
    proposed_path: str
    error: Optional[str]

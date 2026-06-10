"""LangSmith-ready trace adapter (Tooling Addendum §5) — DISABLED by default.

Design:
- LANGSMITH_TRACING=false is the default; the demo never depends on tracing.
- TRACE_REDACTION=true is the default and the redaction step CANNOT be
  bypassed: emit_trace() always calls redact_for_trace() first; the
  TRACE_REDACTION flag only adds an extra hard-fail guard if someone tries to
  turn it off while tracing is on (we refuse to trace rather than leak).
- No hard dependency: if the `langsmith` package is absent, enabled tracing
  degrades to structured local log lines with the same redacted payload, so
  the observability story is testable offline.
- The adapter is write-only telemetry. It can never influence the engine.
"""
from __future__ import annotations

import json
import logging
import os
from typing import Any

from backend.observability.redaction import redact_for_trace

_log = logging.getLogger("sanad.trace")


def tracing_enabled() -> bool:
    return os.getenv("LANGSMITH_TRACING", "false").lower() in ("1", "true", "yes")


def _redaction_enabled() -> bool:
    return os.getenv("TRACE_REDACTION", "true").lower() in ("1", "true", "yes")


def _project() -> str:
    return os.getenv("LANGSMITH_PROJECT", "agent-sanad-demo")


def build_trace_payload(*, case_id: str, recommendation: str, path: str,
                        fired_rules: list[str], latency_ms: int,
                        mock_mode: bool, orchestrator: str = "plain",
                        graph_path: list[str] | None = None,
                        request_id: str = "") -> dict[str, Any]:
    """Assemble the ONLY shape we ever trace: synthetic ids, node names,
    decision metadata, latency. Never documents, never narratives, never names."""
    payload: dict[str, Any] = {
        "project": _project(),
        "case_id": case_id,
        "request_id": request_id,
        "recommendation": recommendation,
        "path": path,
        "fired_rules": list(fired_rules or []),
        "latency_ms": int(latency_ms),
        "mock_mode": bool(mock_mode),
        "orchestrator": orchestrator,
    }
    if graph_path:
        payload["graph_path"] = list(graph_path)
    return payload


def emit_trace(payload: dict) -> dict | None:
    """Redact and emit one trace event. Returns the redacted payload that was
    (or would be) sent, or None when tracing is disabled / refused.

    Redaction is unconditional. If someone sets TRACE_REDACTION=false while
    tracing is on, we REFUSE to emit rather than send unredacted data.
    """
    if not tracing_enabled():
        return None
    if not _redaction_enabled():
        _log.warning("tracing requested with TRACE_REDACTION=false — refusing to emit")
        return None
    safe = redact_for_trace(payload)
    try:
        import langsmith  # noqa: F401  — optional dependency
        # A real exporter would create a run via the langsmith client here.
        # Kept as a stub by design: external auth must never gate the demo.
        _log.info("trace.emit (langsmith client available) %s",
                  json.dumps(safe, ensure_ascii=False))
    except Exception:
        _log.info("trace.emit (local fallback) %s",
                  json.dumps(safe, ensure_ascii=False))
    return safe

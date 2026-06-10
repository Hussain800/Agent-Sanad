"""Observability layer (T2, Tooling Addendum §5).

Local audit remains the source of truth (backend/audit.py). This package adds
an OPTIONAL, PII-safe trace exporter: every payload passes through
redact_for_trace() before anything could leave the process, and tracing is
DISABLED by default (LANGSMITH_TRACING=false). The demo never depends on it.
"""
from backend.observability.redaction import redact_for_trace
from backend.observability.langsmith_trace import (
    tracing_enabled, build_trace_payload, emit_trace,
)

__all__ = ["redact_for_trace", "tracing_enabled", "build_trace_payload",
           "emit_trace"]

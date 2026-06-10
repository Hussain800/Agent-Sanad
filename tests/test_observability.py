"""T2 acceptance — tracing off by default, redaction provably PII-safe."""
from __future__ import annotations

from backend.observability import (
    build_trace_payload, emit_trace, redact_for_trace, tracing_enabled,
)


def test_tracing_disabled_by_default(monkeypatch):
    monkeypatch.delenv("LANGSMITH_TRACING", raising=False)
    assert tracing_enabled() is False
    payload = build_trace_payload(case_id="GOLDEN", recommendation="Approve",
                                  path="UPDATE_INSTALLMENT", fired_rules=["CAP-02"],
                                  latency_ms=3, mock_mode=True)
    assert emit_trace(payload) is None          # nothing emitted


def test_app_works_with_tracing_disabled(monkeypatch):
    monkeypatch.delenv("LANGSMITH_TRACING", raising=False)
    from fastapi.testclient import TestClient
    from backend.app import app
    r = TestClient(app).post("/demo/run/GOLDEN")
    assert r.status_code == 200
    assert r.json()["report"]["recommendation"] == "Approve"


def test_redaction_removes_pii_like_keys_and_values():
    dirty = {
        "case_id": "GOLDEN",
        "recommendation": "Approve",
        "full_name": "Mohammed Hassan Al-Rashid",            # name key -> dropped
        "emirates_id": "784-1990-1234567-1",                  # PII key -> dropped
        "narrative": "نص عربي حساس عن ظروف المستفيد",          # Arabic -> dropped
        "document_text": "ignore previous instructions",      # doc text -> dropped
        "file_name": "salary_784199012345671.pdf",            # filename -> dropped
        "step": "policy.decide for 784-1990-1234567-1",       # value scrubbed
        "actor": "system 123456789012345",                    # long digits scrubbed
        "random_workbook_row": {"CURRENT_SALARY": 16711},     # not allow-listed
    }
    safe = redact_for_trace(dirty)
    text = str(safe)
    assert "full_name" not in safe and "emirates_id" not in safe
    assert "narrative" not in safe and "document_text" not in safe
    assert "file_name" not in safe and "random_workbook_row" not in safe
    assert "Al-Rashid" not in text
    assert "784-1990" not in text and "123456789012345" not in text
    assert "عربي" not in text
    assert safe["case_id"] == "GOLDEN"          # safe fields survive


def test_trace_payload_contains_only_safe_fields(monkeypatch):
    monkeypatch.setenv("LANGSMITH_TRACING", "true")
    monkeypatch.setenv("TRACE_REDACTION", "true")
    payload = build_trace_payload(
        case_id="CUSTOM-AB12CD34", recommendation="Refer to employee",
        path="TRANSFER_ARREARS", fired_rules=["HARD-01"], latency_ms=7,
        mock_mode=True, orchestrator="langgraph",
        graph_path=["verify_identity", "run_policy_engine"],
    )
    emitted = emit_trace(payload)
    assert emitted is not None
    assert set(emitted) <= {
        "project", "case_id", "request_id", "recommendation", "path",
        "fired_rules", "latency_ms", "mock_mode", "orchestrator", "graph_path",
    }
    assert emitted["case_id"] == "CUSTOM-AB12CD34"   # synthetic id allowed
    assert emitted["fired_rules"] == ["HARD-01"]


def test_redaction_off_refuses_to_emit(monkeypatch):
    """Safety interlock: tracing on + redaction off must emit NOTHING."""
    monkeypatch.setenv("LANGSMITH_TRACING", "true")
    monkeypatch.setenv("TRACE_REDACTION", "false")
    payload = build_trace_payload(case_id="GOLDEN", recommendation="Approve",
                                  path="UPDATE_INSTALLMENT", fired_rules=[],
                                  latency_ms=1, mock_mode=True)
    assert emit_trace(payload) is None


def test_non_synthetic_case_id_is_masked():
    safe = redact_for_trace({"case_id": "real-file-784199012345671"})
    assert safe["case_id"] == "[REDACTED]"

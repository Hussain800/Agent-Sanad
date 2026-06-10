"""v1.6 API contract model tests."""
from __future__ import annotations
from fastapi.testclient import TestClient
from backend.app import app
from backend.api_models import (
    ConsentValidateRequest, ConsentValidateResponse,
    SessionStartRequest, SessionCallbackRequest,
    AppealCreateRequest, AppealDecisionRequest,
    CaseAssignRequest, LifecycleTransitionRequest,
    ConnectorFailureProfileRequest, AuditExportManifest,
)

client = TestClient(app)


def test_consent_validate_model():
    m = ConsentValidateRequest(purpose_code="identity.verify", connector_scope="uaepass.access")
    assert m.purpose_code == "identity.verify"
    assert m.connector_scope == "uaepass.access"


def test_session_start_model():
    m = SessionStartRequest(purpose_code="identity.verify", beneficiary_ref="BEN-001")
    assert m.beneficiary_ref == "BEN-001"


def test_session_callback_model():
    m = SessionCallbackRequest(session_id="S1", code="ABC", nonce="N1")
    assert m.session_id == "S1"


def test_appeal_create_model():
    m = AppealCreateRequest(reason="Test reason")
    assert m.reason == "Test reason"


def test_appeal_decision_model():
    m = AppealDecisionRequest(decision="upheld", rationale="Valid")
    assert m.decision == "upheld"


def test_case_assign_model():
    m = CaseAssignRequest(case_id="GOLDEN", officer_ref="off-001")
    assert m.officer_ref == "off-001"


def test_lifecycle_transition_model():
    m = LifecycleTransitionRequest(target_state="policy_ready")
    assert m.target_state == "policy_ready"


def test_failure_profile_model():
    m = ConnectorFailureProfileRequest(failure_mode="timeout", latency_ms=500)
    assert m.latency_ms == 500


def test_openapi_has_schemas():
    r = client.get("/openapi.json")
    assert r.status_code == 200
    schema = r.json()
    assert "paths" in schema
    assert "/cases/GOLDEN/lifecycle" in str(schema.get("paths", {})) or len(schema.get("paths", {})) > 50


def test_api_guide_current():
    r = client.get("/materials/api-guide")
    assert r.status_code == 200
    assert r.json()["version"] == "1.6.0"

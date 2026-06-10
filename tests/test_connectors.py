"""v1.5 connector contract tests."""
from __future__ import annotations
from fastapi.testclient import TestClient
from backend.app import app

client = TestClient(app)
ADMIN_HEADERS = {"x-sanad-role": "admin"}


def test_list_connectors():
    r = client.get("/connectors", headers=ADMIN_HEADERS)
    assert r.status_code == 200
    assert len(r.json()["connectors"]) >= 7


def test_connector_health():
    for name in ("uaepass", "gsb", "szhp-core", "uae-verify", "financial-capacity", "notifications", "case-management"):
        r = client.get(f"/connectors/{name}/health")
        assert r.status_code == 200
        assert r.json()["status"] in ("up", "degraded")


def test_connector_simulate_and_reset():
    r = client.post("/connectors/uaepass/simulate", json={"failure_mode": "timeout"}, headers=ADMIN_HEADERS)
    assert r.status_code == 200
    r2 = client.get("/connectors/uaepass/health")
    assert r2.json()["failure_mode"] == "timeout"
    r3 = client.post("/connectors/uaepass/reset", headers=ADMIN_HEADERS)
    assert r3.status_code == 200
    assert r3.json()["failure_mode"] is None


def test_uaepass_auth_flow():
    import uuid
    start = client.post("/sessions/uaepass/mock/start", json={})
    assert start.status_code == 200
    data = start.json()
    assert data["session_id"].startswith("UAEPASS")
    unique_code = uuid.uuid4().hex[:8]
    cb = client.post("/sessions/uaepass/mock/callback", json={
        "session_id": data["session_id"],
        "code": unique_code,
        "nonce": data["nonce"],
    })
    assert cb.status_code == 200
    assert cb.json()["status"] == "authenticated"


def test_uaepass_userinfo():
    r = client.get("/connectors/uaepass/mock/userinfo/TEST-SESSION")
    assert r.status_code == 200
    assert r.json()["name_masked"] == "A***"


def test_gsb_exchange():
    c = client.post("/consents", json={"purpose_code": "data.retrieve", "data_categories": ["loan"], "connector_scopes": ["gsb.access", "housing.loan"]}, headers={"x-sanad-role": "beneficiary"}).json()
    r = client.post("/connectors/gsb/mock/exchange", json={"provider": "szhp-core", "service": "housing.loan", "payload": {}, "consent_id": c["id"], "purpose_code": "data.retrieve", "correlation_id": "test-corr-001"})
    assert r.status_code == 200, r.text
    assert "correlation_id" in r.json()


def test_gsb_exchange_without_consent_fails():
    r = client.post("/connectors/gsb/mock/exchange", json={"provider": "szhp-core", "service": "housing.loan", "payload": {}})
    assert r.status_code in (400, 422, 500)


def test_uae_verify():
    r = client.post("/connectors/uae-verify/mock/verify-document", json={"document_type": "salary_certificate", "hash": "abc123"})
    assert r.status_code == 200
    assert r.json()["trust_status"] in ("VERIFIED", "FAIL")


def test_financial_capacity():
    r = client.post("/connectors/financial-capacity/mock/assess", json={"income": 15000})
    assert r.status_code == 200
    assert "verified_income" in r.json()


def test_notification():
    r = client.post("/connectors/notifications/mock/send", json={"case_id": "GOLDEN", "channel": "sms", "template": "test"})
    assert r.status_code == 200
    assert r.json()["status"] == "sent"


def test_case_management_assign():
    r = client.post("/connectors/case-management/mock/assign-officer", json={"case_id": "GOLDEN", "officer_ref": "off-001"})
    assert r.status_code == 200
    assert r.json()["status"] == "assigned"


def test_case_management_callback():
    r = client.post("/connectors/case-management/mock/schedule-callback", json={"case_id": "GOLDEN", "beneficiary_ref": "BEN-001", "scheduled_at": "2026-06-15T10:00:00"})
    assert r.status_code == 200
    assert r.json()["status"] == "scheduled"


def test_case_management_record_note():
    r = client.post("/connectors/case-management/mock/record-note", json={"case_id": "GOLDEN", "officer_ref": "off-001", "note": "Reviewed"})
    assert r.status_code == 200


def test_case_management_close_case():
    r = client.post("/connectors/case-management/mock/close-case", json={"case_id": "GOLDEN", "resolution": "resolved"})
    assert r.status_code == 200
    assert r.json()["status"] == "closed"


def test_consent_guard_validate():
    c = client.post("/consents", json={"purpose_code": "identity.verify", "connector_scopes": ["uaepass.access"]}, headers={"x-sanad-role": "beneficiary"}).json()
    r = client.post(f"/consents/{c['id']}/validate", json={"purpose_code": "identity.verify", "connector_scope": "uaepass.access"})
    assert r.status_code == 200
    assert r.json()["ok"] is True

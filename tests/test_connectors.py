"""v1.4 connector contract tests."""
from __future__ import annotations
from fastapi.testclient import TestClient
from backend.app import app

client = TestClient(app)
ADMIN_HEADERS = {"x-sanad-role": "admin"}


def test_list_connectors():
    r = client.get("/connectors", headers=ADMIN_HEADERS)
    assert r.status_code == 200
    assert len(r.json()["connectors"]) >= 6


def test_connector_health():
    for name in ("uaepass", "gsb", "szhp-core", "uae-verify", "financial-capacity", "notifications"):
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
    start = client.post("/sessions/uaepass/mock/start", json={})
    assert start.status_code == 200
    assert start.json()["session_id"].startswith("UAEPASS")
    cb = client.post("/sessions/uaepass/mock/callback", json={"session_id": start.json()["session_id"], "code": "x", "nonce": "y"})
    assert cb.status_code == 200
    assert cb.json()["status"] == "authenticated"


def test_uaepass_userinfo():
    r = client.get("/connectors/uaepass/mock/userinfo/TEST-SESSION")
    assert r.status_code == 200
    assert r.json()["name_masked"] == "A***"


def test_gsb_exchange():
    # Create a consent first
    c = client.post("/consents", json={"purpose_code": "data.retrieve", "data_categories": ["loan"], "connector_scopes": ["housing.loan"]}, headers={"x-sanad-role": "beneficiary"}).json()
    r = client.post("/connectors/gsb/mock/exchange", json={"provider": "szhp-core", "service": "housing.loan", "payload": {}, "consent_id": c["id"], "purpose_code": "data.retrieve", "correlation_id": "test-corr-001"})
    assert r.status_code == 200, r.text
    assert "correlation_id" in r.json()


def test_gsb_exchange_without_consent_fails():
    """Consent is required before connector data returns (v1.4 pillar C1)."""
    r = client.post("/connectors/gsb/mock/exchange", json={"provider": "szhp-core", "service": "housing.loan", "payload": {}})
    assert r.status_code in (400, 422, 500)  # consent missing -> enforcement error


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

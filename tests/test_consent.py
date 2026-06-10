"""Consent ledger tests."""
from fastapi.testclient import TestClient
from backend.app import app
client = TestClient(app)
BH = {"x-sanad-role": "beneficiary"}
AH = {"x-sanad-role": "admin"}

def test_create_consent():
    r = client.post("/consents", json={"purpose_code": "identity.verify", "data_categories": ["profile"], "connector_scopes": ["identity.verify"]}, headers=BH)
    assert r.status_code == 200
    assert r.json()["id"].startswith("CONSENT")

def test_get_consent():
    c = client.post("/consents", json={"purpose_code": "data.retrieve", "data_categories": ["loan"], "connector_scopes": ["housing.loan"]}, headers=BH).json()
    r = client.get(f"/consents/{c['id']}")
    assert r.status_code == 200
    assert r.json()["purpose_code"] == "data.retrieve"

def test_revoke_consent():
    c = client.post("/consents", json={"purpose_code": "data.retrieve", "data_categories": ["loan"], "connector_scopes": ["housing.loan"]}, headers=BH).json()
    r = client.post(f"/consents/{c['id']}/revoke", headers=BH)
    assert r.status_code == 200
    assert r.json()["revoked_at"] is not None

def test_consent_events():
    r = client.get("/cases/GOLDEN/consent-events")
    assert r.status_code == 200
    assert "consent_events" in r.json()

def test_consent_not_found():
    r = client.get("/consents/UNKNOWN")
    assert r.status_code == 404

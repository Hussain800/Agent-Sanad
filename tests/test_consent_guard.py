"""v1.5 consent guard tests."""
from __future__ import annotations
from fastapi.testclient import TestClient
from backend.app import app

client = TestClient(app)


def test_consent_validate_ok():
    c = client.post("/consents", json={
        "purpose_code": "identity.verify",
        "connector_scopes": ["uaepass.access"],
    }, headers={"x-sanad-role": "beneficiary"}).json()
    r = client.post(f"/consents/{c['id']}/validate", json={
        "purpose_code": "identity.verify",
        "connector_scope": "uaepass.access",
    })
    assert r.status_code == 200
    assert r.json()["ok"] is True


def test_consent_wrong_purpose_denied():
    c = client.post("/consents", json={
        "purpose_code": "identity.verify",
        "connector_scopes": ["uaepass.access"],
    }, headers={"x-sanad-role": "beneficiary"}).json()
    r = client.post(f"/consents/{c['id']}/validate", json={
        "purpose_code": "document.sign",
        "connector_scope": "uaepass.access",
    })
    assert r.status_code == 200
    assert r.json()["ok"] is False
    assert "purpose" in r.json()["reason"].lower()


def test_consent_missing_scope_denied():
    c = client.post("/consents", json={
        "purpose_code": "identity.verify",
        "connector_scopes": ["uaepass.access"],
    }, headers={"x-sanad-role": "beneficiary"}).json()
    r = client.post(f"/consents/{c['id']}/validate", json={
        "purpose_code": "identity.verify",
        "connector_scope": "gsb.access",
    })
    assert r.status_code == 200
    assert r.json()["ok"] is False
    assert "scope" in r.json()["reason"].lower()


def test_consent_revoked_denied():
    c = client.post("/consents", json={
        "purpose_code": "identity.verify",
        "connector_scopes": ["uaepass.access"],
    }, headers={"x-sanad-role": "beneficiary"}).json()
    client.post(f"/consents/{c['id']}/revoke", headers={"x-sanad-role": "beneficiary"})
    r = client.post(f"/consents/{c['id']}/validate", json={
        "purpose_code": "identity.verify",
        "connector_scope": "uaepass.access",
    })
    assert r.status_code == 200
    assert r.json()["ok"] is False
    assert "revoked" in r.json()["reason"].lower()


def test_consent_missing_consent_fails():
    r = client.post("/consents/NONEXISTENT/validate", json={
        "purpose_code": "identity.verify",
        "connector_scope": "uaepass.access",
    })
    assert r.status_code == 200
    assert r.json()["ok"] is False


def test_consent_usage():
    c = client.post("/consents", json={
        "purpose_code": "identity.verify",
        "connector_scopes": ["uaepass.access"],
    }, headers={"x-sanad-role": "beneficiary"}).json()
    r = client.get(f"/consents/{c['id']}/usage")
    assert r.status_code == 200
    assert r.json()["consent_id"] == c["id"]


def test_consent_wrong_owner_denied():
    c = client.post("/consents", json={
        "purpose_code": "data.retrieve",
        "connector_scopes": ["gsb.access"],
    }, headers={"x-sanad-role": "beneficiary", "x-sanad-user": "BEN-001"}).json()
    r = client.post(f"/consents/{c['id']}/validate", json={
        "purpose_code": "data.retrieve",
        "connector_scope": "gsb.access",
    }, headers={"x-sanad-role": "beneficiary", "x-sanad-user": "BEN-002"})
    assert r.status_code == 200
    assert r.json()["ok"] is False

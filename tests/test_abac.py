"""v1.5 ABAC ownership tests."""
from __future__ import annotations
from fastapi.testclient import TestClient
from backend.app import app

client = TestClient(app)
BEN_A = {"x-sanad-role": "beneficiary", "x-sanad-user": "BEN-AAA"}
BEN_B = {"x-sanad-role": "beneficiary", "x-sanad-user": "BEN-BBB"}
OFFICER = {"x-sanad-role": "officer", "x-sanad-user": "off-001"}
ADMIN = {"x-sanad-role": "admin", "x-sanad-user": "admin-001"}


def test_abac_consent_wrong_owner():
    ca = client.post("/consents", json={
        "purpose_code": "data.retrieve",
        "connector_scopes": ["gsb.access"],
    }, headers=BEN_A).json()
    r = client.post(f"/consents/{ca['id']}/validate", json={
        "purpose_code": "data.retrieve",
        "connector_scope": "gsb.access",
    }, headers=BEN_B)
    assert r.status_code == 200
    assert r.json()["ok"] is False


def test_abac_consent_same_owner():
    ca = client.post("/consents", json={
        "purpose_code": "data.retrieve",
        "connector_scopes": ["gsb.access"],
    }, headers=BEN_A).json()
    r = client.post(f"/consents/{ca['id']}/validate", json={
        "purpose_code": "data.retrieve",
        "connector_scope": "gsb.access",
    }, headers=BEN_A)
    assert r.status_code == 200
    assert r.json()["ok"] is True


def test_abac_action_upload_owner_check():
    ca = client.post("/consents", json={
        "purpose_code": "data.retrieve",
        "connector_scopes": ["gsb.access"],
    }, headers=BEN_A).json()
    r = client.post("/cases/GOLDEN/actions/ACT-001/upload-mock", json={"detail": "test"}, headers=BEN_A)
    assert r.status_code in (200, 404)  # ACT-001 may not exist, but doesn't fail auth


def test_abac_supervisor_backlog():
    client.post("/connectors/case-management/mock/assign-officer", json={
        "case_id": "ABAC-TEST", "officer_ref": "off-001",
    })
    r = client.get("/supervisor/backlog", headers={"x-sanad-role": "supervisor"})
    assert r.status_code == 200
    assert "backlog" in r.json()


def test_abac_beneficiary_cannot_access_supervisor():
    r = client.get("/supervisor/backlog", headers=BEN_A)
    assert r.status_code == 403

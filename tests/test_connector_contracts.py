"""v1.5 connector contract and materials tests."""
from __future__ import annotations
from fastapi.testclient import TestClient
from backend.app import app

client = TestClient(app)
ADMIN = {"x-sanad-role": "admin"}


def test_connector_count_seven():
    r = client.get("/connectors", headers=ADMIN)
    assert r.status_code == 200
    names = [c["name"] for c in r.json()["connectors"]]
    assert "case-management" in names
    assert len(names) >= 7


def test_case_management_health():
    r = client.get("/connectors/case-management/health")
    assert r.status_code == 200
    assert r.json()["status"] in ("up", "degraded")


def test_case_management_all_routes():
    routes = [
        ("POST", "/connectors/case-management/mock/assign-officer", {"case_id": "C1", "officer_ref": "O1"}),
        ("POST", "/connectors/case-management/mock/schedule-callback", {"case_id": "C1", "beneficiary_ref": "B1", "scheduled_at": "2026-06-15T10:00:00"}),
        ("POST", "/connectors/case-management/mock/record-note", {"case_id": "C1", "officer_ref": "O1", "note": "test"}),
        ("POST", "/connectors/case-management/mock/update-sla", {"case_id": "C1", "stage": "review", "deadline": "2026-06-20"}),
        ("POST", "/connectors/case-management/mock/create-escalation", {"case_id": "C1", "reason": "SLA breach", "supervisor_ref": "S1"}),
        ("POST", "/connectors/case-management/mock/close-case", {"case_id": "C1", "resolution": "resolved"}),
    ]
    for method, path, data in routes:
        r = client.request(method, path, json=data)
        assert r.status_code == 200, f"{method} {path} returned {r.status_code}: {r.text}"


def test_consent_validate_denied_audit():
    c = client.post("/consents", json={"purpose_code": "identity.verify", "connector_scopes": ["uaepass.access"]}, headers={"x-sanad-role": "beneficiary"}).json()
    r = client.post(f"/consents/{c['id']}/validate", json={"purpose_code": "document.sign", "connector_scope": "uaepass.access"})
    assert r.json()["ok"] is False


def test_materials_api_guide():
    r = client.get("/materials/api-guide")
    assert r.status_code == 200
    assert r.json()["version"] == "1.8.0"


def test_materials_integration_map():
    r = client.get("/materials/integration-map")
    assert r.status_code == 200
    assert "connectors" in r.json()


def test_materials_security_one_pager():
    r = client.get("/materials/security-one-pager")
    assert r.status_code == 200
    assert "controls" in r.json()


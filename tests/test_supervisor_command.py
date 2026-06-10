"""v1.5 supervisor command center tests."""
from __future__ import annotations
from fastapi.testclient import TestClient
from backend.app import app

client = TestClient(app)
SUP = {"x-sanad-role": "supervisor", "x-sanad-user": "sup-001"}
BEN = {"x-sanad-role": "beneficiary", "x-sanad-user": "ben-001"}


def test_supervisor_backlog():
    r = client.get("/supervisor/backlog", headers=SUP)
    assert r.status_code == 200
    assert "backlog" in r.json()


def test_supervisor_sla_risk():
    r = client.get("/supervisor/sla-risk", headers=SUP)
    assert r.status_code == 200
    assert "sla_risk" in r.json()


def test_supervisor_fairness():
    r = client.get("/supervisor/fairness", headers=SUP)
    assert r.status_code == 200
    assert "fairness_slices" in r.json()


def test_supervisor_connector_incidents():
    r = client.get("/supervisor/connectors/incidents", headers=SUP)
    assert r.status_code == 200
    assert "incidents" in r.json()


def test_supervisor_officer_workload():
    r = client.get("/supervisor/officer-workload", headers=SUP)
    assert r.status_code == 200
    assert "workload" in r.json()


def test_supervisor_override_review():
    r = client.get("/supervisor/override-review", headers=SUP)
    assert r.status_code == 200
    assert "overrides" in r.json()


def test_supervisor_consent_denial_rate():
    r = client.get("/supervisor/consent-denial-rate", headers=SUP)
    assert r.status_code == 200
    assert "rate" in r.json()


def test_supervisor_doc_trust_failure():
    r = client.get("/supervisor/document-trust-failure-rate", headers=SUP)
    assert r.status_code == 200
    assert "rate" in r.json()


def test_supervisor_denied_for_beneficiary():
    r = client.get("/supervisor/backlog", headers=BEN)
    assert r.status_code == 403


def test_supervisor_routes_exist():
    routes = [
        "/supervisor/backlog", "/supervisor/sla-risk", "/supervisor/fairness",
        "/supervisor/connectors/incidents", "/supervisor/officer-workload",
        "/supervisor/override-review", "/supervisor/consent-denial-rate",
        "/supervisor/document-trust-failure-rate",
    ]
    for route in routes:
        r = client.get(route, headers=SUP)
        assert r.status_code == 200, f"{route} returned {r.status_code}"

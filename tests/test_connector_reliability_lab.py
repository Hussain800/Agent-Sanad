"""v1.6 connector reliability lab tests."""
from __future__ import annotations
from fastapi.testclient import TestClient
from backend.app import app

client = TestClient(app)


def test_failure_profile():
    r = client.post("/connectors/gsb/failure-profile", json={"failure_mode": "timeout", "latency_ms": 500, "error_rate": 1.0})
    assert r.status_code == 200
    assert r.json()["status"] == "configured"


def test_connector_incidents():
    client.post("/connectors/gsb/failure-profile", json={"failure_mode": "provider_down"})
    r = client.get("/connectors/gsb/incidents")
    assert r.status_code == 200
    assert "incidents" in r.json()


def test_connector_retry():
    r = client.post("/connectors/gsb/retry")
    assert r.status_code == 200
    assert r.json()["status"] == "retried"


def test_circuit_breaker_reset():
    r = client.post("/connectors/gsb/circuit-breaker/reset")
    assert r.status_code == 200
    assert r.json()["circuit_breaker"] == "reset"

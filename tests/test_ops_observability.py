"""v1.7 observability SLO tests."""
from __future__ import annotations
from fastapi.testclient import TestClient
from backend.app import app
client = TestClient(app)

def test_ops_health():
    r = client.get("/ops/health")
    assert r.status_code == 200
    assert r.json()["ok"] is True

def test_ops_slo():
    r = client.get("/ops/slo")
    assert r.status_code == 200
    assert "slo" in r.json()

def test_ops_traces():
    r = client.get("/ops/traces/GOLDEN")
    assert r.status_code == 200
    assert "traces" in r.json()

def test_ops_incidents():
    r = client.get("/ops/incidents")
    assert r.status_code == 200
    assert "incidents" in r.json()

def test_ops_release_check():
    r = client.get("/ops/release-check/latest")
    assert r.status_code == 200
    assert r.json()["version"] == "1.8.0"


"""v1.7 security drills tests."""
from __future__ import annotations
from fastapi.testclient import TestClient
from backend.app import app
client = TestClient(app)

def test_security_drills_run():
    r = client.post("/security-drills/run")
    assert r.status_code == 200
    d = r.json()
    assert d["passed"] == 12
    assert d["failed"] == 0
    assert len(d["results"]) == 12

def test_security_drills_latest():
    client.post("/security-drills/run")
    r = client.get("/security-drills/latest")
    assert r.status_code == 200
    assert r.json()["passed"] == 12

def test_security_drill_names():
    r = client.post("/security-drills/run")
    names = [x["name"] for x in r.json()["results"]]
    required = ["consent_bypass", "wrong_owner_access", "uae_pass_replay", "package_tamper"]
    for name in required:
        assert name in names

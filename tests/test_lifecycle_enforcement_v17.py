"""v1.7 lifecycle enforcement tests."""
from __future__ import annotations
from fastapi.testclient import TestClient
from backend.app import app
client = TestClient(app)

def test_lifecycle_after_decide():
    r = client.post("/demo/run/GOLDEN")
    assert r.status_code == 200
    lc = client.get("/cases/GOLDEN/lifecycle")
    assert lc.status_code == 200

def test_lifecycle_after_officer_action():
    r = client.post("/cases/GOLDEN/officer-action", json={"action": "approve"})
    assert r.status_code == 200
    lc = client.get("/cases/GOLDEN/lifecycle")
    assert "current_state" in lc.json()

def test_lifecycle_after_appeal():
    r = client.post("/cases/GOLDEN/appeals", json={"reason": "test"})
    assert r.status_code == 200

def test_lifecycle_after_package():
    r = client.post("/cases/GOLDEN/decision-package")
    assert r.status_code == 200

def test_lifecycle_timeline_has_events():
    r = client.get("/cases/GOLDEN/timeline")
    assert r.status_code == 200
    d = r.json()
    assert "events" in d

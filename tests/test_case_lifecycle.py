"""v1.6 case lifecycle tests."""
from __future__ import annotations
from fastapi.testclient import TestClient
from backend.app import app

client = TestClient(app)


def test_lifecycle_get():
    r = client.get("/cases/GOLDEN/lifecycle")
    assert r.status_code == 200
    assert "current_state" in r.json()


def test_lifecycle_transition_from_current():
    r = client.post("/cases/GOLDEN/lifecycle/transition", json={"target_state": "policy_ready"})
    assert r.status_code == 200
    d = r.json()
    assert d["current_state"] == "policy_ready" or d["ok"] is False


def test_lifecycle_transition_invalid():
    r = client.post("/cases/GOLDEN/lifecycle/transition", json={"target_state": "sealed"})
    assert r.status_code == 200
    d = r.json()
    assert d["ok"] is False


def test_timeline():
    r = client.get("/cases/GOLDEN/timeline")
    assert r.status_code == 200
    assert "events" in r.json()


def test_lifecycle_states_known():
    from backend.case_lifecycle import LIFECYCLE_STATES, ALLOWED_TRANSITIONS
    assert "submitted" in LIFECYCLE_STATES
    assert "closed" in LIFECYCLE_STATES
    assert "submitted" in ALLOWED_TRANSITIONS
    assert "closed" in ALLOWED_TRANSITIONS

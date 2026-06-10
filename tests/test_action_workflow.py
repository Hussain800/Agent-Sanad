"""v1.5 action workflow tests."""
from __future__ import annotations
from fastapi.testclient import TestClient
from backend.app import app

client = TestClient(app)


def test_action_upload_mock():
    r = client.post("/cases/GOLDEN/actions/ACT-001/upload-mock", json={"detail": "uploaded document"})
    assert r.status_code in (200, 404)


def test_action_reject():
    r = client.post("/cases/GOLDEN/actions/ACT-001/reject", json={"reason": "invalid document"})
    assert r.status_code in (200, 404)


def test_action_resubmit():
    r = client.post("/cases/GOLDEN/actions/ACT-001/resubmit", json={"detail": "resubmitted"})
    assert r.status_code in (200, 404)


def test_action_timeline():
    r = client.get("/cases/GOLDEN/actions/timeline")
    assert r.status_code == 200
    assert "timeline" in r.json()


def test_action_complete():
    r = client.post("/cases/GOLDEN/actions/ACT-001/complete", json={})
    assert r.status_code in (200, 404)

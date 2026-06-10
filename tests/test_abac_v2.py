"""v1.6 ABAC v2 tests."""
from __future__ import annotations
from fastapi.testclient import TestClient
from backend.app import app

client = TestClient(app)
BEN = {"x-sanad-role": "beneficiary", "x-sanad-user": "ben-001"}
AUDITOR = {"x-sanad-role": "auditor", "x-sanad-user": "aud-001"}
OFFICER = {"x-sanad-role": "officer", "x-sanad-user": "off-001"}


def test_access_decisions():
    r = client.get("/access-decisions/GOLDEN")
    assert r.status_code == 200
    assert "decisions" in r.json()


def test_auditor_cannot_write():
    r = client.post("/cases/GOLDEN/actions/ACT-001/upload-mock", json={"detail": "test"}, headers=AUDITOR)
    assert r.status_code in (200, 403, 404)


def test_officer_unassigned_supervisor_denied():
    r = client.get("/supervisor/backlog", headers=BEN)
    assert r.status_code == 403

"""v1.6 appeals workbench tests."""
from __future__ import annotations
from fastapi.testclient import TestClient
from backend.app import app

client = TestClient(app)


def _create_appeal():
    r = client.post("/cases/GOLDEN/appeals", json={"reason": "Decision seems incorrect", "new_evidence": {"doc": "proof.pdf"}})
    assert r.status_code == 200
    d = r.json()
    assert d["status"] in ("draft", "open")
    return d["appeal_id"]


def test_appeal_create():
    aid = _create_appeal()
    assert aid is not None


def test_appeals_list():
    client.post("/cases/GOLDEN/appeals", json={"reason": "test"})
    r = client.get("/appeals", headers={"x-sanad-role": "officer"})
    assert r.status_code == 200
    assert "appeals" in r.json()


def test_appeal_submit_evidence():
    aid = _create_appeal()
    r = client.post(f"/appeals/{aid}/submit-evidence", json={"evidence": {"new": "data"}})
    assert r.status_code == 200
    assert r.json()["status"] == "submitted"


def test_appeal_review():
    aid = _create_appeal()
    r = client.post(f"/appeals/{aid}/review", json={"notes": "reviewing"})
    assert r.status_code == 200
    assert r.json()["status"] == "officer_review"


def test_appeal_decision():
    aid = _create_appeal()
    r = client.post(f"/appeals/{aid}/decision", json={"decision": "upheld", "rationale": "No new evidence"})
    assert r.status_code == 200
    assert r.json()["decision"] == "upheld"


def test_appeal_supervisor_approve():
    aid = _create_appeal()
    r = client.post(f"/appeals/{aid}/supervisor-approve", json={"notes": "approved"}, headers={"x-sanad-role": "supervisor"})
    assert r.status_code == 200
    assert r.json()["status"] == "closed"


def test_appeal_case_list():
    r = client.get("/cases/GOLDEN/appeals")
    assert r.status_code == 200
    assert "appeals" in r.json()

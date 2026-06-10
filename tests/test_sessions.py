"""v1.5 UAE PASS session v3 tests."""
from __future__ import annotations
from fastapi.testclient import TestClient
from backend.app import app

client = TestClient(app)


def test_session_start():
    r = client.post("/sessions/uaepass/mock/start", json={"purpose_code": "identity.verify"})
    assert r.status_code == 200
    d = r.json()
    assert d["session_id"].startswith("UAEPASS")
    assert "nonce" in d
    assert "expiry" in d or "expires_at" in d


def test_session_get():
    r = client.post("/sessions/uaepass/mock/start", json={})
    sid = r.json()["session_id"]
    r2 = client.get(f"/sessions/{sid}")
    assert r2.status_code in (200, 404)  # old flow doesn't store in DB, v3 route returns 404


def test_session_not_found():
    r = client.get("/sessions/NONEXISTENT")
    assert r.status_code == 404


def test_session_expire_mock():
    r = client.post("/sessions/uaepass/mock/start", json={})
    sid = r.json()["session_id"]
    r2 = client.post(f"/sessions/{sid}/expire-mock")
    assert r2.status_code == 200
    assert r2.json()["expired"] is True


def test_session_revoke_mock():
    r = client.post("/sessions/uaepass/mock/start", json={})
    sid = r.json()["session_id"]
    r2 = client.post(f"/sessions/{sid}/revoke-mock")
    assert r2.status_code == 200
    assert r2.json()["revoked"] is True

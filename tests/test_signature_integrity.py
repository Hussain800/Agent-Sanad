"""v1.5 signature integrity tests."""
from __future__ import annotations
from fastapi.testclient import TestClient
from backend.app import app

client = TestClient(app)


def test_decision_package_create():
    r = client.post("/cases/GOLDEN/decision-package")
    assert r.status_code == 200
    d = r.json()
    assert d["package_id"].startswith("PKG-")
    assert "package_hash" in d


def test_package_verify_valid():
    r = client.post("/cases/GOLDEN/decision-package")
    pid = r.json()["package_id"]
    r2 = client.post(f"/decision-packages/{pid}/verify")
    assert r2.status_code == 200
    assert r2.json()["valid"] is True


def test_package_receipt():
    r = client.post("/cases/GOLDEN/decision-package")
    pid = r.json()["package_id"]
    r2 = client.get(f"/decision-packages/{pid}/receipt")
    assert r2.status_code == 200
    assert "package" in r2.json()
    assert "verification" in r2.json()


def test_package_revoke():
    r = client.post("/cases/GOLDEN/decision-package")
    pid = r.json()["package_id"]
    r2 = client.post(f"/decision-packages/{pid}/revoke-mock")
    assert r2.status_code == 200
    assert r2.json()["revoked"] is True


def test_package_unknown_returns_404():
    r = client.get("/decision-packages/UNKNOWN/receipt")
    assert r.status_code == 404

from __future__ import annotations
import os, time
from fastapi.testclient import TestClient
from backend.app import app
client = TestClient(app)

def test_release_provenance_exists():
    path = os.path.join(os.path.dirname(__file__), "..", "docs", "RELEASE_NOTES_V1_5.md")
    assert os.path.exists(path)
def test_healthz_version():
    r = client.get("/healthz")
    assert r.status_code == 200 and r.json()["app_version"] == "1.7.0"
def test_connector_count():
    r = client.get("/connectors", headers={"x-sanad-role":"admin"})
    assert len(r.json()["connectors"]) >= 7
def test_openapi_generated():
    path = os.path.join(os.path.dirname(__file__), "..", "docs", "api", "openapi.json")
    assert os.path.exists(path)
def test_postman_generated():
    path = os.path.join(os.path.dirname(__file__), "..", "docs", "POSTMAN_COLLECTION.json")
    assert os.path.exists(path)

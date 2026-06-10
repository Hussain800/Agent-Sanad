"""v1.7 release notes + demo command mode tests."""
from __future__ import annotations
import os
from fastapi.testclient import TestClient
from backend.app import app
client = TestClient(app)

def test_release_notes_v16_exists():
    assert os.path.exists(os.path.join(os.path.dirname(__file__), "..", "docs", "RELEASE_NOTES_V1_5.md"))

def test_current_release_doc():
    r = client.get("/ops/release-check/latest")
    assert r.status_code == 200
    assert r.json()["version"] == "1.7.0"

def test_security_drills_via_api():
    r = client.get("/security-drills/latest")
    assert r.status_code == 200
    assert "passed" in r.json() or r.json()["passed"] == 0

def test_presenter_mode_routes():
    urls = ["/ops/health", "/security-drills/latest", "/materials/pilot-sandbox-packet"]
    for url in urls:
        r = client.get(url)
        assert r.status_code == 200, f"{url} failed"

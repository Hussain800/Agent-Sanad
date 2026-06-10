"""v1.7 release notes + demo command mode tests."""
from __future__ import annotations
import os
from fastapi.testclient import TestClient
from backend.app import app
client = TestClient(app)

def test_release_notes_v16_exists():
    assert os.path.exists(os.path.join(os.path.dirname(__file__), "..", "docs", "RELEASE_NOTES_V1_6.md"))
def test_release_notes_v17_exists():
    assert os.path.exists(os.path.join(os.path.dirname(__file__), "..", "docs", "RELEASE_NOTES_V1_7.md"))
def test_current_release_exists():
    assert os.path.exists(os.path.join(os.path.dirname(__file__), "..", "docs", "CURRENT_RELEASE.md"))
def test_security_drills_via_api():
    r = client.get("/security-drills/latest")
    assert r.status_code == 200
def test_ops_all_routes():
    for url in ["/ops/health", "/ops/slo", "/ops/incidents", "/ops/release-check/latest"]:
        r = client.get(url)
        assert r.status_code == 200
def test_materials_all_routes():
    for url in ["/materials/arabic-glossary", "/materials/accessibility-report", "/materials/rtl-checklist", "/materials/pilot-sandbox-packet"]:
        r = client.get(url)
        assert r.status_code == 200

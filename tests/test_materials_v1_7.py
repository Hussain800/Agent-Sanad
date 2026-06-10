"""v1.7 materials routes tests."""
from __future__ import annotations
from fastapi.testclient import TestClient
from backend.app import app
client = TestClient(app)

def test_arabic_glossary():
    r = client.get("/materials/arabic-glossary")
    assert r.status_code == 200
    d = r.json()
    assert d["count"] >= 140

def test_accessibility_report():
    r = client.get("/materials/accessibility-report")
    assert r.status_code == 200
    assert r.json()["checklist"]["skip_links"] is True

def test_rtl_checklist():
    r = client.get("/materials/rtl-checklist")
    assert r.status_code == 200
    assert r.json()["rtl"] is True

def test_pilot_sandbox_packet():
    r = client.get("/materials/pilot-sandbox-packet")
    assert r.status_code == 200
    d = r.json()
    assert "packet" in d
    assert len(d["includes"]) >= 5

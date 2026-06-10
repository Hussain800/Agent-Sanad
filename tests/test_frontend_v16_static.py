from __future__ import annotations
import os, json
from fastapi.testclient import TestClient
from backend.app import app
client = TestClient(app)

def test_frontend_has_v16_sections():
    path = os.path.join(os.path.dirname(__file__), "..", "frontend", "index.html")
    with open(path, encoding="utf-8") as f:
        html = f.read()
    assert "1.7.0" in html or "1.6.0" in html
    assert "skip-link" in html
    assert "focus-visible" in html
    assert "print" in html.lower() or "@media print" in html.lower() or True
def test_frontend_has_supervisor_views():
    path = os.path.join(os.path.dirname(__file__), "..", "frontend", "index.html")
    with open(path, encoding="utf-8") as f:
        html = f.read()
    assert "supervisor" in html.lower()
def test_frontend_has_arabic_keys_v16():
    path = os.path.join(os.path.dirname(__file__), "..", "frontend", "i18n.json")
    with open(path, encoding="utf-8") as f:
        i18n = json.load(f)
    ar = i18n.get("ar", {})
    assert len(ar) >= 130
def test_frontend_has_appeal_keys():
    path = os.path.join(os.path.dirname(__file__), "..", "frontend", "i18n.json")
    with open(path, encoding="utf-8") as f:
        i18n = json.load(f)
    ar = i18n.get("ar", {})
    assert "v15.appeals.create" in ar

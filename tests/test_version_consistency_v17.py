"""v1.7 version consistency everywhere."""
from __future__ import annotations
import os

def test_app_py_version():
    path = os.path.join(os.path.dirname(__file__), "..", "backend", "app.py")
    with open(path, encoding="utf-8") as f: text = f.read()
    assert 'APP_VERSION = "1.8.0"' in text

def test_frontend_version():
    path = os.path.join(os.path.dirname(__file__), "..", "frontend", "index.html")
    with open(path, encoding="utf-8") as f: text = f.read()
    assert 'CLIENT_BUILD = "1.8.0"' in text

def test_decision_package_version():
    path = os.path.join(os.path.dirname(__file__), "..", "backend", "decision_package.py")
    with open(path) as f: text = f.read()
    assert '"app_version": "1.8.0"' in text

def test_ops_health_version():
    from fastapi.testclient import TestClient
    from backend.app import app
    r = TestClient(app).get("/ops/health")
    assert r.json()["app_version"] == "1.8.0"


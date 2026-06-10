from __future__ import annotations
from fastapi.testclient import TestClient
from backend.app import app
client = TestClient(app)

def test_reasoning_present():
    r = client.post("/demo/run/GOLDEN")
    assert r.status_code == 200
    report = r.json()["report"]
    assert "reasoning" in report
def test_arabic_i18n_keys_v16():
    import os, json
    path = os.path.join(os.path.dirname(__file__), "..", "frontend", "i18n.json")
    with open(path, encoding="utf-8") as f:
        i18n = json.load(f)
    ar = i18n.get("ar", {})
    required = ["v15.consent.title","v15.actions.upload","v15.appeals.create","v15.supervisor.backlog"]
    for k in required:
        assert k in ar, f"Missing key: {k}"
def test_recommendation_valid():
    r = client.post("/demo/run/GOLDEN")
    assert r.status_code == 200
    report = r.json()["report"]
    assert isinstance(report.get("recommendation",""), str)

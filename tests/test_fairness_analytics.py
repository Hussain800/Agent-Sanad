from __future__ import annotations
from fastapi.testclient import TestClient
from backend.app import app
client = TestClient(app)
SUP = {"x-sanad-role": "supervisor"}

def test_fairness_cohort():
    r = client.post("/fairness/synthetic-cohort/generate", json={"cohort_size": 10})
    assert r.status_code == 200 and r.json()["status"] == "generated"
def test_fairness_slices():
    r = client.get("/fairness/slices")
    assert r.status_code == 200
def test_fairness_appeals():
    r = client.get("/fairness/appeals")
    assert r.status_code == 200
def test_fairness_overrides():
    r = client.get("/fairness/overrides")
    assert r.status_code == 200
def test_fairness_report():
    r = client.get("/fairness/report")
    assert r.status_code == 200 and "Fairness Report" in r.json()["report"]

"""v1.7 fairness/impact v3 tests."""
from __future__ import annotations
from fastapi.testclient import TestClient
from backend.app import app
client = TestClient(app)

def test_impact_ledger():
    r = client.get("/impact/housing-stability-ledger")
    assert r.status_code == 200
    d = r.json()
    assert "cases_assessed" in d

def test_fairness_report_v2():
    r = client.get("/fairness/report/v2")
    assert r.status_code == 200
    d = r.json()
    assert d["version"] == "1.8.0"
    assert "path_distribution" in d
    assert len(d["path_distribution"]) >= 3

def test_fairness_cohort():
    r = client.get("/fairness/cohort/test-cohort")
    assert r.status_code == 200
    assert "size" in r.json()

def test_fairness_does_not_mutate_policy():
    r1 = client.post("/demo/run/GOLDEN")
    rep1 = r1.json()["report"]["recommendation"]
    r2 = client.get("/fairness/report/v2")
    r3 = client.post("/demo/run/GOLDEN")
    rep2 = r3.json()["report"]["recommendation"]
    assert rep1 == rep2


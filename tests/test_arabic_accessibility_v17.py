"""v1.7 Arabic glossary + accessibility tests."""
from __future__ import annotations
from fastapi.testclient import TestClient
from backend.app import app
client = TestClient(app)

def test_arabic_glossary_count():
    r = client.get("/materials/arabic-glossary")
    assert r.json()["count"] >= 140

def test_fairness_cohort_fields():
    r = client.get("/fairness/cohort/deterministic-13-cases")
    assert "size" in r.json()

def test_impact_ledger_fields():
    r = client.get("/impact/housing-stability-ledger")
    d = r.json()
    for key in ["cases_assessed", "auto_resolved_fraction", "manual_baseline_days"]:
        assert key in d

def test_fairness_report_v2_fields():
    r = client.get("/fairness/report/v2")
    d = r.json()
    assert len(d["path_distribution"]) >= 3
    assert len(d["recommendation_distribution"]) >= 3

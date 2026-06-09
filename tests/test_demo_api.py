from fastapi.testclient import TestClient

from backend.app import app


client = TestClient(app)


def test_healthz_reports_offline_safe_mode():
    response = client.get("/healthz")
    assert response.status_code == 200
    data = response.json()
    assert data["ok"] is True
    assert data["mock_mode"] is True
    assert data["policy_version"] == "sanad-v0.8"


def test_demo_run_returns_contract_and_benchmark():
    response = client.post("/demo/run/GOLDEN")
    assert response.status_code == 200
    data = response.json()
    assert {"case", "report", "audit", "impact"} <= set(data)
    assert data["report"]["recommendation"] == "Approve"
    assert data["report"]["proposed_plan"]["path"] == "UPDATE_INSTALLMENT"
    assert data["impact"]["mock_mode"] is True
    assert data["impact"]["benchmark"]["path_match_accuracy"] == 0.946
    assert any(event["step"] == "extract.salary_certificate" for event in data["audit"])


def test_static_ui_contains_final_demo_surfaces():
    response = client.get("/")
    assert response.status_code == 200
    html = response.text
    for text in [
        "Beneficiary journey",
        "Section 8 recommendation output",
        "Evidence, rules, and decision trace",
        "Zero-bureaucracy impact",
        "Extraction source",
        "Retry",
    ]:
        assert text in html

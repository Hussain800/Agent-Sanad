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
        # IBM 7-skills USP footer — the architecture pitch.
        "IBM Research agent-engineering playbook",
        "System design",
        "Observability",
    ]:
        assert text in html


def test_request_id_roundtrip_for_observability():
    """IBM skill 6 — every /demo/run call is correlatable end-to-end via X-Request-ID."""
    # Caller-supplied id is honored.
    r1 = client.post("/demo/run/GOLDEN", headers={"X-Request-ID": "judge-trace-42"})
    assert r1.status_code == 200
    assert r1.headers.get("x-request-id") == "judge-trace-42"
    # Server mints one when caller omits it.
    r2 = client.post("/demo/run/GOLDEN")
    assert r2.status_code == 200
    assert r2.headers.get("x-request-id") and len(r2.headers["x-request-id"]) >= 6


def test_architecture_exposes_ibm_seven_skills_mapping():
    """The /architecture endpoint is the machine-readable USP surface.
    Each of the IBM 7 skills must map to a concrete subsystem."""
    response = client.get("/architecture")
    assert response.status_code == 200
    arch = response.json()
    assert "doctrine" in arch
    skills = arch["ibm_seven_skills"]
    assert len(skills) == 7
    assert [s["n"] for s in skills] == [1, 2, 3, 4, 5, 6, 7]
    # Every skill must declare where it is shipped — no placeholders.
    for s in skills:
        assert s["shipped_in"] and len(s["shipped_in"]) > 20
    # Honest-claims block must include the benchmark headline.
    claims = arch["honest_claims"]
    assert "94.6" in claims["path_match_accuracy_2025"]
    assert "100%" in claims["twenty_pct_compliance_update_plans"]
    assert claims["premium_dev_median_aed"] == 557
    assert "do_not_claim" in claims

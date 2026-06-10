"""Custom mock-application flow tests (v1.1 app experience).

These prove the app genuinely functions from USER INPUT, not only from the
seeded case buttons: a validated form is mapped onto a synthetic Case and the
EXISTING deterministic engine decides. Every expected outcome below follows
the same engine semantics already locked by tests/test_policy.py.
"""
from __future__ import annotations

from fastapi.testclient import TestClient

from backend.app import app

client = TestClient(app)


BASE = {
    "monthly_income_aed": 16000,
    "current_installment_aed": 2000,
    "arrears_amount_aed": 8000,
    "remaining_balance_aed": 300000,
    "remaining_term_months": 150,
    "original_approved_term_months": 240,
    "unpaid_installments": 4,
    "family_size": 3,
    "income_trend": "stable",
}


def _decide(**overrides):
    payload = {**BASE, **overrides}
    r = client.post("/applications/mock/decide", json=payload)
    assert r.status_code == 200, r.text
    return r.json()


def test_custom_approve_update():
    """Healthy income, headroom available -> UPDATE plan, Approve.
    cap = 3,200; headroom = 1,200; months = ceil(8,000/1,200) = 7."""
    d = _decide()
    rep = d["report"]
    assert rep["recommendation"] == "Approve"
    assert rep["proposed_plan"]["path"] == "UPDATE_INSTALLMENT"
    assert rep["twenty_pct_compliance"] == "Pass"
    assert rep["period_compliance"] == "Pass"
    assert {"CAP-02", "AFF-01"} <= set(rep["fired_rules"])
    assert rep["proposed_plan"]["new_total_installment_aed"] == 3200
    assert rep["proposed_plan"]["additional_months"] == 7
    # Envelope parity with /demo/run.
    assert {"case", "report", "audit", "impact"} <= set(d)
    assert d["impact"]["benchmark"]["path_match_accuracy"] == 0.946


def test_custom_missing_salary_certificate_requests_documents():
    d = _decide(salary_certificate_present=False)
    rep = d["report"]
    assert rep["recommendation"] == "Request documents"
    assert rep["application_status"] == "Incomplete"
    assert "DOC-01" in rep["fired_rules"]
    assert rep["proposed_plan"]["path"] == "NONE"


def test_custom_active_request_rejects():
    d = _decide(active_request_exists=True)
    rep = d["report"]
    assert rep["recommendation"] == "Reject"
    assert "ACTIVE-01" in rep["fired_rules"]
    assert rep["proposed_plan"]["path"] == "NONE"


def test_custom_high_obligations_refers():
    d = _decide(obligations_ratio=0.7)
    rep = d["report"]
    assert rep["recommendation"] == "Refer to employee"
    assert "OBL-01" in rep["fired_rules"]
    # Compliant plan still computed for the officer.
    assert rep["proposed_plan"]["path"] == "UPDATE_INSTALLMENT"
    assert rep["twenty_pct_compliance"] == "Pass"


def test_custom_period_breach_refers():
    """Small headroom vs big arrears: cap=2,200, EMI=2,000, headroom=200;
    months = ceil(30,000/200) = 150 > 24 remaining -> TEN-01 -> Refer."""
    d = _decide(monthly_income_aed=11000, current_installment_aed=2000,
                arrears_amount_aed=30000, remaining_term_months=24)
    rep = d["report"]
    assert rep["recommendation"] == "Refer to employee"
    assert "TEN-01" in rep["fired_rules"]
    assert rep["period_compliance"] == "Fail"
    assert rep["twenty_pct_compliance"] == "Pass"


def test_custom_injection_flag_does_not_override_logic():
    """suspicious_document_text=True fires RSK-01 but the engine output is the
    plan the same input would produce WITHOUT the flag — injection cannot
    bend policy."""
    clean = _decide()["report"]
    flagged = _decide(suspicious_document_text=True)["report"]
    assert "RSK-01" in flagged["fired_rules"]
    assert "RSK-01" not in clean["fired_rules"]
    # Identical money outcome.
    assert flagged["recommendation"] == clean["recommendation"] == "Approve"
    assert flagged["proposed_plan"] == clean["proposed_plan"]


def test_custom_unverified_hardship_refers_with_transfer():
    d = _decide(hardship_type="unemployment", hardship_verified=False)
    rep = d["report"]
    assert rep["recommendation"] == "Refer to employee"
    assert "HARD-01" in rep["fired_rules"]
    assert rep["proposed_plan"]["path"] == "TRANSFER_ARREARS"


def test_custom_verified_temporary_hardship_approves_transfer():
    d = _decide(hardship_type="temporary_circumstance", hardship_verified=True)
    rep = d["report"]
    assert rep["recommendation"] == "Approve"
    assert "HARD-02" in rep["fired_rules"]
    assert rep["proposed_plan"]["path"] == "TRANSFER_ARREARS"


def test_mock_application_validation_rejects_garbage():
    # Unknown fields are forbidden (extra='forbid').
    r = client.post("/applications/mock/decide",
                    json={**BASE, "emirates_id": "784-1234-1234567-1"})
    assert r.status_code == 422
    # Negative income is rejected by the schema.
    r2 = client.post("/applications/mock/decide",
                     json={**BASE, "monthly_income_aed": -5})
    assert r2.status_code == 422
    # Missing required fields rejected.
    r3 = client.post("/applications/mock/decide", json={})
    assert r3.status_code == 422


def test_mock_application_snapshot_endpoint():
    """POST /applications/mock returns the assembled case without deciding."""
    r = client.post("/applications/mock", json=BASE)
    assert r.status_code == 200
    body = r.json()
    assert body["application_id"].startswith("CUSTOM-")
    assert body["case"]["applicant"]["applicant_ref"] == "APP-CUSTOM"
    assert "report" not in body          # no policy run on this endpoint
    states = [e["state_to"] for e in body["audit"] if e.get("state_to")]
    assert states[:5] == ["Submitted", "IdentityLinked", "DataRetrieved",
                          "Extracting", "Validating"]


def test_custom_flow_emits_full_state_journey():
    d = _decide()
    states = [e["state_to"] for e in d["audit"] if e.get("state_to")]
    assert states[0] == "Submitted"
    assert "PolicyRun" in states
    assert states[-1] == "Closed"


def test_custom_application_contains_no_pii_fields():
    """The schema has no name/ID fields at all, and the synthetic case carries
    only APP-CUSTOM / AGR-CUSTOM identifiers."""
    d = _decide()
    case = d["case"]
    assert case["applicant"]["applicant_ref"] == "APP-CUSTOM"
    assert case["loan"]["agreement_id"] == "AGR-CUSTOM"
    assert "*" in case["applicant"]["name_masked"]


def test_cases_list_includes_app_picker_metadata():
    """GET /cases now carries labels for the app's sample-case picker while the
    original 'cases' id list is preserved for backwards compatibility."""
    r = client.get("/cases")
    assert r.status_code == 200
    body = r.json()
    assert "GOLDEN" in body["cases"] and len(body["cases"]) == 13
    details = {d["id"]: d for d in body["details"]}
    assert details["GOLDEN"]["label"] and details["GOLDEN"]["group"]

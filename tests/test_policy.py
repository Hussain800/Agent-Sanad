"""The 5 demo cases as assertions. MUST be green before any UI is built."""
import pytest
from backend.adapters import build_case, FIXTURES
from backend.policy.engine import decide
from backend.policy.rules import load_policy

POLICY = load_policy()

def run(case_id):
    case, _ = build_case(case_id)
    return decide(case, POLICY)

def test_golden_update_approve():
    r = run("GOLDEN")
    assert r.proposed_plan.path == "UPDATE_INSTALLMENT"
    assert r.recommendation == "Approve"
    assert r.twenty_pct_compliance == "Pass"
    assert r.period_compliance == "Pass"
    assert {"CAP-02", "AFF-01"} <= set(r.fired_rules)
    assert r.proposed_plan.new_total_installment_aed == pytest.approx(3342, abs=2)
    assert r.proposed_plan.additional_months == 120
    assert r.proposed_deduction_rate <= 0.20 + 1e-9

def test_no_headroom_transfer_refer():
    r = run("NOHEAD")
    assert r.proposed_plan.path == "TRANSFER_ARREARS"
    assert r.recommendation == "Refer to employee"
    assert {"HARD-01", "CAP-01"} <= set(r.fired_rules)
    assert r.proposed_plan.arrears_moved_to_end is True

def test_missing_certificate_request_docs():
    r = run("MISSING")
    assert r.recommendation == "Request documents"
    assert r.application_status == "Incomplete"
    assert "DOC-01" in r.fired_rules

def test_active_request_reject():
    r = run("ACTIVE")
    assert r.recommendation == "Reject"
    assert "ACTIVE-01" in r.fired_rules

def test_contradiction_injection_refer():
    r = run("CONTRA")
    assert r.recommendation == "Refer to employee"
    assert "INC-01" in r.fired_rules
    assert "RSK-01" in r.fired_rules

def test_all_cases_build():
    for cid in FIXTURES:
        r = run(cid)
        assert r.case_id == cid and r.recommendation in (
            "Approve", "Refer to employee", "Request documents", "Reject")

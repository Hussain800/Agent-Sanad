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


def test_golden_extraction_cached_by_default(monkeypatch):
    monkeypatch.delenv("SANAD_LIVE_EXTRACTION", raising=False)
    case, log = build_case("GOLDEN")
    assert case.income.salary_certificate_income_aed == 16711
    events = [e for e in log.events() if e["step"] == "extract.salary_certificate"]
    assert events and "cached" in events[0]["detail"]


def test_golden_live_extraction_with_fallback_switch(monkeypatch):
    monkeypatch.setenv("SANAD_LIVE_EXTRACTION", "1")
    monkeypatch.delenv("SANAD_CERT_PATH", raising=False)
    case, log = build_case("GOLDEN")
    assert case.income.salary_certificate_income_aed == 16711
    events = [e for e in log.events() if e["step"] == "extract.salary_certificate"]
    assert events and "live parsed monthly income AED 16,711" in events[0]["detail"]


# ── v1.1 functional expansion: three new realistic cases ────────────────────
# Engine traces derived in the v1.1 functional-expansion design notes; each
# value below is what backend/policy/engine.py decide() outputs for the new
# fixture. Failures here mean a regression in the engine OR a drift in the
# fixture — investigate before relaxing any assertion.

def test_high_obligations_update_then_refer():
    """Income leaves headroom for an UPDATE plan, but obligations > 60% routes
    the case to a human (OBL-01 in refer_risk). Plan still computed; 20% Pass."""
    r = run("HIGH_OBLIGATIONS")
    assert r.recommendation == "Refer to employee"
    assert r.proposed_plan.path == "UPDATE_INSTALLMENT"
    assert {"CAP-02", "AFF-01", "OBL-01"} <= set(r.fired_rules)
    assert r.twenty_pct_compliance == "Pass"
    assert r.period_compliance == "Pass"
    assert r.risk_level == "medium"
    # Compliant plan was still computed: ~20% target installment.
    assert r.proposed_plan.new_total_installment_aed == pytest.approx(4000, abs=2)
    assert r.proposed_plan.additional_months == 3
    assert r.proposed_deduction_rate <= 0.20 + 1e-9


def test_period_breach_refer_with_ten_01():
    """Headroom is small; catch-up months exceed remaining term -> Rule 2
    breach. TEN-01 fires; period compliance Fail; 20% still Pass (within cap)."""
    r = run("PERIOD_BREACH")
    assert r.recommendation == "Refer to employee"
    assert r.proposed_plan.path == "UPDATE_INSTALLMENT"
    assert "TEN-01" in r.fired_rules
    assert {"CAP-02", "AFF-01"} <= set(r.fired_rules)
    assert r.period_compliance == "Fail"
    assert r.twenty_pct_compliance == "Pass"
    assert r.risk_level == "high"          # TEN-01 is a high-risk rule
    assert r.proposed_plan.period_ok is False
    assert r.proposed_plan.additional_months > r.remaining_term_months


def test_hardship_temporary_circumstance_approve():
    """Verified temporary hardship -> postpone any increase; transfer arrears;
    Approve because the circumstance is verified (HARD-02 branch)."""
    r = run("HARDSHIP")
    assert r.recommendation == "Approve"
    assert r.proposed_plan.path == "TRANSFER_ARREARS"
    assert "HARD-02" in r.fired_rules
    assert r.twenty_pct_compliance == "Pass"
    assert r.period_compliance == "Pass"
    assert r.proposed_plan.arrears_moved_to_end is True
    # Installment unchanged on the transfer path
    assert r.proposed_plan.new_total_installment_aed == pytest.approx(2000, abs=2)


def test_original_five_cases_unchanged_after_expansion():
    """Tight regression net: every original-case headline must hold after the
    fixture format and HardshipEvidence.note additions."""
    g = run("GOLDEN")
    assert g.recommendation == "Approve" and g.proposed_plan.path == "UPDATE_INSTALLMENT"
    assert g.proposed_plan.new_total_installment_aed == pytest.approx(3342, abs=2)
    assert g.proposed_plan.additional_months == 120

    n = run("NOHEAD")
    assert n.recommendation == "Refer to employee"
    assert n.proposed_plan.path == "TRANSFER_ARREARS"
    assert {"HARD-01", "CAP-01"} <= set(n.fired_rules)

    m = run("MISSING")
    assert m.recommendation == "Request documents"
    assert m.application_status == "Incomplete"
    assert "DOC-01" in m.fired_rules

    a = run("ACTIVE")
    assert a.recommendation == "Reject"
    assert "ACTIVE-01" in a.fired_rules

    c = run("CONTRA")
    assert c.recommendation == "Refer to employee"
    assert {"INC-01", "RSK-01"} <= set(c.fired_rules)


def test_all_eight_cases_route_through_endpoint():
    """End-to-end via the FastAPI route — guards the adapter+endpoint wiring."""
    from fastapi.testclient import TestClient
    from backend.app import app
    client = TestClient(app)
    expected = {
        "GOLDEN":            "Approve",
        "NOHEAD":            "Refer to employee",
        "MISSING":           "Request documents",
        "ACTIVE":            "Reject",
        "CONTRA":            "Refer to employee",
        "HIGH_OBLIGATIONS":  "Refer to employee",
        "PERIOD_BREACH":     "Refer to employee",
        "HARDSHIP":          "Approve",
    }
    for cid, rec in expected.items():
        resp = client.post(f"/demo/run/{cid}")
        assert resp.status_code == 200, f"{cid} -> HTTP {resp.status_code}"
        assert resp.json()["report"]["recommendation"] == rec, cid

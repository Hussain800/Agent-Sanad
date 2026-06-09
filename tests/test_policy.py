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


# ── v1.1 completion cases (9–13) ─────────────────────────────────────────────
# Each fixture was hand-traced through engine.py before the assertions below
# were written. If any assertion fails it indicates either a fixture drift OR
# a regression in the engine — investigate before relaxing it.

def test_zero_or_missing_income_request_doc_02():
    """Cert received but income unverifiable -> DOC-02 -> Request documents.
    No financial computation should occur."""
    r = run("ZERO_OR_MISSING_INCOME")
    assert r.recommendation == "Request documents"
    assert r.application_status == "Incomplete"
    assert "DOC-02" in r.fired_rules
    assert r.proposed_plan.path == "NONE"
    assert r.twenty_pct_compliance == "N/A"
    assert r.period_compliance == "N/A"
    # Plan must not exist — no path, no premium, no months computed.
    assert r.proposed_plan.new_total_installment_aed == 0
    assert r.proposed_plan.additional_premium_aed == 0
    assert r.proposed_plan.additional_months == 0


def test_low_income_per_member_approve_with_fam_01_lowering_confidence():
    """Per-member < AED 2,500 fires FAM-01 in risk. FAM-01 is NOT in refer_risk,
    so the case Approves with FAM-01 retained on the final report and confidence
    lowered (1 risk rule -> 0.15 penalty)."""
    r = run("LOW_INCOME_PER_MEMBER")
    assert r.recommendation == "Approve"
    assert r.proposed_plan.path == "UPDATE_INSTALLMENT"
    assert {"CAP-02", "AFF-01", "FAM-01"} <= set(r.fired_rules)
    assert r.twenty_pct_compliance == "Pass"
    assert r.period_compliance == "Pass"
    # 1 risk rule -> "medium" risk by engine semantics.
    assert r.risk_level == "medium"
    # Plan numbers (engine-derived): 500 premium + 3 months, new EMI = 1000.
    assert r.proposed_plan.new_total_installment_aed == pytest.approx(1000, abs=2)
    assert r.proposed_plan.additional_months == 3


def test_unverified_hardship_refer_with_hard_01():
    """Hardship claimed (unemployed_flag=True) but unverified=True. HARD-01
    branch transfers arrears; unverified flips recommendation to Refer."""
    r = run("UNVERIFIED_HARDSHIP")
    assert r.recommendation == "Refer to employee"
    assert r.proposed_plan.path == "TRANSFER_ARREARS"
    assert "HARD-01" in r.fired_rules
    assert r.proposed_plan.arrears_moved_to_end is True
    # Installment unchanged on transfer path.
    assert r.proposed_plan.new_total_installment_aed == pytest.approx(1400, abs=2)


def test_prompt_injection_only_logs_rsk_01_without_changing_decision():
    """Document contains injection text but cert/verification AGREE. RSK-01 fires
    but the policy logic is untouched: headroom present -> UPDATE -> Approve.
    THIS IS THE SECURITY POINT: document text cannot alter the decision."""
    r = run("PROMPT_INJECTION_ONLY")
    assert r.recommendation == "Approve"
    assert r.proposed_plan.path == "UPDATE_INSTALLMENT"
    assert "RSK-01" in r.fired_rules
    assert "INC-01" not in r.fired_rules            # values agreed; no contradiction
    assert {"CAP-02", "AFF-01"} <= set(r.fired_rules)
    assert r.twenty_pct_compliance == "Pass"
    assert r.period_compliance == "Pass"
    # The computed plan must be exactly what the engine would have produced
    # WITHOUT the injection — proves the injected text moved no number.
    assert r.proposed_plan.new_total_installment_aed == pytest.approx(3000, abs=2)
    assert r.proposed_plan.additional_premium_aed == pytest.approx(2000, abs=2)
    assert r.proposed_plan.additional_months == 2


def test_high_capacity_update_uses_real_headroom():
    """High salary + low EMI -> engine computes a large UPDATE plan. Proves the
    engine uses real headroom (cap - EMI), not a fixed payment."""
    r = run("HIGH_CAPACITY_UPDATE")
    assert r.recommendation == "Approve"
    assert r.proposed_plan.path == "UPDATE_INSTALLMENT"
    assert {"CAP-02", "AFF-01"} <= set(r.fired_rules)
    assert r.twenty_pct_compliance == "Pass"
    assert r.period_compliance == "Pass"
    assert r.risk_level == "low"
    # New installment is exactly the 20% cap (6,000 on a 30,000 income).
    assert r.proposed_plan.new_total_installment_aed == pytest.approx(6000, abs=2)
    # Headroom is the difference, not a fixed value.
    assert r.proposed_plan.additional_premium_aed == pytest.approx(4000, abs=2)
    assert r.proposed_plan.additional_months == 3
    assert r.proposed_deduction_rate <= 0.20 + 1e-9


def test_all_thirteen_cases_route_through_endpoint():
    """End-to-end via the FastAPI route for the full v1.1 case set (8 + 5)."""
    from fastapi.testclient import TestClient
    from backend.app import app
    client = TestClient(app)
    expected = {
        # original 5 v0.8
        "GOLDEN":                 "Approve",
        "NOHEAD":                 "Refer to employee",
        "MISSING":                "Request documents",
        "ACTIVE":                 "Reject",
        "CONTRA":                 "Refer to employee",
        # v1.1 expansion (cases 6–8)
        "HIGH_OBLIGATIONS":       "Refer to employee",
        "PERIOD_BREACH":          "Refer to employee",
        "HARDSHIP":               "Approve",
        # v1.1 completion (cases 9–13)
        "ZERO_OR_MISSING_INCOME": "Request documents",
        "LOW_INCOME_PER_MEMBER":  "Approve",
        "UNVERIFIED_HARDSHIP":    "Refer to employee",
        "PROMPT_INJECTION_ONLY":  "Approve",
        "HIGH_CAPACITY_UPDATE":   "Approve",
    }
    for cid, rec in expected.items():
        resp = client.post(f"/demo/run/{cid}")
        assert resp.status_code == 200, f"{cid} -> HTTP {resp.status_code}"
        assert resp.json()["report"]["recommendation"] == rec, cid

"""Agent Sanad — deterministic policy engine. THE MONEY PATH. Review this personally.

Implements the canonical decide() from the PRD (Section 3.2):
  cap = 0.20 * verified salary ; headroom = cap - current_installment
  headroom > 0  -> UPDATE_INSTALLMENT (raise installment toward cap, clear arrears)
  headroom <= 0 -> TRANSFER_ARREARS  (move arrears to loan end, installment unchanged)
plus the three official gates (active request, eligibility, completeness) and refer logic.
The LLM never runs through here.
"""
from __future__ import annotations
import math
from backend.schemas import Case, PolicyConfig, ProposedPlan, RecommendationReport
from backend.policy import period as period_mod
from backend.policy.rules import text as rule_text
from backend.confidence import confidence_band, risk_level
from backend.reasoning import build_reasoning, build_summary, build_income_analysis


# ---------- rounding helpers ----------
def _floor(x: float, policy: PolicyConfig) -> int:
    return int(round(x)) if policy.rounding == "nearest" else int(math.floor(x))

def _ceil(x: float, policy: PolicyConfig) -> int:
    return int(round(x)) if policy.rounding == "nearest" else int(math.ceil(x))


# ---------- plan builders ----------
def transfer_plan(case: Case, policy: PolicyConfig) -> ProposedPlan:
    return ProposedPlan(
        path="TRANSFER_ARREARS",
        new_total_installment_aed=case.loan.current_installment_aed,
        additional_premium_aed=0, additional_months=0,
        arrears_moved_to_end=True,
        period_ok=period_mod.transfer_period_ok(case, policy),
    )

def update_plan(case: Case, policy: PolicyConfig, new_total: float,
                add_prem: float, add_months: int) -> ProposedPlan:
    return ProposedPlan(
        path="UPDATE_INSTALLMENT",
        new_total_installment_aed=new_total,
        additional_premium_aed=add_prem, additional_months=add_months,
        arrears_moved_to_end=False,
        period_ok=period_mod.update_months_ok(case, policy, add_months),
    )


# ---------- report assembly ----------
def _report(case, recommendation, fired, salary, plan=None, status="Complete",
            twenty=None, period=None) -> RecommendationReport:
    plan = plan or ProposedPlan()
    arrears = case.arrears.arrears_amount_aed if case.arrears else 0
    balance = case.loan.remaining_balance_aed if case.loan else 0
    term = case.loan.remaining_term_months if case.loan else 0
    ded_rate = (plan.new_total_installment_aed / salary) if (salary and plan.new_total_installment_aed) else 0
    if twenty is None:
        twenty = "N/A" if plan.path == "NONE" else ("Pass" if ded_rate <= policy_cap(case) + 1e-9 else "Fail")
    if period is None:
        period = "N/A" if plan.path == "NONE" else ("Pass" if plan.period_ok else "Fail")
    return RecommendationReport(
        case_id=case.case_id,
        application_status=status,
        case_summary=build_summary(case, recommendation, plan),
        income_analysis=build_income_analysis(case, salary),
        arrears_amount_aed=arrears, remaining_balance_aed=balance, remaining_term_months=term,
        proposed_deduction_rate=round(ded_rate, 4),
        proposed_plan=plan,
        twenty_pct_compliance=twenty, period_compliance=period,
        recommendation=recommendation,
        reasoning=build_reasoning(case, recommendation, plan, fired, salary),
        risk_level=risk_level(fired), confidence=confidence_band(case, fired),
        fired_rules=fired, policy_version="sanad-v0.8",
    )

# cap used by _report for the compliance check (0.20 * salary captured via closure-free helper)
_CAP_PCT = 0.20
def policy_cap(case):  # deduction rate ceiling = cap pct (rate space)
    return _CAP_PCT


def _reject(case, fired, salary, msg):
    return _report(case, "Reject", fired, salary, status="Complete")

def _refer(case, fired, salary, plan=None):
    return _report(case, "Refer to employee", fired, salary, plan=plan)

def _request_docs(case, fired, salary):
    return _report(case, "Request documents", fired, salary, status="Incomplete",
                   twenty="N/A", period="N/A")


# ---------- the decision ----------
def decide(case: Case, policy: PolicyConfig) -> RecommendationReport:
    global _CAP_PCT
    _CAP_PCT = policy.deduction_cap_pct
    fired: list[str] = []

    # GATE 1 — Rule 3: active application
    if case.arrears and case.arrears.active_request_exists and policy.active_request_policy == "always_reject":
        return _reject(case, fired + ["ACTIVE-01"], 0, rule_text("ACTIVE-01"))

    # GATE 2 — eligibility
    if not case.applicant or not case.applicant.uae_national:
        return _refer(case, fired + ["ELIG-01"], 0)

    # GATE 3 — completeness (salary certificate mandatory)
    if case.documents.missing_required:
        return _request_docs(case, fired + ["DOC-01"], 0)

    # injected/suspicious text: treat as content only, flag, continue
    if case.documents.injection_flags:
        fired.append("RSK-01")

    # verified income
    salary = case.income.verified_monthly_income_aed
    if salary is None or salary <= 0:
        return _request_docs(case, fired + ["DOC-02"], 0)

    current_emi = case.loan.current_installment_aed
    cap = policy.deduction_cap_pct * salary
    base = current_emi if policy.cap_applies_to == "total_installment" else 0.0
    headroom = cap - base

    # risk signals
    risk: list[str] = []
    if case.income.contradiction_flag:
        risk.append("INC-01")
    if case.income.obligations_ratio and case.income.obligations_ratio > policy.high_obligations_pct:
        risk.append("OBL-01")
    ipm = case.applicant.income_per_member_aed
    if ipm is None and case.applicant.family_size:
        ipm = salary / case.applicant.family_size
    if ipm is not None and ipm < policy.low_income_per_member_aed:
        risk.append("FAM-01")

    # hard contradiction -> human immediately
    if "INC-01" in risk:
        return _refer(case, fired + risk, salary)

    refer_risk = [r for r in risk if r == "OBL-01"]   # FAM-01 lowers confidence only

    # hardship / no-capacity paths (assessment matrix)
    if case.hardship.unemployed_flag or salary < current_emi:
        fired.append("HARD-01")
        if headroom <= 0:
            fired.append("CAP-01")
        plan = transfer_plan(case, policy)
        rec = "Refer to employee" if (case.hardship.unverified or salary <= 0 or salary < current_emi) else "Approve"
        return _report(case, rec, fired + risk, salary, plan=plan)
    if case.hardship.temporary_circumstance_flag:
        fired.append("HARD-02")
        return _report(case, "Approve", fired + risk, salary, plan=transfer_plan(case, policy))

    # core two-path decision
    if headroom <= policy.min_headroom_aed:                 # no room to increase under cap
        fired.append("CAP-01")
        plan = transfer_plan(case, policy)
        if not plan.period_ok:
            return _report(case, "Refer to employee", fired + ["TEN-01"] + risk, salary, plan=plan)
        rec = "Refer to employee" if refer_risk else "Approve"
        return _report(case, rec, fired + risk, salary, plan=plan)

    # headroom > 0 -> UPDATE_INSTALLMENT
    add_prem = _floor(headroom, policy)
    add_months = _ceil(case.arrears.arrears_amount_aed / add_prem, policy) if add_prem > 0 else 0
    new_total = current_emi + add_prem
    plan = update_plan(case, policy, new_total, add_prem, add_months)
    fired += ["CAP-02", "AFF-01"]

    if not plan.period_ok:
        return _report(case, "Refer to employee", fired + ["TEN-01"] + risk, salary, plan=plan)
    if refer_risk:
        return _report(case, "Refer to employee", fired + risk, salary, plan=plan)
    return _report(case, "Approve", fired + [r for r in risk if r == "FAM-01"], salary, plan=plan)

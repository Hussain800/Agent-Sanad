"""What-if simulation engine for policy scenario exploration.

Allows interactive exploration of how changes in income, arrears, term,
or hardship status would affect the policy decision — without modifying
the seeded fixtures. This is the 'what if this person earned X instead of Y?'
feature that demonstrates the engine's determinism and transparency.
"""
from __future__ import annotations

from copy import deepcopy
from typing import Any

from backend.adapters import FIXTURES, build_case
from backend.policy.engine import decide
from backend.policy.rules import load_policy
from backend.schemas import Case

POLICY = load_policy()


def what_if(case_id: str, overrides: dict[str, Any]) -> dict:
    """Run the policy engine with modified parameters on a seeded case.

    Takes a fixture case and applies overrides to income, loan, arrears,
    hardship, or documents. Returns the original and modified reports
    side by side for comparison.
    """
    case_id = case_id.upper()
    if case_id not in FIXTURES:
        return {"error": f"unknown case '{case_id}'", "case_id": case_id}

    base_case, _ = build_case(case_id)
    base_report = decide(base_case, POLICY)

    modified = _apply_overrides(base_case, overrides)
    modified_report = decide(modified, POLICY)

    return {
        "case_id": case_id,
        "overrides_applied": overrides,
        "control": {
            "recommendation": base_report.recommendation,
            "path": base_report.proposed_plan.path,
            "fired_rules": base_report.fired_rules,
            "deduction_rate": round(base_report.proposed_deduction_rate, 4),
            "twenty_pct_compliance": base_report.twenty_pct_compliance,
            "period_compliance": base_report.period_compliance,
            "installment": base_report.proposed_plan.new_total_installment_aed,
            "additional_months": base_report.proposed_plan.additional_months,
            "risk_level": base_report.risk_level,
            "confidence": base_report.confidence,
        },
        "what_if": {
            "recommendation": modified_report.recommendation,
            "path": modified_report.proposed_plan.path,
            "fired_rules": modified_report.fired_rules,
            "deduction_rate": round(modified_report.proposed_deduction_rate, 4),
            "twenty_pct_compliance": modified_report.twenty_pct_compliance,
            "period_compliance": modified_report.period_compliance,
            "installment": modified_report.proposed_plan.new_total_installment_aed,
            "additional_months": modified_report.proposed_plan.additional_months,
            "risk_level": modified_report.risk_level,
            "confidence": modified_report.confidence,
        },
        "delta": _compute_delta(base_report, modified_report),
        "note": "What-if simulation: deterministic comparison, not a prediction.",
    }


def _apply_overrides(case: Case, overrides: dict) -> Case:
    """Return a new Case with overridden fields.

    Only affects the specific fields provided; all other fixture data
    remains unchanged. Supports: income, installment, arrears, balance,
    term, family_size, obligations, hardship, active_request, injection.
    """
    modified = deepcopy(case)

    income = overrides.get("income")
    if income is not None:
        modified.income.verified_monthly_income_aed = income
        modified.income.salary_certificate_income_aed = income

    installment = overrides.get("installment")
    if installment is not None and modified.loan:
        modified.loan.current_installment_aed = installment

    arrears = overrides.get("arrears")
    if arrears is not None and modified.arrears:
        modified.arrears.arrears_amount_aed = arrears

    balance = overrides.get("balance")
    if balance is not None and modified.loan:
        modified.loan.remaining_balance_aed = balance

    term = overrides.get("term")
    if term is not None and modified.loan:
        modified.loan.remaining_term_months = term

    family = overrides.get("family_size")
    if family is not None and modified.applicant:
        modified.applicant.family_size = family

    obligations = overrides.get("obligations_ratio")
    if obligations is not None:
        modified.income.obligations_ratio = obligations

    hardship_unemp = overrides.get("hardship_unemployed")
    if hardship_unemp is not None:
        modified.hardship.unemployed_flag = hardship_unemp

    hardship_temp = overrides.get("hardship_temporary")
    if hardship_temp is not None:
        modified.hardship.temporary_circumstance_flag = hardship_temp

    hardship_unv = overrides.get("hardship_unverified")
    if hardship_unv is not None:
        modified.hardship.unverified = hardship_unv

    active = overrides.get("active_request")
    if active is not None and modified.arrears:
        modified.arrears.active_request_exists = active

    injection = overrides.get("injection")
    if injection is not None:
        modified.documents.injection_flags = ["RSK-01"] if injection else []

    return modified


def _compute_delta(base, modified) -> dict:
    """Compute what changed between control and what-if."""
    changes = {}
    if base.recommendation != modified.recommendation:
        changes["recommendation"] = f"{base.recommendation} → {modified.recommendation}"
    if base.proposed_plan.path != modified.proposed_plan.path:
        changes["path"] = f"{base.proposed_plan.path} → {modified.proposed_plan.path}"
    if base.proposed_plan.new_total_installment_aed != modified.proposed_plan.new_total_installment_aed:
        changes["installment"] = (
            f"AED {base.proposed_plan.new_total_installment_aed:,.0f} → "
            f"AED {modified.proposed_plan.new_total_installment_aed:,.0f}"
        )
    if base.proposed_plan.additional_months != modified.proposed_plan.additional_months:
        changes["additional_months"] = (
            f"{base.proposed_plan.additional_months} → {modified.proposed_plan.additional_months}"
        )
    rules_base = set(base.fired_rules)
    rules_mod = set(modified.fired_rules)
    added = rules_mod - rules_base
    removed = rules_base - rules_mod
    if added:
        changes["rules_added"] = sorted(added)
    if removed:
        changes["rules_removed"] = sorted(removed)
    return changes

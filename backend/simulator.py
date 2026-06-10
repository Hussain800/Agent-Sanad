"""Fair Plan Simulator — advisory plan options without changing the engine."""
from __future__ import annotations
import math
from backend.schemas import Case, PolicyConfig
from backend.policy import period as period_mod


def simulate_options(case: Case, policy: PolicyConfig) -> list[dict]:
    """Generate multiple compliant plan options for officer comparison.
    All options must pass the 20% cap. Invalid options are marked with reason.
    The official recommendation remains the deterministic decide() output."""
    salary = case.income.verified_monthly_income_aed or 0
    emi = case.loan.current_installment_aed if case.loan else 0
    arrears = case.arrears.arrears_amount_aed if case.arrears else 0
    cap = policy.deduction_cap_pct * salary
    remaining_term = case.loan.remaining_term_months if case.loan else 0
    options = []

    # Option 1: Fastest compliant (maximum headroom)
    headroom = cap - emi
    if headroom > policy.min_headroom_aed:
        add_prem = int(math.floor(headroom))
        add_months = int(math.ceil(arrears / add_prem)) if add_prem > 0 else 0
        new_total = emi + add_prem
        period_ok = add_months <= remaining_term if policy.respect_approved_period else True
        options.append({
            "id": "fastest", "label": "Fastest compliant plan",
            "new_total_installment_aed": new_total,
            "additional_premium_aed": add_prem,
            "additional_months": add_months,
            "deduction_rate": round(new_total / salary, 4) if salary else 0,
            "twenty_pct_ok": new_total / salary <= policy.deduction_cap_pct + 1e-9 if salary else False,
            "period_ok": period_ok,
            "valid": period_ok,
            "invalid_reason": None if period_ok else "Extends beyond approved repayment period",
        })

    # Option 2: Lower-pressure (half headroom)
    low_headroom = headroom / 2
    if low_headroom > policy.min_headroom_aed:
        add_prem_low = int(math.floor(low_headroom))
        add_months_low = int(math.ceil(arrears / add_prem_low)) if add_prem_low > 0 else 0
        new_total_low = emi + add_prem_low
        period_ok_low = add_months_low <= remaining_term if policy.respect_approved_period else True
        options.append({
            "id": "lower", "label": "Lower-pressure plan",
            "new_total_installment_aed": new_total_low,
            "additional_premium_aed": add_prem_low,
            "additional_months": add_months_low,
            "deduction_rate": round(new_total_low / salary, 4) if salary else 0,
            "twenty_pct_ok": new_total_low / salary <= policy.deduction_cap_pct + 1e-9 if salary else False,
            "period_ok": period_ok_low,
            "valid": period_ok_low,
            "invalid_reason": None if period_ok_low else "Extends beyond approved repayment period",
        })

    # Option 3: Transfer arrears (hardship-sensitive)
    options.append({
        "id": "transfer", "label": "Transfer arrears (installment unchanged)",
        "new_total_installment_aed": emi,
        "additional_premium_aed": 0,
        "additional_months": int(math.ceil(arrears / emi)) if emi > 0 else 0,
        "deduction_rate": round(emi / salary, 4) if salary else 0,
        "twenty_pct_ok": True,
        "period_ok": True,
        "valid": True,
        "invalid_reason": None,
    })

    return options

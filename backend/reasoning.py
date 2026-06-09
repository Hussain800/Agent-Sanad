"""Plain-language text for the report.

Templated + deterministic by default (works fully offline). Optionally, set
SANAD_LLM=1 to generate the reasoning with one JSON-mode LLM call — but it ALWAYS
falls back to the template on any error/timeout, and results should be cached per
case for the demo. The LLM never changes the numbers (PRD 8).
"""
from backend.schemas import Case
from backend.policy.rules import text as rule_text

_AED = lambda x: f"AED {x:,.0f}"


def build_summary(case: Case, recommendation, plan) -> str:
    a = case.applicant
    who = f"{a.marital_status} beneficiary, family size {a.family_size}" if a else "beneficiary"
    arr = case.arrears.arrears_amount_aed if case.arrears else 0
    return (f"{who.capitalize()} with arrears of {_AED(arr)}. "
            f"Recommendation: {recommendation} via {plan.path.replace('_', ' ').lower()}.")


def build_income_analysis(case: Case, salary) -> str:
    a = case.applicant
    fam = a.family_size if a else 1
    per = salary / fam if (salary and fam) else 0
    trend = case.income.income_trend if case.income else "unknown"
    return (f"Verified monthly income {_AED(salary or 0)} (trend: {trend}); "
            f"average income per family member {_AED(per)} across {fam} member(s).")


def build_reasoning(case: Case, recommendation, plan, fired, salary) -> str:
    lines = []
    if plan and plan.path == "UPDATE_INSTALLMENT":
        cap = 0.20 * (salary or 0)
        lines.append(f"20% cap on income is {_AED(cap)}; current installment "
                     f"{_AED(case.loan.current_installment_aed)} leaves headroom of "
                     f"{_AED(plan.additional_premium_aed)}.")
        lines.append(f"Installment increased to {_AED(plan.new_total_installment_aed)} to clear "
                     f"arrears over {plan.additional_months} additional month(s), within the 20% cap.")
    elif plan and plan.path == "TRANSFER_ARREARS":
        lines.append("No headroom under the 20% cap to raise the installment; "
                     "arrears are transferred to the end of the loan with the installment unchanged.")
    for r in fired:
        lines.append(f"[{r}] {rule_text(r)}")
    if recommendation == "Refer to employee":
        lines.append("Routed to a human officer for final judgement.")
    return " ".join(lines)


# Optional live LLM hook (cached fallback). Kept thin and safe.
def build_reasoning_llm(case, recommendation, plan, fired, salary, cache=None):
    if cache and case.case_id in cache:
        return cache[case.case_id]
    import os
    if os.getenv("SANAD_LLM") != "1":
        return build_reasoning(case, recommendation, plan, fired, salary)
    try:
        # Wire your provider here; must return prose only and never alter numbers.
        raise RuntimeError("LLM provider not configured")
    except Exception:
        return build_reasoning(case, recommendation, plan, fired, salary)

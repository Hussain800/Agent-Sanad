"""Plain-language text for the report.

Templated + deterministic by default (works fully offline). Optionally, set
SANAD_LLM=1 to generate the reasoning with one JSON-mode LLM call — but it ALWAYS
falls back to the template on any error/timeout, and results should be cached per
case for the demo. The LLM never changes the numbers (PRD 8).
"""
from backend.schemas import Case
from backend.policy.rules import text as rule_text

_AED = lambda x: f"AED {x:,.0f}"

CACHED_REASONING = {
    "GOLDEN": (
        "Salary verification confirms AED 16,711 monthly income. The current installment is "
        "AED 3,287, so the 20% cap is AED 3,342 and leaves AED 55 of headroom. Agent Sanad "
        "therefore recommends UPDATE_INSTALLMENT: raise the total installment to AED 3,342 "
        "and clear AED 6,574 of arrears over 120 months. The plan passes both the 20% cap "
        "and the remaining-period check."
    ),
    "NOHEAD": (
        "The beneficiary's verified income is AED 3,000 while the current installment is "
        "AED 3,667, so there is no safe headroom under the 20% cap. Agent Sanad does not "
        "increase the deduction. It recommends TRANSFER_ARREARS and refers the case to an "
        "employee because the existing installment is already above income capacity."
    ),
    "MISSING": (
        "The mandatory salary certificate was not received, so monthly income cannot be "
        "verified. Agent Sanad stops before calculating a repayment plan and requests the "
        "missing document instead of creating a plan from incomplete evidence."
    ),
    "ACTIVE": (
        "Programme records show an existing active rescheduling request. Rule ACTIVE-01 is "
        "applied before any financial computation, so the application is rejected at the "
        "governance gate."
    ),
    "CONTRA": (
        "The uploaded certificate states AED 15,000, but salary verification returns AED 4,000. "
        "That variance exceeds the policy threshold, and suspicious instruction-like text was "
        "detected in the document. Agent Sanad treats document text as untrusted content, keeps "
        "the policy rules unchanged, and refers the case to an employee."
    ),
    # ── v1.1 expansion cases ─────────────────────────────────────────────────
    "HIGH_OBLIGATIONS": (
        "Verified income is AED 20,000, current installment AED 1,800, so the 20% cap "
        "leaves AED 2,200 of headroom for an UPDATE plan. However, total financial obligations "
        "stand at 65% of income, exceeding the 60% policy threshold. Agent Sanad keeps the "
        "compliant plan (raise to AED 4,000, clear arrears in 3 months) but refers the case to "
        "an employee because the wider obligations picture is a human-judgement call."
    ),
    "PERIOD_BREACH": (
        "Verified income is AED 10,000 with a current installment of AED 1,800; the 20% cap "
        "leaves AED 200 of headroom. Clearing AED 30,000 of arrears at AED 200 per month would "
        "take 150 months, but only 24 months remain on the original approved term. The plan "
        "would breach Rule 2 (TEN-01) — the new schedule must not exceed the original repayment "
        "period — so Agent Sanad refers the case to an employee."
    ),
    "HARDSHIP": (
        "The beneficiary has a verified temporary circumstance (e.g. official assignment or "
        "medical leave) supported by documentation. Per the assessment matrix, any increase is "
        "postponed and arrears are transferred to the end of the loan. Income is sufficient, "
        "the plan stays well within the 20% cap, and the loan still ends within the original "
        "approved period. Recommendation: Approve via TRANSFER_ARREARS (HARD-02)."
    ),
}


def build_summary(case: Case, recommendation, plan) -> str:
    a = case.applicant
    who = f"{a.marital_status} beneficiary, family size {a.family_size}" if a else "beneficiary"
    arr = case.arrears.arrears_amount_aed if case.arrears else 0
    if plan.path == "NONE":
        return f"{who.capitalize()} with arrears of {_AED(arr)}. Recommendation: {recommendation}."
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
    cached = CACHED_REASONING.get(case.case_id)
    if cached:
        return cached
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

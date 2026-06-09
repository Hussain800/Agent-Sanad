"""Confidence band + risk level (PRD 10.3 / 4)."""
from backend.schemas import Case

_REFER_RULES = {"INC-01", "OBL-01", "TEN-01", "ELIG-01"}
_RISK_RULES  = {"INC-01", "OBL-01", "FAM-01", "TEN-01", "HARD-01", "RSK-01"}


def risk_level(fired) -> str:
    n = len([r for r in fired if r in _RISK_RULES])
    if any(r in fired for r in ("INC-01", "TEN-01", "ELIG-01")) or n >= 2:
        return "high"
    if n == 1:
        return "medium"
    return "low"


def confidence_band(case: Case, fired) -> str:
    extraction_conf = 1.0 if (case.income and case.income.verified_monthly_income_aed) else 0.5
    completeness = 1.0 if not case.documents.missing_required else 0.4
    risk_penalty = 0.15 * len([r for r in fired if r in _RISK_RULES])
    score = 0.45 * extraction_conf + 0.35 * completeness + 0.20 * (1 - min(risk_penalty, 1))
    return "high" if score >= 0.80 else "medium" if score >= 0.55 else "low"

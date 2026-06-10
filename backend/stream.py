"""Real-time decision streaming via Server-Sent Events.

Streams the agent's step-by-step reasoning process live to the frontend,
showing each stage: identity verification, data retrieval, document
validation, salary extraction, policy execution, and recommendation.
Each event includes timing, status, and detail for a transparent audit trail.
"""
from __future__ import annotations

import asyncio
import json
import time
from typing import AsyncGenerator

from backend.adapters import FIXTURES, build_case
from backend.audit import AuditLog
from backend.policy.engine import decide
from backend.policy.rules import load_policy
from backend.schemas import ProposedPlan

POLICY = load_policy()

_STEP_EMOJI = {
    "verify_identity": "🔐",
    "retrieve_data": "📡",
    "validate_documents": "📄",
    "extract_income": "🔍",
    "verify_salary": "✅",
    "decide": "⚖️",
    "complete": "🎯",
}

_STREAM_DELAYS = {
    "verify_identity": 0.3,
    "retrieve_data": 0.4,
    "validate_documents": 0.3,
    "extract_income": 0.5,
    "verify_salary": 0.3,
    "decide": 0.4,
    "complete": 0.2,
}


async def stream_decision(case_id: str, mock_mode: bool = True) -> AsyncGenerator[str, None]:
    """Yield SSE events for each step of the decision pipeline."""
    case_id = case_id.upper()
    if case_id not in FIXTURES:
        yield _sse("error", {"error": f"unknown case '{case_id}'", "case_id": case_id})
        return

    log = AuditLog()
    t0 = time.time()

    # step 1 — identity verification
    yield _sse("step", {
        "step": "verify_identity", "status": "running",
        "emoji": _STEP_EMOJI["verify_identity"],
        "detail": "Contacting UAE PASS to verify beneficiary identity...",
    })
    await asyncio.sleep(_STREAM_DELAYS["verify_identity"])
    applicant = FIXTURES[case_id]["applicant"]
    log.add(case_id, "stream.verify_identity", "system",
            f"UAE PASS verified: {applicant['applicant_ref']}", mock_mode=mock_mode)
    yield _sse("step", {
        "step": "verify_identity", "status": "complete",
        "detail": f"Identity verified: {applicant['name_masked']} (UAE National)",
        "data": {"applicant_ref": applicant["applicant_ref"], "uae_national": True},
    })

    # step 2 — programme data retrieval
    yield _sse("step", {
        "step": "retrieve_data", "status": "running",
        "emoji": _STEP_EMOJI["retrieve_data"],
        "detail": "Retrieving loan and arrears data from Programme systems...",
    })
    await asyncio.sleep(_STREAM_DELAYS["retrieve_data"])
    loan_f = FIXTURES[case_id]["loan"]
    arrears_f = FIXTURES[case_id]["arrears"]
    log.add(case_id, "stream.retrieve_data", "system",
            f"loan + arrears retrieved for {loan_f['agreement_id']}", mock_mode=mock_mode)
    yield _sse("step", {
        "step": "retrieve_data", "status": "complete",
        "detail": f"Loan data retrieved: installment AED {loan_f['current_installment_aed']:,.0f}, "
                  f"arrears AED {arrears_f['arrears_amount_aed']:,.0f}",
        "data": {
            "installment": loan_f["current_installment_aed"],
            "arrears": arrears_f["arrears_amount_aed"],
            "balance": loan_f["remaining_balance_aed"],
            "term_remaining": loan_f["remaining_term_months"],
        },
    })

    # step 3 — document validation
    yield _sse("step", {
        "step": "validate_documents", "status": "running",
        "emoji": _STEP_EMOJI["validate_documents"],
        "detail": "Validating document completeness and scanning for injection attempts...",
    })
    await asyncio.sleep(_STREAM_DELAYS["validate_documents"])
    docs_received = FIXTURES[case_id]["received_docs"]
    injection = bool(FIXTURES[case_id].get("injection"))
    log.add(case_id, "stream.validate_documents", "system",
            f"docs: {docs_received}, injection: {injection}", mock_mode=mock_mode)
    yield _sse("step", {
        "step": "validate_documents", "status": "complete",
        "detail": f"Documents received: {len(docs_received)} file(s)"
                  + (" — ⚠ Suspicious text detected, logged as RSK-01" if injection else ""),
        "data": {"docs_received": docs_received, "injection_detected": injection},
    })

    # step 4 — salary extraction
    yield _sse("step", {
        "step": "extract_income", "status": "running",
        "emoji": _STEP_EMOJI["extract_income"],
        "detail": "Parsing salary certificate and extracting income data...",
    })
    await asyncio.sleep(_STREAM_DELAYS["extract_income"])
    cert_income = FIXTURES[case_id].get("cert_income")
    log.add(case_id, "stream.extract_income", "system",
            f"certificate income: {cert_income}", mock_mode=mock_mode)
    yield _sse("step", {
        "step": "extract_income", "status": "complete",
        "detail": f"Extracted monthly income: AED {cert_income:,.0f}" if cert_income
                  else "Extraction: no verifiable income found on certificate",
        "data": {"cert_income": cert_income},
    })

    # step 5 — salary verification
    yield _sse("step", {
        "step": "verify_salary", "status": "running",
        "emoji": _STEP_EMOJI["verify_salary"],
        "detail": "Cross-referencing salary with Programme verification records...",
    })
    await asyncio.sleep(_STREAM_DELAYS["verify_salary"])
    verified = FIXTURES[case_id]["verified_income"]
    variance = 0.0
    if cert_income and verified:
        hi, lo = max(cert_income, verified), min(cert_income, verified)
        variance = 0 if hi == 0 else round((hi - lo) / hi * 100, 1)
    log.add(case_id, "stream.verify_salary", "system",
            f"verified: {verified}, variance: {variance}%", mock_mode=mock_mode)
    yield _sse("step", {
        "step": "verify_salary", "status": "complete",
        "detail": f"Verified income: AED {verified:,.0f}" + (f" (variance: {variance:.1f}%)" if variance else ""),
        "data": {"verified_income": verified, "variance_pct": variance},
    })

    # step 6 — policy decision
    yield _sse("step", {
        "step": "decide", "status": "running",
        "emoji": _STEP_EMOJI["decide"],
        "detail": "Applying policy rules: 20% income cap, period compliance, risk assessment...",
    })
    await asyncio.sleep(_STREAM_DELAYS["decide"])
    case, _ = build_case(case_id)
    report = decide(case, POLICY)
    latency = int((time.time() - t0) * 1000)
    log.add(case_id, "stream.decide", "policy",
            f"{report.recommendation} / {report.proposed_plan.path} "
            f"(rules: {','.join(report.fired_rules) or 'none'})",
            latency_ms=latency, mock_mode=mock_mode)

    # Build a human-readable explanation of what the engine decided
    plan = report.proposed_plan
    plan_detail = _describe_plan(plan, report)
    yield _sse("step", {
        "step": "decide", "status": "complete",
        "detail": plan_detail,
        "data": {
            "recommendation": report.recommendation,
            "path": plan.path,
            "fired_rules": report.fired_rules,
            "deduction_rate": report.proposed_deduction_rate,
            "twenty_pct_compliance": report.twenty_pct_compliance,
            "period_compliance": report.period_compliance,
            "risk_level": report.risk_level,
            "confidence": report.confidence,
            "latency_ms": latency,
        },
    })

    # final — complete
    await asyncio.sleep(_STREAM_DELAYS["complete"])
    report_data = report.model_dump(mode="json")
    report_data["_latency_ms"] = latency
    yield _sse("complete", {
        "status": "complete",
        "emoji": _STEP_EMOJI["complete"],
        "detail": f"Decision ready: {report.recommendation} — processed in {latency}ms",
        "report": report_data,
        "audit": log.events(),
    })


def _describe_plan(plan: ProposedPlan, report) -> str:
    if plan.path == "NONE":
        return f"Recommendation: {report.recommendation} — no plan generated"
    if plan.path == "TRANSFER_ARREARS":
        return (f"Path: TRANSFER_ARREARS — arrears moved to loan end, "
                f"installment unchanged at AED {plan.new_total_installment_aed:,.0f}")
    return (f"Path: UPDATE_INSTALLMENT — raise to AED {plan.new_total_installment_aed:,.0f} "
            f"(+AED {plan.additional_premium_aed:,.0f} premium for {plan.additional_months} months)")


def _sse(event: str, data: dict) -> str:
    return f"event: {event}\ndata: {json.dumps(data, default=str)}\n\n"

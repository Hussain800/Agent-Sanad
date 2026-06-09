"""Custom mock-application flow (v1.1 app experience).

Takes validated beneficiary form input (MockApplication), constructs a fully
synthetic Case, emits the same canonical v1.1 §7 state transitions as the
fixture path, and lets the EXISTING deterministic engine decide. Nothing in
here computes money — it is adapter-shaped glue between a web form and
decide(), exactly like backend/adapters/__init__.py is for fixtures.

No persistence: each submission is stateless and returns the full envelope.
"""
from __future__ import annotations

import time
import uuid

from backend.audit import AuditLog
from backend.schemas import (
    ApplicantProfile, ArrearsData, Case, DocumentManifest, HardshipEvidence,
    IncomeEvidence, LoanData, MockApplication,
)


def build_case_from_application(app_in: MockApplication) -> tuple[Case, AuditLog, str]:
    """Map a MockApplication onto the canonical Case schema.

    Mirrors build_case() for fixtures: same adapters story, same audit
    transitions, same downstream contract. Returns (case, log, application_id).
    """
    application_id = f"CUSTOM-{uuid.uuid4().hex[:8].upper()}"
    log = AuditLog()
    log.add(application_id, "case.created", "system",
            f"custom mock application {application_id}",
            state_from="", state_to="Submitted")

    # UAE PASS (mock) — identity is always synthetic and pre-verified.
    applicant = ApplicantProfile(
        applicant_ref="APP-CUSTOM",
        name_masked="A*** (custom application)",
        uae_national=True,
        marital_status="unknown",
        family_size=app_in.family_size,
    )
    log.add(application_id, "retrieve.uae_pass", "adapter",
            "identity APP-CUSTOM (mock UAE PASS verification)")
    log.transition(application_id, "Submitted", "IdentityLinked",
                   detail="UAE PASS verified (mock) for APP-CUSTOM")

    # Programme systems (mock) — loan + arrears from the form values.
    loan = LoanData(
        agreement_id="AGR-CUSTOM",
        remaining_balance_aed=app_in.remaining_balance_aed,
        original_approved_term_months=app_in.original_approved_term_months,
        remaining_term_months=app_in.remaining_term_months,
        current_installment_aed=app_in.current_installment_aed,
    )
    log.add(application_id, "retrieve.loan", "adapter",
            f"installment {app_in.current_installment_aed}, "
            f"term {app_in.remaining_term_months}mo")
    arrears = ArrearsData(
        agreement_id="AGR-CUSTOM",
        arrears_amount_aed=app_in.arrears_amount_aed,
        unpaid_installments=app_in.unpaid_installments,
        active_request_exists=app_in.active_request_exists,
    )
    log.add(application_id, "retrieve.arrears", "adapter",
            f"arrears {app_in.arrears_amount_aed}, "
            f"active={app_in.active_request_exists}")
    log.transition(application_id, "IdentityLinked", "DataRetrieved",
                   detail="loan AGR-CUSTOM + arrears retrieved from Programme (mock)")

    # Documents (mock) — salary certificate presence + injection scan result.
    received = ["salary_certificate"] if app_in.salary_certificate_present else []
    if app_in.hardship_type != "none":
        received.append("supporting_document")
    log.add(application_id, "validate.documents", "adapter",
            f"docs {received}, injection={app_in.suspicious_document_text}")

    # Extraction (mock) — the form's salary IS the certificate value here;
    # a real upload would go through backend/extraction.py instead.
    log.transition(application_id, "DataRetrieved", "Extracting", actor="adapter",
                   detail="reading declared income from application form (mock certificate)")
    cert_income = app_in.monthly_income_aed if app_in.salary_certificate_present else None
    log.add(application_id, "extract.salary_certificate", "adapter",
            f"form-declared income {cert_income if cert_income is not None else 'n/a'} "
            "(custom application; no document parse)")

    # Salary verification (mock) — verified == declared, variance 0.
    verified = cert_income
    log.add(application_id, "verify.salary", "adapter",
            f"verified {verified}, variance 0.0%")
    log.transition(application_id, "Extracting", "Validating",
                   detail="documents + salary verification complete")

    income = IncomeEvidence(
        salary_certificate_income_aed=cert_income,
        verified_monthly_income_aed=verified,
        income_trend=app_in.income_trend,
        obligations_ratio=app_in.obligations_ratio,
        variance_pct=0,
        contradiction_flag=False,
    )
    hardship = HardshipEvidence(
        unemployed_flag=(app_in.hardship_type == "unemployment"),
        temporary_circumstance_flag=(app_in.hardship_type == "temporary_circumstance"),
        unverified=(app_in.hardship_type != "none" and not app_in.hardship_verified),
        note=("self-declared hardship (custom application)"
              if app_in.hardship_type != "none" else ""),
    )
    documents = DocumentManifest(
        received_document_types=received,
        injection_flags=["RSK-01"] if app_in.suspicious_document_text else [],
    )

    case = Case(case_id=application_id, applicant=applicant, loan=loan,
                arrears=arrears, income=income, hardship=hardship,
                documents=documents)
    return case, log, application_id

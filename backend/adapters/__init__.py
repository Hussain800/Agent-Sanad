"""Five mock integration adapters (contract-true, fixture-backed) + case assembly.

UAE PASS · Loan · Arrears · Salary Verification · Document Validation.
Each returns seeded data and records an AuditEvent. Swap the body for a real
endpoint in pilot; the workflow core never changes.
"""
from backend.schemas import (Case, ApplicantProfile, LoanData, ArrearsData,
                             IncomeEvidence, HardshipEvidence, DocumentManifest)
from backend.audit import AuditLog
from backend.extraction import extract_salary_certificate

# ---- seeded fixtures keyed by case_id (values mirror real workbook rows; ids synthetic) ----
FIXTURES = {
    "GOLDEN": {  # clean UPDATE_INSTALLMENT -> Approve
        "applicant": dict(applicant_ref="APP-0001", name_masked="A***", uae_national=True,
                          marital_status="married", family_size=3),
        "loan": dict(agreement_id="AGR-GOLDEN", remaining_balance_aed=410000,
                     original_approved_term_months=240, remaining_term_months=144,
                     loan_original_end_date="2032-01-01", current_installment_aed=3287),
        "arrears": dict(agreement_id="AGR-GOLDEN", arrears_amount_aed=6574,
                        unpaid_installments=2, active_request_exists=False),
        "cert_income": 16711, "verified_income": 16711, "income_trend": "stable",
        "received_docs": ["salary_certificate"], "injection": False,
    },
    "NOHEAD": {  # current installment already exceeds salary -> TRANSFER + Refer
        "applicant": dict(applicant_ref="APP-0002", name_masked="B***", uae_national=True,
                          marital_status="married", family_size=5),
        "loan": dict(agreement_id="AGR-NOHEAD", remaining_balance_aed=210000,
                     original_approved_term_months=180, remaining_term_months=60,
                     loan_original_end_date="2029-06-01", current_installment_aed=3667),
        "arrears": dict(agreement_id="AGR-NOHEAD", arrears_amount_aed=69673,
                        unpaid_installments=19, active_request_exists=False),
        "cert_income": 3000, "verified_income": 3000, "income_trend": "decreased",
        "received_docs": ["salary_certificate"], "injection": False,
    },
    "MISSING": {  # no salary certificate -> Request documents (Incomplete)
        "applicant": dict(applicant_ref="APP-0003", name_masked="C***", uae_national=True,
                          family_size=4),
        "loan": dict(agreement_id="AGR-MISS", remaining_balance_aed=300000,
                     original_approved_term_months=240, remaining_term_months=180,
                     current_installment_aed=2500),
        "arrears": dict(agreement_id="AGR-MISS", arrears_amount_aed=10000,
                        unpaid_installments=4, active_request_exists=False),
        "cert_income": None, "verified_income": None,
        "received_docs": [], "injection": False,
    },
    "ACTIVE": {  # existing active request -> Reject at GATE 1
        "applicant": dict(applicant_ref="APP-0004", name_masked="D***", uae_national=True,
                          family_size=2),
        "loan": dict(agreement_id="AGR-ACT", remaining_balance_aed=350000,
                     original_approved_term_months=240, remaining_term_months=150,
                     current_installment_aed=3000),
        "arrears": dict(agreement_id="AGR-ACT", arrears_amount_aed=20922,
                        unpaid_installments=6, active_request_exists=True),
        "cert_income": 18000, "verified_income": 18000,
        "received_docs": ["salary_certificate"], "injection": False,
    },
    "CONTRA": {  # salary mismatch + injected text -> Refer (INC-01, RSK-01)
        "applicant": dict(applicant_ref="APP-0005", name_masked="E***", uae_national=True,
                          family_size=4),
        "loan": dict(agreement_id="AGR-CON", remaining_balance_aed=260000,
                     original_approved_term_months=240, remaining_term_months=160,
                     current_installment_aed=1500),
        "arrears": dict(agreement_id="AGR-CON", arrears_amount_aed=22000,
                        unpaid_installments=7, active_request_exists=False),
        "cert_income": 15000, "verified_income": 4000, "income_trend": "unknown",
        "received_docs": ["salary_certificate"], "injection": True,
    },
    # ── v1.1 functional expansion: three new realistic scenarios ─────────────
    "HIGH_OBLIGATIONS": {  # plenty of headroom but obligations > 60% -> Refer (OBL-01)
        # Engine trace: cap=4,000, base=1,800, headroom=2,200 (>50) -> UPDATE.
        # add_prem=2,200, add_months=ceil(5,500/2,200)=3, new_total=4,000.
        # risk=[OBL-01]; refer_risk=[OBL-01] -> Refer to employee.
        # 20% = 4,000/20,000 = 0.20 (Pass). Period: 3 <= 200 (Pass).
        "applicant": dict(applicant_ref="APP-0006", name_masked="F***", uae_national=True,
                          marital_status="married", family_size=3),
        "loan": dict(agreement_id="AGR-OBL", remaining_balance_aed=350000,
                     original_approved_term_months=240, remaining_term_months=200,
                     loan_original_end_date="2034-09-01", current_installment_aed=1800),
        "arrears": dict(agreement_id="AGR-OBL", arrears_amount_aed=5500,
                        unpaid_installments=3, active_request_exists=False),
        "cert_income": 20000, "verified_income": 20000, "income_trend": "stable",
        "received_docs": ["salary_certificate"], "injection": False,
        # Assessment-matrix knob: obligations_ratio is 0.65 -> OBL-01 fires.
        "obligations_ratio": 0.65,
    },
    "PERIOD_BREACH": {  # UPDATE math runs the catch-up past the remaining term -> Refer (TEN-01)
        # Engine trace: cap=2,000, base=1,800, headroom=200 (>50) -> UPDATE.
        # add_prem=200, add_months=ceil(30,000/200)=150, new_total=2,000.
        # period_ok: 150 > 24 -> False -> Refer + TEN-01.
        # 20% = 2,000/10,000 = 0.20 (Pass). Period: Fail.
        "applicant": dict(applicant_ref="APP-0007", name_masked="G***", uae_national=True,
                          marital_status="married", family_size=2),
        "loan": dict(agreement_id="AGR-PER", remaining_balance_aed=120000,
                     original_approved_term_months=240, remaining_term_months=24,
                     loan_original_end_date="2027-06-01", current_installment_aed=1800),
        "arrears": dict(agreement_id="AGR-PER", arrears_amount_aed=30000,
                        unpaid_installments=12, active_request_exists=False),
        "cert_income": 10000, "verified_income": 10000, "income_trend": "stable",
        "received_docs": ["salary_certificate"], "injection": False,
    },
    "HARDSHIP": {  # verified temporary circumstance -> Approve via TRANSFER_ARREARS (HARD-02)
        # Engine trace: hardship.temporary_circumstance_flag=True, unverified=False.
        # Engine takes the HARD-02 branch (after EMI<=salary check). Path=TRANSFER,
        # installment unchanged, period check uses ceil(8,000/2,000)=4 months <= 100.
        # 20% = 2,000/15,000 = 0.13 (Pass). Period: Pass.
        "applicant": dict(applicant_ref="APP-0008", name_masked="H***", uae_national=True,
                          marital_status="married", family_size=3),
        "loan": dict(agreement_id="AGR-HARD", remaining_balance_aed=240000,
                     original_approved_term_months=240, remaining_term_months=100,
                     loan_original_end_date="2030-04-01", current_installment_aed=2000),
        "arrears": dict(agreement_id="AGR-HARD", arrears_amount_aed=8000,
                        unpaid_installments=4, active_request_exists=False),
        "cert_income": 15000, "verified_income": 15000, "income_trend": "decreased",
        "received_docs": ["salary_certificate", "supporting_document"], "injection": False,
        # Assessment-matrix knob: verified temporary circumstance (e.g. official assignment).
        "hardship": {"temporary_circumstance_flag": True, "unverified": False,
                     "note": "verified medical leave; 6-month assignment abroad"},
    },
}

INCOME_VARIANCE_THRESHOLD = 0.30


def uae_pass(case_id, log: AuditLog) -> ApplicantProfile:
    f = FIXTURES[case_id]["applicant"]
    log.add(case_id, "retrieve.uae_pass", "adapter", f"identity {f['applicant_ref']}")
    return ApplicantProfile(**f)


def loan(case_id, log: AuditLog) -> LoanData:
    f = FIXTURES[case_id]["loan"]
    log.add(case_id, "retrieve.loan", "adapter",
            f"installment {f['current_installment_aed']}, term {f['remaining_term_months']}mo")
    return LoanData(**f)


def arrears(case_id, log: AuditLog) -> ArrearsData:
    f = FIXTURES[case_id]["arrears"]
    log.add(case_id, "retrieve.arrears", "adapter",
            f"arrears {f['arrears_amount_aed']}, active={f['active_request_exists']}")
    return ArrearsData(**f)


def salary_verify(case_id, cert_income, log: AuditLog) -> dict:
    f = FIXTURES[case_id]
    verified = f["verified_income"]
    variance = 0.0
    if cert_income and verified:
        hi, lo = max(cert_income, verified), min(cert_income, verified)
        variance = 0 if hi == 0 else round((hi - lo) / hi * 100, 1)
    log.add(case_id, "verify.salary", "adapter",
            f"verified {verified}, variance {variance}%")
    return {"verified_income": verified, "variance_pct": variance,
            "verified": bool(verified) and variance / 100 <= INCOME_VARIANCE_THRESHOLD}


def doc_validate(case_id, log: AuditLog) -> dict:
    f = FIXTURES[case_id]
    inj = bool(f.get("injection"))
    log.add(case_id, "validate.documents", "adapter",
            f"docs {f['received_docs']}, injection={inj}")
    return {"received_docs": list(f["received_docs"]), "injection_flag": inj}


def salary_extract(case_id, fallback_income, received_docs, log: AuditLog) -> dict:
    result = extract_salary_certificate(case_id, fallback_income, received_docs)
    detail = f"{result.mode}: {result.detail}"
    if result.income_aed is not None:
        detail += f"; extracted={result.income_aed:,.0f}"
    log.add(case_id, "extract.salary_certificate", "adapter", detail)
    return {"cert_income": result.income_aed, "mode": result.mode, "detail": result.detail}


def build_case(case_id: str):
    """Assemble a Case by calling the five adapters in order. Returns (Case, AuditLog)."""
    if case_id not in FIXTURES:
        raise KeyError(case_id)
    f = FIXTURES[case_id]
    log = AuditLog()
    log.add(case_id, "case.created", "system", f"case {case_id}")
    applicant = uae_pass(case_id, log)
    loan_d = loan(case_id, log)
    arr_d = arrears(case_id, log)
    docs = doc_validate(case_id, log)
    ext = salary_extract(case_id, f.get("cert_income"), docs["received_docs"], log)
    ver = salary_verify(case_id, ext["cert_income"], log)
    variance = ver["variance_pct"]
    income_kwargs = dict(
        salary_certificate_income_aed=ext["cert_income"],
        verified_monthly_income_aed=ver["verified_income"],
        income_trend=f.get("income_trend", "unknown"),
        variance_pct=variance,
        contradiction_flag=(variance / 100) > INCOME_VARIANCE_THRESHOLD,
    )
    # v1.1 — assessment-matrix signal: financial obligations ratio (Rule OBL-01).
    # Optional in the fixture; flowing through here lets HIGH_OBLIGATIONS fire
    # without touching engine.py.
    if "obligations_ratio" in f:
        income_kwargs["obligations_ratio"] = f["obligations_ratio"]
    income = IncomeEvidence(**income_kwargs)

    manifest = DocumentManifest(
        received_document_types=docs["received_docs"],
        injection_flags=["RSK-01"] if docs["injection_flag"] else [],
    )

    # v1.1 — assessment-matrix signal: hardship flags. Optional in the fixture,
    # default empty so the original 5 cases are unchanged.
    hardship = HardshipEvidence(**f.get("hardship", {}))

    case = Case(case_id=case_id, applicant=applicant, loan=loan_d, arrears=arr_d,
                income=income, hardship=hardship, documents=manifest)
    return case, log

"""Agent Sanad — canonical Pydantic v2 schemas (MVP). Single source of truth."""
from __future__ import annotations
from datetime import date
from typing import Literal, Optional
from pydantic import BaseModel, Field, ConfigDict, conint, confloat

Path           = Literal["UPDATE_INSTALLMENT", "TRANSFER_ARREARS", "NONE"]
Recommendation = Literal["Approve", "Request documents", "Refer to employee", "Reject"]
RiskLevel      = Literal["low", "medium", "high"]
Confidence     = Literal["high", "medium", "low"]
IncomeTrend    = Literal["increased", "stable", "decreased", "unknown"]


class ApplicantProfile(BaseModel):                 # from UAE PASS adapter (retrieved)
    model_config = ConfigDict(extra="forbid")
    applicant_ref: str
    name_masked: str
    uae_national: bool
    marital_status: Literal["single", "married", "unknown"] = "unknown"
    family_size: conint(ge=1, le=20) = 1
    income_per_member_aed: Optional[confloat(ge=0)] = None


class LoanData(BaseModel):                          # from Loan adapter
    model_config = ConfigDict(extra="forbid")
    agreement_id: str
    remaining_balance_aed: confloat(ge=0)
    original_approved_term_months: conint(ge=1, le=600)
    remaining_term_months: conint(ge=0, le=600)
    loan_original_end_date: Optional[date] = None
    current_installment_aed: confloat(ge=0)


class ArrearsData(BaseModel):                       # from Arrears adapter
    model_config = ConfigDict(extra="forbid")
    agreement_id: str
    arrears_amount_aed: confloat(ge=0)
    unpaid_installments: conint(ge=0, le=600)
    active_request_exists: bool = False


class IncomeEvidence(BaseModel):                    # extraction + Salary Verification adapter
    model_config = ConfigDict(extra="forbid")
    salary_certificate_income_aed: Optional[confloat(ge=0)] = None
    verified_monthly_income_aed: Optional[confloat(ge=0)] = None   # the engine consumes this
    income_trend: IncomeTrend = "unknown"
    obligations_ratio: Optional[confloat(ge=0, le=5)] = None
    variance_pct: confloat(ge=0, le=100) = 0
    contradiction_flag: bool = False


class HardshipEvidence(BaseModel):
    model_config = ConfigDict(extra="forbid")
    unemployed_flag: bool = False
    temporary_circumstance_flag: bool = False
    unverified: bool = False
    # v1.1 — short, human-readable description of the verified circumstance.
    # Officer-facing only; never shown to beneficiary. Empty for the original
    # 5 v0.8 cases so behavior is unchanged.
    note: str = Field(default="", max_length=400)


class DocumentManifest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    required_document_types: list[str] = Field(default_factory=lambda: ["salary_certificate"])
    received_document_types: list[str] = Field(default_factory=list)
    injection_flags: list[str] = Field(default_factory=list)

    @property
    def missing_required(self) -> list[str]:
        return [d for d in self.required_document_types if d not in self.received_document_types]


class ProposedPlan(BaseModel):
    model_config = ConfigDict(extra="forbid")
    path: Path = "NONE"
    new_total_installment_aed: confloat(ge=0) = 0
    additional_premium_aed: confloat(ge=0) = 0
    additional_months: conint(ge=0, le=600) = 0
    arrears_moved_to_end: bool = False
    period_ok: bool = True
    proposed_schedule_end_date: Optional[date] = None


class RecommendationReport(BaseModel):              # the official Section-8 output
    model_config = ConfigDict(extra="forbid")
    case_id: str
    application_status: Literal["Complete", "Incomplete"]
    case_summary: str
    income_analysis: str
    arrears_amount_aed: confloat(ge=0) = 0
    remaining_balance_aed: confloat(ge=0) = 0
    remaining_term_months: conint(ge=0, le=600) = 0
    proposed_deduction_rate: confloat(ge=0, le=5) = 0
    proposed_plan: ProposedPlan = Field(default_factory=ProposedPlan)
    twenty_pct_compliance: Literal["Pass", "Fail", "N/A"] = "N/A"
    period_compliance: Literal["Pass", "Fail", "N/A"] = "N/A"
    recommendation: Recommendation
    reasoning: str
    risk_level: RiskLevel = "low"
    confidence: Confidence = "high"
    fired_rules: list[str] = Field(default_factory=list)
    policy_version: str = "sanad-v0.8"


class PolicyConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")
    deduction_cap_pct: confloat(gt=0, le=1) = 0.20
    respect_approved_period: bool = True
    auto_reject_active_request: bool = True
    salary_basis: Literal["verified_monthly", "gross", "net"] = "verified_monthly"
    cap_applies_to: Literal["total_installment", "additional_premium"] = "total_installment"
    period_basis: Literal["remaining_term", "original_term_end_date"] = "remaining_term"
    active_request_policy: Literal["always_reject", "status_conditional"] = "always_reject"
    rounding: Literal["premium_floor_months_ceil", "nearest"] = "premium_floor_months_ceil"
    min_headroom_aed: confloat(ge=0) = 50
    high_obligations_pct: confloat(ge=0, le=5) = 0.60
    low_income_per_member_aed: confloat(ge=0) = 2500
    income_variance_threshold: confloat(ge=0, le=1) = 0.30
    policy_version: str = "sanad-v0.8"


class Case(BaseModel):                              # the orchestrator's working object
    model_config = ConfigDict(extra="forbid")
    case_id: str
    applicant: Optional[ApplicantProfile] = None
    loan: Optional[LoanData] = None
    arrears: Optional[ArrearsData] = None
    income: IncomeEvidence = Field(default_factory=IncomeEvidence)
    hardship: HardshipEvidence = Field(default_factory=HardshipEvidence)
    documents: DocumentManifest = Field(default_factory=DocumentManifest)

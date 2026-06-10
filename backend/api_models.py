"""v1.6 API models — typed Pydantic request/response schemas."""
from __future__ import annotations
from pydantic import BaseModel, Field
from typing import Optional


class ConsentValidateRequest(BaseModel):
    purpose_code: str = "identity.verify"
    connector_scope: str = "gsb.access"


class ConsentValidateResponse(BaseModel):
    ok: bool
    reason: str
    consent: Optional[dict] = None


class ConsentCreateRequest(BaseModel):
    beneficiary_ref: str = ""
    purpose_code: str = "identity.verify"
    data_categories: list[str] = ["profile"]
    connector_scopes: list[str] = ["identity.verify"]
    expires_at: Optional[str] = None


class SessionStartRequest(BaseModel):
    purpose_code: str = "identity.verify"
    beneficiary_ref: str = ""


class SessionStartResponse(BaseModel):
    session_id: str
    nonce: str
    auth_url: str
    expires_at: str
    purpose_code: str
    mock: bool = True


class SessionCallbackRequest(BaseModel):
    session_id: str = Field(..., min_length=1)
    code: str = Field(..., min_length=1)
    nonce: str = Field(..., min_length=1)


class SessionCallbackResponse(BaseModel):
    session_id: str
    auth_code: Optional[str] = None
    status: str
    subject_ref: Optional[str] = None
    assurance_level: Optional[str] = None
    auth_time: Optional[str] = None
    error: Optional[str] = None
    mock: bool = True


class ActionUploadRequest(BaseModel):
    detail: str = ""


class ActionRejectRequest(BaseModel):
    reason: str = ""


class ActionResubmitRequest(BaseModel):
    detail: str = ""


class AppealCreateRequest(BaseModel):
    reason: str = Field(..., min_length=1)
    new_evidence: dict = {}


class AppealCreateResponse(BaseModel):
    appeal_id: int
    status: str
    case_id: str


class AppealEvidenceRequest(BaseModel):
    evidence: dict = {}


class AppealReviewRequest(BaseModel):
    notes: str = ""


class AppealDecisionRequest(BaseModel):
    decision: str = Field(..., min_length=1)
    rationale: str = ""


class AppealSupervisorApproveRequest(BaseModel):
    notes: str = ""


class PackageVerifyResponse(BaseModel):
    valid: bool
    package_id: Optional[str] = None
    package_hash: Optional[str] = None
    error: Optional[str] = None


class CaseAssignRequest(BaseModel):
    case_id: str = Field(..., min_length=1)
    officer_ref: str = Field(..., min_length=1)
    priority: str = "normal"
    sla_hours: int = 72


class CaseAssignResponse(BaseModel):
    case_id: str
    officer_ref: str
    priority: str
    sla_hours: int
    status: str
    mock: bool = True


class LifecycleTransitionRequest(BaseModel):
    target_state: str = Field(..., min_length=1)
    actor: str = "system"
    detail: str = ""


class LifecycleTransitionResponse(BaseModel):
    case_id: str
    previous_state: Optional[str] = None
    current_state: str
    transition: str
    ok: bool
    reason: Optional[str] = None


class ConnectorFailureProfileRequest(BaseModel):
    failure_mode: str = "timeout"
    latency_ms: int = 500
    error_rate: float = 1.0


class ConnectorIncidentResponse(BaseModel):
    id: int
    connector: str
    incident_type: str
    detail: Optional[str] = None
    created_at: str


class FairnessSyntheticCohortRequest(BaseModel):
    cohort_size: int = 100
    income_range: tuple[float, float] = (0, 50000)
    family_size_range: tuple[int, int] = (1, 10)


class FairnessSlice(BaseModel):
    slice_name: str
    metric: str
    value: float
    sample_size: int


class AuditExportManifest(BaseModel):
    case_id: str
    entries: int
    includes: list[str]
    generated_at: str


class EvidenceGraphNode(BaseModel):
    id: str
    type: str
    label: str
    metadata: dict = {}


class EvidenceGraphEdge(BaseModel):
    from_id: str
    to_id: str
    label: str


class EvidenceGraphResponse(BaseModel):
    case_id: str
    nodes: list[dict]
    edges: list[dict]
    mermaid: Optional[str] = None

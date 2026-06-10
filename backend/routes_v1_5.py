"""v1.5 routes — consent guard, sessions, actions, appeals, supervisor, case-management."""
from __future__ import annotations
import json
import time
import uuid
from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse

from backend.store import STORE
from backend.rbac import check_access, get_role, get_user
from backend.connectors import (
    list_connectors, health as connector_health,
    case_management_assign_officer, case_management_schedule_callback,
    case_management_record_note, case_management_update_sla,
    case_management_create_escalation, case_management_close_case,
)
from backend.consent_guard import validate_consent, get_consent_usage
from backend.uaepass_session import get_session, expire_session_mock, revoke_session_mock
from backend.audit_chain import add_chain_event
from backend.decision_package import verify_decision_package


def register_routes(app, MOCK_MODE, APP_VERSION):
    """Register all v1.5 routes on the FastAPI app."""

    # ── Consent Guard v2 ──
    @app.post("/consents/{consent_id}/validate")
    def post_consent_validate(consent_id: str, body: dict, request: Request):
        role = get_role(request)
        user = get_user(request)
        result = validate_consent(
            consent_id.upper(),
            body.get("purpose_code", "identity.verify"),
            body.get("connector_scope", "gsb.access"),
            user if role == "beneficiary" else "",
            str(request.url.path),
        )
        return result

    @app.get("/consents/{consent_id}/usage")
    def get_consent_usage_route(consent_id: str):
        return {"consent_id": consent_id.upper(), "usage": get_consent_usage(consent_id.upper())}

    # ── UAE PASS Session v3 ──
    @app.get("/sessions/{session_id}")
    def get_session_route(session_id: str):
        s = get_session(session_id.upper())
        if not s:
            raise HTTPException(404, f"Session '{session_id}' not found")
        return s

    @app.post("/sessions/{session_id}/expire-mock")
    def post_session_expire(session_id: str):
        return expire_session_mock(session_id.upper())

    @app.post("/sessions/{session_id}/revoke-mock")
    def post_session_revoke(session_id: str):
        return revoke_session_mock(session_id.upper())

    # ── Action Workflow v4: upload-mock ──
    @app.post("/cases/{case_id}/actions/{action_id}/upload-mock")
    def post_action_upload(case_id: str, action_id: str, body: dict, request: Request):
        user = get_user(request)
        cid = case_id.upper()
        if STORE._db:
            owner_row = STORE._db.execute(
                "SELECT owner FROM case_actions WHERE case_id=? AND action_id=?",
                (cid, action_id)).fetchone()
            if owner_row and owner_row[0] != user and owner_row[0] != "beneficiary":
                raise HTTPException(403, "Only the action owner can upload")
            ts = time.strftime("%Y-%m-%dT%H:%M:%S")
            STORE._db.execute(
                "UPDATE case_actions SET status='uploaded', updated_at=? WHERE case_id=? AND action_id=?",
                (ts, cid, action_id))
            STORE._db.execute(
                "INSERT INTO action_events (case_id, action_id, event_type, actor, detail, created_at) VALUES (?,?,?,?,?,?)",
                (cid, action_id, "uploaded", user, body.get("detail", ""), ts))
            STORE._db.commit()
            add_chain_event(cid, user, "action.uploaded", {"action_id": action_id})
        return {"status": "uploaded", "action_id": action_id, "case_id": cid}

    # ── Action Workflow v4: reject ──
    @app.post("/cases/{case_id}/actions/{action_id}/reject")
    def post_action_reject_v15(case_id: str, action_id: str, body: dict, request: Request):
        user = get_user(request)
        cid = case_id.upper()
        reason = body.get("reason", "")
        if STORE._db:
            ts = time.strftime("%Y-%m-%dT%H:%M:%S")
            STORE._db.execute(
                "UPDATE case_actions SET status='rejected', officer_note=?, updated_at=? WHERE case_id=? AND action_id=?",
                (reason, ts, cid, action_id))
            STORE._db.execute(
                "INSERT INTO action_events (case_id, action_id, event_type, actor, detail, created_at) VALUES (?,?,?,?,?,?)",
                (cid, action_id, "rejected", user, reason, ts))
            STORE._db.commit()
            add_chain_event(cid, user, "action.rejected", {"action_id": action_id, "reason": reason})
        return {"status": "rejected", "action_id": action_id, "case_id": cid}

    # ── Action Workflow v4: resubmit ──
    @app.post("/cases/{case_id}/actions/{action_id}/resubmit")
    def post_action_resubmit_v15(case_id: str, action_id: str, body: dict, request: Request):
        user = get_user(request)
        cid = case_id.upper()
        if STORE._db:
            ts = time.strftime("%Y-%m-%dT%H:%M:%S")
            STORE._db.execute(
                "UPDATE case_actions SET status='resubmitted', updated_at=? WHERE case_id=? AND action_id=?",
                (ts, cid, action_id))
            STORE._db.execute(
                "INSERT INTO action_events (case_id, action_id, event_type, actor, detail, created_at) VALUES (?,?,?,?,?,?)",
                (cid, action_id, "resubmitted", user, body.get("detail", ""), ts))
            STORE._db.commit()
        return {"status": "resubmitted", "action_id": action_id, "case_id": cid}

    # ── Action Timeline ──
    @app.get("/cases/{case_id}/actions/timeline")
    def get_action_timeline(case_id: str):
        if STORE._db is None:
            return {"timeline": []}
        rows = STORE._db.execute(
            "SELECT event_type, actor, detail, created_at FROM action_events WHERE case_id=? ORDER BY id",
            (case_id.upper(),)).fetchall()
        return {"timeline": [{"event": r[0], "actor": r[1], "detail": r[2], "at": r[3]} for r in rows]}

    # ── Appeals Workbench ──
    @app.get("/appeals")
    def get_all_appeals_route(request: Request):
        check_access("GET", "/appeals", get_role(request))
        if STORE._db is None:
            return {"appeals": []}
        rows = STORE._db.execute(
            "SELECT id, case_id, reason, status, created_at, decided_at, decision FROM appeals ORDER BY id DESC"
        ).fetchall()
        return {"appeals": [
            {"id": r[0], "case_id": r[1], "reason": r[2], "status": r[3],
             "created_at": r[4], "decided_at": r[5], "decision": r[6]} for r in rows
        ]}

    @app.get("/appeals/{appeal_id}")
    def get_appeal_route(appeal_id: int):
        if STORE._db is None:
            raise HTTPException(404, "store unavailable")
        row = STORE._db.execute(
            "SELECT id, case_id, reason, new_evidence, status, created_at, decided_at, decision, decision_by FROM appeals WHERE id=?",
            (appeal_id,)).fetchone()
        if not row:
            raise HTTPException(404, f"Appeal '{appeal_id}' not found")
        return {
            "appeal_id": row[0], "case_id": row[1], "reason": row[2],
            "new_evidence": json.loads(row[3]) if row[3] else {},
            "status": row[4], "created_at": row[5],
            "decided_at": row[6], "decision": row[7], "decision_by": row[8],
        }

    @app.post("/appeals/{appeal_id}/submit-evidence")
    def post_appeal_evidence(appeal_id: int, body: dict, request: Request):
        user = get_user(request)
        if STORE._db is None:
            return {"status": "error", "message": "store unavailable"}
        evidence = json.dumps(body.get("evidence", {}))
        STORE._db.execute(
            "UPDATE appeals SET new_evidence=?, status='submitted' WHERE id=?",
            (evidence, appeal_id))
        STORE._db.execute(
            "INSERT INTO appeal_events (appeal_id, event_type, actor, detail, created_at) VALUES (?,?,?,?,?)",
            (appeal_id, "evidence_submitted", user, "", time.strftime("%Y-%m-%dT%H:%M:%S")))
        STORE._db.commit()
        return {"appeal_id": appeal_id, "status": "submitted"}

    @app.post("/appeals/{appeal_id}/review")
    def post_appeal_review(appeal_id: int, body: dict, request: Request):
        user = get_user(request)
        if STORE._db is None:
            return {"status": "error", "message": "store unavailable"}
        STORE._db.execute(
            "UPDATE appeals SET status='officer_review' WHERE id=?", (appeal_id,))
        STORE._db.execute(
            "INSERT INTO appeal_events (appeal_id, event_type, actor, detail, created_at) VALUES (?,?,?,?,?)",
            (appeal_id, "review_started", user, body.get("notes", ""), time.strftime("%Y-%m-%dT%H:%M:%S")))
        STORE._db.commit()
        return {"appeal_id": appeal_id, "status": "officer_review"}

    @app.post("/appeals/{appeal_id}/decision")
    def post_appeal_decision(appeal_id: int, body: dict, request: Request):
        user = get_user(request)
        decision = body.get("decision", "upheld")
        if STORE._db is None:
            return {"status": "error", "message": "store unavailable"}
        ts = time.strftime("%Y-%m-%dT%H:%M:%S")
        STORE._db.execute(
            "UPDATE appeals SET status=?, decision=?, decided_at=?, decision_by=? WHERE id=?",
            (decision, decision, ts, user, appeal_id))
        STORE._db.execute(
            "INSERT INTO appeal_events (appeal_id, event_type, actor, detail, created_at) VALUES (?,?,?,?,?)",
            (appeal_id, f"decided_{decision}", user, body.get("rationale", ""), ts))
        STORE._db.commit()
        return {"appeal_id": appeal_id, "status": decision, "decision": decision}

    @app.post("/appeals/{appeal_id}/supervisor-approve")
    def post_appeal_supervisor_approve(appeal_id: int, body: dict, request: Request):
        user = get_user(request)
        check_access("POST", "/supervisor", get_role(request))
        if STORE._db is None:
            return {"status": "error", "message": "store unavailable"}
        ts = time.strftime("%Y-%m-%dT%H:%M:%S")
        STORE._db.execute(
            "UPDATE appeals SET status='closed', decided_at=? WHERE id=?",
            (ts, appeal_id))
        STORE._db.execute(
            "INSERT INTO appeal_events (appeal_id, event_type, actor, detail, created_at) VALUES (?,?,?,?,?)",
            (appeal_id, "supervisor_approved", user, body.get("notes", ""), ts))
        STORE._db.commit()
        return {"appeal_id": appeal_id, "status": "closed"}

    # ── Decision Package v2: Verify ──
    @app.post("/decision-packages/{package_id}/verify")
    def post_package_verify(package_id: str):
        return verify_decision_package(package_id.upper())

    @app.get("/decision-packages/{package_id}/receipt")
    def get_package_receipt(package_id: str):
        from backend.decision_package import get_decision_package
        pkg = get_decision_package(package_id.upper())
        if not pkg:
            raise HTTPException(404, f"Package '{package_id}' not found")
        from backend.decision_package import verify_decision_package
        verification = verify_decision_package(package_id.upper())
        return {"package": pkg, "verification": verification}

    @app.post("/decision-packages/{package_id}/revoke-mock")
    def post_package_revoke(package_id: str):
        if STORE._db:
            STORE._db.execute(
                "UPDATE decision_packages SET signed_at=NULL WHERE id=?",
                (package_id.upper(),))
            STORE._db.commit()
            add_chain_event(package_id.upper(), "system", "package.revoked", {})
        return {"package_id": package_id.upper(), "revoked": True}

    # ── Supervisor Command Center v2 ──
    @app.get("/supervisor/backlog")
    def get_supervisor_backlog(request: Request):
        check_access("GET", "/supervisor", get_role(request))
        if STORE._db is None:
            return {"backlog": [], "total": 0}
        rows = STORE._db.execute(
            "SELECT ca.case_id, ca.officer_ref, ca.status, ca.priority, ca.assigned_at, ca.due_date "
            "FROM case_assignments ca ORDER BY ca.assigned_at DESC"
        ).fetchall()
        backlog = [
            {"case_id": r[0], "officer": r[1], "status": r[2], "priority": r[3],
             "assigned_at": r[4], "due_date": r[5]} for r in rows
        ]
        return {"backlog": backlog, "total": len(backlog)}

    @app.get("/supervisor/sla-risk")
    def get_supervisor_sla_risk(request: Request):
        check_access("GET", "/supervisor", get_role(request))
        if STORE._db is None:
            return {"sla_risk": [], "at_risk": 0}
        rows = STORE._db.execute(
            "SELECT case_id, stage, deadline, breached FROM case_sla ORDER BY deadline ASC"
        ).fetchall()
        items = [
            {"case_id": r[0], "stage": r[1], "deadline": r[2], "breached": bool(r[3])}
            for r in rows
        ]
        at_risk = sum(1 for i in items if i["breached"] or i["deadline"] < time.strftime("%Y-%m-%dT%H:%M:%S"))
        return {"sla_risk": items, "at_risk": at_risk}

    @app.get("/supervisor/fairness")
    def get_supervisor_fairness(request: Request):
        check_access("GET", "/supervisor", get_role(request))
        if STORE._db is None:
            return {"fairness_slices": []}
        rows = STORE._db.execute(
            "SELECT slice_name, metric, value, sample_size FROM fairness_slices ORDER BY id DESC LIMIT 20"
        ).fetchall()
        return {"fairness_slices": [
            {"slice": r[0], "metric": r[1], "value": r[2], "sample_size": r[3]} for r in rows
        ]}

    @app.get("/supervisor/connectors/incidents")
    def get_supervisor_connector_incidents(request: Request):
        check_access("GET", "/supervisor", get_role(request))
        if STORE._db is None:
            return {"incidents": []}
        rows = STORE._db.execute(
            "SELECT connector_name, service, status, failure_mode, created_at "
            "FROM connector_calls WHERE status!='ok' ORDER BY created_at DESC LIMIT 50"
        ).fetchall()
        return {"incidents": [
            {"connector": r[0], "service": r[1], "status": r[2],
             "failure_mode": r[3], "at": r[4]} for r in rows
        ]}

    @app.get("/supervisor/officer-workload")
    def get_supervisor_officer_workload(request: Request):
        check_access("GET", "/supervisor", get_role(request))
        if STORE._db is None:
            return {"workload": []}
        rows = STORE._db.execute(
            "SELECT officer_ref, COUNT(*) as cnt, "
            "SUM(CASE WHEN status='open' THEN 1 ELSE 0 END) as open_count "
            "FROM case_assignments GROUP BY officer_ref ORDER BY cnt DESC"
        ).fetchall()
        return {"workload": [
            {"officer": r[0], "total_cases": r[1], "open_cases": r[2]} for r in rows
        ]}

    @app.get("/supervisor/override-review")
    def get_supervisor_override_review(request: Request):
        check_access("GET", "/supervisor", get_role(request))
        if STORE._db is None:
            return {"overrides": []}
        rows = STORE._db.execute(
            "SELECT case_id, action, override_reason_code, notes, created_at "
            "FROM officer_actions WHERE override_reason_code IS NOT NULL ORDER BY created_at DESC LIMIT 30"
        ).fetchall()
        return {"overrides": [
            {"case_id": r[0], "action": r[1], "reason_code": r[2],
             "notes": r[3], "at": r[4]} for r in rows
        ]}

    @app.get("/supervisor/consent-denial-rate")
    def get_supervisor_consent_denial_rate(request: Request):
        check_access("GET", "/supervisor", get_role(request))
        if STORE._db is None:
            return {"total": 0, "denied": 0, "rate": 0.0}
        total = STORE._db.execute(
            "SELECT COUNT(*) FROM connector_calls WHERE consent_id IS NOT NULL").fetchone()[0]
        denied = STORE._db.execute(
            "SELECT COUNT(*) FROM connector_calls WHERE consent_id IS NOT NULL AND status='consent_denied'"
        ).fetchone()[0]
        rate = denied / total if total > 0 else 0.0
        return {"total": total, "denied": denied, "rate": round(rate, 4)}

    @app.get("/supervisor/document-trust-failure-rate")
    def get_supervisor_doc_trust_failure(request: Request):
        check_access("GET", "/supervisor", get_role(request))
        if STORE._db is None:
            return {"total": 0, "failures": 0, "rate": 0.0}
        total = STORE._db.execute("SELECT COUNT(*) FROM document_checks").fetchone()[0]
        failures = STORE._db.execute(
            "SELECT COUNT(*) FROM document_checks WHERE trust_status='FAIL'"
        ).fetchone()[0]
        rate = failures / total if total > 0 else 0.0
        return {"total": total, "failures": failures, "rate": round(rate, 4)}

    # ── Case-Management Connector Routes ──
    @app.post("/connectors/case-management/mock/assign-officer")
    def post_cm_assign_officer(body: dict):
        return case_management_assign_officer(
            body.get("case_id", ""),
            body.get("officer_ref", ""),
            body.get("priority", "normal"),
            body.get("sla_hours", 72),
        )

    @app.post("/connectors/case-management/mock/schedule-callback")
    def post_cm_schedule_callback(body: dict):
        return case_management_schedule_callback(
            body.get("case_id", ""),
            body.get("beneficiary_ref", ""),
            body.get("scheduled_at", ""),
            body.get("channel", "phone"),
        )

    @app.post("/connectors/case-management/mock/record-note")
    def post_cm_record_note(body: dict):
        return case_management_record_note(
            body.get("case_id", ""),
            body.get("officer_ref", ""),
            body.get("note", ""),
        )

    @app.post("/connectors/case-management/mock/update-sla")
    def post_cm_update_sla(body: dict):
        return case_management_update_sla(
            body.get("case_id", ""),
            body.get("stage", ""),
            body.get("deadline", ""),
        )

    @app.post("/connectors/case-management/mock/create-escalation")
    def post_cm_create_escalation(body: dict):
        return case_management_create_escalation(
            body.get("case_id", ""),
            body.get("reason", ""),
            body.get("supervisor_ref", ""),
        )

    @app.post("/connectors/case-management/mock/close-case")
    def post_cm_close_case(body: dict):
        return case_management_close_case(
            body.get("case_id", ""),
            body.get("resolution", "resolved"),
        )

    # ── Connector Schemas (typed Pydantic models) ──
    from pydantic import BaseModel, Field
    from typing import Optional

    class ConnectorHealthResponse(BaseModel):
        name: str
        status: str
        failure_mode: Optional[str] = None
        mock: bool = True
        timestamp: str

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

    class ConsentValidateRequest(BaseModel):
        purpose_code: str = "identity.verify"
        connector_scope: str = "gsb.access"

    class ConsentValidateResponse(BaseModel):
        ok: bool
        reason: str
        consent: Optional[dict] = None

    class AppealCreateRequest(BaseModel):
        reason: str = Field(..., min_length=1)
        new_evidence: dict = {}

    class AppealCreateResponse(BaseModel):
        appeal_id: int
        status: str
        case_id: str

    class AppealDecisionRequest(BaseModel):
        decision: str = Field(..., min_length=1)
        rationale: str = ""

    # ── API Guide Materials Router ──
    @app.get("/openapi.json")
    def get_openapi_json():
        return app.openapi()

    @app.get("/materials/api-guide")
    def get_materials_api_guide():
        return {
            "title": "Agent Sanad v1.5 API Guide",
            "version": APP_VERSION,
            "base_url": "http://127.0.0.1:8000",
            "endpoints": [
                {"method": "GET", "path": "/healthz", "description": "Liveness check"},
                {"method": "POST", "path": "/consents/{id}/validate", "description": "Validate consent (v2)"},
                {"method": "GET", "path": "/sessions/{id}", "description": "Get session state (v3)"},
                {"method": "POST", "path": "/cases/{id}/actions/{id}/upload-mock", "description": "Upload action evidence"},
                {"method": "POST", "path": "/appeals/{id}/decision", "description": "Make appeal decision"},
                {"method": "GET", "path": "/supervisor/backlog", "description": "Supervisor backlog view"},
                {"method": "GET", "path": "/supervisor/sla-risk", "description": "SLA risk board"},
                {"method": "GET", "path": "/supervisor/fairness", "description": "Fairness slices"},
                {"method": "GET", "path": "/supervisor/connectors/incidents", "description": "Connector incidents"},
            ],
            "auth": "x-sanad-role header",
            "mock_mode": MOCK_MODE,
        }

    @app.get("/materials/integration-map")
    def get_materials_integration_map():
        connectors = list_connectors()
        return {
            "title": "UAE Integration Map",
            "version": APP_VERSION,
            "connectors": [
                {"name": c["name"], "owner": c.get("owner", ""), "services": c.get("services", []),
                 "purpose_codes": c.get("purpose_codes", []), "mock": c.get("mock", True)}
                for c in connectors
            ],
            "note": "All connectors are mock. Contract-shaped, fixture-backed, test-enforced.",
        }

    @app.get("/materials/security-one-pager")
    def get_materials_security_one_pager():
        return {
            "title": "Agent Sanad v1.5 Security One-Pager",
            "version": APP_VERSION,
            "controls": [
                {"name": "Consent Guard v2", "status": "Active", "description": "Purpose, scope, expiry, revocation, ownership enforcement"},
                {"name": "UAE PASS Session v3", "status": "Active", "description": "Stored nonce, expiry, consumed callback, replay rejection"},
                {"name": "ABAC Ownership", "status": "Active", "description": "Object-level authorization for cases, consents, actions, appeals"},
                {"name": "Signature Integrity", "status": "Active", "description": "Package hash binding, tamper detection, revocation"},
                {"name": "Audit Chain", "status": "Active", "description": "SHA256 hash chain, immutable, verifiable"},
                {"name": "Denied-Access Audit", "status": "Active", "description": "All denied consent/access attempts recorded"},
                {"name": "RBAC", "status": "Active", "description": "5 roles via x-sanad-role header"},
                {"name": "Security Headers", "status": "Active", "description": "CSP, HSTS, XSS protection, rate limiting"},
                {"name": "PII Discipline", "status": "Active", "description": "No real credentials, no real personal data, synthetic identifiers only"},
            ],
            "doctrine": "LLM reads and explains. Deterministic code decides. Human owns the exception.",
        }

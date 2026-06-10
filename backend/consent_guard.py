"""Consent guard v2 — enforces purpose, scope, expiry, revocation, and beneficiary ownership."""
from __future__ import annotations
import json
from datetime import datetime, timezone
from typing import Any

from backend.store import STORE
from backend.audit_chain import add_chain_event


def validate_consent(
    consent_id: str,
    required_purpose: str,
    required_scope: str,
    beneficiary_ref: str,
    request_path: str = "",
) -> dict:
    """
    Validate a consent record against required purpose, scope, and ownership.
    Returns {ok: bool, reason: str, consent: dict|None}.
    Denied attempts are recorded in the audit chain.
    """
    if not consent_id:
        _audit_denied("", "missing_consent", required_purpose, required_scope, beneficiary_ref, request_path)
        return {"ok": False, "reason": "Consent required", "consent": None}

    if STORE._db is None:
        # Demo mode: allow without DB
        return {"ok": True, "reason": "demo_mode", "consent": None}

    row = STORE._db.execute(
        "SELECT id, beneficiary_ref, purpose_code, connector_scopes, granted_at, expires_at, revoked_at FROM consents WHERE id=?",
        (consent_id,),
    ).fetchone()

    if not row:
        _audit_denied(consent_id, "not_found", required_purpose, required_scope, beneficiary_ref, request_path)
        return {"ok": False, "reason": f"Consent '{consent_id}' not found", "consent": None}

    consent = {
        "id": row[0], "beneficiary_ref": row[1], "purpose_code": row[2],
        "connector_scopes": row[3].split(",") if row[3] else [],
        "granted_at": row[4], "expires_at": row[5] or None, "revoked_at": row[6] or None,
    }

    # Check revoked
    if consent["revoked_at"]:
        _audit_denied(consent_id, "revoked", required_purpose, required_scope, beneficiary_ref, request_path)
        return {"ok": False, "reason": "Consent revoked", "consent": consent}

    # Check expiry
    if consent["expires_at"]:
        try:
            expiry = datetime.fromisoformat(consent["expires_at"].replace("Z", "+00:00"))
            if expiry < datetime.now(timezone.utc):
                _audit_denied(consent_id, "expired", required_purpose, required_scope, beneficiary_ref, request_path)
                return {"ok": False, "reason": "Consent expired", "consent": consent}
        except Exception:
            pass

    # Check purpose
    if consent["purpose_code"] != required_purpose:
        _audit_denied(consent_id, "purpose_mismatch", required_purpose, required_scope, beneficiary_ref, request_path)
        return {"ok": False, "reason": f"Purpose mismatch: required '{required_purpose}', got '{consent['purpose_code']}'", "consent": consent}

    # Check scope
    scopes = consent["connector_scopes"]
    if required_scope not in scopes and "*" not in scopes:
        _audit_denied(consent_id, "scope_mismatch", required_purpose, required_scope, beneficiary_ref, request_path)
        return {"ok": False, "reason": f"Scope mismatch: required '{required_scope}', got {scopes}", "consent": consent}

    # Check ownership (beneficiary must own the consent, unless admin/officer override)
    if beneficiary_ref and consent["beneficiary_ref"] != beneficiary_ref:
        _audit_denied(consent_id, "wrong_owner", required_purpose, required_scope, beneficiary_ref, request_path)
        return {"ok": False, "reason": "Consent belongs to another beneficiary", "consent": consent}

    return {"ok": True, "reason": "valid", "consent": consent}


def _audit_denied(consent_id: str, denial_reason: str, required_purpose: str,
                 required_scope: str, beneficiary_ref: str, request_path: str) -> None:
    """Record a denied access attempt in the audit chain."""
    try:
        add_chain_event(
            case_id=f"ACCESS-DENIED-{denial_reason}",
            actor="consent_guard",
            action="consent.denied",
            payload={
                "consent_id": consent_id,
                "denial_reason": denial_reason,
                "required_purpose": required_purpose,
                "required_scope": required_scope,
                "beneficiary_ref": beneficiary_ref,
                "request_path": request_path,
            },
        )
    except Exception:
        pass


def get_consent_usage(consent_id: str) -> list[dict]:
    """Return audit events for a consent."""
    if STORE._db is None:
        return []
    rows = STORE._db.execute(
        "SELECT id, connector_name, service, consent_id, purpose_code, status, created_at FROM connector_calls WHERE consent_id=? ORDER BY created_at DESC",
        (consent_id,),
    ).fetchall()
    return [
        {
            "id": r[0], "connector": r[1], "service": r[2],
            "consent_id": r[3], "purpose_code": r[4], "status": r[5], "created_at": r[6],
        }
        for r in rows
    ]

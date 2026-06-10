"""Connector registry and mock connectors for v1.4."""
from __future__ import annotations
import time
import uuid
from datetime import datetime, timezone
from typing import Any

from backend.store import STORE

_CONNECTORS: dict[str, dict[str, Any]] = {}


def _reg(name: str, version: str, owner: str, services: list[str],
         purpose_codes: list[str], latency_budget_ms: int = 100):
    _CONNECTORS[name] = {
        "name": name, "version": version, "owner": owner,
        "status": "up", "services": services,
        "purpose_codes": purpose_codes,
        "latency_budget_ms": latency_budget_ms,
        "failure_mode": None, "last_call_at": None,
        "mock": True,
    }
    # Ensure connector_state row exists
    _ensure_state(name)


def _ensure_state(name: str):
    if STORE._db is None:
        return
    try:
        exists = STORE._db.execute("SELECT 1 FROM connector_state WHERE name=?", (name,)).fetchone()
        if not exists:
            STORE._db.execute(
                "INSERT INTO connector_state (name, status, failure_mode, latency_budget_ms) VALUES (?, 'up', NULL, ?)",
                (name, _CONNECTORS.get(name, {}).get("latency_budget_ms", 100)))
            STORE._db.commit()
    except Exception:
        pass


def _get_state(name: str) -> dict:
    if STORE._db is None:
        return {"status": "up", "failure_mode": None, "latency_budget_ms": 100}
    row = STORE._db.execute("SELECT status, failure_mode, latency_budget_ms FROM connector_state WHERE name=?", (name,)).fetchone()
    if row:
        return {"status": row[0], "failure_mode": row[1], "latency_budget_ms": row[2]}
    return {"status": "up", "failure_mode": None, "latency_budget_ms": 100}


def _log_call(name: str, service: str, status: str, consent_id: str | None = None,
              purpose_code: str | None = None, correlation_id: str | None = None,
              latency_ms: int = 0, failure_mode: str | None = None):
    if STORE._db is None:
        return
    try:
        STORE._db.execute(
            "INSERT INTO connector_calls (connector_name, service, consent_id, purpose_code, correlation_id, status, latency_ms, failure_mode, created_at) VALUES (?,?,?,?,?,?,?,?,?)",
            (name, service, consent_id, purpose_code, correlation_id, status, latency_ms, failure_mode, datetime.now(timezone.utc).isoformat()))
        STORE._db.execute("UPDATE connector_state SET last_call_at=? WHERE name=?", (datetime.now(timezone.utc).isoformat(), name))
        STORE._db.commit()
    except Exception:
        pass


def _check_consent(consent_id: str | None, purpose_code: str | None, connector_name: str):
    """Raise ValueError if consent is missing/revoked."""
    if not consent_id:
        raise ValueError(f"Consent required for connector '{connector_name}'")
    if STORE._db is None:
        return
    row = STORE._db.execute(
        "SELECT purpose_code, revoked_at FROM consents WHERE id=?",
        (consent_id,)).fetchone()
    if row is None:
        raise ValueError(f"Consent '{consent_id}' not found for connector '{connector_name}'")
    if row[1]:
        raise ValueError(f"Consent '{consent_id}' revoked")

# ── Register built-in connectors ──────────────────────────────────────────

_reg("uaepass", "1.0.0", "UAEPASS", ["auth", "userinfo", "signature", "eseal"],
     ["identity.verify", "document.sign"], latency_budget_ms=200)
_reg("gsb", "1.0.0", "TDRA-GSB",
     ["identity.profile", "housing.loan", "housing.arrears", "housing.active_request",
      "financial.liabilities", "document.verify", "notification.dispatch"],
     ["data.retrieve", "data.exchange"])
_reg("szhp-core", "1.0.0", "SZHP",
     ["applicant.profile", "loan.account", "arrears.ledger", "payment.history",
      "active.request", "officer.notes", "prior.decisions"],
     ["programme.data"], latency_budget_ms=150)
_reg("uae-verify", "1.0.0", "TDRA-UAEVerify",
     ["verify.document", "verify.batch"],
     ["document.verify"], latency_budget_ms=300)
_reg("financial-capacity", "1.0.0", "ECB-Mock",
     ["salary.verify", "obligations.summary", "credit.risk-band", "bank.statement-trend"],
     ["financial.assessment"], latency_budget_ms=250)
_reg("notifications", "1.0.0", "NIA-Mock",
     ["sms", "email", "push", "callback"],
     ["notification.send"], latency_budget_ms=50)

# ── API helpers ──────────────────────────────────────────────────────────

def list_connectors() -> list[dict]:
    result = []
    for name, info in _CONNECTORS.items():
        state = _get_state(name)
        entry = {**info, "status": state["status"], "failure_mode": state["failure_mode"]}
        result.append(entry)
    return result


def get_connector(name: str) -> dict | None:
    info = _CONNECTORS.get(name)
    if not info:
        return None
    state = _get_state(name)
    return {**info, "status": state["status"], "failure_mode": state["failure_mode"]}


def health(name: str) -> dict:
    info = get_connector(name)
    if not info:
        return {"status": "unknown", "error": f"connector '{name}' not found"}
    return {"name": name, "status": info["status"], "failure_mode": info["failure_mode"],
            "mock": True, "timestamp": datetime.now(timezone.utc).isoformat()}


def simulate(name: str, failure_mode: str | None) -> dict:
    if name not in _CONNECTORS:
        return {"error": f"connector '{name}' not found"}
    if STORE._db:
        STORE._db.execute("UPDATE connector_state SET failure_mode=? WHERE name=?", (failure_mode, name))
        STORE._db.commit()
    _log_call(name, "simulate", "simulated", failure_mode=failure_mode)
    return {"name": name, "failure_mode": failure_mode, "status": "degraded" if failure_mode else "up"}


def reset(name: str) -> dict:
    if name not in _CONNECTORS:
        return {"error": f"connector '{name}' not found"}
    if STORE._db:
        STORE._db.execute("UPDATE connector_state SET failure_mode=NULL, status='up', latency_budget_ms=? WHERE name=?",
                          (_CONNECTORS[name]["latency_budget_ms"], name))
        STORE._db.commit()
    _log_call(name, "reset", "reset")
    return {"name": name, "status": "up", "failure_mode": None}


# ── Mock connector implementations ───────────────────────────────────────

def uaepass_auth_start(purpose_code: str = "identity.verify") -> dict:
    session_id = f"UAEPASS-{uuid.uuid4().hex[:12].upper()}"
    nonce = uuid.uuid4().hex[:16]
    expiry = datetime.now(timezone.utc).isoformat()
    return {
        "session_id": session_id, "nonce": nonce, "auth_url": f"/connectors/uaepass/mock/auth/callback?session={session_id}",
        "expiry": expiry, "purpose_code": purpose_code, "mock": True,
    }


def uaepass_auth_callback(session_id: str, code: str, nonce: str) -> dict:
    """Validate callback (mock replay protection via nonce)."""
    return {
        "session_id": session_id, "auth_code": code, "status": "authenticated",
        "subject_ref": f"SANAD-{uuid.uuid4().hex[:8].upper()}",
        "assurance_level": "SOP2", "auth_time": datetime.now(timezone.utc).isoformat(),
        "mock": True,
    }


def uaepass_userinfo(session_id: str) -> dict:
    return {
        "subject_ref": f"SUB-{session_id[-8:]}", "name_masked": "A***",
        "nationality": "UAE", "mobile_masked": "05XX-XXX-1234",
        "assurance_level": "SOP2", "email_masked": "a***@example.ae",
        "mock": True,
    }


def uaepass_signature_request(case_id: str, signatory_ref: str) -> dict:
    sig_id = f"SIG-{uuid.uuid4().hex[:8].upper()}"
    return {
        "signature_id": sig_id, "case_id": case_id, "signatory_ref": signatory_ref,
        "status": "pending", "mock_signature_url": f"/connectors/uaepass/mock/signature/{sig_id}",
        "created_at": datetime.now(timezone.utc).isoformat(), "mock": True,
    }


def uaepass_signature_verify(signature_id: str, package_hash: str) -> dict:
    return {
        "signature_id": signature_id, "package_hash": package_hash,
        "valid": True, "verified_at": datetime.now(timezone.utc).isoformat(),
        "mock": True,
    }


def uaepass_eseal(issuer: str, document_hash: str) -> dict:
    seal_id = f"SEAL-{uuid.uuid4().hex[:8].upper()}"
    return {
        "seal_id": seal_id, "issuer": issuer, "document_hash": document_hash,
        "valid": True, "seal_time": datetime.now(timezone.utc).isoformat(),
        "mock": True,
    }


def gsb_exchange(provider: str, service: str, payload: dict,
                 consent_id: str | None = None, purpose_code: str | None = None,
                 correlation_id: str | None = None) -> dict:
    _check_consent(consent_id, purpose_code, "gsb")
    state = _get_state("gsb")
    corr = correlation_id or uuid.uuid4().hex[:16]

    if state["failure_mode"] == "timeout":
        time.sleep(0.5)
        _log_call("gsb", f"{provider}.{service}", "timeout", consent_id, purpose_code, corr)
        return {"status": "timeout", "provider": provider, "service": service, "correlation_id": corr, "mock": True}
    if state["failure_mode"] == "provider_down":
        _log_call("gsb", f"{provider}.{service}", "provider_down", consent_id, purpose_code, corr)
        return {"status": "provider_down", "provider": provider, "service": service, "correlation_id": corr, "mock": True}
    if state["failure_mode"] == "stale_data":
        _log_call("gsb", f"{provider}.{service}", "stale_data", consent_id, purpose_code, corr)
        return {"status": "ok", "provider": provider, "service": service, "stale": True, "data": payload, "correlation_id": corr, "mock": True}
    if state["failure_mode"] == "consent_missing":
        return {"status": "consent_denied", "error": "Consent missing or revoked", "mock": True}

    _log_call("gsb", f"{provider}.{service}", "ok", consent_id, purpose_code, corr)
    return {
        "status": "ok", "provider": provider, "service": service,
        "data": payload, "correlation_id": corr, "evidence_ref": f"EVID-{corr}",
        "issued_at": datetime.now(timezone.utc).isoformat(), "mock": True,
    }


def uae_verify_document(document_type: str, doc_hash: str) -> dict:
    state = _get_state("uae-verify")
    _log_call("uae-verify", "verify.document", state["failure_mode"] or "ok")
    if state["failure_mode"] == "tampered":
        return {"document_type": document_type, "hash": doc_hash, "tamper_result": "TAMPERED",
                "signature_valid": False, "confidence": 0.0, "trust_status": "FAIL", "mock": True}
    return {"document_type": document_type, "hash": doc_hash, "tamper_result": "CLEAN",
            "signature_valid": True, "confidence": 0.95, "trust_status": "VERIFIED",
            "issuer": "SZHP-Documents", "mock": True}


def financial_capacity(income: float, obligations: float | None = None) -> dict:
    state = _get_state("financial-capacity")
    _log_call("financial-capacity", "salary.verify", state["failure_mode"] or "ok")
    if state["failure_mode"] == "stale_data":
        return {"verified_income": income, "income_trend": "unknown", "obligations_ratio": obligations,
                "repayment_risk": "HIGH", "signal_freshness": "stale", "mock": True}
    return {
        "verified_income": income, "income_trend": "stable",
        "obligations_ratio": obligations or 0.0,
        "repayment_risk": "LOW" if (obligations or 0) < 0.4 else "MEDIUM",
        "signal_freshness": "fresh", "mock": True,
    }


def send_notification(case_id: str, channel: str, template: str) -> dict:
    _log_call("notifications", f"send.{channel}", "ok")
    return {
        "notification_id": f"NOTIF-{uuid.uuid4().hex[:8].upper()}",
        "case_id": case_id, "channel": channel, "template": template,
        "status": "sent", "sent_at": datetime.now(timezone.utc).isoformat(), "mock": True,
    }

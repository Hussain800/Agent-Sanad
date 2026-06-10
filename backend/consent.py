"""Consent and purpose ledger for v1.4."""
from __future__ import annotations
import uuid
from datetime import datetime, timezone
from backend.store import STORE


def create_consent(beneficiary_ref: str, purpose_code: str,
                   data_categories: list[str], connector_scopes: list[str],
                   expires_at: str | None = None) -> dict:
    consent_id = f"CONSENT-{uuid.uuid4().hex[:8].upper()}"
    now = datetime.now(timezone.utc).isoformat()
    if STORE._db:
        STORE._db.execute(
            "INSERT INTO consents (id, beneficiary_ref, purpose_code, data_categories, connector_scopes, granted_at, expires_at, created_at) VALUES (?,?,?,?,?,?,?,?)",
            (consent_id, beneficiary_ref, purpose_code, ",".join(data_categories),
             ",".join(connector_scopes), now, expires_at or "", now))
        STORE._db.commit()
    return {
        "id": consent_id, "beneficiary_ref": beneficiary_ref,
        "purpose_code": purpose_code, "data_categories": data_categories,
        "connector_scopes": connector_scopes, "granted_at": now,
        "expires_at": expires_at, "revoked_at": None,
    }


def get_consent(consent_id: str) -> dict | None:
    if STORE._db is None:
        return None
    row = STORE._db.execute(
        "SELECT id, beneficiary_ref, purpose_code, data_categories, connector_scopes, granted_at, expires_at, revoked_at FROM consents WHERE id=?",
        (consent_id,)).fetchone()
    if not row:
        return None
    return {
        "id": row[0], "beneficiary_ref": row[1], "purpose_code": row[2],
        "data_categories": row[3].split(",") if row[3] else [],
        "connector_scopes": row[4].split(",") if row[4] else [],
        "granted_at": row[5], "expires_at": row[6] or None, "revoked_at": row[7] or None,
    }


def revoke_consent(consent_id: str) -> dict | None:
    consent = get_consent(consent_id)
    if not consent:
        return None
    now = datetime.now(timezone.utc).isoformat()
    if STORE._db:
        STORE._db.execute("UPDATE consents SET revoked_at=? WHERE id=?", (now, consent_id))
        STORE._db.commit()
    consent["revoked_at"] = now
    return consent


def check_consent(consent_id: str) -> bool:
    """Check consent exists and is not revoked."""
    consent = get_consent(consent_id)
    if not consent:
        return False
    if consent.get("revoked_at"):
        return False
    return True


def case_consent_events(case_id: str) -> list[dict]:
    """Return consent events related to a case."""
    events = []
    if STORE._db is None:
        return events
    rows = STORE._db.execute(
        "SELECT id, beneficiary_ref, purpose_code, granted_at, revoked_at FROM consents WHERE beneficiary_ref LIKE ? ORDER BY created_at DESC",
        (f"%{case_id}%",)).fetchall()
    for row in rows:
        events.append({
            "consent_id": row[0], "beneficiary_ref": row[1],
            "purpose_code": row[2], "granted_at": row[3], "revoked_at": row[4] or None,
        })
    if not events:
        # Fallback: show all consents (demo mode)
        rows = STORE._db.execute(
            "SELECT id, beneficiary_ref, purpose_code, granted_at, revoked_at FROM consents ORDER BY created_at DESC LIMIT 5"
        ).fetchall()
        for row in rows:
            events.append({
                "consent_id": row[0], "beneficiary_ref": row[1],
                "purpose_code": row[2], "granted_at": row[3], "revoked_at": row[4] or None,
            })
    return events

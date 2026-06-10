"""UAE PASS session v3 — stored nonce, expiry, consumed callback, replay rejection."""
from __future__ import annotations
import hashlib
import uuid
from datetime import datetime, timezone, timedelta
from typing import Any

from backend.store import STORE


SESSION_TTL_SECONDS = 300  # 5 minutes


def start_session(purpose_code: str = "identity.verify", beneficiary_ref: str = "") -> dict:
    """Start a new UAE PASS mock session with stored nonce and expiry."""
    session_id = f"UAEPASS-{uuid.uuid4().hex[:12].upper()}"
    nonce = uuid.uuid4().hex[:16]
    expires_at = datetime.now(timezone.utc) + timedelta(seconds=SESSION_TTL_SECONDS)
    now = datetime.now(timezone.utc).isoformat()

    if STORE._db:
        STORE._db.execute(
            "INSERT INTO sessions (id, beneficiary_ref, state, created_at, auth_time, consent_id, assurance_level, nonce, expiry) VALUES (?,?,?,?,?,?,?,?,?)",
            (session_id, beneficiary_ref, "started", now, None, None, "low", nonce, expires_at.isoformat()),
        )
        STORE._db.commit()

    return {
        "session_id": session_id,
        "nonce": nonce,
        "auth_url": f"/connectors/uaepass/mock/auth/callback?session={session_id}",
        "expires_at": expires_at.isoformat(),
        "purpose_code": purpose_code,
        "mock": True,
    }


def consume_callback(session_id: str, code: str, nonce: str) -> dict:
    """
    Validate callback: wrong nonce, expired session, replay (already consumed), reused code all fail.
    """
    if not session_id or not code or not nonce:
        return {"status": "error", "error": "Missing session_id, code, or nonce", "mock": True}

    if STORE._db is None:
        # Demo fallback
        return {
            "session_id": session_id,
            "auth_code": code,
            "status": "authenticated",
            "subject_ref": f"SANAD-{uuid.uuid4().hex[:8].upper()}",
            "assurance_level": "SOP2",
            "auth_time": datetime.now(timezone.utc).isoformat(),
            "mock": True,
        }

    row = STORE._db.execute(
        "SELECT id, beneficiary_ref, state, nonce, expiry, auth_time, assurance_level FROM sessions WHERE id=?",
        (session_id,),
    ).fetchone()

    if not row:
        return {"status": "error", "error": "Session not found", "mock": True}

    _, beneficiary_ref, state, stored_nonce, expiry_str, auth_time, assurance_level = row

    # Wrong nonce
    if stored_nonce != nonce:
        _update_session_state(session_id, "wrong_nonce")
        return {"status": "error", "error": "Wrong nonce — possible replay attack", "mock": True}

    # Expired session
    if expiry_str:
        try:
            expiry = datetime.fromisoformat(expiry_str.replace("Z", "+00:00"))
            if expiry < datetime.now(timezone.utc):
                _update_session_state(session_id, "expired")
                return {"status": "error", "error": "Session expired", "mock": True}
        except Exception:
            pass

    # Already consumed
    if state == "consumed":
        return {"status": "error", "error": "Session already consumed — replay rejected", "mock": True}

    # Reused code check — only within THIS session
    if state != "started" and auth_time:
        _update_session_state(session_id, "reused_code")
        return {"status": "error", "error": "Auth code already used in this session", "mock": True}

    # Check across ALL sessions for code reuse
    code_hash = hashlib.sha256(code.encode()).hexdigest()[:16]
    existing = STORE._db.execute(
        "SELECT 1 FROM sessions WHERE id!=? AND state='consumed' AND nonce=? LIMIT 1",
        (session_id, code_hash),
    ).fetchone()
    if existing:
        _update_session_state(session_id, "reused_code")
        return {"status": "error", "error": "Auth code already used in another session", "mock": True}

    # Success
    now = datetime.now(timezone.utc).isoformat()
    subject_ref = f"SANAD-{uuid.uuid4().hex[:8].upper()}"
    STORE._db.execute(
        "UPDATE sessions SET state='consumed', auth_time=?, assurance_level='SOP2', nonce=? WHERE id=?",
        (now, code_hash, session_id),
    )
    STORE._db.commit()

    return {
        "session_id": session_id,
        "auth_code": code,
        "status": "authenticated",
        "subject_ref": subject_ref,
        "assurance_level": "SOP2",
        "auth_time": now,
        "mock": True,
    }


def get_session(session_id: str) -> dict | None:
    """Return session state."""
    if STORE._db is None:
        return None
    row = STORE._db.execute(
        "SELECT id, beneficiary_ref, state, created_at, auth_time, consent_id, assurance_level, nonce, expiry FROM sessions WHERE id=?",
        (session_id,),
    ).fetchone()
    if not row:
        return None
    return {
        "session_id": row[0], "beneficiary_ref": row[1], "state": row[2],
        "created_at": row[3], "auth_time": row[4], "consent_id": row[5],
        "assurance_level": row[6], "nonce": row[7], "expires_at": row[8],
    }


def expire_session_mock(session_id: str) -> dict:
    """Force-expire a session (for testing)."""
    if STORE._db:
        past = (datetime.now(timezone.utc) - timedelta(seconds=1)).isoformat()
        STORE._db.execute("UPDATE sessions SET expiry=? WHERE id=?", (past, session_id))
        STORE._db.commit()
    return {"session_id": session_id, "expired": True}


def revoke_session_mock(session_id: str) -> dict:
    """Revoke a session (for testing)."""
    if STORE._db:
        STORE._db.execute("UPDATE sessions SET state='revoked' WHERE id=?", (session_id,))
        STORE._db.commit()
    return {"session_id": session_id, "revoked": True}


def _update_session_state(session_id: str, state: str) -> None:
    if STORE._db:
        STORE._db.execute("UPDATE sessions SET state=? WHERE id=?", (state, session_id))
        STORE._db.commit()

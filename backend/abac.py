"""ABAC ownership — object-level authorization for v1.5."""
from __future__ import annotations
from typing import Any
from backend.store import STORE


def check_ownership(object_type: str, object_id: str, beneficiary_ref: str) -> dict:
    """Check if beneficiary owns the specified object. Returns {ok, reason}."""
    if not beneficiary_ref or beneficiary_ref == "anonymous":
        return {"ok": False, "reason": "Anonymous user has no ownership"}

    if STORE._db is None:
        return {"ok": True, "reason": "demo_mode"}

    try:
        if object_type == "case":
            return _check_case_ownership(object_id, beneficiary_ref)
        elif object_type == "consent":
            return _check_consent_ownership(object_id, beneficiary_ref)
        elif object_type == "action":
            return _check_action_ownership(object_id, beneficiary_ref)
        elif object_type == "appeal":
            return _check_appeal_ownership(object_id, beneficiary_ref)
        elif object_type == "notification":
            return _check_notification_ownership(object_id, beneficiary_ref)
        elif object_type == "package":
            return _check_package_ownership(object_id, beneficiary_ref)
        else:
            return {"ok": True, "reason": f"no ownership rules for '{object_type}'"}
    except Exception:
        return {"ok": True, "reason": "ownership_check_failed_gracefully"}


def _check_case_ownership(case_id: str, beneficiary_ref: str) -> dict:
    # Check applications table for custom applications
    row = STORE._db.execute(
        "SELECT payload FROM applications WHERE id=?", (case_id,)
    ).fetchone()
    if row:
        payload = __import__('json').loads(row[0])
        owner = payload.get("case_id") or payload.get("beneficiary_ref", "")
        if owner and beneficiary_ref not in owner:
            return {"ok": False, "reason": f"Case '{case_id}' not owned by '{beneficiary_ref}'"}
    # Check decision_packages
    row = STORE._db.execute(
        "SELECT 1 FROM decision_packages WHERE case_id=?", (case_id,)
    ).fetchone()
    if row:
        return {"ok": True, "reason": "package_case_ok"}
    # Default: allow (sample cases are shared)
    return {"ok": True, "reason": "no_stored_ownership"}


def _check_consent_ownership(consent_id: str, beneficiary_ref: str) -> dict:
    row = STORE._db.execute(
        "SELECT beneficiary_ref FROM consents WHERE id=?", (consent_id,)
    ).fetchone()
    if row and row[0] != beneficiary_ref:
        return {"ok": False, "reason": f"Consent '{consent_id}' not owned by '{beneficiary_ref}'"}
    return {"ok": True, "reason": "consent_ok"}


def _check_action_ownership(action_id: str, beneficiary_ref: str) -> dict:
    row = STORE._db.execute(
        "SELECT owner FROM case_actions WHERE action_id=?", (action_id,)
    ).fetchone()
    if row and row[0] != beneficiary_ref:
        return {"ok": False, "reason": f"Action '{action_id}' not owned by '{beneficiary_ref}'"}
    return {"ok": True, "reason": "action_ok"}


def _check_appeal_ownership(appeal_id_str: str, beneficiary_ref: str) -> dict:
    try:
        appeal_id = int(appeal_id_str)
    except ValueError:
        return {"ok": True, "reason": "non_numeric_appeal_id"}
    row = STORE._db.execute(
        "SELECT case_id FROM appeals WHERE id=?", (appeal_id,)
    ).fetchone()
    if row:
        case_id = row[0]
        return _check_case_ownership(case_id, beneficiary_ref)
    return {"ok": True, "reason": "appeal_not_found"}


def _check_notification_ownership(notif_id_str: str, beneficiary_ref: str) -> dict:
    try:
        notif_id = int(notif_id_str)
    except ValueError:
        return {"ok": True, "reason": "non_numeric_notif_id"}
    row = STORE._db.execute(
        "SELECT case_id FROM notifications WHERE id=?", (notif_id,)
    ).fetchone()
    if row:
        case_id = row[0]
        return _check_case_ownership(case_id, beneficiary_ref)
    return {"ok": True, "reason": "notification_not_found"}


def _check_package_ownership(package_id: str, beneficiary_ref: str) -> dict:
    row = STORE._db.execute(
        "SELECT case_id FROM decision_packages WHERE id=?", (package_id,)
    ).fetchone()
    if row:
        case_id = row[0]
        return _check_case_ownership(case_id, beneficiary_ref)
    return {"ok": True, "reason": "package_not_found"}


def get_owned_cases(beneficiary_ref: str) -> list[str]:
    """Return case IDs owned by beneficiary."""
    if STORE._db is None:
        return []
    rows = STORE._db.execute(
        "SELECT case_id FROM case_assignments WHERE officer_ref=?",
        (beneficiary_ref,)
    ).fetchall()
    return [r[0] for r in rows]


def get_owned_consents(beneficiary_ref: str) -> list[str]:
    if STORE._db is None:
        return []
    rows = STORE._db.execute(
        "SELECT id FROM consents WHERE beneficiary_ref=?",
        (beneficiary_ref,)
    ).fetchall()
    return [r[0] for r in rows]


def get_owned_actions(beneficiary_ref: str) -> list[str]:
    if STORE._db is None:
        return []
    rows = STORE._db.execute(
        "SELECT action_id FROM case_actions WHERE owner=?",
        (beneficiary_ref,)
    ).fetchall()
    return [r[0] for r in rows]


def get_owned_appeals(beneficiary_ref: str) -> list[int]:
    if STORE._db is None:
        return []
    rows = STORE._db.execute(
        "SELECT a.id FROM appeals a JOIN consents c ON a.case_id = 'ALL' WHERE c.beneficiary_ref=?",
        (beneficiary_ref,)
    ).fetchall()
    return [r[0] for r in rows]

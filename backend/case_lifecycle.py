"""v1.6 case lifecycle — canonical states and transition validation."""
from __future__ import annotations
import time
from backend.store import STORE
from backend.audit_chain import add_chain_event

LIFECYCLE_STATES = [
    "submitted", "identity_verified", "consent_granted", "data_retrieved",
    "evidence_needed", "evidence_submitted", "policy_ready", "recommendation_ready",
    "officer_review", "beneficiary_repair", "appeal_draft", "appeal_submitted",
    "appeal_review", "supervisor_review", "approved", "adjusted", "rejected",
    "referred", "signed", "sealed", "closed",
]

ALLOWED_TRANSITIONS: dict[str, set[str]] = {
    "submitted": {"identity_verified", "consent_granted"},
    "identity_verified": {"consent_granted", "closed"},
    "consent_granted": {"data_retrieved", "closed"},
    "data_retrieved": {"evidence_needed", "evidence_submitted", "policy_ready", "closed"},
    "evidence_needed": {"evidence_submitted", "beneficiary_repair", "closed"},
    "evidence_submitted": {"policy_ready", "officer_review", "closed"},
    "policy_ready": {"recommendation_ready", "closed"},
    "recommendation_ready": {"officer_review", "approved", "adjusted", "rejected", "referred", "signed", "closed"},
    "officer_review": {"approved", "adjusted", "rejected", "referred", "beneficiary_repair", "closed"},
    "beneficiary_repair": {"evidence_submitted", "appeal_draft", "closed"},
    "appeal_draft": {"appeal_submitted", "closed"},
    "appeal_submitted": {"appeal_review", "closed"},
    "appeal_review": {"supervisor_review", "approved", "rejected", "closed"},
    "supervisor_review": {"approved", "adjusted", "rejected", "closed"},
    "approved": {"signed", "sealed", "closed"},
    "adjusted": {"signed", "sealed", "closed"},
    "rejected": {"appeal_draft", "closed"},
    "referred": {"officer_review", "closed"},
    "signed": {"sealed", "closed"},
    "sealed": {"closed"},
    "closed": set(),
}


def get_lifecycle(case_id: str) -> dict:
    cid = case_id.upper()
    if STORE._db is None:
        return {"case_id": cid, "current_state": "unknown", "history": []}
    row = STORE._db.execute(
        "SELECT current_state FROM case_lifecycle WHERE case_id=? ORDER BY id DESC LIMIT 1",
        (cid,)).fetchone()
    current = row[0] if row else None
    rows = STORE._db.execute(
        "SELECT previous_state, current_state, transitioned_at, actor, detail FROM case_lifecycle WHERE case_id=? ORDER BY id",
        (cid,)).fetchall()
    history = [
        {"from": r[0] or "start", "to": r[1], "at": r[2], "actor": r[3], "detail": r[4]}
        for r in rows
    ]
    return {"case_id": cid, "current_state": current, "history": history}


def transition(case_id: str, target_state: str, actor: str = "system", detail: str = "") -> dict:
    cid = case_id.upper()
    if target_state not in LIFECYCLE_STATES:
        return {"ok": False, "reason": f"Invalid state: {target_state}", "case_id": cid,
                "previous_state": None, "current_state": None, "transition": target_state}

    lifecycle = get_lifecycle(cid)
    current = lifecycle["current_state"] or "submitted"

    allowed = ALLOWED_TRANSITIONS.get(current, set())
    if target_state not in allowed:
        return {"ok": False, "reason": f"Transition '{current} -> {target_state}' not allowed",
                "case_id": cid, "previous_state": current, "current_state": current, "transition": target_state}

    ts = time.strftime("%Y-%m-%dT%H:%M:%S")
    if STORE._db:
        STORE._db.execute(
            "INSERT INTO case_lifecycle (case_id, previous_state, current_state, transitioned_at, actor, detail) VALUES (?,?,?,?,?,?)",
            (cid, current, target_state, ts, actor, detail))
        STORE._db.commit()

    add_chain_event(cid, actor, f"lifecycle.{target_state}",
                    {"from": current, "to": target_state, "detail": detail})

    return {"ok": True, "case_id": cid, "previous_state": current, "current_state": target_state,
            "transition": f"{current} -> {target_state}"}


def get_timeline(case_id: str) -> dict:
    cid = case_id.upper()
    _ = get_lifecycle(cid)
    if STORE._db is None:
        return {"case_id": cid, "events": []}
    rows = STORE._db.execute(
        "SELECT timestamp, actor, action, payload_digest FROM audit_chain WHERE case_id=? ORDER BY id",
        (cid,)).fetchall()
    lifecycle_rows = STORE._db.execute(
        "SELECT previous_state, current_state, transitioned_at, actor, detail FROM case_lifecycle WHERE case_id=? ORDER BY id",
        (cid,)).fetchall()
    events = []
    for r in rows:
        events.append({"type": "audit", "at": r[0], "actor": r[1], "action": r[2]})
    for r in lifecycle_rows:
        events.append({"type": "lifecycle", "at": r[2], "actor": r[3], "from": r[0] or "start", "to": r[1], "detail": r[4]})
    events.sort(key=lambda e: e["at"])
    return {"case_id": cid, "events": events}

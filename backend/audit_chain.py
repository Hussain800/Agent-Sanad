"""Immutable audit hash chain for v1.4."""
from __future__ import annotations
import hashlib
import json
from datetime import datetime, timezone
from backend.store import STORE


def _hash_entry(previous_hash: str, timestamp: str, actor: str, action: str,
                payload_digest: str, policy_version: str, app_version: str) -> str:
    raw = f"{previous_hash}|{timestamp}|{actor}|{action}|{payload_digest}|{policy_version}|{app_version}"
    return hashlib.sha256(raw.encode()).hexdigest()


def add_chain_event(case_id: str, actor: str, action: str, payload: dict | None = None,
                    policy_version: str = "", app_version: str = "1.4.0") -> dict:
    now = datetime.now(timezone.utc).isoformat()
    payload_digest = hashlib.sha256(json.dumps(payload or {}, sort_keys=True).encode()).hexdigest()[:16]
    previous_hash = ""
    if STORE._db:
        last = STORE._db.execute(
            "SELECT event_hash FROM audit_chain WHERE case_id=? ORDER BY id DESC LIMIT 1",
            (case_id,)).fetchone()
        if last:
            previous_hash = last[0]
    event_hash = _hash_entry(previous_hash, now, actor, action, payload_digest, policy_version, app_version)
    if STORE._db:
        STORE._db.execute(
            "INSERT INTO audit_chain (case_id, previous_hash, event_hash, timestamp, actor, action, payload_digest, policy_version, app_version) VALUES (?,?,?,?,?,?,?,?,?)",
            (case_id, previous_hash, event_hash, now, actor, action, payload_digest, policy_version, app_version))
        STORE._db.commit()
    return {
        "case_id": case_id, "previous_hash": previous_hash, "event_hash": event_hash,
        "timestamp": now, "actor": actor, "action": action,
        "payload_digest": payload_digest, "policy_version": policy_version,
        "app_version": app_version,
    }


def get_chain(case_id: str) -> list[dict]:
    if STORE._db is None:
        return []
    rows = STORE._db.execute(
        "SELECT id, case_id, previous_hash, event_hash, timestamp, actor, action, payload_digest, policy_version, app_version FROM audit_chain WHERE case_id=? ORDER BY id",
        (case_id,)).fetchall()
    return [{
        "id": r[0], "case_id": r[1], "previous_hash": r[2], "event_hash": r[3],
        "timestamp": r[4], "actor": r[5], "action": r[6],
        "payload_digest": r[7], "policy_version": r[8], "app_version": r[9],
    } for r in rows]


def verify_chain(case_id: str) -> dict:
    """Verify the hash chain for a case. Returns ok + first broken link if any."""
    entries = get_chain(case_id)
    if not entries:
        return {"ok": True, "message": "No audit entries to verify", "case_id": case_id}
    for i, entry in enumerate(entries):
        expected_prev = entries[i - 1]["event_hash"] if i > 0 else ""
        if entry["previous_hash"] != expected_prev:
            return {
                "ok": False, "case_id": case_id,
                "broken_link": i + 1,
                "message": f"Entry {i+1}: expected prev_hash {expected_prev[:16]}..., got {entry['previous_hash'][:16]}...",
            }
        expected_hash = _hash_entry(
            entry["previous_hash"], entry["timestamp"], entry["actor"],
            entry["action"], entry["payload_digest"],
            entry["policy_version"], entry["app_version"],
        )
        if entry["event_hash"] != expected_hash:
            return {
                "ok": False, "case_id": case_id,
                "broken_link": i + 1,
                "message": f"Entry {i+1}: hash mismatch",
            }
    return {"ok": True, "case_id": case_id, "entries": len(entries), "message": "Chain intact"}

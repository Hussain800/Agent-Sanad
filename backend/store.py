"""Lightweight SQLite persistence layer (product gaps P1 — G2).

Stores custom applications, recommendations, audit events, and officer
actions so the demo survives page refreshes and feels like a real system.

Built on Python's built-in sqlite3 — zero external dependencies. The store
is optional: if the DB file cannot be created (read-only filesystem, etc.),
all write operations gracefully no-op and the app continues working.
"""
from __future__ import annotations

import json
import logging
import os
import sqlite3
import threading
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

_log = logging.getLogger("sanad.store")


# ── schema ───────────────────────────────────────────────────────────────────

_SCHEMA = """
CREATE TABLE IF NOT EXISTS applications (
    id              TEXT PRIMARY KEY,
    created_at      TEXT NOT NULL,
    payload         TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS recommendations (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    application_id  TEXT NOT NULL REFERENCES applications(id),
    report          TEXT NOT NULL,
    created_at      TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS audit_events (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    application_id  TEXT NOT NULL REFERENCES applications(id),
    event           TEXT NOT NULL,
    created_at      TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS officer_actions (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    case_id         TEXT NOT NULL,
    action          TEXT NOT NULL,
    override_reason_code TEXT,
    notes           TEXT DEFAULT '',
    created_at      TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_recommendations_app
    ON recommendations(application_id);
CREATE INDEX IF NOT EXISTS idx_audit_events_app
    ON audit_events(application_id);
CREATE INDEX IF NOT EXISTS idx_officer_actions_case
    ON officer_actions(case_id);

-- v1.4 tables
CREATE TABLE IF NOT EXISTS sessions (
    id              TEXT PRIMARY KEY,
    beneficiary_ref TEXT NOT NULL,
    state           TEXT NOT NULL DEFAULT 'started',
    created_at      TEXT NOT NULL,
    auth_time       TEXT,
    consent_id      TEXT,
    assurance_level TEXT DEFAULT 'low',
    nonce           TEXT,
    expiry          TEXT
);

CREATE TABLE IF NOT EXISTS consents (
    id              TEXT PRIMARY KEY,
    beneficiary_ref TEXT NOT NULL,
    purpose_code    TEXT NOT NULL,
    data_categories TEXT NOT NULL,
    connector_scopes TEXT NOT NULL,
    granted_at      TEXT NOT NULL,
    expires_at      TEXT,
    revoked_at      TEXT,
    created_at      TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS connector_calls (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    connector_name  TEXT NOT NULL,
    service         TEXT NOT NULL,
    consent_id      TEXT,
    purpose_code    TEXT,
    correlation_id  TEXT,
    status          TEXT NOT NULL DEFAULT 'pending',
    request_summary TEXT,
    response_summary TEXT,
    latency_ms      INTEGER DEFAULT 0,
    failure_mode    TEXT,
    created_at      TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS connector_state (
    name            TEXT PRIMARY KEY,
    status          TEXT NOT NULL DEFAULT 'up',
    failure_mode    TEXT,
    latency_budget_ms INTEGER DEFAULT 100,
    last_call_at    TEXT
);

CREATE TABLE IF NOT EXISTS case_actions (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    case_id         TEXT NOT NULL,
    action_id       TEXT NOT NULL,
    status          TEXT NOT NULL DEFAULT 'open',
    action_type     TEXT NOT NULL,
    label           TEXT NOT NULL,
    description     TEXT,
    repair_hint     TEXT,
    owner           TEXT DEFAULT 'beneficiary',
    due_date        TEXT,
    officer_note    TEXT,
    created_at      TEXT NOT NULL,
    updated_at      TEXT
);

CREATE TABLE IF NOT EXISTS document_checks (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    case_id         TEXT NOT NULL,
    document_type   TEXT NOT NULL,
    issuer          TEXT,
    hash            TEXT,
    tamper_result   TEXT,
    signature_valid INTEGER DEFAULT 0,
    confidence      REAL DEFAULT 0.0,
    trust_status    TEXT DEFAULT 'pending',
    checked_at      TEXT
);

CREATE TABLE IF NOT EXISTS decision_packages (
    id              TEXT PRIMARY KEY,
    case_id         TEXT NOT NULL,
    decision_summary TEXT NOT NULL,
    letter_arabic   TEXT,
    letter_english  TEXT,
    package_hash    TEXT,
    created_at      TEXT NOT NULL,
    signed_at       TEXT
);

CREATE TABLE IF NOT EXISTS signatures (
    id              TEXT PRIMARY KEY,
    case_id         TEXT NOT NULL,
    package_id      TEXT,
    signatory_ref   TEXT,
    signature_value TEXT,
    signature_type  TEXT DEFAULT 'mock',
    status          TEXT DEFAULT 'pending',
    created_at      TEXT NOT NULL,
    verified_at     TEXT
);

CREATE TABLE IF NOT EXISTS audit_chain (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    case_id         TEXT NOT NULL,
    previous_hash   TEXT NOT NULL DEFAULT '',
    event_hash      TEXT NOT NULL,
    timestamp       TEXT NOT NULL,
    actor           TEXT NOT NULL,
    action          TEXT NOT NULL,
    payload_digest  TEXT DEFAULT '',
    policy_version  TEXT,
    app_version     TEXT
);

CREATE TABLE IF NOT EXISTS appeals (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    case_id         TEXT NOT NULL,
    reason          TEXT NOT NULL,
    new_evidence    TEXT,
    status          TEXT DEFAULT 'open',
    created_at      TEXT NOT NULL,
    decided_at      TEXT,
    decision        TEXT,
    decision_by     TEXT
);

CREATE TABLE IF NOT EXISTS notifications (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    case_id         TEXT NOT NULL,
    channel         TEXT NOT NULL,
    template        TEXT NOT NULL,
    status          TEXT NOT NULL DEFAULT 'pending',
    sent_at         TEXT,
    read_at         TEXT,
    created_at      TEXT NOT NULL
);
"""


# ── store class ──────────────────────────────────────────────────────────────

class SQLiteStore:
    """Thread-safe SQLite store for demo persistence."""

    def __init__(self, db_path: str | Path) -> None:
        self._path = Path(db_path)
        self._lock = threading.Lock()
        self._db: sqlite3.Connection | None = None
        self._init()

    def _init(self) -> None:
        try:
            self._path.parent.mkdir(parents=True, exist_ok=True)
            self._db = sqlite3.connect(str(self._path), timeout=5, check_same_thread=False)
            self._db.execute("PRAGMA journal_mode=WAL")
            self._db.execute("PRAGMA synchronous=NORMAL")
            self._db.executescript(_SCHEMA)
            self._db.commit()
        except Exception as exc:
            _log.warning("store init failed: %s", exc)
            self._db = None

    def _now(self) -> str:
        return datetime.now(timezone.utc).isoformat()

    # ── applications ──────────────────────────────────────────────────────

    def save_application(self, app_id: str, payload: dict) -> None:
        if self._db is None:
            return
        try:
            with self._lock:
                self._db.execute(
                    "INSERT OR IGNORE INTO applications (id, created_at, payload) VALUES (?, ?, ?)",
                    (app_id, self._now(), json.dumps(payload)),
                )
                self._db.commit()
        except Exception:
            pass

    def save_recommendation(self, app_id: str, report: dict) -> None:
        if self._db is None:
            return
        try:
            with self._lock:
                self._db.execute(
                    "INSERT INTO recommendations (application_id, report, created_at) VALUES (?, ?, ?)",
                    (app_id, json.dumps(report), self._now()),
                )
                self._db.commit()
        except Exception:
            pass

    def save_audit_events(self, app_id: str, events: list[dict]) -> None:
        if self._db is None:
            return
        try:
            with self._lock:
                self._db.executemany(
                    "INSERT INTO audit_events (application_id, event, created_at) VALUES (?, ?, ?)",
                    [(app_id, json.dumps(e), self._now()) for e in events],
                )
                self._db.commit()
        except Exception:
            pass

    def list_applications(self) -> list[dict]:
        """Return a summary list sorted newest-first."""
        if self._db is None:
            return []
        try:
            with self._lock:
                rows = self._db.execute(
                    "SELECT id, created_at FROM applications ORDER BY created_at DESC"
                ).fetchall()
                return [{"id": r[0], "created_at": r[1]} for r in rows]
        except Exception:
            return []

    def get_application(self, app_id: str) -> dict | None:
        """Return full application detail with recommendation and audit."""
        if self._db is None:
            return None
        try:
            with self._lock:
                app_row = self._db.execute(
                    "SELECT id, created_at, payload FROM applications WHERE id = ?",
                    (app_id,),
                ).fetchone()
                if app_row is None:
                    return None
                rec_rows = self._db.execute(
                    "SELECT report, created_at FROM recommendations WHERE application_id = ? ORDER BY created_at DESC LIMIT 1",
                    (app_id,),
                ).fetchone()
                audit_rows = self._db.execute(
                    "SELECT event FROM audit_events WHERE application_id = ? ORDER BY id",
                    (app_id,),
                ).fetchall()
                return {
                    "application_id": app_row[0],
                    "created_at": app_row[1],
                    "payload": json.loads(app_row[2]),
                    "report": json.loads(rec_rows[0]) if rec_rows else None,
                    "audit": [json.loads(r[0]) for r in audit_rows],
                }
        except Exception:
            return None

    # ── officer actions ───────────────────────────────────────────────────

    def save_officer_action(self, case_id: str, action: str,
                            override_reason_code: str | None = None,
                            notes: str = "") -> None:
        if self._db is None:
            return
        try:
            with self._lock:
                self._db.execute(
                    "INSERT INTO officer_actions (case_id, action, override_reason_code, notes, created_at) VALUES (?, ?, ?, ?, ?)",
                    (case_id, action, override_reason_code, notes, self._now()),
                )
                self._db.commit()
        except Exception:
            pass

    def list_officer_actions(self) -> list[dict]:
        if self._db is None:
            return []
        try:
            with self._lock:
                rows = self._db.execute(
                    "SELECT case_id, action, override_reason_code, notes, created_at FROM officer_actions ORDER BY created_at DESC"
                ).fetchall()
                return [
                    {"case_id": r[0], "action": r[1],
                     "override_reason_code": r[2], "notes": r[3],
                     "created_at": r[4]}
                    for r in rows
                ]
        except Exception:
            return []


# ── global singleton (initialised at import time) ──────────────────────────

def _default_db_path() -> str:
    return str(
        Path(__file__).resolve().parent.parent / "data" / "agent_sanad.db"
    )


STORE: SQLiteStore = SQLiteStore(
    os.getenv("SANAD_DB_PATH", "") or _default_db_path()
)

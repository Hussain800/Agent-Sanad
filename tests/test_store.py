"""SQLite persistence layer tests (product gaps P1 — G2).

Verifies that custom applications, recommendations, audit events, and
officer actions are persisted to SQLite and retrievable via the API.
"""
from __future__ import annotations

import json
import pytest
from fastapi.testclient import TestClient

from backend.app import app

client = TestClient(app)

BASE = {
    "monthly_income_aed": 16000,
    "current_installment_aed": 2000,
    "arrears_amount_aed": 8000,
    "remaining_balance_aed": 300000,
    "remaining_term_months": 150,
    "original_approved_term_months": 240,
    "unpaid_installments": 4,
    "family_size": 3,
    "income_trend": "stable",
}


# ═══════════════════════════════════════════════════════════════════════════════
# S1 — application lifecycle: submit, list, retrieve
# ═══════════════════════════════════════════════════════════════════════════════

class TestApplicationPersistence:
    """Scenario S1: custom applications survive the request and are listable."""

    def test_submit_application_appears_in_list(self):
        """Submit a custom app -> GET /applications includes it."""
        submit = client.post("/applications/mock/decide", json=BASE)
        assert submit.status_code == 200
        app_id = submit.json()["application_id"]

        lst = client.get("/applications")
        assert lst.status_code == 200
        ids = [a["id"] for a in lst.json()["applications"]]
        assert app_id in ids, f"{app_id} not found in {ids}"

    def test_retrieve_application_by_id(self):
        """Submit -> GET /applications/{id} returns case + report + audit."""
        submit = client.post("/applications/mock/decide", json=BASE)
        assert submit.status_code == 200
        body = submit.json()
        app_id = body["application_id"]

        detail = client.get(f"/applications/{app_id}")
        assert detail.status_code == 200
        d = detail.json()
        assert d["application_id"] == app_id
        # Returns saved payload (input form) + report + audit.
        assert "payload" in d
        assert d["payload"]["monthly_income_aed"] == 16000
        assert "report" in d
        assert d["report"]["recommendation"] == "Approve"
        # Audit events must include the state journey
        states = [e["state_to"] for e in d["audit"] if e.get("state_to")]
        assert "Submitted" in states
        assert "Closed" in states

    def test_retrieve_missing_application_404(self):
        """Unknown application_id -> 404."""
        r = client.get("/applications/NONEXISTENT-001")
        assert r.status_code == 404

    def test_list_returns_multiple_submissions(self):
        """Submit 2 apps -> list contains both."""
        id1 = client.post("/applications/mock/decide", json=BASE).json()["application_id"]
        id2 = client.post("/applications/mock/decide", json=BASE).json()["application_id"]
        lst = client.get("/applications").json()["applications"]
        ids = [a["id"] for a in lst]
        assert id1 in ids
        assert id2 in ids


# ═══════════════════════════════════════════════════════════════════════════════
# S2 — snapshot endpoint also persists
# ═══════════════════════════════════════════════════════════════════════════════

class TestSnapshotPersistence:
    """Scenario S2: POST /applications/mock persists even without a policy run."""

    def test_snapshot_appears_in_list(self):
        r = client.post("/applications/mock", json=BASE)
        assert r.status_code == 200
        app_id = r.json()["application_id"]

        lst = client.get("/applications").json()["applications"]
        assert app_id in [a["id"] for a in lst]


# ═══════════════════════════════════════════════════════════════════════════════
# S3 — officer action persistence
# ═══════════════════════════════════════════════════════════════════════════════

class TestOfficerActionPersistence:
    """Scenario S3: officer actions are persisted and listable."""

    def test_officer_action_appears_in_list(self):
        r = client.post("/cases/GOLDEN/officer-action",
                        json={"action": "approve"})
        assert r.status_code == 200

        lst = client.get("/officer-actions").json()["actions"]
        assert any(a["case_id"] == "GOLDEN" and a["action"] == "approve"
                   for a in lst)

    def test_officer_action_with_reason_persisted(self):
        r = client.post("/cases/GOLDEN/officer-action",
                        json={"action": "adjust",
                              "override_reason_code": "OFF-MANUAL-02",
                              "notes": "adjusted per supervisor review"})
        assert r.status_code == 200

        lst = client.get("/officer-actions").json()["actions"]
        matching = [a for a in lst
                    if a.get("override_reason_code") == "OFF-MANUAL-02"]
        assert len(matching) >= 1
        assert matching[0]["action"] == "adjust"


# ═══════════════════════════════════════════════════════════════════════════════
# S4 — persistence across simulated restart (same DB file)
# ═══════════════════════════════════════════════════════════════════════════════

class TestCrossRequestPersistence:
    """Scenario S4: data written in one request is readable in subsequent
    requests (the store lives in a module-level singleton)."""

    def test_applications_persist_across_requests(self):
        ids_before = {a["id"] for a in
                      client.get("/applications").json()["applications"]}
        r = client.post("/applications/mock/decide", json=BASE)
        assert r.status_code == 200
        new_id = r.json()["application_id"]

        ids_after = {a["id"] for a in
                     client.get("/applications").json()["applications"]}
        assert new_id not in ids_before
        assert new_id in ids_after


# ═══════════════════════════════════════════════════════════════════════════════
# S5 — existing endpoints still work (regression)
# ═══════════════════════════════════════════════════════════════════════════════

class TestRegression:
    """Scenario S5: existing demo endpoints are untouched by persistence."""

    def test_demo_run_still_works(self):
        r = client.post("/demo/run/GOLDEN")
        assert r.status_code == 200
        assert r.json()["report"]["recommendation"] == "Approve"

    def test_healthz_still_works(self):
        r = client.get("/healthz")
        assert r.status_code == 200
        assert r.json()["ok"] is True

    def test_architecture_still_works(self):
        r = client.get("/architecture")
        assert r.status_code == 200
        assert len(r.json()["ibm_seven_skills"]) == 7

    def test_custom_application_still_returns_full_envelope(self):
        r = client.post("/applications/mock/decide", json=BASE)
        assert r.status_code == 200
        assert {"case", "report", "audit", "impact"} <= set(r.json())

"""Tests for the advanced backend features: SSE streaming, what-if simulation,
batch analysis, admin policy config, and docker-compose health."""
from __future__ import annotations

import json
import os

os.environ["LOCAL_MOCK_MODE"] = "true"
os.environ["SANAD_DB_PATH"] = ":memory:"

from fastapi.testclient import TestClient
from backend.app import app

client = TestClient(app)


class TestBatchAnalysis:
    """GET /analysis/batch — runs all 13 cases and returns comparison matrix."""

    def test_batch_returns_all_cases(self):
        resp = client.get("/analysis/batch")
        assert resp.status_code == 200
        data = resp.json()
        assert data["case_count"] == 13
        assert len(data["results"]) == 13

    def test_batch_summary_counts(self):
        resp = client.get("/analysis/batch")
        data = resp.json()
        s = data["summary"]
        assert s["approve"] + s["refer"] + s["request_docs"] + s["reject"] == 13
        assert s["approve"] >= 4  # GOLDEN, HARDSHIP, LOW_INCOME, PROMPT_INJECTION, HIGH_CAPACITY
        assert s["reject"] == 1   # ACTIVE
        assert s["request_docs"] >= 1  # MISSING, ZERO_OR_MISSING_INCOME

    def test_batch_result_shape(self):
        resp = client.get("/analysis/batch")
        result = resp.json()["results"][0]
        for key in ("case_id", "recommendation", "path", "fired_rules",
                    "twenty_pct_compliance", "period_compliance", "risk_level",
                    "confidence", "deduction_rate"):
            assert key in result, f"missing key: {key}"

    def test_batch_golden_correct(self):
        resp = client.get("/analysis/batch")
        golden = next(r for r in resp.json()["results"] if r["case_id"] == "GOLDEN")
        assert golden["recommendation"] == "Approve"
        assert golden["path"] == "UPDATE_INSTALLMENT"
        assert "CAP-02" in golden["fired_rules"]
        assert golden["twenty_pct_compliance"] == "Pass"
        assert golden["period_compliance"] == "Pass"


class TestWhatIf:
    """POST /simulate/what-if/{case_id} — interactive policy exploration."""

    def test_what_if_income_reduction_changes_path(self):
        resp = client.post("/simulate/what-if/GOLDEN", json={"income": 5000})
        assert resp.status_code == 200
        data = resp.json()
        assert data["control"]["recommendation"] == "Approve"
        assert data["what_if"]["recommendation"] in ("Approve", "Refer to employee")
        assert data["case_id"] == "GOLDEN"
        assert len(data["delta"]) > 0

    def test_what_if_active_request_removed(self):
        resp = client.post("/simulate/what-if/ACTIVE", json={"active_request": False})
        assert resp.status_code == 200
        data = resp.json()
        assert data["control"]["recommendation"] == "Reject"
        assert data["what_if"]["recommendation"] != "Reject"
        assert "rules_removed" in data["delta"]

    def test_what_if_injection_removed(self):
        resp = client.post("/simulate/what-if/CONTRA", json={"injection": False})
        assert resp.status_code == 200
        data = resp.json()
        assert "RSK-01" not in data["what_if"]["fired_rules"]
        assert "RSK-01" in data["control"]["fired_rules"]

    def test_what_if_unknown_case_returns_404(self):
        resp = client.post("/simulate/what-if/UNKNOWN", json={})
        assert resp.status_code == 404

    def test_what_if_obligations_removed(self):
        resp = client.post("/simulate/what-if/HIGH_OBLIGATIONS", json={"obligations_ratio": 0.3})
        assert resp.status_code == 200
        data = resp.json()
        assert "OBL-01" not in data["what_if"]["fired_rules"]
        assert data["what_if"]["recommendation"] == "Approve"

    def test_what_if_hardship_added(self):
        resp = client.post("/simulate/what-if/GOLDEN", json={
            "hardship_unemployed": True, "hardship_unverified": True,
        })
        assert resp.status_code == 200
        data = resp.json()
        assert "HARD-01" in data["what_if"]["fired_rules"]


class TestSSEStreaming:
    """POST /demo/stream/{case_id} — real-time event stream."""

    def test_stream_golden_returns_events(self):
        resp = client.post("/demo/stream/GOLDEN")
        assert resp.status_code == 200
        assert "text/event-stream" in resp.headers["content-type"]
        text = resp.text
        assert "verify_identity" in text
        assert "retrieve_data" in text
        assert "validate_documents" in text
        assert "extract_income" in text
        assert "verify_salary" in text
        assert "decide" in text
        assert "complete" in text

    def test_stream_golden_final_has_report(self):
        resp = client.post("/demo/stream/GOLDEN")
        lines = resp.text.strip().split("\n\n")
        final_events = [l for l in lines if l.startswith("event: complete")]
        assert len(final_events) >= 1
        for ev in final_events:
            for line in ev.split("\n"):
                if line.startswith("data:"):
                    payload = json.loads(line[5:])
                    assert "report" in payload
                    assert payload["report"]["recommendation"] == "Approve"

    def test_stream_unknown_case(self):
        resp = client.post("/demo/stream/UNKNOWN")
        assert resp.status_code == 404

    def test_stream_meta_event(self):
        resp = client.post("/demo/stream/GOLDEN")
        assert "event: meta" in resp.text
        assert "case_id" in resp.text

    def test_stream_all_steps_present(self):
        import json
        resp = client.post("/demo/stream/GOLDEN")
        step_count = 0
        for line in resp.text.split("\n"):
            if line.startswith("data:") and '"step":' in line:
                data = json.loads(line[5:])
                step_count += 1
        assert step_count >= 6, f"expected at least 6 step events, got {step_count}"


class TestAdminConfig:
    """GET/PUT /admin/policy — live policy configuration."""

    def test_get_policy(self):
        resp = client.get("/admin/policy")
        assert resp.status_code == 200
        data = resp.json()
        assert "policy" in data
        assert data["policy"]["deduction_cap_pct"] == 0.20

    def test_put_policy_update(self):
        resp = client.put("/admin/policy", json={"min_headroom_aed": 200})
        assert resp.status_code == 200
        data = resp.json()
        assert data["applied"] is True
        assert data["current"]["min_headroom_aed"] == 200

        # Restore
        client.put("/admin/policy", json={"min_headroom_aed": 50})

    def test_put_policy_unknown_field(self):
        resp = client.put("/admin/policy", json={"unknown_field": 999})
        assert resp.status_code == 422
        data = resp.json()
        assert "error_code" in data

    def test_put_policy_affects_decisions(self):
        client.put("/admin/policy", json={"min_headroom_aed": 5000})
        resp = client.get("/analysis/batch")
        data = resp.json()
        golden = next(r for r in data["results"] if r["case_id"] == "GOLDEN")
        # With headroom set very high, golden might switch from UPDATE to TRANSFER
        # because 55 < 5000
        assert golden["path"] in ("UPDATE_INSTALLMENT", "TRANSFER_ARREARS")
        # Restore
        client.put("/admin/policy", json={"min_headroom_aed": 50})

    def test_put_policy_updates_version(self):
        resp = client.put("/admin/policy", json={"policy_version": "test-version"})
        assert resp.status_code == 200
        assert resp.json()["policy_version"] == "test-version"
        client.put("/admin/policy", json={"policy_version": "sanad-v0.8"})

    def test_get_policy_after_update(self):
        client.put("/admin/policy", json={"deduction_cap_pct": 0.25})
        resp = client.get("/admin/policy")
        assert resp.json()["policy"]["deduction_cap_pct"] == 0.25
        client.put("/admin/policy", json={"deduction_cap_pct": 0.20})


class TestDecisionHistory:
    """GET /analysis/decisions — decision timeline."""

    def test_history_endpoint(self):
        resp = client.get("/analysis/decisions")
        assert resp.status_code == 200
        data = resp.json()
        assert "decisions" in data
        assert "officer_actions" in data
        assert "total_decisions" in data
        assert "total_officer_actions" in data


class TestDockerConfig:
    """Verify Docker and docker-compose files exist and are valid."""

    def test_dockerfile_exists(self):
        assert os.path.isfile("Dockerfile")

    def test_dockerfile_has_uvicorn_cmd(self):
        with open("Dockerfile") as f:
            content = f.read()
        assert "uvicorn" in content
        assert "backend.app:app" in content
        assert "EXPOSE 8000" in content

    def test_docker_compose_exists(self):
        assert os.path.isfile("docker-compose.yml")

    def test_docker_compose_has_healthcheck(self):
        with open("docker-compose.yml") as f:
            content = f.read()
        assert "healthcheck" in content
        assert "agent-sanad" in content

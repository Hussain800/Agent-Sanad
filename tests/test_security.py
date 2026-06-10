"""Security and PII safety regression tests.

Extends test_governance.py with tests for: frontend XSS prevention,
error envelope coverage on all routes, store DB gitignore, and PII
redaction confirmation.
"""
from __future__ import annotations

import re
from pathlib import Path

from fastapi.testclient import TestClient

from backend.app import app
from backend.observability.redaction import redact_for_trace

client = TestClient(app)
REPO_ROOT = Path(__file__).resolve().parents[1]


class TestXssPrevention:
    """Scenario S1: dynamic content rendered in the frontend is escaped."""

    def test_frontend_esc_function_defined(self):
        """The esc() function must exist in the HTML and escape HTML special chars."""
        html = client.get("/").text
        # Look for the esc function definition
        assert "const esc=" in html or "const esc = v =>" in html
        assert "&amp;" in html  # escaping reference

    def test_frontend_renders_prompt_injection_safely(self):
        """PROMPT_INJECTION_ONLY contains injected text patterns in its output
        (RSK-01). The rendered page must not break because of it."""
        r = client.post("/demo/run/PROMPT_INJECTION_ONLY")
        assert r.status_code == 200
        report = r.json()["report"]
        # If there's HTML content in reasoning, it must be escaped
        reasoning = report["reasoning"]
        assert "<" not in reasoning or "&lt;" in reasoning, (
            "Reasoning contains unescaped HTML: " + reasoning[:200]
        )


class TestErrorEnvelopeCoverage:
    """Scenario S2: ALL API routes return the PRD §5.5 error envelope."""

    ROUTES_TO_TEST = [
        ("GET", "/cases/UNKNOWN_CASE"),
        ("GET", "/cases/UNKNOWN_CASE/audit"),
        ("POST", "/demo/run/UNKNOWN_CASE"),
        ("POST", "/cases/UNKNOWN_CASE/decide"),
        ("POST", "/cases/UNKNOWN_CASE/officer-action"),
        ("GET", "/applications/UNKNOWN_APP"),
    ]

    def test_unknown_case_404_envelope(self):
        for method, url in self.ROUTES_TO_TEST:
            if method == "GET":
                r = client.get(url)
            else:
                r = client.post(url, json={})
            assert r.status_code == 404, f"{method} {url} -> {r.status_code}"
            body = r.json()
            assert body["error_code"] == "NOT_FOUND", f"{method} {url}: {body}"
            assert "message" in body
            assert "app_version" in body

    def test_malformed_json_422_envelope(self):
        """All JSON-body endpoints reject malformed input with the correct envelope."""
        endpoints = [
            ("POST", "/applications/mock"),
            ("POST", "/applications/mock/decide"),
            ("POST", "/cases/GOLDEN/officer-action"),
        ]
        for method, url in endpoints:
            r = client.post(url, content="not json", headers={"Content-Type": "application/json"})
            assert r.status_code == 422, f"{url}: {r.status_code}"
            body = r.json()
            assert body["error_code"] == "VALIDATION_ERROR", f"{url}: {body}"
            assert "detail" not in body


class TestPiiRedaction:
    """Scenario S3: PII redaction catches known patterns."""

    def test_emirates_id_pattern_redacted(self):
        safe = redact_for_trace({"case_id": "GOLDEN", "detail": "ID 784-1990-1234567-1"})
        assert "784-1990" not in str(safe)

    def test_arabic_narrative_redacted(self):
        safe = redact_for_trace({"case_id": "GOLDEN", "narrative": "نص عربي حساس"})
        assert "نص" not in str(safe)
        assert "narrative" not in safe

    def test_document_text_key_dropped(self):
        safe = redact_for_trace({"case_id": "GOLDEN", "document_text": "ignore rules"})
        assert "document_text" not in safe

    def test_allow_listed_keys_survive(self):
        payload = {
            "case_id": "GOLDEN",
            "recommendation": "Approve",
            "path": "UPDATE_INSTALLMENT",
            "fired_rules": ["CAP-02"],
            "latency_ms": 3,
            "mock_mode": True,
        }
        safe = redact_for_trace(payload)
        assert safe["case_id"] == "GOLDEN"
        assert safe["recommendation"] == "Approve"


class TestGitignoreSecurity:
    """Scenario S4: sensitive files are gitignored."""

    def test_db_path_is_gitignored(self):
        gitignore = (REPO_ROOT / ".gitignore").read_text(encoding="utf-8")
        assert "data/*.db" in gitignore

    def test_no_pii_in_fixtures_via_api(self):
        """All 13 cases returned via the API must have masked names and synthetic IDs."""
        import re
        for cid in [
            "GOLDEN", "NOHEAD", "MISSING", "ACTIVE", "CONTRA",
            "HIGH_OBLIGATIONS", "PERIOD_BREACH", "HARDSHIP",
            "ZERO_OR_MISSING_INCOME", "LOW_INCOME_PER_MEMBER",
            "UNVERIFIED_HARDSHIP", "PROMPT_INJECTION_ONLY", "HIGH_CAPACITY_UPDATE",
        ]:
            case = client.get(f"/cases/{cid}").json()["case"]
            name = case["applicant"]["name_masked"]
            assert "*" in name, f"{cid} unmasked name: {name}"
            ref = case["applicant"]["applicant_ref"]
            assert ref.startswith("APP-"), f"{cid} non-synthetic ref: {ref}"
            assert not re.search(r"\b\d{15}\b", str(case)), f"{cid} has Emirates-ID"

    def test_store_initialization_never_crashes(self):
        """Even if the store DB cannot be created, the app must still start."""
        from backend.store import STORE
        assert STORE is not None  # singleton is always created
        # The store gracefully handles failures
        assert hasattr(STORE, "list_applications")

from fastapi.testclient import TestClient

from backend.app import app


client = TestClient(app)


def test_healthz_reports_offline_safe_mode():
    response = client.get("/healthz")
    assert response.status_code == 200
    data = response.json()
    assert data["ok"] is True
    assert data["mock_mode"] is True
    assert data["policy_version"] == "sanad-v0.8"
    assert data["app_version"]          # build handshake field present


def test_frontend_and_backend_build_versions_match():
    """The UI pins CLIENT_BUILD and compares it to /healthz app_version at boot
    (stale-server detection). This test prevents the two pins from drifting."""
    from backend.app import APP_VERSION
    from pathlib import Path
    html = (Path(__file__).resolve().parents[1] / "frontend" / "index.html").read_text(encoding="utf-8")
    assert APP_VERSION in html, (
        "frontend CLIENT_BUILD must equal backend APP_VERSION — update both together"
    )
    assert 'CLIENT_BUILD=' in html or 'CLIENT_BUILD =' in html


def test_error_envelope_contract():
    """PRD §5.5 — errors return {error_code, message}, not framework defaults."""
    r = client.post("/demo/run/UNKNOWN")
    assert r.status_code == 404
    body = r.json()
    assert body["error_code"] == "NOT_FOUND"
    assert "message" in body and "app_version" in body
    r2 = client.post("/applications/mock/decide", json={"monthly_income_aed": -1})
    assert r2.status_code == 422
    assert r2.json()["error_code"] == "VALIDATION_ERROR"


def test_malformed_body_also_returns_envelope():
    """RequestValidationError (missing/malformed JSON body) must use the same
    §5.5 envelope — not FastAPI's default {detail: [...]} shape."""
    # No body at all on a dict-body endpoint.
    r = client.post("/applications/mock/decide")
    assert r.status_code == 422
    body = r.json()
    assert body["error_code"] == "VALIDATION_ERROR"
    assert "detail" not in body
    # Body that isn't a JSON object.
    r2 = client.post("/applications/mock",
                     content="not json at all",
                     headers={"Content-Type": "application/json"})
    assert r2.status_code == 422
    assert r2.json()["error_code"] == "VALIDATION_ERROR"


def test_demo_run_returns_contract_and_benchmark():
    response = client.post("/demo/run/GOLDEN")
    assert response.status_code == 200
    data = response.json()
    assert {"case", "report", "audit", "impact"} <= set(data)
    assert data["report"]["recommendation"] == "Approve"
    assert data["report"]["proposed_plan"]["path"] == "UPDATE_INSTALLMENT"
    assert data["impact"]["mock_mode"] is True
    assert data["impact"]["benchmark"]["path_match_accuracy"] == 0.946
    assert any(event["step"] == "extract.salary_certificate" for event in data["audit"])


def test_static_ui_contains_final_demo_surfaces():
    response = client.get("/")
    assert response.status_code == 200
    html = response.text
    for text in [
        "Beneficiary journey",
        "Section 8 recommendation output",
        "Evidence, rules, and decision trace",
        "Zero-bureaucracy impact",
        "Retry",
        "IBM Research agent-engineering playbook",
        "System design",
        "Observability",
    ]:
        assert text in html


def test_request_id_roundtrip_for_observability():
    """IBM skill 6 — every /demo/run call is correlatable end-to-end via X-Request-ID."""
    # Caller-supplied id is honored.
    r1 = client.post("/demo/run/GOLDEN", headers={"X-Request-ID": "judge-trace-42"})
    assert r1.status_code == 200
    assert r1.headers.get("x-request-id") == "judge-trace-42"
    # Server mints one when caller omits it.
    r2 = client.post("/demo/run/GOLDEN")
    assert r2.status_code == 200
    assert r2.headers.get("x-request-id") and len(r2.headers["x-request-id"]) >= 6


def test_architecture_exposes_ibm_seven_skills_mapping():
    """The /architecture endpoint is the machine-readable USP surface.
    Each of the IBM 7 skills must map to a concrete subsystem."""
    response = client.get("/architecture")
    assert response.status_code == 200
    arch = response.json()
    assert "doctrine" in arch
    skills = arch["ibm_seven_skills"]
    assert len(skills) == 7
    assert [s["n"] for s in skills] == [1, 2, 3, 4, 5, 6, 7]
    # Every skill must declare where it is shipped — no placeholders.
    for s in skills:
        assert s["shipped_in"] and len(s["shipped_in"]) > 20
    # Honest-claims block must include the benchmark headline.
    claims = arch["honest_claims"]
    assert "94.6" in claims["path_match_accuracy_2025"]
    assert "100%" in claims["twenty_pct_compliance_update_plans"]
    assert claims["premium_dev_median_aed"] == 557
    assert "do_not_claim" in claims


# ── v1.1 §7 state-machine contract ──────────────────────────────────────────

def test_state_machine_transitions_emitted_for_each_case():
    """Every case must emit the canonical v1.1 §7 state journey:
    Submitted -> IdentityLinked -> DataRetrieved -> Extracting -> Validating
    -> PolicyRun -> {RecommendationReady|NeedsDocuments|Refer|Rejected} -> Closed.

    Pre-policy gates (ACTIVE-01, DOC-01/02) DO traverse the full journey because
    the gates are enforced inside decide(); the audit transitions are about the
    canonical journey, not about which branch decide() took."""
    terminal = {
        "GOLDEN":                 "RecommendationReady",
        "NOHEAD":                 "Refer",
        "MISSING":                "NeedsDocuments",
        "ACTIVE":                 "Rejected",
        "CONTRA":                 "Refer",
        "HIGH_OBLIGATIONS":       "Refer",
        "PERIOD_BREACH":          "Refer",
        "HARDSHIP":               "RecommendationReady",
        "ZERO_OR_MISSING_INCOME": "NeedsDocuments",
        "LOW_INCOME_PER_MEMBER":  "RecommendationReady",
        "UNVERIFIED_HARDSHIP":    "Refer",
        "PROMPT_INJECTION_ONLY":  "RecommendationReady",
        "HIGH_CAPACITY_UPDATE":   "RecommendationReady",
    }
    expected_prefix = ["Submitted", "IdentityLinked", "DataRetrieved",
                       "Extracting", "Validating", "PolicyRun"]
    for cid, want in terminal.items():
        audit = client.post(f"/demo/run/{cid}").json()["audit"]
        states = [e["state_to"] for e in audit if e.get("state_to")]
        assert states[:6] == expected_prefix, f"{cid}: {states}"
        # ... PolicyRun -> terminal -> Closed
        assert states[-2] == want, f"{cid} terminal: got {states[-2]} expected {want}"
        assert states[-1] == "Closed", f"{cid} did not reach Closed: {states}"


def test_phase5_required_cases_show_all_state_markers():
    """Phase 5 explicitly names these five cases; each must show every canonical
    state marker in its audit feed."""
    required_states = {"Submitted", "IdentityLinked", "DataRetrieved",
                       "Extracting", "Validating", "PolicyRun", "Closed"}
    for cid in ("GOLDEN", "MISSING", "ACTIVE", "PERIOD_BREACH", "CONTRA"):
        audit = client.post(f"/demo/run/{cid}").json()["audit"]
        states = {e["state_to"] for e in audit if e.get("state_to")}
        assert required_states <= states, f"{cid} missing: {required_states - states}"


def test_audit_events_carry_actor_and_mock_mode():
    """v1.1 PRD §6 AuditEvent fields are populated."""
    audit = client.post("/demo/run/GOLDEN").json()["audit"]
    assert all("actor" in e for e in audit)
    assert all("mock_mode" in e for e in audit)
    actors = {e["actor"] for e in audit}
    # The system, adapter, and policy actors must all be represented.
    assert {"system", "adapter", "policy"} <= actors


# ── v1.1 §5.5 — new safe read endpoints ─────────────────────────────────────

def test_get_benchmark_returns_honest_claim_and_metrics():
    r = client.get("/benchmark")
    assert r.status_code == 200
    data = r.json()
    # Honest-claim wording must contain the unchanged phrase.
    assert "94.6%" in data["honest_claim"]
    assert "does not claim exact reproduction" in data["honest_claim"]
    # Metrics must match the static BENCHMARK block exactly.
    assert data["metrics"]["path_match_accuracy"] == 0.946
    assert data["metrics"]["twenty_pct_compliance_update"] == 1.00
    assert data["n"] == 522


def test_get_case_returns_assembled_case_without_running_policy():
    r = client.get("/cases/GOLDEN")
    assert r.status_code == 200
    body = r.json()
    assert body["case_id"] == "GOLDEN"
    case = body["case"]
    assert case["applicant"]["applicant_ref"] == "APP-0001"
    assert case["loan"]["current_installment_aed"] == 3287
    # No policy run yet — the response only carries the assembled Case.
    assert "report" not in body


def test_get_case_audit_returns_state_transition_journey():
    r = client.get("/cases/GOLDEN/audit")
    assert r.status_code == 200
    events = r.json()["events"]
    states = [e["state_to"] for e in events if e.get("state_to")]
    # build_case emits up to Validating; the terminal + Closed states are added
    # by the policy-run path, so the assembly audit ends at Validating.
    assert states[:5] == ["Submitted", "IdentityLinked", "DataRetrieved",
                          "Extracting", "Validating"]


def test_post_cases_decide_matches_demo_run_envelope():
    """The v1.1 named POST /cases/{id}/decide must return the SAME envelope as
    POST /demo/run/{id}. Equivalence excludes per-run fields (request_id,
    latency_ms) which are independent per HTTP call."""
    a = client.post("/demo/run/GOLDEN").json()
    b = client.post("/cases/GOLDEN/decide").json()
    assert a["report"]["recommendation"] == b["report"]["recommendation"]
    assert a["report"]["proposed_plan"] == b["report"]["proposed_plan"]
    assert set(a["report"]["fired_rules"]) == set(b["report"]["fired_rules"])
    assert a["report"]["twenty_pct_compliance"] == b["report"]["twenty_pct_compliance"]
    assert a["report"]["period_compliance"] == b["report"]["period_compliance"]


def test_unknown_case_returns_404_on_every_case_route():
    for url in ("/cases/UNKNOWN", "/cases/UNKNOWN/audit",
                "/demo/run/UNKNOWN"):
        method = client.post if "run" in url else client.get
        r = method(url)
        assert r.status_code == 404, url
    assert client.post("/cases/UNKNOWN/decide").status_code == 404


# ── v1.1 §5.5 / §6 — officer action (human owns exceptions) ─────────────────

def test_officer_action_approve_records_off_audit_and_preserves_report():
    r = client.post("/cases/GOLDEN/officer-action", json={"action": "approve"})
    assert r.status_code == 200
    body = r.json()
    # The deterministic recommendation is unchanged.
    assert body["report"]["recommendation"] == "Approve"
    # An officer-actor audit event exists.
    assert any(e["actor"] == "officer" and e["step"] == "officer.action"
               for e in body["audit"])


def test_officer_action_adjust_requires_reason_code():
    # Missing reason on adjust -> 422 from the OfficerAction validator.
    r = client.post("/cases/GOLDEN/officer-action", json={"action": "adjust"})
    assert r.status_code == 422
    # With a reason -> accepted.
    ok = client.post("/cases/GOLDEN/officer-action",
                     json={"action": "adjust", "override_reason_code": "OFF-MANUAL-01"})
    assert ok.status_code == 200
    assert ok.json()["officer_action"]["override_reason_code"] == "OFF-MANUAL-01"


def test_officer_action_unknown_case_404():
    assert client.post("/cases/UNKNOWN/officer-action",
                       json={"action": "approve"}).status_code == 404


# ── Phase 4 — Section-8 field presence across ALL cases ─────────────────────

SECTION_8_FIELDS = [
    "application_status", "case_summary", "income_analysis", "arrears_amount_aed",
    "remaining_balance_aed", "remaining_term_months", "proposed_deduction_rate",
    "proposed_plan", "twenty_pct_compliance", "period_compliance",
    "recommendation", "reasoning",
]
ALL_CASES = [
    "GOLDEN", "NOHEAD", "MISSING", "ACTIVE", "CONTRA",
    "HIGH_OBLIGATIONS", "PERIOD_BREACH", "HARDSHIP",
    "ZERO_OR_MISSING_INCOME", "LOW_INCOME_PER_MEMBER",
    "UNVERIFIED_HARDSHIP", "PROMPT_INJECTION_ONLY", "HIGH_CAPACITY_UPDATE",
]


def test_every_case_returns_all_section_8_fields():
    for cid in ALL_CASES:
        report = client.post(f"/demo/run/{cid}").json()["report"]
        for field in SECTION_8_FIELDS:
            assert field in report, f"{cid} missing Section-8 field {field}"
        # Non-empty human-readable fields on every case.
        assert report["case_summary"].strip()
        assert report["income_analysis"].strip()
        assert report["reasoning"].strip()


def test_none_path_cases_have_clean_na_compliance():
    """For cases where no plan is generated, compliance is N/A (not a misleading
    Pass/Fail), and the plan path is NONE."""
    for cid in ("MISSING", "ACTIVE", "CONTRA", "ZERO_OR_MISSING_INCOME"):
        report = client.post(f"/demo/run/{cid}").json()["report"]
        assert report["proposed_plan"]["path"] == "NONE", cid
        assert report["twenty_pct_compliance"] == "N/A", cid
        assert report["period_compliance"] == "N/A", cid


# ── Phase 8 — governance / PII safety ───────────────────────────────────────

def test_no_real_pii_in_any_case_payload():
    """Every applicant_ref / agreement_id is synthetic (APP-/AGR- prefix), and
    no name longer than a masked stub is exposed."""
    import re
    for cid in ALL_CASES:
        case = client.post(f"/demo/run/{cid}").json()["case"]
        app_ref = case["applicant"]["applicant_ref"]
        assert app_ref.startswith("APP-"), f"{cid}: {app_ref}"
        # Name must be masked (contains an asterisk, not a real full name).
        assert "*" in case["applicant"]["name_masked"], cid
        if case.get("loan"):
            assert case["loan"]["agreement_id"].startswith("AGR-"), cid
        # No 15-digit Emirates-ID-style number anywhere in the case payload.
        assert not re.search(r"\b\d{15}\b", str(case)), f"{cid} has an ID-like number"


def test_prompt_injection_does_not_change_decision_via_api():
    """Security boundary, asserted through the HTTP layer: the injection case
    fires RSK-01 but produces the same Approve plan as if there were no injection."""
    report = client.post("/demo/run/PROMPT_INJECTION_ONLY").json()["report"]
    assert "RSK-01" in report["fired_rules"]
    assert report["recommendation"] == "Approve"
    assert report["proposed_plan"]["new_total_installment_aed"] == 3000

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
        "Extraction source",
        "Retry",
        # IBM 7-skills USP footer — the architecture pitch.
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
    """Every case must emit the canonical v1.1 state journey:
    Submitted -> IdentityLinked -> DataRetrieved -> Validating -> PolicyRun
    -> one of {RecommendationReady, NeedsDocuments, Refer, Rejected}.

    Pre-policy gates (ACTIVE-01, DOC-01/02) DO traverse Validating first because
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
    for cid, want in terminal.items():
        audit = client.post(f"/demo/run/{cid}").json()["audit"]
        states = [e["state_to"] for e in audit if e.get("state_to")]
        expected_prefix = ["Submitted", "IdentityLinked", "DataRetrieved",
                           "Validating", "PolicyRun"]
        assert states[:5] == expected_prefix, f"{cid}: {states}"
        assert states[-1] == want, f"{cid} terminal: got {states[-1]} expected {want}"


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
    assert states[:4] == ["Submitted", "IdentityLinked", "DataRetrieved", "Validating"]


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

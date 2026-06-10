"""v1.4 integration tests: RBAC, audit chain, simulator, decision package."""
from fastapi.testclient import TestClient
from backend.app import app
client = TestClient(app)

# ── RBAC ──────────────────────────────────────────────────────────────────

class TestRBAC:
    def test_admin_can_access_connectors(self):
        r = client.get("/connectors", headers={"x-sanad-role": "admin"})
        assert r.status_code == 200

    def test_beneficiary_can_access_connectors(self):
        r = client.get("/connectors", headers={"x-sanad-role": "beneficiary"})
        assert r.status_code == 200

    def test_supervisor_can_access_metrics(self):
        r = client.get("/supervisor/metrics", headers={"x-sanad-role": "supervisor"})
        assert r.status_code == 200

    def test_beneficiary_cannot_access_supervisor(self):
        r = client.get("/supervisor/metrics", headers={"x-sanad-role": "beneficiary"})
        assert r.status_code == 403

# ── Simulator ─────────────────────────────────────────────────────────────

class TestSimulator:
    def test_golden_returns_options(self):
        r = client.post("/cases/GOLDEN/simulate-plan")
        assert r.status_code == 200
        data = r.json()
        assert len(data["options"]) >= 2
        # All options must be valid or have invalid_reason
        for opt in data["options"]:
            assert "valid" in opt
            assert "twenty_pct_ok" in opt

    def test_unknown_case_404(self):
        r = client.post("/cases/UNKNOWN/simulate-plan")
        assert r.status_code == 404

# ── Decision Package ──────────────────────────────────────────────────────

class TestDecisionPackage:
    def test_create_package(self):
        r = client.post("/cases/GOLDEN/decision-package")
        assert r.status_code == 200
        pkg = r.json()
        assert pkg["package_id"].startswith("PKG")
        assert pkg["package_hash"] is not None

    def test_get_package(self):
        pkg_id = client.post("/cases/GOLDEN/decision-package").json()["package_id"]
        r = client.get(f"/cases/GOLDEN/decision-package")
        assert r.status_code == 200

    def test_signature_flow(self):
        sig = client.post("/cases/GOLDEN/signature/request").json()
        assert sig["status"] == "pending"
        assert sig["signature_id"].startswith("SIG")

# ── Audit Chain ───────────────────────────────────────────────────────────

class TestAuditChain:
    def test_audit_chain_returns_entries(self):
        # Create a package first to generate an audit event
        client.post("/cases/GOLDEN/decision-package")
        r = client.get("/cases/GOLDEN/audit-chain")
        assert r.status_code == 200
        assert "chain" in r.json()

    def test_audit_verify(self):
        r = client.post("/audit/verify", json={"case_id": "GOLDEN"})
        assert r.status_code == 200
        # May be True or have no entries, but must not error
        assert "ok" in r.json()

# ── Supervisor ────────────────────────────────────────────────────────────

class TestSupervisor:
    def test_metrics(self):
        r = client.get("/supervisor/metrics", headers={"x-sanad-role": "supervisor"})
        assert r.status_code == 200
        assert r.json()["total_applications"] >= 0

    def test_connector_health(self):
        r = client.get("/supervisor/connector-health", headers={"x-sanad-role": "supervisor"})
        assert r.status_code == 200
        assert len(r.json()["connectors"]) >= 6

    def test_policy_drift(self):
        r = client.get("/supervisor/policy-drift", headers={"x-sanad-role": "supervisor"})
        assert r.status_code == 200
        assert "policy_version" in r.json()

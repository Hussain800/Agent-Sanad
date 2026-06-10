"""v1.8 material routes tests."""
from fastapi.testclient import TestClient
from backend.app import app
client = TestClient(app)

def test_judge_packet(): r = client.get("/materials/v1.8/judge-packet"); assert r.status_code == 200; assert "packet" in r.json()
def test_run_of_show(): r = client.get("/materials/v1.8/run-of-show"); assert r.status_code == 200
def test_interop_cert_pack(): r = client.get("/materials/v1.8/interop-certification-pack"); assert r.status_code == 200
def test_digital_twin_guide(): r = client.get("/materials/v1.8/policy-digital-twin-guide"); assert r.status_code == 200
def test_evidence_vault_guide(): r = client.get("/materials/v1.8/evidence-vault-guide"); assert r.status_code == 200
def test_copilot_safety_material(): r = client.get("/materials/v1.8/copilot-safety-case"); assert r.status_code == 200
def test_redteam_coverage(): r = client.get("/redteam/coverage"); assert r.status_code == 200; assert r.json()["total_drills"] >= 20
def test_mission_demo_script(): r = client.get("/mission-control/live-demo-script"); assert r.status_code == 200
def test_release_drift_check(): r = client.post("/release/drift/check"); assert r.status_code == 200
def test_interop_onboarding(): r = client.get("/interop/onboarding-pack"); assert r.status_code == 200
def test_copilot_safety(): r = client.get("/copilot/safety-case"); assert r.status_code == 200
def test_trust_receipt_flow():
    client.post("/cases/GOLDEN/evidence-vault/build")
    r = client.get("/cases/GOLDEN/trust-receipt"); assert r.status_code == 200
    if r.json().get("built"):
        rid = r.json()["receipt_id"]
        r2 = client.post("/trust-receipts/tamper-demo", json={"receipt_id": rid}); assert r2.status_code == 200; assert r2.json()["mismatch"] is True
def test_interop_api_marketplace(): r = client.get("/interop/api-marketplace-readiness"); assert r.status_code == 200
def test_interop_gsb(): r = client.get("/interop/gsb-onboarding-checklist"); assert r.status_code == 200
def test_interop_uaepass(): r = client.get("/interop/uaepass-readiness"); assert r.status_code == 200

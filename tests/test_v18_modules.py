"""v1.8 modules existence and smoke tests."""
from fastapi.testclient import TestClient
from backend.app import app
client = TestClient(app)

def test_release_brain(): r = client.get("/release/brain"); assert r.status_code == 200; assert r.json()["app_version"] == "1.8.0"
def test_release_provenance(): r = client.get("/release/provenance"); assert r.status_code == 200
def test_release_drift(): r = client.get("/release/drift"); assert r.status_code == 200
def test_release_drift_check(): r = client.post("/release/drift/check"); assert r.status_code == 200
def test_warning_budget(): r = client.get("/release/warning-budget"); assert r.status_code == 200
def test_rescue_radar(): r = client.get("/rescue/radar"); assert r.status_code == 200
def test_rescue_case(): r = client.get("/rescue/radar/GOLDEN"); assert r.status_code == 200
def test_rescue_simulate(): r = client.post("/rescue/radar/simulate"); assert r.status_code == 200
def test_rescue_outreach(): r = client.post("/rescue/outreach/GOLDEN"); assert r.status_code == 200
def test_rescue_interventions(): r = client.get("/rescue/interventions"); assert r.status_code == 200
def test_digital_twin_scenarios(): r = client.get("/digital-twin/scenarios"); assert r.status_code == 200
def test_digital_twin_run(): r = client.post("/digital-twin/run?scenario_id=baseline"); assert r.status_code == 200
def test_evidence_vault_build(): r = client.post("/cases/GOLDEN/evidence-vault/build"); assert r.status_code == 200
def test_evidence_vault_get(): r = client.get("/cases/GOLDEN/evidence-vault"); assert r.status_code == 200
def test_trust_receipt(): r = client.get("/cases/GOLDEN/trust-receipt"); assert r.status_code == 200
def test_interop_cert(): r = client.get("/interop/certification"); assert r.status_code == 200
def test_interop_run(): r = client.post("/interop/certification/run"); assert r.status_code == 200
def test_copilot_start(): r = client.post("/copilot/session/start?lang=en"); assert r.status_code == 200
def test_copilot_message(): r = client.post("/copilot/session/X/message?message=status"); sid = client.post("/copilot/session/start?lang=en").json()["id"]; r2 = client.post(f"/copilot/session/{sid}/message?message=status"); assert r2.status_code == 200
def test_copilot_scripts(): r = client.get("/copilot/scripts"); assert r.status_code == 200
def test_copilot_safety(): r = client.get("/copilot/safety-case"); assert r.status_code == 200
def test_mission_control(): r = client.get("/mission-control"); assert r.status_code == 200
def test_mission_playbooks(): r = client.get("/mission-control/playbooks"); assert r.status_code == 200
def test_mission_tasks(): r = client.get("/mission-control/tasks"); assert r.status_code == 200
def test_mission_risk(): r = client.get("/mission-control/risk-brief"); assert r.status_code == 200
def test_mission_demo(): r = client.get("/mission-control/live-demo-script"); assert r.status_code == 200
def test_redteam_run(): r = client.post("/redteam/run"); assert r.status_code == 200
def test_redteam_latest(): r = client.get("/redteam/latest"); assert r.status_code == 200
def test_redteam_coverage(): r = client.get("/redteam/coverage"); assert r.status_code == 200
def test_redteam_history(): r = client.get("/redteam/history"); assert r.status_code == 200

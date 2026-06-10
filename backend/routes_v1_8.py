import json, time, os
from fastapi import HTTPException, Request
from datetime import datetime, timezone
from backend.store import STORE
from backend.release_brain import get_release_brain, get_release_provenance, get_release_drift, post_drift_check, get_warning_budget
from backend.rescue_radar import get_radar, get_case_radar, simulate_radar, outreach, get_interventions
from backend.policy_digital_twin import get_scenarios, run_scenario, get_run, get_run_impact, get_run_fairness, get_run_workload, get_run_explain, compare_runs
from backend.evidence_vault import build_vault, get_vault, get_trust_receipt, verify_receipt, tamper_demo, get_public_receipt
from backend.interop_certification import run_certification, get_certification, get_connector_cert, get_onboarding_pack, get_api_marketplace_readiness, get_gsb_checklist, get_uaepass_readiness, get_uae_verify_readiness
from backend.service_copilot import start_session, handle_message, get_session, get_scripts, get_safety_case, run_redteam as copilot_redteam
from backend.mission_control import get_playbooks, run_playbook, get_tasks, complete_task, get_risk_brief, get_live_demo_script, get_mission_control

def register_v18_routes(app):
    # Release brain
    app.get("/release/brain")(get_release_brain)
    app.get("/release/provenance")(get_release_provenance)
    app.get("/release/drift")(get_release_drift)
    app.post("/release/drift/check")(post_drift_check)
    app.get("/release/warning-budget")(get_warning_budget)
    # Rescue radar
    app.get("/rescue/radar")(get_radar)
    app.get("/rescue/radar/{case_id}")(get_case_radar)
    app.post("/rescue/radar/simulate")(simulate_radar)
    app.post("/rescue/outreach/{case_id}")(outreach)
    app.get("/rescue/interventions")(get_interventions)
    # Policy digital twin
    app.get("/digital-twin/scenarios")(get_scenarios)
    app.post("/digital-twin/run")(run_scenario)
    app.get("/digital-twin/runs/{run_id}")(get_run)
    app.get("/digital-twin/runs/{run_id}/impact")(get_run_impact)
    app.get("/digital-twin/runs/{run_id}/fairness")(get_run_fairness)
    app.get("/digital-twin/runs/{run_id}/workload")(get_run_workload)
    app.get("/digital-twin/runs/{run_id}/explain")(get_run_explain)
    app.get("/digital-twin/runs/{run_id}/compare/{baseline_run_id}")(compare_runs)
    # Evidence vault
    app.post("/cases/{case_id}/evidence-vault/build")(build_vault)
    app.get("/cases/{case_id}/evidence-vault")(get_vault)
    app.get("/cases/{case_id}/trust-receipt")(get_trust_receipt)
    app.post("/trust-receipts/verify")(verify_receipt)
    app.post("/trust-receipts/tamper-demo")(tamper_demo)
    app.get("/trust-receipts/{receipt_id}/public")(get_public_receipt)
    # Interop certification
    app.get("/interop/certification")(get_certification)
    app.get("/interop/certification/{connector}")(get_connector_cert)
    app.post("/interop/certification/run")(run_certification)
    app.get("/interop/onboarding-pack")(get_onboarding_pack)
    app.get("/interop/api-marketplace-readiness")(get_api_marketplace_readiness)
    app.get("/interop/gsb-onboarding-checklist")(get_gsb_checklist)
    app.get("/interop/uaepass-readiness")(get_uaepass_readiness)
    app.get("/interop/uae-verify-readiness")(get_uae_verify_readiness)
    # Arabic service copilot
    app.post("/copilot/session/start")(start_session)
    app.post("/copilot/session/{session_id}/message")(handle_message)
    app.get("/copilot/session/{session_id}")(get_session)
    app.get("/copilot/scripts")(get_scripts)
    app.get("/copilot/safety-case")(get_safety_case)
    app.post("/copilot/redteam/run")(copilot_redteam)
    # Mission control
    app.get("/mission-control")(get_mission_control)
    app.get("/mission-control/playbooks")(get_playbooks)
    app.post("/mission-control/playbooks/{playbook_id}/run")(run_playbook)
    app.get("/mission-control/tasks")(get_tasks)
    app.post("/mission-control/tasks/{task_id}/complete")(complete_task)
    app.get("/mission-control/risk-brief")(get_risk_brief)
    app.get("/mission-control/live-demo-script")(get_live_demo_script)
    # Redteam lab
    from backend.redteam_lab import run, get_latest, get_history, get_coverage
    app.post("/redteam/run")(run)
    app.get("/redteam/latest")(get_latest)
    app.get("/redteam/history")(get_history)
    app.get("/redteam/coverage")(get_coverage)

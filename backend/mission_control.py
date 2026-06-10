"""v1.8 Mission Control — playbooks, tasks, risk brief."""
from __future__ import annotations
from datetime import datetime, timezone

_PLAYBOOKS = {
    "connector_outage": {"owner":"admin","actions":["check_health","simulate_failure","reset_connector"],"severity":"critical"},
    "sla_breach": {"owner":"supervisor","actions":["review_backlog","escalate_case","adjust_sla"],"severity":"high"},
    "appeal_backlog": {"owner":"supervisor","actions":["list_appeals","assign_officer","schedule_review"],"severity":"medium"},
    "security_drill_failure": {"owner":"admin","actions":["review_logs","rerun_drills","patch_control"],"severity":"critical"},
    "consent_spike": {"owner":"supervisor","actions":["review_denials","check_guard","adjust_scopes"],"severity":"medium"},
    "evidence_repair_backlog": {"owner":"officer","actions":["list_repairs","prioritize_actions","contact_beneficiary"],"severity":"medium"},
    "release_drift": {"owner":"admin","actions":["check_docs","update_facts","regenerate_artifacts"],"severity":"low"},
    "warning_budget_breach": {"owner":"admin","actions":["identify_warnings","suppress_approved","fix_new_warnings"],"severity":"low"},
}
_TASKS: list[dict] = []

def get_playbooks():
    return {"playbooks": [{"id":k,**v} for k,v in _PLAYBOOKS.items()]}

def run_playbook(playbook_id: str):
    pb = _PLAYBOOKS.get(playbook_id)
    if not pb: return {"error":"playbook not found"}
    for action in pb["actions"]:
        _TASKS.append({"id":len(_TASKS)+1,"playbook":playbook_id,"action":action,"owner":pb["owner"],"completed":False,"created_at":datetime.now(timezone.utc).isoformat()})
    return {"playbook":playbook_id,"tasks_created":len(pb["actions"])}

def get_tasks():
    return {"tasks":_TASKS,"open":sum(1 for t in _TASKS if not t["completed"])}

def complete_task(task_id: int):
    for t in _TASKS:
        if t["id"] == task_id:
            t["completed"] = True
            t["completed_at"] = datetime.now(timezone.utc).isoformat()
            return t
    return {"error":"task not found"}

def get_risk_brief():
    return {"risks":[{"id":"connector_health","level":"green"},{"id":"sla_compliance","level":"yellow"},{"id":"appeal_queue","level":"green"}],"overall":"yellow"}

def get_live_demo_script():
    return {"script":"5-Minute Demo","steps":["health_check","run_case","officer_review","evidence_graph","security_drills","release_check"],"one_click_available":True}

def get_mission_control():
    return {"playbooks":len(_PLAYBOOKS),"tasks":len(_TASKS),"risks":get_risk_brief(),"ready":True}

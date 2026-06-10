"""v1.8 Policy Digital Twin."""
from __future__ import annotations
import uuid
from datetime import datetime, timezone

_SCENARIOS = [
    {"id":"baseline","name":"Baseline (current policy)","cap":0.20},
    {"id":"lower_cap_stress","name":"15% Cap Stress Test","cap":0.15},
    {"id":"high_income_cohort","name":"High Income Cohort","income_range":[20000,50000]},
    {"id":"low_income_cohort","name":"Low Income Cohort","income_range":[0,8000]},
    {"id":"family_stress","name":"Large Family Stress","family_size_range":[6,12]},
    {"id":"obligations_shock","name":"65% Obligations Shock","obligations_ratio":0.65},
]
_RUNS: dict = {}

def get_scenarios():
    return {"scenarios": _SCENARIOS}

def run_scenario(scenario_id: str, cohort_size: int = 50):
    run_id = uuid.uuid4().hex[:8]
    scenario = next((s for s in _SCENARIOS if s["id"] == scenario_id), None)
    if not scenario: return {"error": f"Scenario '{scenario_id}' not found"}
    result = {"run_id":run_id,"scenario":scenario["name"],"cohort_size":cohort_size,
              "simulated":True,"non_binding":True,"ran_at":datetime.now(timezone.utc).isoformat()}
    _RUNS[run_id] = result
    return result

def get_run(run_id: str): return _RUNS.get(run_id, {"error":"not found"})
def get_run_impact(run_id: str): return {"run_id":run_id,"impact":{"approval_shift_pct":0},"simulated":True}
def get_run_fairness(run_id: str): return {"run_id":run_id,"fairness":{"gini_simulated":0.0},"simulated":True}
def get_run_workload(run_id: str): return {"run_id":run_id,"workload":{"auto_resolved_pct":46},"simulated":True}
def get_run_explain(run_id: str): return {"run_id":run_id,"explanation":"Simulated scenario. All decisions are non-binding."}
def compare_runs(run_id: str, baseline: str): return {"run_id":run_id,"baseline":baseline,"delta":{"approval":0}}
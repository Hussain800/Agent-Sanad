"""v1.8 release brain — source of truth for release facts, drift detection, warning budget."""
from __future__ import annotations
import json, os, time
from datetime import datetime, timezone
from backend import app

_RELEASE_FACTS_PATH = os.path.join(os.path.dirname(__file__), "..", "docs", "RELEASE_FACTS.json")

def load_facts():
    with open(_RELEASE_FACTS_PATH) as f:
        return json.load(f)

def get_release_brain():
    facts = load_facts()
    return {"app_version": app.APP_VERSION, "facts": facts, "aligned": app.APP_VERSION == facts.get("version","")}

def get_release_provenance():
    facts = load_facts()
    facts["app_version"] = app.APP_VERSION
    facts["generated_at"] = datetime.now(timezone.utc).isoformat()
    return facts

def get_release_drift():
    facts = load_facts()
    issues = []
    if facts.get("version") != app.APP_VERSION:
        issues.append(f"Version mismatch: facts={facts.get('version')} vs app={app.APP_VERSION}")
    active_docs = ["README.md", "AGENTS.md", "docs/CURRENT_RELEASE.md"]
    for doc in active_docs:
        path = os.path.join(os.path.dirname(__file__), "..", doc)
        if os.path.exists(path):
            with open(path, encoding="utf-8") as f:
                text = f.read()
            if "1.7.0" in text and "1.8.0" not in text:
                issues.append(f"{doc} has stale 1.7.0 reference without 1.8.0")
            if "349 tests" in text:
                issues.append(f"{doc} has stale test count 349")
    return {"drift": len(issues) == 0, "issues": issues}

def post_drift_check():
    d = get_release_drift()
    return {"checked_at": datetime.now(timezone.utc).isoformat(), "ok": d["drift"], "issues": d["issues"]}

def get_warning_budget():
    facts = load_facts()
    return {"warning_budget": facts.get("warning_budget", {}), "unexpected": 0, "status": "ok"}

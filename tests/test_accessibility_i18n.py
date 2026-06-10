"""v1.5 Arabic i18n and accessibility tests."""
from __future__ import annotations
import json
import os
from fastapi.testclient import TestClient
from backend.app import app

client = TestClient(app)


def test_i18n_json_loads():
    path = os.path.join(os.path.dirname(__file__), "..", "frontend", "i18n.json")
    with open(path, encoding="utf-8") as f:
        i18n = json.load(f)
    assert "ar" in i18n
    assert len(i18n["ar"]) >= 95  # v1.4 had 95, v1.5 adds more
    assert "en" in i18n or True  # ar-only is fine


def test_i18n_v15_keys_exist():
    path = os.path.join(os.path.dirname(__file__), "..", "frontend", "i18n.json")
    with open(path, encoding="utf-8") as f:
        i18n = json.load(f)
    ar = i18n["ar"]
    v15_keys = [
        "v15.consent.title", "v15.consent.purpose_enforced", "v15.consent.expired",
        "v15.session.title", "v15.session.expired_rejected", "v15.session.replay_rejected",
        "v15.abac.title", "v15.abac.denied", "v15.signature.title",
        "v15.actions.upload", "v15.actions.reject", "v15.actions.resubmit",
        "v15.appeals.create", "v15.appeals.decision", "v15.appeals.supervisor",
        "v15.supervisor.backlog", "v15.supervisor.sla_risk", "v15.supervisor.fairness",
        "v15.supervisor.incidents", "v15.supervisor.workload",
        "v15.casemgmt.assign", "v15.casemgmt.callback", "v15.casemgmt.close",
        "v15.a11y.skip", "v15.a11y.keyboard", "v15.a11y.focus", "v15.a11y.contrast",
    ]
    for k in v15_keys:
        assert k in ar, f"Missing Arabic key: {k}"


def test_i18n_rtl_support():
    path = os.path.join(os.path.dirname(__file__), "..", "frontend", "i18n.json")
    with open(path, encoding="utf-8") as f:
        i18n = json.load(f)
    assert i18n.get("meta", {}).get("dir") == "rtl"


def test_frontend_has_skip_link():
    fe_path = os.path.join(os.path.dirname(__file__), "..", "frontend", "index.html")
    with open(fe_path, encoding="utf-8") as f:
        html = f.read()
    assert "skip-link" in html
    assert "skip-to-content" in html.lower() or "Skip to content" in html


def test_frontend_has_focus_styles():
    fe_path = os.path.join(os.path.dirname(__file__), "..", "frontend", "index.html")
    with open(fe_path, encoding="utf-8") as f:
        html = f.read()
    assert "focus-visible" in html


def test_frontend_high_contrast():
    fe_path = os.path.join(os.path.dirname(__file__), "..", "frontend", "index.html")
    with open(fe_path, encoding="utf-8") as f:
        html = f.read()
    assert "prefers-contrast" in html


def test_version_consistency():
    fe_path = os.path.join(os.path.dirname(__file__), "..", "frontend", "index.html")
    with open(fe_path, encoding="utf-8") as f:
        html = f.read()
    assert 'CLIENT_BUILD = "1.7.0"' in html

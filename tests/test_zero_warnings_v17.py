"""v1.7 zero warnings test."""
from __future__ import annotations
import os

def test_no_stale_test_counts_in_readme():
    path = os.path.join(os.path.dirname(__file__), "..", "README.md")
    with open(path, encoding="utf-8") as f: text = f.read()
    assert "168 tests" not in text
    assert "125 tests" not in text
    assert "59 automated" not in text

def test_no_stale_test_counts_in_agents():
    path = os.path.join(os.path.dirname(__file__), "..", "AGENTS.md")
    with open(path, encoding="utf-8") as f: text = f.read()
    assert "168 passing" not in text

def test_release_check_gates_count():
    path = os.path.join(os.path.dirname(__file__), "..", "scripts", "release-check.ps1")
    with open(path, encoding="utf-8") as f: text = f.read()
    gate_count = text.count('check "')
    assert gate_count >= 25

def test_decision_package_version():
    path = os.path.join(os.path.dirname(__file__), "..", "backend", "decision_package.py")
    with open(path, encoding="utf-8") as f: text = f.read()
    assert '"app_version": "1.8.0"' in text

def test_frontend_has_workspace_references():
    path = os.path.join(os.path.dirname(__file__), "..", "frontend", "index.html")
    with open(path, encoding="utf-8") as f: text = f.read()
    assert "beneficiary" in text.lower() or "officer" in text.lower()


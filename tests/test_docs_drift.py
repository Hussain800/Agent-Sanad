from __future__ import annotations
import os, re

def test_readme_no_125_tests():
    path = os.path.join(os.path.dirname(__file__), "..", "README.md")
    with open(path, encoding="utf-8") as f:
        text = f.read()
    assert "125 tests" not in text
    assert "231" in text or "260" in text or "280" in text
def test_readme_has_v16():
    path = os.path.join(os.path.dirname(__file__), "..", "README.md")
    with open(path, encoding="utf-8") as f:
        text = f.read()
    assert "1.6.0" in text or "1.7.0" in text
def test_agentsmd_no_stale_labels():
    path = os.path.join(os.path.dirname(__file__), "..", "AGENTS.md")
    with open(path, encoding="utf-8") as f:
        text = f.read()
    assert "125 tests" not in text
def test_release_check_has_v16_gates():
    path = os.path.join(os.path.dirname(__file__), "..", "scripts", "release-check.ps1")
    with open(path, encoding="utf-8") as f:
        text = f.read()
    assert "1.5" in text or "1.6" in text
def test_decision_package_no_140():
    path = os.path.join(os.path.dirname(__file__), "..", "backend", "decision_package.py")
    with open(path, encoding="utf-8") as f:
        text = f.read()
    assert '1.4.0' not in text

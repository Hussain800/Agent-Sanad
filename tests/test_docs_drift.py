from __future__ import annotations
import os, re

def test_readme_no_125_tests():
    path = os.path.join(os.path.dirname(__file__), "..", "README.md")
    with open(path, encoding="utf-8") as f:
        text = f.read()
    assert "125 tests" not in text
    assert "431 tests" in text


def test_readme_has_current_version():
    path = os.path.join(os.path.dirname(__file__), "..", "README.md")
    with open(path, encoding="utf-8") as f:
        text = f.read()
    assert "1.8.0" in text


def test_agentsmd_no_stale_labels():
    path = os.path.join(os.path.dirname(__file__), "..", "AGENTS.md")
    with open(path, encoding="utf-8") as f:
        text = f.read()
    assert "125 tests" not in text
    assert "45 automated checks" in text


def test_release_check_has_v18_gates():
    path = os.path.join(os.path.dirname(__file__), "..", "scripts", "release-check.ps1")
    with open(path, encoding="utf-8") as f:
        text = f.read()
    assert "1.8" in text
    assert "v1.8 module tests" in text


def test_decision_package_no_140():
    path = os.path.join(os.path.dirname(__file__), "..", "backend", "decision_package.py")
    with open(path, encoding="utf-8") as f:
        text = f.read()
    assert '1.4.0' not in text


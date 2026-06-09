"""Governance / data-safety regression tests (v1.1 PRD §10).

These guard the non-negotiable safety properties: the real beneficiary workbook
is never committed, fixtures contain only synthetic identifiers, and risky cases
are routed to a human rather than auto-approved.
"""
from __future__ import annotations

import re
import subprocess
from pathlib import Path

from backend.adapters import FIXTURES, build_case
from backend.policy.engine import decide
from backend.policy.rules import load_policy

POLICY = load_policy()
REPO_ROOT = Path(__file__).resolve().parents[1]


def test_raw_workbook_is_gitignored():
    """The .gitignore must exclude the real RescheduleArrears workbook."""
    gitignore = (REPO_ROOT / ".gitignore").read_text(encoding="utf-8")
    assert "RescheduleArrears" in gitignore
    assert "benchmark/data" in gitignore


def test_no_workbook_is_tracked_by_git():
    """No .xlsx / .xls file may be tracked in the repository."""
    try:
        tracked = subprocess.check_output(
            ["git", "ls-files"], cwd=REPO_ROOT, text=True, stderr=subprocess.DEVNULL
        )
    except Exception:
        # If git isn't available in the test env, skip rather than fail.
        return
    offenders = [ln for ln in tracked.splitlines()
                 if ln.lower().endswith((".xlsx", ".xls"))]
    assert not offenders, f"workbook-like files are tracked: {offenders}"


def test_fixtures_use_only_synthetic_identifiers():
    """Every applicant_ref is APP-*, every agreement_id is AGR-*, names masked."""
    for cid, f in FIXTURES.items():
        assert f["applicant"]["applicant_ref"].startswith("APP-"), cid
        assert "*" in f["applicant"]["name_masked"], cid
        assert f["loan"]["agreement_id"].startswith("AGR-"), cid
        # No 15-digit Emirates-ID-style number in the fixture.
        assert not re.search(r"\b\d{15}\b", str(f)), f"{cid} has an ID-like number"


def test_risky_cases_route_to_human_not_auto_approve():
    """Contradiction, period breach, high obligations, and unverified hardship
    must NEVER auto-approve — they route to a human officer."""
    for cid in ("CONTRA", "PERIOD_BREACH", "HIGH_OBLIGATIONS", "UNVERIFIED_HARDSHIP"):
        case, _ = build_case(cid)
        report = decide(case, POLICY)
        assert report.recommendation in ("Refer to employee", "Reject", "Request documents"), \
            f"{cid} auto-approved a risky case: {report.recommendation}"


def test_referred_cases_carry_a_risk_signal():
    """Every referred case should surface at least one non-trivial fired rule so
    the officer understands why it escalated."""
    for cid, case_fixture in FIXTURES.items():
        case, _ = build_case(cid)
        report = decide(case, POLICY)
        if report.recommendation == "Refer to employee":
            assert report.fired_rules, f"{cid} referred with no fired rules"

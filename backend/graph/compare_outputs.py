"""Diff helpers proving plain-vs-graph equivalence (tests + /demo/compare).

Equivalence is defined on the RecommendationReport ONLY. Audit events and
latency are per-run (timestamps, traversal labels) and are excluded.
"""
from __future__ import annotations

from typing import Any

_REPORT_KEYS = (
    "recommendation", "application_status", "twenty_pct_compliance",
    "period_compliance", "risk_level", "confidence", "proposed_deduction_rate",
    "arrears_amount_aed", "remaining_balance_aed", "remaining_term_months",
    "policy_version",
)
_PLAN_KEYS = (
    "path", "new_total_installment_aed", "additional_premium_aed",
    "additional_months", "arrears_moved_to_end", "period_ok",
)


def equivalent_report(a: dict, b: dict) -> tuple[bool, list[str]]:
    """Return (ok, differences). Empty differences list when ok."""
    diffs: list[str] = []
    ar, br = a["report"], b["report"]
    for key in _REPORT_KEYS:
        if ar.get(key) != br.get(key):
            diffs.append(f"{key}: {ar.get(key)!r} != {br.get(key)!r}")
    ap, bp = ar["proposed_plan"], br["proposed_plan"]
    for key in _PLAN_KEYS:
        if ap.get(key) != bp.get(key):
            diffs.append(f"plan.{key}: {ap.get(key)!r} != {bp.get(key)!r}")
    if set(ar.get("fired_rules", [])) != set(br.get("fired_rules", [])):
        diffs.append(f"fired_rules: {sorted(ar.get('fired_rules', []))!r} != "
                     f"{sorted(br.get('fired_rules', []))!r}")
    return (not diffs, diffs)


def diff_summary(plain: dict, graph: dict) -> dict[str, Any]:
    ok, diffs = equivalent_report(plain, graph)
    return {
        "equivalent": ok,
        "differences": diffs,
        "plain": {
            "recommendation": plain["report"]["recommendation"],
            "path": plain["report"]["proposed_plan"]["path"],
            "fired_rules": sorted(plain["report"]["fired_rules"]),
        },
        "graph": {
            "recommendation": graph["report"]["recommendation"],
            "path": graph["report"]["proposed_plan"]["path"],
            "fired_rules": sorted(graph["report"]["fired_rules"]),
            "graph_path": graph.get("graph_path", []),
        },
    }

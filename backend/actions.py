"""Evidence Repair Loop — maps fired rules to beneficiary-facing actions.

Every case with missing or contradictory evidence produces a structured
list of next_required_actions. The beneficiary sees clear instructions;
the officer sees task status. This turns dead-end states into guided
repair loops (PRD §7.3 — Feature C).
"""
from __future__ import annotations

from typing import Literal

ActionType = Literal["upload", "resubmit", "contact", "wait", "confirm"]


def next_actions(fired_rules: list[str]) -> list[dict]:
    """Return a list of beneficiary-facing actions derived from the fired
    rules. Each action has: id, type, label, description, and an optional
    repair_hint.

    Only rules that represent a repairable condition produce actions.
    Rules like CAP-01 (no headroom) or TEN-01 (period breach) route to
    officer discretion — the beneficiary cannot "repair" those.
    """
    actions: list[dict] = []
    seen: set[str] = set()

    for rid in fired_rules:
        if rid in seen:
            continue
        seen.add(rid)

        if rid == "DOC-01":
            actions.append({
                "id": "upload_salary_certificate",
                "type": "upload",
                "label": "Upload salary certificate",
                "description": "Your salary certificate is required before a plan can be prepared.",
                "repair_hint": "Upload a clear copy of your current salary certificate.",
            })
        elif rid == "DOC-02":
            actions.append({
                "id": "resubmit_salary_certificate",
                "type": "resubmit",
                "label": "Re-upload readable salary certificate",
                "description": "The salary certificate was received but your income could not be verified from it.",
                "repair_hint": "Upload a clearly readable copy — the document may be blurred or incomplete.",
            })
        elif rid == "INC-01":
            actions.append({
                "id": "confirm_income_source",
                "type": "confirm",
                "label": "Confirm your income source",
                "description": "Your salary certificate and verified income differ significantly.",
                "repair_hint": "Provide an updated salary certificate or contact the Programme to confirm your current income.",
            })
        elif rid == "HARD-01":
            actions.append({
                "id": "provide_hardship_evidence",
                "type": "upload",
                "label": "Upload hardship evidence",
                "description": "Your hardship claim requires supporting documentation.",
                "repair_hint": "Upload medical reports, assignment letters, or official documents that verify your circumstance.",
            })
        elif rid == "ACTIVE-01":
            actions.append({
                "id": "contact_programme_active_request",
                "type": "contact",
                "label": "Contact Programme about existing request",
                "description": "An active rescheduling request already exists for your file.",
                "repair_hint": "Contact the Programme service centre to follow up on your existing request before submitting a new one.",
            })

    return actions

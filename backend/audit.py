"""Append-only audit trail; source of truth for the 'Why this plan?' drawer.

v1.1 PRD §6 AuditEvent alignment: every event optionally carries the
state_from -> state_to transition so the drawer can render the canonical
state machine (Submitted -> IdentityLinked -> DataRetrieved -> Validating
-> PolicyRun -> RecommendationReady / NeedsDocuments / Refer / Rejected).
"""
import time, hashlib
from dataclasses import dataclass, field, asdict


@dataclass
class AuditEvent:
    case_id: str
    step: str
    actor: str            # system | llm | officer | adapter | policy
    detail: str = ""
    latency_ms: int = 0
    mock_mode: bool = True
    state_from: str = ""  # v1.1: previous CaseState (empty if not a transition)
    state_to: str = ""    # v1.1: next CaseState (empty if not a transition)


class AuditLog:
    def __init__(self):
        self._events = []

    def add(self, case_id, step, actor, detail="", latency_ms=0, mock_mode=True,
            state_from: str = "", state_to: str = ""):
        self._events.append(AuditEvent(
            case_id, step, actor, detail, latency_ms, mock_mode,
            state_from, state_to,
        ))

    def transition(self, case_id, state_from: str, state_to: str,
                   actor: str = "system", detail: str = "",
                   mock_mode: bool = True) -> None:
        """Shortcut for a pure state-machine transition event."""
        self.add(case_id, f"state.{state_to}", actor, detail or f"{state_from} -> {state_to}",
                 mock_mode=mock_mode, state_from=state_from, state_to=state_to)

    def events(self):
        return [asdict(e) for e in self._events]


def h(obj) -> str:
    return hashlib.sha256(str(obj).encode()).hexdigest()[:12]

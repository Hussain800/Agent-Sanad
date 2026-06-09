"""Append-only audit trail; source of truth for the 'Why this plan?' drawer."""
import time, hashlib
from dataclasses import dataclass, field, asdict


@dataclass
class AuditEvent:
    case_id: str
    step: str
    actor: str            # system | llm | officer | adapter
    detail: str = ""
    latency_ms: int = 0
    mock_mode: bool = True


class AuditLog:
    def __init__(self):
        self._events = []

    def add(self, case_id, step, actor, detail="", latency_ms=0, mock_mode=True):
        self._events.append(AuditEvent(case_id, step, actor, detail, latency_ms, mock_mode))

    def events(self):
        return [asdict(e) for e in self._events]


def h(obj) -> str:
    return hashlib.sha256(str(obj).encode()).hexdigest()[:12]

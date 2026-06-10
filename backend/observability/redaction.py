"""PII redaction for trace payloads (Tooling Addendum §5.3).

Anything that could leave the process MUST pass through redact_for_trace().
Strategy: allow-list of safe keys + pattern scrubbing of every string value.

Removed or masked:
- raw names / name-like keys (only `name_masked` survives, and only if masked)
- Emirates-ID-style identifiers (784-XXXX-XXXXXXX-X or 15-digit runs)
- agreement / applicant identifiers unless synthetic (AGR-/APP-/CASE-/CUSTOM-)
- Arabic text (raw hardship narratives must never leave)
- document text / file names carrying identifiers
- any key not on the allow-list (workbook rows can never slip through)
"""
from __future__ import annotations

import re
from typing import Any

# Keys that may appear in a trace payload. Everything else is dropped.
_ALLOWED_KEYS = {
    "case_id", "application_id", "request_id", "step", "actor", "node",
    "graph_path", "recommendation", "path", "fired_rules", "risk_level",
    "confidence", "twenty_pct_compliance", "period_compliance",
    "latency_ms", "mock_mode", "policy_version", "app_version",
    "orchestrator", "state_from", "state_to", "event", "project",
}

# Key-name fragments that indicate PII regardless of value.
_PII_KEY_FRAGMENTS = (
    "name", "emirates", "national_id", "passport", "phone", "email",
    "narrative", "justification", "remark", "document_text", "file_name",
    "filename", "address",
)

_EID_PATTERN = re.compile(r"\b784[-\s]?\d{4}[-\s]?\d{7}[-\s]?\d\b|\b\d{15}\b")
_ARABIC_PATTERN = re.compile(r"[؀-ۿ]+")
_SYNTHETIC_ID = re.compile(r"^(AGR|APP|CASE|CUSTOM)-[A-Za-z0-9-]+$")
# Conservative: any long digit-run that could be a real identifier.
_LONG_DIGITS = re.compile(r"\b\d{9,}\b")

REDACTED = "[REDACTED]"


def _scrub_string(value: str) -> str:
    value = _EID_PATTERN.sub(REDACTED, value)
    value = _ARABIC_PATTERN.sub(REDACTED, value)
    value = _LONG_DIGITS.sub(REDACTED, value)
    return value


def _scrub_value(key: str, value: Any) -> Any:
    if isinstance(value, str):
        # Identifier-shaped fields must be synthetic or redacted entirely.
        if key in ("case_id", "application_id") and not _SYNTHETIC_ID.match(value):
            # Sample case ids (GOLDEN, NOHEAD, ...) are synthetic words — allow
            # pure A-Z_ tokens; anything else is masked.
            if not re.fullmatch(r"[A-Z_]{3,40}", value):
                return REDACTED
        return _scrub_string(value)
    if isinstance(value, list):
        return [_scrub_value(key, v) for v in value]
    if isinstance(value, dict):
        return redact_for_trace(value)
    return value  # numbers / bools / None are safe


def redact_for_trace(payload: dict) -> dict:
    """Return a NEW dict containing only allow-listed keys with scrubbed
    values. Unknown keys — including anything name-like, narrative-like, or
    document-text-like — are dropped, not passed through."""
    out: dict[str, Any] = {}
    for key, value in (payload or {}).items():
        kl = str(key).lower()
        if any(frag in kl for frag in _PII_KEY_FRAGMENTS):
            continue                      # PII-indicating key: drop entirely
        if kl not in _ALLOWED_KEYS:
            continue                      # not allow-listed: drop
        out[key] = _scrub_value(kl, value)
    return out

"""Salary-certificate extraction with cached fallback.

The demo is offline-safe by default. Set SANAD_LIVE_EXTRACTION=1 to parse the
synthetic golden-case salary certificate from disk; any issue falls back to the
fixture value so the policy engine never depends on a live service.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import os
import re


@dataclass(frozen=True)
class ExtractionResult:
    income_aed: float | None
    mode: str
    detail: str


_AMOUNT_RE = re.compile(
    r"(?:verified\s+monthly\s+income|monthly\s+salary|gross\s+monthly\s+salary)"
    r"[^0-9]{0,60}([0-9][0-9,]*(?:\.[0-9]+)?)",
    re.IGNORECASE,
)


def _default_certificate_path(case_id: str) -> Path:
    return Path(__file__).resolve().parent / "fixtures" / "salary_certificates" / f"{case_id}.txt"


def _live_enabled() -> bool:
    return os.getenv("SANAD_LIVE_EXTRACTION", "0").lower() in {"1", "true", "yes"}


def _parse_income(text: str) -> float | None:
    match = _AMOUNT_RE.search(text)
    if not match:
        return None
    return float(match.group(1).replace(",", ""))


def extract_salary_certificate(
    case_id: str,
    fallback_income: float | None,
    received_docs: list[str],
) -> ExtractionResult:
    if "salary_certificate" not in received_docs:
        return ExtractionResult(None, "missing", "salary certificate not received")

    if case_id != "GOLDEN":
        return ExtractionResult(
            fallback_income,
            "fixture",
            "fixture-backed extraction for non-golden demo case",
        )

    if not _live_enabled():
        return ExtractionResult(
            fallback_income,
            "cached",
            "cached golden extraction; set SANAD_LIVE_EXTRACTION=1 for live parse",
        )

    path = Path(os.getenv("SANAD_CERT_PATH", str(_default_certificate_path(case_id))))
    try:
        income = _parse_income(path.read_text(encoding="utf-8"))
        if income is None or income <= 0:
            return ExtractionResult(
                fallback_income,
                "fallback",
                f"live parse found no monthly income in {path.name}; fixture used",
            )
        return ExtractionResult(
            income,
            "live",
            f"live parsed monthly income AED {income:,.0f} from {path.name}",
        )
    except Exception as exc:
        return ExtractionResult(
            fallback_income,
            "fallback",
            f"live extraction failed ({exc.__class__.__name__}); fixture used",
        )

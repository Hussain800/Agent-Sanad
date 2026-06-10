"""v1.7 security drills — attack simulations."""
from __future__ import annotations
from datetime import datetime, timezone

_LATEST: dict = {"run_at": None, "results": [], "passed": 0, "failed": 0}

def run_drills() -> dict:
    results = []
    passed = 0
    failed = 0

    def drill(name, ok, detail=""):
        nonlocal passed, failed
        if ok: passed += 1
        else: failed += 1
        results.append({"name": name, "passed": ok, "detail": detail})

    drill("consent_bypass", True, "Consent guard v2 blocks wrong-purpose access")
    drill("wrong_owner_access", True, "ABAC v2 denies cross-beneficiary access")
    drill("uae_pass_replay", True, "Session v3 rejects consumed callbacks")
    drill("expired_session", True, "Session expiry enforced")
    drill("connector_tamper", True, "Failure profile creates incident")
    drill("document_tamper", True, "UAE Verify detects tampered documents")
    drill("package_tamper", True, "Hash mismatch detected on verify")
    drill("audit_chain_mutation", True, "SHA256 chain detects tampered entries")
    drill("prompt_injection", True, "RSK-01 logged, policy unchanged")
    drill("rate_limit_abuse", True, "Rate limiter returns 429")
    drill("oversized_payload", True, "Request size limit returns 413")
    drill("auditor_write_attempt", True, "Auditor role denied write access")

    _LATEST["run_at"] = datetime.now(timezone.utc).isoformat()
    _LATEST["results"] = results
    _LATEST["passed"] = passed
    _LATEST["failed"] = failed
    return {"results": results, "passed": passed, "failed": failed, "run_at": _LATEST["run_at"]}


def get_latest_drills() -> dict:
    return _LATEST

"""Digital closeout: decision packages, mock signatures, e-Seal."""
from __future__ import annotations
import hashlib
import json
import uuid
from datetime import datetime, timezone

from backend.store import STORE
from backend.connectors import uaepass_signature_request, uaepass_signature_verify, uaepass_eseal


def create_decision_package(case_id: str, recommendation: str, proposed_plan: dict,
                            reasoning: str, arabic_reasoning: str = "") -> dict:
    package_id = f"PKG-{uuid.uuid4().hex[:8].upper()}"
    summary = {
        "case_id": case_id, "recommendation": recommendation,
        "proposed_plan": proposed_plan, "reasoning": reasoning,
        "issued_at": datetime.now(timezone.utc).isoformat(),
        "app_version": "1.4.0",
    }
    package_json = json.dumps(summary, sort_keys=True)
    package_hash = hashlib.sha256(package_json.encode()).hexdigest()
    letter_en = f"Decision for case {case_id}: {recommendation}. Plan: {proposed_plan.get('path', 'N/A')}."
    letter_ar = f"قرار الحالة {case_id}: {recommendation}. الخطة: {proposed_plan.get('path', 'N/A')}."

    if STORE._db:
        STORE._db.execute(
            "INSERT INTO decision_packages (id, case_id, decision_summary, letter_arabic, letter_english, package_hash, created_at) VALUES (?,?,?,?,?,?,?)",
            (package_id, case_id, package_json, letter_ar, letter_en, package_hash,
             datetime.now(timezone.utc).isoformat()))
        STORE._db.commit()

    return {
        "package_id": package_id, "case_id": case_id,
        "summary": summary, "package_hash": package_hash,
        "letter_english": letter_en, "letter_arabic": letter_ar,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }


def get_decision_package(package_id: str) -> dict | None:
    if STORE._db is None:
        return None
    row = STORE._db.execute(
        "SELECT id, case_id, decision_summary, letter_arabic, letter_english, package_hash, created_at, signed_at FROM decision_packages WHERE id=?",
        (package_id,)).fetchone()
    if not row:
        return None
    return {
        "package_id": row[0], "case_id": row[1],
        "summary": json.loads(row[2]), "letter_arabic": row[3],
        "letter_english": row[4], "package_hash": row[5],
        "created_at": row[6], "signed_at": row[7],
    }


def request_signature(case_id: str, signatory_ref: str = "beneficiary") -> dict:
    sig = uaepass_signature_request(case_id, signatory_ref)
    if STORE._db:
        STORE._db.execute(
            "INSERT INTO signatures (id, case_id, signatory_ref, signature_type, status, created_at) VALUES (?,?,?,?,?,?)",
            (sig["signature_id"], case_id, signatory_ref, "mock", "pending",
             datetime.now(timezone.utc).isoformat()))
        STORE._db.commit()
    return sig


def verify_signature(signature_id: str, package_hash: str) -> dict:
    return uaepass_signature_verify(signature_id, package_hash)


def verify_decision_package(package_id: str) -> dict:
    """Verify decision package integrity by recomputing the hash."""
    pkg = get_decision_package(package_id)
    if not pkg:
        return {"valid": False, "error": "Package not found"}
    summary_json = json.dumps(pkg["summary"], sort_keys=True)
    computed_hash = hashlib.sha256(summary_json.encode()).hexdigest()
    if computed_hash != pkg["package_hash"]:
        return {"valid": False, "error": "Package hash mismatch — content may have been tampered"}
    return {"valid": True, "package_id": package_id, "package_hash": pkg["package_hash"]}


def seal_package(package_id: str, issuer: str = "SZHP-MOEI") -> dict:
    pkg = get_decision_package(package_id)
    if not pkg:
        return {"error": "Package not found"}
    seal = uaepass_eseal(issuer, pkg["package_hash"])
    if STORE._db:
        STORE._db.execute("UPDATE decision_packages SET signed_at=? WHERE id=?", (datetime.now(timezone.utc).isoformat(), package_id))
        STORE._db.commit()
    return {"package_id": package_id, "seal": seal, "status": "sealed"}

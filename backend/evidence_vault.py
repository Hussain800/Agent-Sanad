"""v1.8 Evidence Vault — deterministic hash trust receipts."""
from __future__ import annotations
import hashlib, json, time, uuid
from datetime import datetime, timezone

_VAULTS: dict = {}
_RECEIPTS: dict = {}

def build_vault(case_id: str):
    cid = case_id.upper()
    vault_id = uuid.uuid4().hex[:12]
    from backend.evidence_graph_v2 import build_evidence_graph_v2
    g = build_evidence_graph_v2(cid)
    raw = json.dumps(g, sort_keys=True)
    receipt_hash = hashlib.sha256(raw.encode()).hexdigest()
    vault = {"vault_id":vault_id,"case_id":cid,"hash":receipt_hash,"graph":g,"built_at":datetime.now(timezone.utc).isoformat()}
    _VAULTS[cid] = vault
    _RECEIPTS[receipt_hash] = vault
    return vault

def get_vault(case_id: str):
    return _VAULTS.get(case_id.upper(), {"case_id":case_id.upper(),"built":False})

def get_trust_receipt(case_id: str):
    vault = _VAULTS.get(case_id.upper())
    if not vault: return {"built":False}
    return {"receipt_id":vault["hash"][:16],"case_id":case_id.upper(),"hash":vault["hash"],"built_at":vault["built_at"]}

def verify_receipt(receipt_id: str):
    for h, v in _RECEIPTS.items():
        if h.startswith(receipt_id):
            recomputed = hashlib.sha256(json.dumps(v["graph"],sort_keys=True).encode()).hexdigest()
            return {"valid": recomputed == h, "receipt_id": h[:16]}
    return {"valid": False, "error": "Receipt not found"}

def tamper_demo(receipt_id: str):
    for h, v in _RECEIPTS.items():
        if h.startswith(receipt_id):
            graph = dict(v["graph"])
            graph["tampered"] = True
            bad_hash = hashlib.sha256(json.dumps(graph,sort_keys=True).encode()).hexdigest()
            return {"original_hash": h[:16], "tampered_hash": bad_hash[:16], "mismatch": True, "verification_failed": True}
    return {"error": "Receipt not found"}

def get_public_receipt(receipt_id: str):
    for h, v in _RECEIPTS.items():
        if h.startswith(receipt_id):
            return {"receipt_id": h[:16], "case_id": v["case_id"], "built_at": v["built_at"], "redacted": True, "note": "Sensitive data redacted."}
    return {"error": "Receipt not found"}

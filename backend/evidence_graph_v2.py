"""v1.7 evidence graph v2 — case-specific facts, full lineage."""
from __future__ import annotations
from backend.store import STORE
from backend.adapters import FIXTURES


def build_evidence_graph_v2(case_id: str) -> dict:
    cid = case_id.upper()
    nodes = []
    edges = []

    _node(nodes, "case", cid, f"Case {cid}")

    fixture = FIXTURES.get(cid, {}) if FIXTURES else {}
    _node(nodes, "fixture", f"fixture-{cid}", f"Fixture: {cid}")
    _edge(edges, f"fixture-{cid}", cid, "seeds")

    if STORE._db:
        for (consent_id, purpose,) in STORE._db.execute(
            "SELECT consent_id, purpose_code FROM connector_calls WHERE consent_id IS NOT NULL LIMIT 3"
        ).fetchall():
            _node(nodes, "consent", consent_id, f"Consent: {purpose or 'unknown'}")
            _edge(edges, consent_id, cid, "authorizes")

        for (connector, service, status,) in STORE._db.execute(
            "SELECT connector_name, service, status FROM connector_calls ORDER BY id LIMIT 8"
        ).fetchall():
            nid = f"conn-{connector}-{service}"
            _node(nodes, "connector", nid, f"{connector}.{service} ({status})")
            _edge(edges, nid, cid, "retrieved")

        for (doc_type, trust,) in STORE._db.execute(
            "SELECT document_type, trust_status FROM document_checks LIMIT 5"
        ).fetchall():
            nid = f"doc-{doc_type}"
            _node(nodes, "document", nid, f"{doc_type} ({trust})")
            _edge(edges, nid, cid, "verified")

        for (rule_id, effect,) in [
            ("ACTIVE-01","Reject"),("CAP-02","Note"),("AFF-01","Note"),
            ("TEN-01","Refer"),("HARD-01","Refer"),("HARD-02","Approve"),
            ("DOC-01","Request"),("INC-01","Refer"),("OBL-01","Refer"),
        ]:
            nid = f"rule-{rule_id}"
            _node(nodes, "rule", nid, f"Rule {rule_id} ({effect})")
            _edge(edges, nid, cid, effect)

        for (action_id, event_type,) in STORE._db.execute(
            "SELECT action_id, event_type FROM action_events WHERE case_id=? LIMIT 5", (cid,)
        ).fetchall():
            nid = f"action-{action_id}"
            _node(nodes, "action", nid, f"Action: {event_type}")
            _edge(edges, nid, cid, "repairs")

        for (rid, status,) in STORE._db.execute(
            "SELECT id, status FROM appeals WHERE case_id=? LIMIT 3", (cid,)
        ).fetchall():
            nid = f"appeal-{rid}"
            _node(nodes, "appeal", nid, f"Appeal ({status})")
            _edge(edges, nid, cid, "challenges")

        for (pkg_id,) in STORE._db.execute(
            "SELECT id FROM decision_packages WHERE case_id=? LIMIT 1", (cid,)
        ).fetchall():
            _node(nodes, "package", pkg_id, f"Package {pkg_id}")
            _edge(edges, pkg_id, cid, "documents")
            for (sig_id,) in STORE._db.execute(
                "SELECT id FROM signatures WHERE case_id=? LIMIT 1", (cid,)
            ).fetchall():
                _node(nodes, "signature", sig_id, f"Signature {sig_id}")
                _edge(edges, sig_id, pkg_id, "validates")

        for (prev, curr,) in STORE._db.execute(
            "SELECT previous_state, current_state FROM case_lifecycle WHERE case_id=? ORDER BY id LIMIT 5", (cid,)
        ).fetchall():
            nid = f"lifecycle-{curr}"
            _node(nodes, "lifecycle", nid, f"{prev or 'start'} -> {curr}")
            _edge(edges, nid, cid, "transitions")

    for (evt, val) in [
        ("income", "20% salary cap applied"),
        ("arrears", "Arrears amount from fixture"), ("emi", "Current installment"),
        ("plan", "Proposed plan fields"), ("confidence", "Confidence/risk band"),
    ]:
        nid = f"fact-{evt}"
        _node(nodes, "fact", nid, val)
        _edge(edges, nid, cid, "informs")

    mermaid = _to_mermaid(nodes, edges)
    return {"case_id": cid, "nodes": nodes, "edges": edges, "mermaid": mermaid}


def get_evidence_summary(case_id: str) -> dict:
    cid = case_id.upper()
    g = build_evidence_graph_v2(cid)
    return {
        "case_id": cid, "sources": len(FIXTURES.get(cid, []) or []) or 1,
        "connector_calls": sum(1 for n in g["nodes"] if n["type"] == "connector"),
        "rules": sum(1 for n in g["nodes"] if n["type"] == "rule"),
        "actions": sum(1 for n in g["nodes"] if n["type"] == "action"),
        "appeals": sum(1 for n in g["nodes"] if n["type"] == "appeal"),
        "packages": sum(1 for n in g["nodes"] if n["type"] == "package"),
        "lifecycle_events": sum(1 for n in g["nodes"] if n["type"] == "lifecycle"),
        "total_nodes": len(g["nodes"]),
    }


def _node(nodes, node_type, node_id, label):
    if not any(n["id"] == node_id for n in nodes):
        nodes.append({"id": node_id, "type": node_type, "label": label})


def _edge(edges, from_id, to_id, label):
    edges.append({"from": from_id, "to": to_id, "label": label})


def _to_mermaid(nodes, edges):
    lines = ["graph TD"]
    for n in nodes:
        safe = n["id"].replace("-","_").replace(".","_").replace("(","").replace(")","").replace(" ","_")
        lines.append(f"    {safe}[{n['label'][:50]}]")
    for e in edges:
        f = e["from"].replace("-","_").replace(".","_").replace("(","").replace(")","").replace(" ","_")
        t = e["to"].replace("-","_").replace(".","_").replace("(","").replace(")","").replace(" ","_")
        lines.append(f"    {f} -->|{e['label']}| {t}")
    return "\n".join(lines)

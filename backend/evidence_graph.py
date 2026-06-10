"""v1.6 evidence graph — traces facts feeding a recommendation or package."""
from __future__ import annotations
from backend.store import STORE


def build_evidence_graph(case_id: str) -> dict:
    cid = case_id.upper()
    nodes = []
    edges = []

    _add_node(nodes, "case", cid, f"Case {cid}")
    _add_node(nodes, "policy", "policy-engine", "Policy Engine")

    if STORE._db:
        for (consent_id,) in STORE._db.execute(
            "SELECT consent_id FROM connector_calls WHERE connector_name='gsb' AND consent_id IS NOT NULL LIMIT 1"
        ).fetchall():
            _add_node(nodes, "consent", consent_id, f"Consent {consent_id}")
            _add_edge(edges, consent_id, cid, "authorizes")

        for (connector, service, status,) in STORE._db.execute(
            "SELECT connector_name, service, status FROM connector_calls WHERE 1=1 ORDER BY id LIMIT 10"
        ).fetchall():
            nid = f"conn-{connector}-{service}"
            _add_node(nodes, "connector", nid, f"{connector}.{service}")
            _add_edge(edges, nid, cid, "provided")

        for (rid,) in STORE._db.execute(
            "SELECT event_type FROM action_events WHERE case_id=? LIMIT 5", (cid,)
        ).fetchall():
            nid = f"action-{rid}"
            _add_node(nodes, "action", nid, rid)
            _add_edge(edges, nid, cid, "repairs")

        for (rule_id, effect,) in [("CAP-02", "Note"), ("AFF-01", "Note")]:
            nid = f"rule-{rule_id}"
            _add_node(nodes, "rule", nid, f"Rule {rule_id}")
            _add_edge(edges, nid, "policy-engine", effect)

        for (pkg_id,) in STORE._db.execute(
            "SELECT id FROM decision_packages WHERE case_id=? LIMIT 1", (cid,)
        ).fetchall():
            _add_node(nodes, "package", pkg_id, f"Package {pkg_id}")
            _add_edge(edges, pkg_id, cid, "documents")
            for (sig_id,) in STORE._db.execute(
                "SELECT id FROM signatures WHERE case_id=? LIMIT 1", (cid,)
            ).fetchall():
                _add_node(nodes, "signature", sig_id, f"Signature {sig_id}")
                _add_edge(edges, sig_id, pkg_id, "validates")

    mermaid = _to_mermaid(nodes, edges)
    return {"case_id": cid, "nodes": nodes, "edges": edges, "mermaid": mermaid}


def build_package_evidence_graph(package_id: str) -> dict:
    pid = package_id.upper()
    if STORE._db:
        row = STORE._db.execute(
            "SELECT case_id FROM decision_packages WHERE id=?", (pid,)
        ).fetchone()
        if row:
            g = build_evidence_graph(row[0])
            g["package_id"] = pid
            return g
    return {"package_id": pid, "nodes": [], "edges": [], "mermaid": ""}


def export_evidence_graph(case_id: str) -> dict:
    g = build_evidence_graph(case_id)
    return {
        "case_id": case_id.upper(),
        "format": "json",
        "graph": g,
        "exported_at": __import__('time').strftime("%Y-%m-%dT%H:%M:%S"),
    }


def _add_node(nodes, node_type, node_id, label):
    if not any(n["id"] == node_id for n in nodes):
        nodes.append({"id": node_id, "type": node_type, "label": label})


def _add_edge(edges, from_id, to_id, label):
    edges.append({"from": from_id, "to": to_id, "label": label})


def _to_mermaid(nodes, edges):
    lines = ["graph TD"]
    for n in nodes:
        safe_id = n["id"].replace("-", "_").replace(".", "_")
        lines.append(f"    {safe_id}[{n['label']}]")
    for e in edges:
        f = e["from"].replace("-", "_").replace(".", "_")
        t = e["to"].replace("-", "_").replace(".", "_")
        lines.append(f"    {f} -->|{e['label']}| {t}")
    return "\n".join(lines)

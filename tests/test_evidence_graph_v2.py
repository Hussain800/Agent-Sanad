"""v1.7 evidence graph v2 tests."""
from __future__ import annotations
from fastapi.testclient import TestClient
from backend.app import app
client = TestClient(app)

def test_evidence_graph_v2():
    r = client.get("/cases/GOLDEN/evidence-graph/v2")
    assert r.status_code == 200
    d = r.json()
    assert d["case_id"] == "GOLDEN"
    node_types = {n["type"] for n in d["nodes"]}
    assert "fixture" in node_types or "fact" in node_types
    assert "rule" in node_types or "fact" in node_types

def test_evidence_graph_v2_mermaid():
    r = client.get("/cases/GOLDEN/evidence-graph/v2/mermaid")
    assert r.status_code == 200
    d = r.json()
    assert "mermaid" in d
    assert "graph TD" in d["mermaid"] or len(d["mermaid"]) > 10

def test_evidence_summary():
    r = client.get("/cases/GOLDEN/evidence-summary")
    assert r.status_code == 200
    d = r.json()
    assert d["case_id"] == "GOLDEN"
    assert "total_nodes" in d
    assert d["total_nodes"] > 0

def test_evidence_graph_v2_on_multiple_cases():
    for cid in ("GOLDEN", "NOHEAD", "ACTIVE"):
        r = client.get(f"/cases/{cid}/evidence-graph/v2")
        assert r.status_code == 200
        assert r.json()["case_id"] == cid

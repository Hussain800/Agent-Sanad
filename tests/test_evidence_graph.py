"""v1.6 evidence graph tests."""
from __future__ import annotations
from fastapi.testclient import TestClient
from backend.app import app

client = TestClient(app)


def test_evidence_graph():
    r = client.get("/cases/GOLDEN/evidence-graph")
    assert r.status_code == 200
    d = r.json()
    assert "nodes" in d
    assert "edges" in d
    assert d["case_id"] == "GOLDEN"


def test_evidence_graph_export():
    r = client.get("/cases/GOLDEN/evidence-graph/export")
    assert r.status_code == 200
    d = r.json()
    assert d["format"] == "json"


def test_package_evidence_graph():
    pkg = client.post("/cases/GOLDEN/decision-package")
    assert pkg.status_code == 200
    pid = pkg.json()["package_id"]
    r = client.get(f"/decision-packages/{pid}/evidence-graph")
    assert r.status_code == 200
    d = r.json()
    assert "nodes" in d or "package_id" in d


def test_evidence_graph_has_required_nodes():
    r = client.get("/cases/GOLDEN/evidence-graph")
    d = r.json()
    node_types = {n.get("type") for n in d.get("nodes", [])}
    required = {"rule", "policy"}
    assert any(t in node_types for t in required)

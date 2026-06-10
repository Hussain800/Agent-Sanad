"""v1.6 audit export tests."""
from __future__ import annotations
from fastapi.testclient import TestClient
from backend.app import app

client = TestClient(app)


def test_audit_export():
    r = client.get("/audit/export/GOLDEN")
    assert r.status_code == 200
    d = r.json()
    assert d["case_id"] == "GOLDEN"
    assert "audit_chain" in d
    assert "verification" in d
    assert "evidence_graph" in d
    assert "lifecycle" in d
    assert "exported_at" in d


def test_audit_export_manifest():
    r = client.get("/audit/export/GOLDEN/zip-manifest")
    assert r.status_code == 200
    d = r.json()
    assert "includes" in d


def test_audit_export_verify():
    r = client.post("/audit/export/GOLDEN/verify")
    assert r.status_code == 200
    d = r.json()
    assert "verified" in d

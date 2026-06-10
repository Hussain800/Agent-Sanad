"""v1.8 release gates specific tests."""
from fastapi.testclient import TestClient
from backend.app import app
client = TestClient(app)

def test_release_facts_version_18():
    import json, os
    path = os.path.join(os.path.dirname(__file__), "..", "docs", "RELEASE_FACTS.json")
    f = json.load(open(path))
    assert f["version"] == "1.8.0"

def test_interop_uaepass_readiness():
    r = client.get("/interop/uaepass-readiness"); assert r.status_code == 200; assert r.json()["score"] >= 0.9

def test_interop_uae_verify_readiness():
    r = client.get("/interop/uae-verify-readiness"); assert r.status_code == 200

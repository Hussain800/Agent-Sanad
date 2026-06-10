from __future__ import annotations
from fastapi.testclient import TestClient
from backend.app import app
client = TestClient(app)

def test_sig_verify():
    pkg = client.post("/cases/GOLDEN/decision-package")
    r = client.post(f"/decision-packages/{pkg.json()['package_id']}/verify")
    assert r.status_code == 200 and r.json()["valid"] is True
def test_sig_revoke():
    pkg = client.post("/cases/GOLDEN/decision-package")
    r = client.post(f"/decision-packages/{pkg.json()['package_id']}/revoke-mock")
    assert r.status_code == 200 and r.json()["revoked"] is True
def test_wrong_nonce():
    s = client.post("/sessions/uaepass/mock/start", json={})
    cb = client.post("/sessions/uaepass/mock/callback", json={"session_id": s.json()["session_id"], "code":"x","nonce":"WRONG"})
    assert cb.status_code == 200 and cb.json()["status"] == "error"
def test_expired_session():
    import uuid; s = client.post("/sessions/uaepass/mock/start", json={})
    sid = s.json()["session_id"]; nonce = s.json()["nonce"]
    client.post(f"/sessions/{sid}/expire-mock")
    cb = client.post("/sessions/uaepass/mock/callback", json={"session_id":sid,"code":uuid.uuid4().hex[:8],"nonce":nonce})
    assert cb.json()["status"] == "error"
def test_pkg_version_current():
    pkg = client.post("/cases/GOLDEN/decision-package")
    r = client.get(f"/decision-packages/{pkg.json()['package_id']}/receipt")
    assert r.status_code == 200

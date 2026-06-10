"""v1.8 copilot and interop full tests."""
from fastapi.testclient import TestClient
from backend.app import app
client = TestClient(app)

def test_copilot_full_flow():
    s = client.post("/copilot/session/start?lang=en"); assert s.status_code == 200
    sid = s.json()["id"]
    r = client.post(f"/copilot/session/{sid}/message?message=status"); assert r.status_code == 200
    assert "intent" in r.json()
    r2 = client.post(f"/copilot/session/{sid}/message?message=appeal"); assert r.status_code == 200
    assert r2.json()["intent"] == "appeal_guidance"
    r3 = client.get(f"/copilot/session/{sid}"); assert r3.status_code == 200
    assert len(r3.json()["messages"]) >= 4

def test_copilot_redteam():
    r = client.post("/copilot/redteam/run"); assert r.status_code == 200
    assert r.json()["passed"] == 3

def test_interop_full():
    r = client.post("/interop/certification/run"); assert r.status_code == 200
    scores = r.json()["scores"]
    assert len(scores) >= 7

def test_mission_playbook_run():
    r = client.post("/mission-control/playbooks/connector_outage/run"); assert r.status_code == 200
    assert r.json()["tasks_created"] >= 2

def test_mission_tasks_complete():
    client.post("/mission-control/playbooks/connector_outage/run")
    tasks = client.get("/mission-control/tasks").json()["tasks"]
    if tasks:
        r = client.post(f"/mission-control/tasks/{tasks[0]['id']}/complete"); assert r.status_code == 200

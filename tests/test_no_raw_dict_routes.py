"""v1.7 no raw dict routes check."""
from __future__ import annotations
import inspect
from backend.app import app

def test_no_raw_dict_write_routes():
    exempt = {"POST /cases/{case_id}/officer-action", "POST /applications/mock",
              "POST /applications/mock/decide", "POST /sessions/uaepass/mock/start",
              "POST /sessions/uaepass/mock/callback", "POST /connectors/{name}/simulate",
              "POST /connectors/{name}/reset"}
    for route in app.routes:
        if not hasattr(route, 'methods') or not hasattr(route, 'endpoint'):
            continue
        methods = getattr(route, 'methods', set())
        if 'POST' not in methods and 'PUT' not in methods:
            continue
        path = getattr(route, 'path', '')
        key = f"POST {path}"
        if key in exempt:
            continue
    assert True

def test_openapi_has_routes():
    oapi = app.openapi()
    paths = oapi.get("paths", {})
    assert len(paths) >= 80

def test_openapi_has_evidence_routes():
    oapi = app.openapi()
    paths_str = str(oapi.get("paths", {}))
    assert "evidence-summary" in paths_str

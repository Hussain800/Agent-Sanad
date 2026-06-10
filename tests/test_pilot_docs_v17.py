"""v1.7 pilot docs existence tests."""
from __future__ import annotations
import os
DOCS = os.path.join(os.path.dirname(__file__), "..", "docs")

def test_pilot_sandbox_packet(): assert os.path.exists(os.path.join(DOCS, "PILOT_SANDBOX_PACKET.md"))
def test_data_processing_record(): assert os.path.exists(os.path.join(DOCS, "DATA_PROCESSING_RECORD.md"))
def test_dpia_lite(): assert os.path.exists(os.path.join(DOCS, "DPIA_LITE.md"))
def test_monitoring_plan(): assert os.path.exists(os.path.join(DOCS, "MONITORING_PLAN.md"))
def test_deployment_topology(): assert os.path.exists(os.path.join(DOCS, "DEPLOYMENT_TOPOLOGY.md"))
def test_migration_path(): assert os.path.exists(os.path.join(DOCS, "MIGRATION_PATH.md"))
def test_service_centre_scripts(): assert os.path.exists(os.path.join(DOCS, "SERVICE_CENTRE_SCRIPTS.md"))
def test_go_no_go_checklist(): assert os.path.exists(os.path.join(DOCS, "GO_NO_GO_CHECKLIST.md"))
def test_release_notes_v16(): assert os.path.exists(os.path.join(DOCS, "RELEASE_NOTES_V1_6.md"))
def test_release_notes_v17(): assert os.path.exists(os.path.join(DOCS, "RELEASE_NOTES_V1_7.md"))
def test_current_release(): assert os.path.exists(os.path.join(DOCS, "CURRENT_RELEASE.md"))

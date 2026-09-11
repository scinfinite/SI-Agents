"""Phase 42 Web/API deployment boundary coverage."""

import json
import threading
import urllib.request
from pathlib import Path

from core.control_api.service import ControlApiService
from core.web.audit import AuditLogger
from core.web.models import WebConfig
from core.web.server import create_server

ROOT = Path(__file__).resolve().parents[1]


def test_web_deployment_get_and_post(tmp_path: Path) -> None:
    service = ControlApiService(ROOT)
    config = WebConfig(host="127.0.0.1", port=0, audit_log=tmp_path / "audit.jsonl")
    server = create_server(config, service)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        base = f"http://127.0.0.1:{server.server_port}"
        with urllib.request.urlopen(base + "/api/v1/deployments") as response:
            data = json.load(response)
        assert "targets" in data and "plans" in data
        request = urllib.request.Request(
            base + "/api/v1/deployments",
            data=json.dumps({"id": "web-plan", "harness_id": "opencode", "agents": [], "teams": [], "skills": []}).encode(),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(request) as response:
            created = json.load(response)
        assert created["state"] == "valid"
    finally:
        server.shutdown()
        thread.join(timeout=3)
        server.server_close()


def test_deployment_assets_are_present_and_audit_logger_is_constructible(tmp_path: Path) -> None:
    assert (ROOT / "core" / "web" / "assets" / "deployment.html").exists()
    assert (ROOT / "core" / "web" / "assets" / "deployment.js").exists()
    assert (ROOT / "core" / "web" / "assets" / "deployment.css").exists()
    AuditLogger(tmp_path / "audit.jsonl")

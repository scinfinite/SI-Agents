"""Phase 38 visual organization/workflow contract tests."""

from __future__ import annotations

import json
import threading
from pathlib import Path
from urllib.request import Request, urlopen

from core.control_api.openapi import document
from core.control_api.service import ControlApiService
from core.web.models import WebConfig
from core.web.server import create_server

ROOT = Path(__file__).resolve().parents[1]


def _start(tmp_path: Path):
    server = create_server(WebConfig(port=0, audit_log=tmp_path / "audit.jsonl"), ControlApiService(ROOT))
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    return server, thread


def _stop(server, thread):
    server.shutdown()
    server.server_close()
    thread.join(timeout=2)


def test_visualization_is_deterministic_and_covers_required_relationships():
    service = ControlApiService(ROOT)
    first = service.visualization()
    second = service.visualization()
    assert first == second
    kinds = {node["kind"] for node in first["nodes"]}
    assert {"division", "team", "agent", "skill", "capability", "permission", "workflow", "step"} <= kinds
    relations = {edge["relation"] for edge in first["edges"]}
    assert {"owns", "contains", "uses", "requests", "declares", "assigned", "depends_on"} <= relations
    assert all(edge["source"] != edge["target"] for edge in first["edges"])


def test_visualization_does_not_add_execution_authority():
    service = ControlApiService(ROOT)
    graph = service.visualization()
    assert graph["runs"] == []
    assert "downstream" in graph["state_note"]
    assert not any(node["kind"] == "executor" for node in graph["nodes"])


def test_visualization_reflects_accepted_control_plane_run():
    service = ControlApiService(ROOT)
    result = service.create_run({"action": "inspect", "subject": "operator"})
    graph = service.visualization()
    assert graph["runs"] == [result]
    assert graph["runs"][0]["status"] == "queued"


def test_visualization_endpoint_and_openapi_are_synchronized(tmp_path):
    server, thread = _start(tmp_path)
    try:
        request = Request(f"http://127.0.0.1:{server.server_port}/api/v1/visualization", headers={"Accept": "application/json"})
        response = urlopen(request, timeout=3)
        payload = json.loads(response.read())
        assert response.status == 200
        assert payload["version"] == "v1"
        assert payload["nodes"] and payload["edges"]
        assert "/api/v1/visualization" in document()["paths"]
    finally:
        _stop(server, thread)


def test_control_center_aggregate_includes_visualization(tmp_path):
    server, thread = _start(tmp_path)
    try:
        request = Request(f"http://127.0.0.1:{server.server_port}/api/v1/control-center")
        payload = json.loads(urlopen(request, timeout=3).read())
        assert payload["visualization"]["version"] == "v1"
    finally:
        _stop(server, thread)

from __future__ import annotations

import json
from http.client import HTTPConnection
from pathlib import Path
from threading import Thread

import pytest

from core.control_api import ControlApiService, create_server, document
from core.governance.engine import GovernanceEngine
from core.governance.models import GovernanceDecision, Permission

ROOT = Path(__file__).resolve().parents[1]


def test_snapshot_exposes_canonical_counts() -> None:
    service = ControlApiService(ROOT)
    snapshot = service.snapshot().as_dict()
    assert snapshot["api_version"] == "v1"
    assert snapshot["counts"]["agents"] == 279
    assert snapshot["counts"]["teams"] >= 1
    assert snapshot["counts"]["workflows"] == 4


def test_read_models_are_deterministic_and_inert() -> None:
    service = ControlApiService(ROOT)
    assert len(service.agents()) == 279
    assert service.agents() == sorted(service.agents(), key=lambda x: (x["division"], x["name"], x["id"]))
    assert len(service.workflows()) == 4
    assert service.memory()["entries"] == []


def test_governed_run_requires_scoped_capability_permission() -> None:
    engine = GovernanceEngine()
    engine.store.add_permission(Permission("agent.demo", "inspect", "/workspace", GovernanceDecision.ALLOW))
    service = ControlApiService(ROOT, engine)
    run = service.create_run({"action": "inspect", "subject": "agent.demo", "capabilities": ["inspect"]})
    assert run["status"] == "queued"
    assert service.events()[0]["event_type"] == "run.accepted"


def test_run_denied_when_capability_has_no_permission() -> None:
    service = ControlApiService(ROOT)
    with pytest.raises(PermissionError):
        service.create_run({"action": "write", "subject": "agent.demo", "capabilities": ["write"]})
    assert service.runs() == []


def test_credential_external_egress_is_not_bypassable() -> None:
    engine = GovernanceEngine()
    engine.store.add_permission(Permission("agent.demo", "net", "/workspace", GovernanceDecision.ALLOW))
    service = ControlApiService(ROOT, engine)
    with pytest.raises(PermissionError):
        service.create_run({"action": "upload", "subject": "agent.demo", "capabilities": ["net"], "external_egress": True, "credential": True})


def test_server_is_localhost_only() -> None:
    service = ControlApiService(ROOT)
    with pytest.raises(ValueError):
        create_server(service, "0.0.0.0", 0)


def test_http_health_and_openapi_and_governed_post() -> None:
    engine = GovernanceEngine()
    service = ControlApiService(ROOT, engine)
    server = create_server(service, "127.0.0.1", 0)
    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()
    port = server.server_address[1]
    try:
        connection = HTTPConnection("127.0.0.1", port, timeout=3)
        connection.request("GET", "/api/v1/health")
        response = connection.getresponse()
        assert response.status == 200
        assert json.loads(response.read())["api_version"] == "v1"

        connection.request("GET", "/api/v1/openapi.json")
        response = connection.getresponse()
        assert response.status == 200
        assert "/api/v1/runs" in json.loads(response.read())["paths"]

        body = json.dumps({"action": "inspect", "subject": "agent.demo"})
        connection.request("POST", "/api/v1/runs", body=body, headers={"Content-Type": "application/json", "Content-Length": str(len(body))})
        response = connection.getresponse()
        assert response.status == 202
        assert json.loads(response.read())["status"] == "queued"
        connection.close()
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=2)


def test_openapi_is_versioned_and_has_required_paths() -> None:
    spec = document()
    assert spec["openapi"] == "3.1.0"
    assert spec["info"]["version"] == "1.0"
    assert "/api/v1/agents" in spec["paths"]
    assert "/api/v1/governance" in spec["paths"]

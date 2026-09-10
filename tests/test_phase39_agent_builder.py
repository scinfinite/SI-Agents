from __future__ import annotations

import json
import threading
from pathlib import Path
from urllib.error import HTTPError
from urllib.request import Request, urlopen

import pytest

from core.agent_builder.models import DraftStatus
from core.agent_builder.service import AgentBuilderService
from core.control_api.service import ControlApiService
from core.web.models import WebConfig
from core.web.server import create_server

ROOT = Path(__file__).resolve().parents[1]


def valid_payload() -> dict[str, object]:
    return {
        "id": "custom-review-agent",
        "name": "Custom Review Agent",
        "division": "si-engineering",
        "description": "Reviews engineering changes against explicit criteria.",
        "responsibilities": ["Review changes"],
        "deliverables": ["Review report"],
        "success_criteria": ["Every finding has evidence"],
        "boundaries": ["Does not execute changes"],
    }


def test_new_agent_validates_without_authority_grants(tmp_path):
    service = AgentBuilderService(tmp_path)
    result = service.validate_payload(valid_payload())
    assert result.valid
    assert result.agent["id"] == "custom-review-agent"
    assert "does not execute" in result.markdown.lower()


def test_new_agent_cannot_self_grant_authority(tmp_path):
    service = AgentBuilderService(tmp_path)
    payload = valid_payload()
    payload["permissions"] = ["shell.execute"]
    result = service.validate_payload(payload)
    assert not result.valid
    assert any("cannot self-grant" in error for error in result.errors)


def test_existing_customization_cannot_add_capability(tmp_path):
    service = AgentBuilderService(tmp_path)
    base = service.from_agent(service.catalog.all()[0].id)
    base["capabilities"] = list(base["capabilities"]) + ["new.privileged.capability"]
    result = service.validate_payload(base)
    assert not result.valid
    assert any("cannot add capabilities" in error for error in result.errors)


def test_existing_customization_must_keep_identity_and_division(tmp_path):
    service = AgentBuilderService(tmp_path)
    base = service.from_agent(service.catalog.all()[0].id)
    base["division"] = "si-finance"
    result = service.validate_payload(base)
    assert not result.valid
    assert any("division" in error for error in result.errors)


def test_save_update_and_archive_are_durable(tmp_path):
    service = AgentBuilderService(tmp_path)
    saved = service.save(valid_payload())
    assert saved["status"] == DraftStatus.VALID.value
    saved["description"] = "Updated description"
    saved = service.save(saved)
    assert saved["revision"] == 2
    reloaded = AgentBuilderService(tmp_path)
    assert reloaded.get("custom-review-agent")["revision"] == 2
    archived = reloaded.archive("custom-review-agent")
    assert archived["status"] == DraftStatus.ARCHIVED.value
    raw = json.loads((tmp_path / ".si" / "agent-builder.json").read_text())
    assert raw["version"] == 1
    assert (tmp_path / ".si" / "agent-builder.json").stat().st_mode & 0o077 == 0


def test_test_requires_existing_draft(tmp_path):
    service = AgentBuilderService(tmp_path)
    with pytest.raises(KeyError):
        service.test("missing")


def test_web_builder_validate_and_save(tmp_path):
    config = WebConfig(port=0, audit_log=tmp_path / "audit.jsonl")
    server = create_server(config, ControlApiService(ROOT))
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        body = json.dumps(valid_payload()).encode()
        response = urlopen(Request(f"http://127.0.0.1:{server.server_port}/api/v1/agent-builder/validate", method="POST", data=body, headers={"Content-Type": "application/json"}), timeout=3)
        result = json.loads(response.read())
        assert result["valid"] is True
        assert "# Custom Review Agent" in result["markdown"]
        response = urlopen(Request(f"http://127.0.0.1:{server.server_port}/api/v1/agent-builder/drafts", method="POST", data=body, headers={"Content-Type": "application/json"}), timeout=3)
        saved = json.loads(response.read())
        assert saved["status"] == "valid"
        response = urlopen(f"http://127.0.0.1:{server.server_port}/api/v1/agent-builder")
        assert json.loads(response.read())[0]["id"] == "custom-review-agent"
        response = urlopen(f"http://127.0.0.1:{server.server_port}/agent-builder")
        assert "Agent Builder" in response.read().decode()
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=2)


def test_web_builder_rejects_authority_grant(tmp_path):
    config = WebConfig(port=0, audit_log=tmp_path / "audit.jsonl")
    server = create_server(config, ControlApiService(ROOT))
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        payload = valid_payload()
        payload["permissions"] = ["shell.execute"]
        request = Request(f"http://127.0.0.1:{server.server_port}/api/v1/agent-builder/drafts", method="POST", data=json.dumps(payload).encode(), headers={"Content-Type": "application/json"})
        with pytest.raises(HTTPError) as exc:
            urlopen(request, timeout=3)
        assert exc.value.code == 400
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=2)

from __future__ import annotations

import json

import pytest

from core.agent_builder.models import DraftStatus
from core.agent_builder.service import AgentBuilderService


def valid_payload() -> dict[str, object]:
    return {
        "id": "custom-review-agent",
        "name": "Custom Review Agent",
        "division": "engineering",
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
    base = service.from_agent("developer")
    base["capabilities"] = list(base["capabilities"]) + ["new.privileged.capability"]
    result = service.validate_payload(base)
    assert not result.valid
    assert any("cannot add capabilities" in error for error in result.errors)


def test_existing_customization_must_keep_identity_and_division(tmp_path):
    service = AgentBuilderService(tmp_path)
    base = service.from_agent("developer")
    base["division"] = "finance"
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

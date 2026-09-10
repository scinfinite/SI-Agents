from __future__ import annotations

import pytest

from core.policies.permission_engine import PermissionDenied, PermissionEngine
from core.skills.executor import SkillExecutionError, SkillExecutor
from core.skills.models import Skill, SkillRequirement, SkillStatus
from core.skills.registry import SkillRegistry
from core.verification.evidence_store import EvidenceStore


def make_skill(**overrides: object) -> Skill:
    values: dict[str, object] = {
        "schema": "si-agents.skill.v1", "version": "1.0", "id": "test-skill",
        "name": "test-skill", "category": "testing", "purpose": "test purpose",
        "procedure": ("perform the operation",), "inputs": ("value",), "outputs": ("result",),
        "prerequisites": ("precondition",), "required_tools": ("test-runner",),
        "requested_capabilities": (), "requested_permissions": ("repository_read",),
        "verification": ("result is correct",), "failure_behavior": ("return failed verification",),
        "evidence_requirements": ("record result",), "examples": ("test example",),
        "compatibility": (SkillRequirement("si-core", "runtime", "1.x"),),
        "provenance": "SI-native test provenance", "status": SkillStatus.VALIDATED,
    }
    values.update(overrides)
    return Skill(**values)


def test_registry_rejects_duplicate_names() -> None:
    registry = SkillRegistry(); registry.register(make_skill())
    with pytest.raises(ValueError, match="Duplicate skill name"):
        registry.register(make_skill(id="test-skill-2"))


def test_registry_rejects_duplicate_ids() -> None:
    registry = SkillRegistry(); registry.register(make_skill())
    with pytest.raises(ValueError, match="Duplicate skill id"):
        registry.register(make_skill())


def test_executor_requires_inputs_and_explicit_verifier() -> None:
    registry = SkillRegistry(); skill = registry.register(make_skill())
    executor = SkillExecutor(registry, PermissionEngine(), EvidenceStore())
    with pytest.raises(SkillExecutionError, match="Missing Skill inputs"):
        executor.execute(skill.id, lambda _: {"result": "ok"}, {})
    with pytest.raises(SkillExecutionError, match="explicit verifier"):
        executor.execute(skill.id, lambda _: {"result": "ok"}, {"value": 1})


def test_executor_records_verified_evidence() -> None:
    registry = SkillRegistry(); skill = registry.register(make_skill())
    evidence = EvidenceStore(); executor = SkillExecutor(registry, PermissionEngine(), evidence)
    result = executor.execute(skill.id, lambda inputs: {"result": inputs["value"] + 1}, {"value": 1}, verifier=lambda outputs: outputs["result"] == 2)
    assert result.status == "succeeded" and result.evidence_ids
    assert evidence.all()[0].verification_status.value == "verified"


def test_executor_denies_ungranted_capability() -> None:
    registry = SkillRegistry(); skill = registry.register(make_skill(requested_capabilities=("workspace_write",)))
    executor = SkillExecutor(registry, PermissionEngine(allow_write_workspace=False), EvidenceStore())
    with pytest.raises(PermissionDenied, match="workspace_write"):
        executor.execute(skill.id, lambda _: {"result": "ok"}, {"value": 1}, verifier=lambda _: True)


def test_executor_fails_closed_on_unverified_result() -> None:
    registry = SkillRegistry(); skill = registry.register(make_skill())
    result = SkillExecutor(registry, PermissionEngine(), EvidenceStore()).execute(skill.id, lambda _: {"result": "bad"}, {"value": 1}, verifier=lambda _: False)
    assert result.status == "failed" and result.evidence_ids and result.error == "verification failed"


def test_blocked_skill_cannot_execute() -> None:
    registry = SkillRegistry(); skill = registry.register(make_skill(status=SkillStatus.BLOCKED))
    with pytest.raises(SkillExecutionError, match="not executable"):
        SkillExecutor(registry, PermissionEngine(), EvidenceStore()).execute(skill.id, lambda _: {"result": "ok"}, {"value": 1}, verifier=lambda _: True)

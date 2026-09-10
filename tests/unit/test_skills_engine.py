from __future__ import annotations

import pytest

from core.policies.permission_engine import PermissionDenied, PermissionEngine
from core.skills.executor import SkillExecutionError, SkillExecutor
from core.skills.models import Skill, SkillStatus
from core.skills.registry import SkillRegistry
from core.verification.evidence_store import EvidenceStore


def make_skill(**overrides: object) -> Skill:
    values: dict[str, object] = {
        "name": "test-skill",
        "category": "testing",
        "procedure": ("perform the operation", "verify the result"),
        "inputs": ("value",),
        "outputs": ("result",),
        "required_permissions": ("repository_read",),
        "verification": ("result is correct",),
        "failure_handling": ("return failed verification",),
        "success_criteria": ("verification passes",),
        "status": SkillStatus.VALIDATED,
    }
    values.update(overrides)
    return Skill(**values)


def test_registry_rejects_duplicate_names() -> None:
    registry = SkillRegistry()
    registry.register(make_skill())
    with pytest.raises(ValueError, match="Duplicate skill name"):
        registry.register(make_skill())


def test_validated_skill_requires_verification_and_failure_handling() -> None:
    with pytest.raises(ValueError, match="verification criteria"):
        make_skill(verification=())
    with pytest.raises(ValueError, match="failure handling"):
        make_skill(failure_handling=())


def test_executor_requires_inputs_and_explicit_verifier() -> None:
    registry = SkillRegistry()
    skill = registry.register(make_skill())
    executor = SkillExecutor(registry, PermissionEngine(), EvidenceStore())
    with pytest.raises(SkillExecutionError, match="Missing skill inputs"):
        executor.execute(skill.id, lambda _: {"result": "ok"}, {})
    with pytest.raises(SkillExecutionError, match="explicit verifier"):
        executor.execute(skill.id, lambda _: {"result": "ok"}, {"value": 1})


def test_executor_records_verified_evidence() -> None:
    registry = SkillRegistry()
    skill = registry.register(make_skill())
    evidence = EvidenceStore()
    executor = SkillExecutor(registry, PermissionEngine(), evidence)
    result = executor.execute(
        skill.id,
        lambda inputs: {"result": inputs["value"] + 1},
        {"value": 1},
        verifier=lambda outputs: outputs["result"] == 2,
    )
    assert result.status == "succeeded"
    assert result.evidence_ids
    assert evidence.all()[0].verification_status.value == "verified"


def test_executor_denies_ungranted_skill_permission() -> None:
    registry = SkillRegistry()
    skill = registry.register(make_skill(required_permissions=("workspace_write",)))
    permissions = PermissionEngine(allow_write_workspace=False)
    executor = SkillExecutor(registry, permissions, EvidenceStore())
    with pytest.raises(PermissionDenied, match="workspace_write"):
        executor.execute(
            skill.id,
            lambda _: {"result": "ok"},
            {"value": 1},
            verifier=lambda _: True,
        )


def test_executor_fails_closed_on_unverified_result() -> None:
    registry = SkillRegistry()
    skill = registry.register(make_skill())
    executor = SkillExecutor(registry, PermissionEngine(), EvidenceStore())
    result = executor.execute(
        skill.id,
        lambda _: {"result": "bad"},
        {"value": 1},
        verifier=lambda _: False,
    )
    assert result.status == "failed"
    assert result.evidence_ids

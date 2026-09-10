from __future__ import annotations

from collections.abc import Callable, Mapping

from core.policies.permission_engine import PermissionEngine
from core.skills.models import SkillResult, SkillStatus
from core.skills.registry import SkillRegistry
from core.verification.evidence import Evidence, VerificationStatus
from core.verification.evidence_store import EvidenceStore


class SkillExecutionError(RuntimeError):
    """Raised when a skill cannot be safely or successfully executed."""


class SkillExecutor:
    """Execute registered procedures through explicit permission and verification gates."""

    def __init__(self, registry: SkillRegistry, permissions: PermissionEngine, evidence: EvidenceStore) -> None:
        self.registry = registry
        self.permissions = permissions
        self.evidence = evidence

    def execute(
        self,
        skill_id: str,
        handler: Callable[[Mapping[str, object]], Mapping[str, object]],
        inputs: Mapping[str, object],
        *,
        agent: str | None = None,
        approval_granted: bool = False,
        verifier: Callable[[Mapping[str, object]], bool] | None = None,
    ) -> SkillResult:
        skill = self.registry.get(skill_id)
        if skill.status in (SkillStatus.BLOCKED, SkillStatus.DEPRECATED):
            raise SkillExecutionError(f"Skill is not executable: {skill.name}")
        missing = [name for name in skill.inputs if name not in inputs]
        if missing:
            raise SkillExecutionError(f"Missing skill inputs: {', '.join(missing)}")
        for permission in skill.required_permissions:
            self.permissions.require(
                permission, approval_granted=approval_granted, agent=agent, tool=f"skill:{skill.name}"
            )
        try:
            raw_outputs = dict(handler(inputs))
        except Exception as exc:
            self.evidence.record(Evidence(
                claim=f"Skill execution failed: {skill.name}",
                source=f"skill:{skill.id}",
                verification_status=VerificationStatus.FAILED,
                details=str(exc),
            ))
            raise SkillExecutionError(f"Skill execution failed: {skill.name}") from exc
        missing_outputs = [name for name in skill.outputs if name not in raw_outputs]
        if missing_outputs:
            raise SkillExecutionError(f"Missing skill outputs: {', '.join(missing_outputs)}")
        if verifier is None:
            raise SkillExecutionError("Skill execution requires an explicit verifier")
        verified = verifier(raw_outputs)
        status = VerificationStatus.VERIFIED if verified else VerificationStatus.FAILED
        evidence = self.evidence.record(Evidence(
            claim=f"Skill verification passed: {skill.name}" if verified else f"Skill verification failed: {skill.name}",
            source=f"skill:{skill.id}",
            verification_status=status,
            details="; ".join(skill.verification),
        ))
        if not verified:
            return SkillResult(skill.id, "failed", raw_outputs, skill.verification, (evidence.id,))
        return SkillResult(skill.id, "succeeded", raw_outputs, skill.verification, (evidence.id,))

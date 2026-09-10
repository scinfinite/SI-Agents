from __future__ import annotations

from collections.abc import Callable, Mapping

from core.events.bus import EventBus
from core.events.models import Event, EventName, EventSource
from core.policies.permission_engine import PermissionEngine
from core.skills.models import SkillResult, SkillStatus
from core.skills.registry import SkillRegistry
from core.verification.evidence import Evidence, VerificationStatus
from core.verification.evidence_store import EvidenceStore


class SkillExecutionError(RuntimeError):
    """Raised when a Skill cannot be safely or successfully executed."""


class SkillExecutor:
    """Execute registered procedures only after explicit governance and verification gates."""

    def __init__(
        self,
        registry: SkillRegistry,
        permissions: PermissionEngine,
        evidence: EvidenceStore,
        event_bus: EventBus | None = None,
    ) -> None:
        self.registry, self.permissions, self.evidence, self.event_bus = registry, permissions, evidence, event_bus

    def _publish(self, name: EventName, skill_id: str, payload: Mapping[str, object]) -> None:
        if self.event_bus is None:
            return
        result = self.event_bus.publish(
            Event(name.value, EventSource.SKILL, f"skill:{skill_id}", dict(payload))
        )
        if not result.dispatched:
            raise SkillExecutionError(result.reason or f"event blocked: {name.value}")

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
            raise SkillExecutionError(f"Missing Skill inputs: {', '.join(missing)}")
        for capability in (*skill.requested_capabilities, *skill.requested_permissions):
            self.permissions.require(capability, approval_granted=approval_granted, agent=agent, tool=f"skill:{skill.name}")
        if verifier is None:
            raise SkillExecutionError("Skill execution requires an explicit verifier")
        dangerous = any(
            capability in {
                "destructive_git",
                "destructive_filesystem",
                "production_deploy",
                "credential_rotation",
                "publication",
                "paid_resource",
                "sensitive_data_transfer",
            }
            for capability in (*skill.requested_capabilities, *skill.requested_permissions)
        )
        self._publish(
            EventName.SKILL_STARTED,
            skill.id,
            {"agent": agent, "dangerous": dangerous},
        )
        try:
            raw_outputs = dict(handler(inputs))
        except Exception as exc:
            self.evidence.record(Evidence(claim=f"Skill execution failed: {skill.name}", source=f"skill:{skill.id}", verification_status=VerificationStatus.FAILED, details=str(exc)))
            if self.event_bus is not None:
                self.event_bus.publish(Event(EventName.TASK_FAILED.value, EventSource.SKILL, f"skill:{skill.id}", {"reason": "handler_failed"}))
            raise SkillExecutionError(f"Skill execution failed: {skill.name}") from exc
        missing_outputs = [name for name in skill.outputs if name not in raw_outputs]
        if missing_outputs:
            raise SkillExecutionError(f"Missing Skill outputs: {', '.join(missing_outputs)}")
        self._publish(EventName.VERIFICATION_STARTED, skill.id, {"agent": agent})
        try:
            verified = bool(verifier(raw_outputs))
        except Exception as exc:
            self.evidence.record(Evidence(claim=f"Skill verification errored: {skill.name}", source=f"skill:{skill.id}", verification_status=VerificationStatus.FAILED, details=str(exc)))
            if self.event_bus is not None:
                self.event_bus.publish(Event(EventName.VERIFICATION_FAILED.value, EventSource.VERIFICATION, f"skill:{skill.id}", {"reason": "verifier_error"}))
            raise SkillExecutionError(f"Skill verification failed: {skill.name}") from exc
        status = VerificationStatus.VERIFIED if verified else VerificationStatus.FAILED
        evidence = self.evidence.record(Evidence(claim=f"Skill verification {'passed' if verified else 'failed'}: {skill.name}", source=f"skill:{skill.id}", verification_status=status, details="; ".join(skill.verification)))
        result = SkillResult(skill.id, "succeeded" if verified else "failed", raw_outputs, skill.verification, (evidence.id,), None if verified else "verification failed")
        self._publish(EventName.SKILL_COMPLETED, skill.id, {"agent": agent, "verified": verified})
        return result

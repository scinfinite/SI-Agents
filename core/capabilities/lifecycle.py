from dataclasses import dataclass
from datetime import UTC, datetime

from core.capabilities.models import Capability, CapabilityStatus
from core.capabilities.registry import CapabilityRegistry


@dataclass(frozen=True)
class CapabilityProposal:
    name: str
    category: str
    reason: str
    source: str
    proposed_version: str = "0.1.0"

    def __post_init__(self) -> None:
        for value, label in ((self.name, "name"), (self.category, "category"), (self.reason, "reason"), (self.source, "source")):
            if not value.strip():
                raise ValueError(f"Proposal {label} must not be empty")


class CapabilityLifecycle:
    """Controlled promotion/deprecation; no automatic promotion to validated."""

    def __init__(self, registry: CapabilityRegistry) -> None:
        self.registry = registry
        self._history: list[tuple[str, CapabilityStatus, CapabilityStatus, datetime]] = []

    def promote(self, capability_id: str, *, verification: tuple[str, ...], evidence: tuple[str, ...], confidence: float) -> Capability:
        current = self.registry.get(capability_id)
        if current.status in (CapabilityStatus.BLOCKED, CapabilityStatus.DEPRECATED):
            raise ValueError("Blocked or deprecated capability cannot be promoted")
        if not verification or not evidence:
            raise ValueError("Promotion requires verification criteria and evidence")
        updated = Capability(
            **{**current.__dict__, "status": CapabilityStatus.VALIDATED, "verification": verification, "evidence": evidence, "confidence": confidence}
        )
        self.registry.replace(updated)
        self._history.append((capability_id, current.status, updated.status, datetime.now(UTC)))
        return updated

    def deprecate(self, capability_id: str, *, reason: str) -> Capability:
        if not reason.strip():
            raise ValueError("Deprecation reason must not be empty")
        current = self.registry.get(capability_id)
        updated = Capability(**{**current.__dict__, "status": CapabilityStatus.DEPRECATED})
        self.registry.replace(updated)
        self._history.append((capability_id, current.status, updated.status, datetime.now(UTC)))
        return updated

    def block(self, capability_id: str, *, reason: str) -> Capability:
        if not reason.strip():
            raise ValueError("Block reason must not be empty")
        current = self.registry.get(capability_id)
        updated = Capability(**{**current.__dict__, "status": CapabilityStatus.BLOCKED, "health": 0.0})
        self.registry.replace(updated)
        self._history.append((capability_id, current.status, updated.status, datetime.now(UTC)))
        return updated

    def history(self) -> tuple[tuple[str, CapabilityStatus, CapabilityStatus, datetime], ...]:
        return tuple(self._history)

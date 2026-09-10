from dataclasses import dataclass

from core.capabilities.models import Capability, CapabilityStatus
from core.capabilities.registry import CapabilityRegistry


@dataclass(frozen=True)
class CapabilityScore:
    capability_id: str
    readiness: float
    reasons: tuple[str, ...]


class CapabilityIntelligence:
    """Deterministic readiness/risk signals; never grants execution permission."""

    def __init__(self, registry: CapabilityRegistry) -> None:
        self.registry = registry

    def score(self, capability: Capability) -> CapabilityScore:
        if capability.status is CapabilityStatus.BLOCKED:
            return CapabilityScore(capability.id, 0.0, ("capability is blocked",))
        evidence = min(len(capability.evidence) / 2.0, 1.0)
        verification = min(len(capability.verification) / 2.0, 1.0)
        benchmark = capability.benchmark_score if capability.benchmark_score is not None else 0.0
        health = capability.health if capability.health is not None else 0.0
        confidence = capability.confidence if capability.confidence is not None else 0.0
        readiness = (
            0.2 * evidence
            + 0.2 * verification
            + 0.25 * benchmark
            + 0.2 * health
            + 0.15 * confidence
        )
        reasons = (
            f"evidence={evidence:.2f}",
            f"verification={verification:.2f}",
            f"benchmark={benchmark:.2f}",
            f"health={health:.2f}",
            f"confidence={confidence:.2f}",
        )
        return CapabilityScore(capability.id, round(readiness, 6), reasons)

    def rank(self, *, category: str | None = None) -> tuple[CapabilityScore, ...]:
        items = self.registry.all() if category is None else self.registry.by_category(category)
        return tuple(
            sorted(
                (self.score(item) for item in items),
                key=lambda item: (-item.readiness, item.capability_id),
            )
        )

    def executable_candidates(self) -> tuple[Capability, ...]:
        return tuple(
            item
            for item in self.registry.all()
            if item.status is CapabilityStatus.VALIDATED and item.health is not None and item.health > 0.0
        )

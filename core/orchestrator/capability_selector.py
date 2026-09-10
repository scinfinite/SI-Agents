from dataclasses import dataclass

from core.capabilities.models import Capability, CapabilityStatus
from core.capabilities.registry import CapabilityRegistry


@dataclass(frozen=True)
class CapabilityMatch:
    capability: Capability
    score: float


class CapabilitySelector:
    """Filter and rank capabilities without granting execution permission."""

    def __init__(self, registry: CapabilityRegistry) -> None:
        self.registry = registry

    def select(
        self,
        *,
        category: str,
        required_tools: tuple[str, ...] = (),
        required_permissions: tuple[str, ...] = (),
        validated_only: bool = True,
    ) -> tuple[Capability, ...]:
        return tuple(match.capability for match in self.rank(
            category=category,
            required_tools=required_tools,
            required_permissions=required_permissions,
            validated_only=validated_only,
        ))

    def rank(
        self,
        *,
        category: str,
        required_tools: tuple[str, ...] = (),
        required_permissions: tuple[str, ...] = (),
        validated_only: bool = True,
    ) -> tuple[CapabilityMatch, ...]:
        if not category.strip():
            raise ValueError("Capability category must not be empty")
        candidates = self.registry.by_category(category)
        allowed = {CapabilityStatus.VALIDATED} if validated_only else {CapabilityStatus.VALIDATED, CapabilityStatus.EXPERIMENTAL, CapabilityStatus.UNKNOWN}
        candidates = tuple(item for item in candidates if item.status in allowed)
        candidates = tuple(
            item for item in candidates
            if all(tool in item.tools for tool in required_tools)
            and all(permission in item.permissions for permission in required_permissions)
        )

        def score(item: Capability) -> float:
            confidence = item.confidence if item.confidence is not None else 0.0
            health = item.health if item.health is not None else 0.5
            benchmark = item.benchmark_score if item.benchmark_score is not None else 0.0
            return (0.5 * confidence) + (0.3 * health) + (0.2 * benchmark)

        return tuple(sorted((CapabilityMatch(item, score(item)) for item in candidates), key=lambda match: (-match.score, match.capability.name)))

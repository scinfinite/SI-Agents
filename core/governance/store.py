"""In-memory governance registry with immutable replacement semantics."""

from dataclasses import dataclass

from core.governance.models import (
    Capability,
    CostConstraint,
    DataClassification,
    Permission,
    Policy,
    TrustBoundary,
)


@dataclass(frozen=True)
class GovernanceSnapshot:
    capabilities: tuple[Capability, ...]
    permissions: tuple[Permission, ...]
    policies: tuple[Policy, ...]
    boundaries: tuple[TrustBoundary, ...]
    classifications: tuple[DataClassification, ...]
    costs: tuple[CostConstraint, ...]


class GovernanceStore:
    """Register governance objects explicitly; never executes or mutates artifacts."""

    def __init__(self) -> None:
        self._capabilities: dict[str, Capability] = {}
        self._permissions: dict[tuple[str, str, str], Permission] = {}
        self._policies: dict[str, Policy] = {}
        self._boundaries: dict[str, TrustBoundary] = {}
        self._classifications: dict[str, DataClassification] = {}
        self._costs: dict[str, CostConstraint] = {}

    def add_capability(self, item: Capability) -> None:
        self._capabilities[item.name] = item

    def add_permission(self, item: Permission) -> None:
        self._permissions[(item.subject, item.capability, item.scope)] = item

    def add_policy(self, item: Policy) -> None:
        self._policies[item.name] = item

    def add_boundary(self, item: TrustBoundary) -> None:
        self._boundaries[item.name] = item

    def add_classification(self, item: DataClassification) -> None:
        self._classifications[item.resource] = item

    def add_cost_constraint(self, item: CostConstraint) -> None:
        self._costs[item.name] = item

    def snapshot(self) -> GovernanceSnapshot:
        return GovernanceSnapshot(
            tuple(sorted(self._capabilities.values(), key=lambda x: x.name)),
            tuple(sorted(self._permissions.values(), key=lambda x: (x.subject, x.capability, x.scope))),
            tuple(sorted(self._policies.values(), key=lambda x: x.name)),
            tuple(sorted(self._boundaries.values(), key=lambda x: x.name)),
            tuple(sorted(self._classifications.values(), key=lambda x: x.resource)),
            tuple(sorted(self._costs.values(), key=lambda x: x.name)),
        )

    def permission_for(self, subject: str, capability: str, scope: str) -> Permission | None:
        return self._permissions.get((subject, capability, scope))

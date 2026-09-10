from __future__ import annotations

from dataclasses import replace

from .models import (
    MemoryEntry,
    MemoryScope,
    MemoryStatus,
    PromotionDecision,
)


_SCOPE_ORDER = (
    MemoryScope.TASK,
    MemoryScope.PROJECT,
    MemoryScope.TEAM,
    MemoryScope.AGENT,
    MemoryScope.DIVISION,
    MemoryScope.ORGANIZATION,
    MemoryScope.GLOBAL,
)


class MemoryPromoter:
    """Fail-closed promotion policy with explicit evidence and scope ancestry."""

    def __init__(self, minimum_confidence: float = 0.8, minimum_verified_evidence: int = 2) -> None:
        if not 0.0 <= minimum_confidence <= 1.0:
            raise ValueError("minimum_confidence must be between 0 and 1")
        if minimum_verified_evidence < 1:
            raise ValueError("minimum_verified_evidence must be positive")
        self.minimum_confidence = minimum_confidence
        self.minimum_verified_evidence = minimum_verified_evidence

    @staticmethod
    def _next_scope(scope: MemoryScope) -> MemoryScope | None:
        try:
            return _SCOPE_ORDER[_SCOPE_ORDER.index(scope) + 1]
        except (ValueError, IndexError):
            return None

    def evaluate(self, entry: MemoryEntry, target_scope: MemoryScope | None = None) -> PromotionDecision:
        expected = self._next_scope(entry.scope)
        target = target_scope or expected
        if expected is None:
            return PromotionDecision(entry.id, False, entry.scope, ("Global memory cannot be promoted further",))
        reasons: list[str] = []
        verified = sum(1 for item in entry.evidence if item.verified)
        if target is not expected:
            reasons.append("Memory may only be promoted one scope at a time")
        if entry.status not in {MemoryStatus.CANDIDATE, MemoryStatus.VALIDATED}:
            reasons.append("Memory is not eligible for promotion")
        if entry.confidence < self.minimum_confidence:
            reasons.append("Confidence is below promotion threshold")
        if verified < self.minimum_verified_evidence:
            reasons.append("Insufficient verified evidence")
        if target is MemoryScope.PROJECT and not entry.project_id:
            reasons.append("Project promotion requires project_id")
        if target is MemoryScope.TEAM and not entry.team_id:
            reasons.append("Team promotion requires team_id")
        if target is MemoryScope.AGENT and not entry.agent_id:
            reasons.append("Agent promotion requires agent_id")
        if target is MemoryScope.DIVISION and not entry.division_id:
            reasons.append("Division promotion requires division_id")
        if target is MemoryScope.ORGANIZATION and not entry.organization_id:
            reasons.append("Organization promotion requires organization_id")
        if target is MemoryScope.GLOBAL and not entry.organization_id:
            reasons.append("Global promotion requires an organization provenance anchor")
        return PromotionDecision(entry.id, not reasons, target, tuple(reasons), self.minimum_verified_evidence, verified)

    def promote(self, entry: MemoryEntry, target_scope: MemoryScope | None = None) -> MemoryEntry:
        decision = self.evaluate(entry, target_scope)
        if not decision.allowed:
            raise ValueError("Memory promotion denied: " + "; ".join(decision.reasons))
        return replace(entry, scope=decision.target_scope, status=MemoryStatus.PROMOTED, version=entry.version + 1)

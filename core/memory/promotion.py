from __future__ import annotations

from dataclasses import replace

from .models import MemoryEntry, MemoryScope, MemoryStatus, PromotionDecision


class MemoryPromoter:
    """Fail-closed promotion policy for moving memories to broader scopes."""

    def __init__(self, minimum_confidence: float = 0.8, minimum_verified_evidence: int = 2) -> None:
        if not 0.0 <= minimum_confidence <= 1.0:
            raise ValueError("minimum_confidence must be between 0 and 1")
        if minimum_verified_evidence < 1:
            raise ValueError("minimum_verified_evidence must be positive")
        self.minimum_confidence = minimum_confidence
        self.minimum_verified_evidence = minimum_verified_evidence

    @staticmethod
    def _next_scope(scope: MemoryScope) -> MemoryScope | None:
        return {
            MemoryScope.TASK: MemoryScope.PROJECT,
            MemoryScope.PROJECT: MemoryScope.GLOBAL,
            MemoryScope.GLOBAL: None,
        }[scope]

    def evaluate(self, entry: MemoryEntry, target_scope: MemoryScope | None = None) -> PromotionDecision:
        target = target_scope or self._next_scope(entry.scope)
        if target is None:
            return PromotionDecision(entry.id, False, entry.scope, ("Global memory cannot be promoted further",))
        reasons: list[str] = []
        verified = sum(1 for item in entry.evidence if item.verified)
        if entry.status is not MemoryStatus.CANDIDATE and entry.status is not MemoryStatus.VALIDATED:
            reasons.append("Memory is not eligible for promotion")
        if entry.confidence < self.minimum_confidence:
            reasons.append("Confidence is below promotion threshold")
        if verified < self.minimum_verified_evidence:
            reasons.append("Insufficient verified evidence")
        if target is MemoryScope.PROJECT and not entry.project_id:
            reasons.append("Project promotion requires project_id")
        if target is MemoryScope.GLOBAL and not entry.project_id:
            reasons.append("Global promotion requires a project provenance anchor")
        if target.value == entry.scope.value:
            reasons.append("Target scope must be broader than current scope")
        return PromotionDecision(
            entry.id, not reasons, target, tuple(reasons), self.minimum_verified_evidence, verified
        )

    def promote(self, entry: MemoryEntry, target_scope: MemoryScope | None = None) -> MemoryEntry:
        decision = self.evaluate(entry, target_scope)
        if not decision.allowed:
            raise ValueError("Memory promotion denied: " + "; ".join(decision.reasons))
        return replace(entry, scope=decision.target_scope, status=MemoryStatus.PROMOTED, version=entry.version + 1)

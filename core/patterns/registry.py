from __future__ import annotations

from .models import EngineeringPattern, PatternStatus, ValidationResult


class PatternRegistry:
    """Immutable-by-replacement registry with explicit promotion evidence."""

    def __init__(self) -> None:
        self._patterns: dict[str, EngineeringPattern] = {}

    def record(self, pattern: EngineeringPattern) -> EngineeringPattern:
        if pattern.id in self._patterns:
            raise ValueError(f"Pattern already exists: {pattern.id}")
        self._patterns[pattern.id] = pattern
        return pattern

    def get(self, pattern_id: str) -> EngineeringPattern:
        try:
            return self._patterns[pattern_id]
        except KeyError as exc:
            raise KeyError(f"Unknown pattern: {pattern_id}") from exc

    def all(self) -> tuple[EngineeringPattern, ...]:
        return tuple(self._patterns.values())

    def by_status(self, status: PatternStatus) -> tuple[EngineeringPattern, ...]:
        return tuple(item for item in self._patterns.values() if item.status is status)

    def promote(self, pattern_id: str, validation: ValidationResult) -> EngineeringPattern:
        pattern = self.get(pattern_id)
        if validation.pattern_id != pattern_id:
            raise ValueError("Validation result does not match pattern")
        if not validation.promotable:
            raise ValueError("Pattern cannot be promoted without passing validation")
        promoted = EngineeringPattern(
            name=pattern.name,
            category=pattern.category,
            intent=pattern.intent,
            context=pattern.context,
            mechanism=pattern.mechanism,
            applicability=pattern.applicability,
            contraindications=pattern.contraindications,
            verification_criteria=pattern.verification_criteria,
            provenance=pattern.provenance,
            evidence=pattern.evidence,
            counterexamples=pattern.counterexamples,
            confidence=validation.confidence,
            status=PatternStatus.VALIDATED,
            version=pattern.version + 1,
            id=pattern.id,
        )
        self._patterns[pattern_id] = promoted
        return promoted

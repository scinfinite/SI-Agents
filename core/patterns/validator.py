from __future__ import annotations

from .models import EngineeringPattern, PatternStatus, ValidationResult


class PatternValidator:
    """Apply fail-closed promotion rules to an extracted pattern."""

    def validate(self, pattern: EngineeringPattern) -> ValidationResult:
        sources = {item.source for item in pattern.evidence if item.verified}
        examples = {item.example_id for item in pattern.evidence if item.verified}
        verified_evidence = sum(item.verified for item in pattern.evidence)
        reasons: list[str] = []

        if len(sources) < 2:
            reasons.append("requires verified evidence from at least two independent sources")
        if len(examples) < 2:
            reasons.append("requires at least two independently observed examples")
        if verified_evidence < 2:
            reasons.append("requires at least two verified evidence records")
        if pattern.counterexamples:
            reasons.append("contains counterexamples that must be assessed before promotion")

        promotable = not reasons and pattern.confidence >= 0.7
        status = PatternStatus.VALIDATED if promotable else PatternStatus.EXPERIMENTAL
        if pattern.confidence < 0.7:
            reasons.append("confidence is below the 0.70 promotion threshold")
        return ValidationResult(
            pattern_id=pattern.id,
            status=status,
            confidence=pattern.confidence,
            independent_sources=len(sources),
            independent_examples=len(examples),
            verified_evidence=verified_evidence,
            counterexamples=len(pattern.counterexamples),
            reasons=tuple(reasons),
        )

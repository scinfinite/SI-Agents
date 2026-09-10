from __future__ import annotations

from collections import defaultdict

from .models import EngineeringPattern, PatternObservation, PatternStatus
from .normalizer import PatternNormalizer


class PatternExtractor:
    """Extract conservative candidates from repeated, independently observed signals."""

    def extract(self, observations: tuple[PatternObservation, ...]) -> tuple[EngineeringPattern, ...]:
        groups: dict[str, list[PatternObservation]] = defaultdict(list)
        for observation in observations:
            key = PatternNormalizer.signature(
                category=observation.category.value,
                problem=observation.problem,
                mechanism=observation.mechanism,
                tags=observation.tags,
            )
            groups[key].append(observation)

        patterns: list[EngineeringPattern] = []
        for group in groups.values():
            if not group:
                continue
            first = group[0]
            sources = tuple(sorted({item.source for item in group}))
            examples = tuple(sorted({item.example_id for item in group}))
            evidence = tuple(item for obs in group for item in obs.evidence)
            counters = tuple(item for obs in group for item in obs.counterexamples)
            applicability = tuple(sorted({item.context for item in group}))
            patterns.append(
                EngineeringPattern(
                    name=self._candidate_name(first),
                    category=first.category,
                    intent=first.problem,
                    context=first.context,
                    mechanism=first.mechanism,
                    applicability=applicability,
                    contraindications=tuple(sorted({c.reason for c in counters})),
                    verification_criteria=(
                        "Verify the intended outcome in an executable or independently reviewed check.",
                        "Confirm the mechanism remains valid in the target technology context.",
                    ),
                    provenance=sources,
                    evidence=evidence,
                    counterexamples=counters,
                    confidence=self._candidate_confidence(examples, sources, evidence, counters),
                    status=PatternStatus.CANDIDATE,
                )
            )
        return tuple(patterns)

    @staticmethod
    def _candidate_name(observation: PatternObservation) -> str:
        return f"{observation.category.value}: {observation.problem.strip()}"

    @staticmethod
    def _candidate_confidence(
        examples: tuple[str, ...],
        sources: tuple[str, ...],
        evidence: tuple,
        counters: tuple,
    ) -> float:
        if not examples:
            return 0.0
        score = min(0.5, 0.2 * len(examples))
        score += min(0.3, 0.15 * len(sources))
        if any(item.verified for item in evidence):
            score += 0.2
        if counters:
            score -= min(0.2, 0.05 * len(counters))
        return round(max(0.0, min(1.0, score)), 4)

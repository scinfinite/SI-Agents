from __future__ import annotations

from .models import EngineeringPattern
from .normalizer import PatternNormalizer


class PatternMatcher:
    """Rank patterns against a context without treating a match as proof."""

    def match(
        self,
        patterns: tuple[EngineeringPattern, ...],
        *,
        category: str,
        context: str,
        tags: tuple[str, ...] = (),
    ) -> tuple[tuple[EngineeringPattern, float], ...]:
        wanted_category = PatternNormalizer.normalize_text(category)
        wanted_context = PatternNormalizer.normalize_text(context)
        wanted_tags = set(PatternNormalizer.normalize_tags(tags))
        ranked: list[tuple[EngineeringPattern, float]] = []
        for pattern in patterns:
            score = 0.0
            if pattern.category.value == wanted_category:
                score += 0.4
            normalized_contexts = {
                PatternNormalizer.normalize_text(value) for value in pattern.applicability
            }
            if wanted_context and any(
                wanted_context in value or value in wanted_context for value in normalized_contexts
            ):
                score += 0.4
            pattern_tags = set(PatternNormalizer.normalize_tags(pattern.applicability))
            if wanted_tags:
                score += 0.2 * len(wanted_tags & pattern_tags) / len(wanted_tags)
            ranked.append((pattern, min(1.0, score)))
        return tuple(sorted(ranked, key=lambda item: (-item[1], item[0].id)))

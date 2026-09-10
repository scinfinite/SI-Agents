from __future__ import annotations

import re
import unicodedata


class PatternNormalizer:
    """Create deterministic, expression-independent signatures for observations."""

    _space = re.compile(r"\s+")
    _punctuation = re.compile(r"[^a-z0-9_ ]+")

    @classmethod
    def normalize_text(cls, value: str) -> str:
        normalized = unicodedata.normalize("NFKC", value).lower().strip()
        normalized = cls._punctuation.sub(" ", normalized)
        return cls._space.sub(" ", normalized).strip()

    @classmethod
    def normalize_tags(cls, tags: tuple[str, ...]) -> tuple[str, ...]:
        return tuple(sorted({cls.normalize_text(tag) for tag in tags if tag.strip()}))

    @classmethod
    def signature(cls, *, category: str, problem: str, mechanism: str, tags: tuple[str, ...]) -> str:
        fields = (
            cls.normalize_text(category),
            cls.normalize_text(problem),
            cls.normalize_text(mechanism),
            ",".join(cls.normalize_tags(tags)),
        )
        return "|".join(fields)

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from hashlib import sha256


class ContextScope(str, Enum):
    USER = "user"
    PROJECT = "project"
    SESSION = "session"
    WORKFLOW = "workflow"
    TEAM = "team"
    TASK = "task"
    AGENT = "agent"


@dataclass(frozen=True)
class ContextBudget:
    scope: ContextScope
    limit_tokens: int
    limit_cost: float | None = None

    def __post_init__(self) -> None:
        if self.limit_tokens < 1:
            raise ValueError("Context token budget must be positive")
        if self.limit_cost is not None and self.limit_cost < 0:
            raise ValueError("Context cost budget must not be negative")


@dataclass(frozen=True)
class ModelContextProfile:
    model_id: str
    context_window_tokens: int
    reserved_output_tokens: int = 0
    input_token_cost: float = 0.0

    def __post_init__(self) -> None:
        if not self.model_id.strip():
            raise ValueError("Model ID must not be empty")
        if self.context_window_tokens < 1:
            raise ValueError("Context window must be positive")
        if self.reserved_output_tokens < 0 or self.reserved_output_tokens >= self.context_window_tokens:
            raise ValueError("Reserved output tokens must be within the context window")
        if self.input_token_cost < 0:
            raise ValueError("Input token cost must not be negative")

    @property
    def input_capacity(self) -> int:
        return self.context_window_tokens - self.reserved_output_tokens


@dataclass(frozen=True)
class ContextItem:
    item_id: str
    content: str
    scope: ContextScope
    importance: float = 0.5
    relevance: float = 0.5
    estimated_tokens: int | None = None
    estimated_cost: float | None = None
    sensitive: bool = False
    secret_like: bool = False
    provenance: tuple[str, ...] = ()
    lineage: tuple[str, ...] = ()
    tags: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not self.item_id.strip() or not self.content.strip():
            raise ValueError("Context items require an ID and non-empty content")
        if not 0 <= self.importance <= 1 or not 0 <= self.relevance <= 1:
            raise ValueError("Importance and relevance must be between 0 and 1")
        if self.estimated_tokens is not None and self.estimated_tokens < 1:
            raise ValueError("Estimated tokens must be positive")
        if self.estimated_cost is not None and self.estimated_cost < 0:
            raise ValueError("Estimated cost must not be negative")
        if not self.provenance:
            raise ValueError("Context items require provenance")

    @property
    def fingerprint(self) -> str:
        normalized = " ".join(self.content.split()).lower()
        return sha256(normalized.encode("utf-8")).hexdigest()

    def token_estimate(self) -> int:
        if self.estimated_tokens is not None:
            return self.estimated_tokens
        return max(1, (len(self.content) + 3) // 4)


@dataclass(frozen=True)
class ContextSelection:
    selected: tuple[ContextItem, ...]
    dropped: tuple[ContextItem, ...]
    total_tokens: int
    estimated_cost: float
    decision_id: str
    reason: str
    evidence: tuple[str, ...] = ()
    redacted: bool = False

    def __post_init__(self) -> None:
        if not self.decision_id.strip() or not self.reason.strip():
            raise ValueError("Context selections require decision identity and reason")
        if self.total_tokens < 0 or self.estimated_cost < 0:
            raise ValueError("Context selection accounting must not be negative")

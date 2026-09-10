"""Typed records used by model/provider intelligence and routing."""

from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import Enum


class Capability(str, Enum):
    CHAT = "chat"
    CODE = "code"
    REASONING = "reasoning"
    VISION = "vision"
    TOOL_USE = "tool_use"
    EMBEDDINGS = "embeddings"


@dataclass(frozen=True)
class ModelProfile:
    model_id: str
    capabilities: frozenset[Capability]
    context_tokens: int = 0
    max_output_tokens: int = 0
    input_cost_per_million: float = 0.0
    output_cost_per_million: float = 0.0
    reliability: float = 1.0
    latency_ms: float = 0.0
    enabled: bool = True

    def __post_init__(self) -> None:
        if not self.model_id.strip():
            raise ValueError("model_id must not be empty")
        if self.context_tokens < 0 or self.max_output_tokens < 0:
            raise ValueError("token limits must be non-negative")
        if self.input_cost_per_million < 0 or self.output_cost_per_million < 0:
            raise ValueError("model costs must be non-negative")
        if not 0.0 <= self.reliability <= 1.0:
            raise ValueError("reliability must be between 0 and 1")
        if self.latency_ms < 0:
            raise ValueError("latency must be non-negative")


@dataclass(frozen=True)
class ProviderProfile:
    provider_id: str
    models: tuple[ModelProfile, ...]
    priority: int = 100
    free: bool = True
    enabled: bool = True
    region: str | None = None

    def __post_init__(self) -> None:
        if not self.provider_id.strip():
            raise ValueError("provider_id must not be empty")
        if self.priority < 0:
            raise ValueError("priority must be non-negative")
        ids = [model.model_id for model in self.models]
        if len(ids) != len(set(ids)):
            raise ValueError("provider models must be unique")


@dataclass(frozen=True)
class QuotaSnapshot:
    provider_id: str
    remaining_requests: int | None = None
    remaining_tokens: int | None = None
    reset_at: datetime | None = None
    observed_at: datetime = field(default_factory=lambda: datetime.now(UTC))

    def __post_init__(self) -> None:
        if not self.provider_id.strip():
            raise ValueError("provider_id must not be empty")
        if self.remaining_requests is not None and self.remaining_requests < 0:
            raise ValueError("remaining_requests must be non-negative")
        if self.remaining_tokens is not None and self.remaining_tokens < 0:
            raise ValueError("remaining_tokens must be non-negative")


@dataclass(frozen=True)
class RoutingRequest:
    required_capabilities: frozenset[Capability]
    estimated_input_tokens: int = 0
    estimated_output_tokens: int = 0
    prefer_free: bool = True
    max_cost: float | None = None
    max_latency_ms: float | None = None
    excluded_providers: frozenset[str] = frozenset()

    def __post_init__(self) -> None:
        if self.estimated_input_tokens < 0 or self.estimated_output_tokens < 0:
            raise ValueError("estimated token counts must be non-negative")
        if self.max_cost is not None and self.max_cost < 0:
            raise ValueError("max_cost must be non-negative")
        if self.max_latency_ms is not None and self.max_latency_ms < 0:
            raise ValueError("max_latency_ms must be non-negative")


@dataclass(frozen=True)
class RoutingDecision:
    provider_id: str
    model_id: str
    score: float
    estimated_cost: float
    reasons: tuple[str, ...]
    selected_at: datetime = field(default_factory=lambda: datetime.now(UTC))

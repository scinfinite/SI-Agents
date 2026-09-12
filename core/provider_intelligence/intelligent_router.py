"""Deterministic task routing and economics policy for SI Core.

The engine ranks already-authorized provider/model profiles. It never grants
capabilities, resolves credentials, or becomes an OmniRoute business authority.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from math import ceil
from typing import Iterable

from core.provider_intelligence.circuit import CircuitBreaker
from core.provider_intelligence.health import HealthTracker
from core.provider_intelligence.models import Capability, ModelProfile, ProviderProfile
from core.provider_intelligence.quota import QuotaTracker
from core.provider_intelligence.registry import ProviderRegistry


class RoutingError(RuntimeError):
    """Base error for deterministic routing failures."""


class BudgetExceededError(RoutingError):
    """Raised when the selected route cannot fit the caller's budget."""


class TaskComplexity(str, Enum):
    SIMPLE = "simple"
    MODERATE = "moderate"
    COMPLEX = "complex"
    CRITICAL = "critical"


@dataclass(frozen=True)
class TaskRequirements:
    """Explicit task constraints; inference is advisory and deterministic."""

    prompt: str = ""
    capabilities: frozenset[Capability] = frozenset({Capability.CHAT})
    estimated_input_tokens: int = 0
    estimated_output_tokens: int = 0
    context_tokens: int = 0
    max_cost: float | None = None
    max_latency_ms: float | None = None
    require_streaming: bool = False
    require_structured_output: bool = False
    require_vision: bool = False
    preferred_providers: tuple[str, ...] = ()
    preferred_models: tuple[str, ...] = ()
    excluded_providers: frozenset[str] = frozenset()
    minimum_reliability: float = 0.0
    allow_escalation: bool = True
    allow_downgrade: bool = True

    def __post_init__(self) -> None:
        if self.estimated_input_tokens < 0 or self.estimated_output_tokens < 0 or self.context_tokens < 0:
            raise ValueError("token estimates must be non-negative")
        if self.max_cost is not None and self.max_cost < 0:
            raise ValueError("max_cost must be non-negative")
        if self.max_latency_ms is not None and self.max_latency_ms < 0:
            raise ValueError("max_latency_ms must be non-negative")
        if not 0.0 <= self.minimum_reliability <= 1.0:
            raise ValueError("minimum_reliability must be between 0 and 1")
        if self.require_vision:
            object.__setattr__(self, "capabilities", self.capabilities | {Capability.VISION})


@dataclass(frozen=True)
class RoutePolicy:
    """Weights and retry limits used for deterministic economics."""

    quality_weight: float = 1.0
    reliability_weight: float = 0.8
    latency_weight: float = 0.25
    cost_weight: float = 0.7
    preference_bonus: float = 15.0
    escalation_margin: float = 0.15
    max_attempts: int = 3
    retry_multiplier: float = 1.5

    def __post_init__(self) -> None:
        if any(value < 0 for value in (self.quality_weight, self.reliability_weight, self.latency_weight, self.cost_weight, self.preference_bonus)):
            raise ValueError("route weights must be non-negative")
        if self.escalation_margin < 0 or self.retry_multiplier < 1:
            raise ValueError("invalid escalation/retry economics")
        if self.max_attempts <= 0:
            raise ValueError("max_attempts must be positive")


@dataclass(frozen=True)
class RouteCandidate:
    provider_id: str
    model_id: str
    score: float
    estimated_cost: float
    expected_latency_ms: float
    reliability: float
    rank: int
    reasons: tuple[str, ...]


@dataclass(frozen=True)
class RouteEvidence:
    """Non-secret, replayable explanation of a routing decision."""

    task_complexity: TaskComplexity
    selected: RouteCandidate
    candidates_considered: int
    escalation_level: int = 0
    attempt: int = 1
    retryable_failure: str | None = None
    estimated_attempt_cost: float = 0.0
    estimated_worst_case_cost: float = 0.0


@dataclass
class BudgetLedger:
    """In-memory budget guard. Persistence remains the responsibility of SI Core."""

    budget: float | None = None
    spent: float = 0.0
    reservations: float = 0.0

    def __post_init__(self) -> None:
        if self.budget is not None and self.budget < 0:
            raise ValueError("budget must be non-negative")

    @property
    def remaining(self) -> float | None:
        return None if self.budget is None else max(0.0, self.budget - self.spent - self.reservations)

    def reserve(self, amount: float) -> None:
        if amount < 0:
            raise ValueError("reservation must be non-negative")
        if self.remaining is not None and amount > self.remaining + 1e-12:
            raise BudgetExceededError("routing reservation exceeds remaining budget")
        self.reservations += amount

    def settle(self, estimated: float, actual: float | None = None) -> None:
        if estimated < 0 or (actual is not None and actual < 0):
            raise ValueError("costs must be non-negative")
        self.reservations = max(0.0, self.reservations - estimated)
        self.spent += estimated if actual is None else actual
        if self.budget is not None and self.spent > self.budget + 1e-12:
            raise BudgetExceededError("settled cost exceeds budget")


def infer_complexity(requirements: TaskRequirements) -> TaskComplexity:
    """Infer complexity from explicit signals without model calls or hidden state."""

    text = requirements.prompt.lower()
    score = 0
    if requirements.estimated_input_tokens + requirements.estimated_output_tokens > 4_000:
        score += 1
    if requirements.context_tokens > 16_000:
        score += 1
    score += 1 if Capability.REASONING in requirements.capabilities else 0
    score += 1 if Capability.CODE in requirements.capabilities else 0
    score += 1 if Capability.TOOL_USE in requirements.capabilities else 0
    score += 1 if requirements.require_structured_output else 0
    score += 1 if any(word in text for word in ("architecture", "debug", "prove", "migrate", "analyze")) else 0
    if score <= 1:
        return TaskComplexity.SIMPLE
    if score <= 3:
        return TaskComplexity.MODERATE
    if score <= 5:
        return TaskComplexity.COMPLEX
    return TaskComplexity.CRITICAL


class IntelligentRouter:
    """SI-side routing intelligence layered above OmniRoute transport."""

    def __init__(
        self,
        registry: ProviderRegistry,
        quota: QuotaTracker | None = None,
        health: HealthTracker | None = None,
        policy: RoutePolicy | None = None,
    ) -> None:
        self.registry = registry
        self.quota = quota or QuotaTracker()
        self.health = health or HealthTracker()
        self.policy = policy or RoutePolicy()
        self._circuits: dict[str, CircuitBreaker] = {}

    def circuit(self, provider_id: str) -> CircuitBreaker:
        return self._circuits.setdefault(provider_id, CircuitBreaker())

    @staticmethod
    def _cost(model: ModelProfile, req: TaskRequirements) -> float:
        return (req.estimated_input_tokens * model.input_cost_per_million + req.estimated_output_tokens * model.output_cost_per_million) / 1_000_000

    def _supports(self, model: ModelProfile, req: TaskRequirements) -> bool:
        required = set(req.capabilities)
        if req.require_streaming:
            required.add(Capability.STREAMING)
        if req.require_structured_output:
            required.add(Capability.STRUCTURED_OUTPUT)
        return required.issubset(model.capabilities) and model.context_tokens >= req.context_tokens and model.max_output_tokens >= req.estimated_output_tokens

    def candidates(self, req: TaskRequirements) -> tuple[RouteCandidate, ...]:
        complexity = infer_complexity(req)
        raw: list[tuple[float, ProviderProfile, ModelProfile, float, tuple[str, ...]]] = []
        for provider, model in self.registry.models():
            if provider.provider_id in req.excluded_providers or not self._supports(model, req):
                continue
            if not self.quota.available(provider.provider_id) or not self.circuit(provider.provider_id).allow():
                continue
            reliability = min(model.reliability, self.health.success_rate(provider.provider_id))
            if reliability < req.minimum_reliability:
                continue
            cost = self._cost(model, req)
            if req.max_cost is not None and cost > req.max_cost:
                continue
            if req.max_latency_ms is not None and model.latency_ms > req.max_latency_ms:
                continue
            quality = model.quality
            score = self.policy.quality_weight * quality + self.policy.reliability_weight * reliability
            score -= self.policy.latency_weight * (model.latency_ms / 1000.0)
            score -= self.policy.cost_weight * cost
            reasons = ["capabilities satisfied", f"complexity={complexity.value}"]
            if provider.provider_id in req.preferred_providers:
                score += self.policy.preference_bonus
                reasons.append("preferred provider")
            if model.model_id in req.preferred_models:
                score += self.policy.preference_bonus
                reasons.append("preferred model")
            raw.append((score, provider, model, cost, tuple(reasons)))
        raw.sort(key=lambda item: (-item[0], item[1].priority, item[1].provider_id, item[2].model_id))
        return tuple(RouteCandidate(p.provider_id, m.model_id, score, cost, m.latency_ms, min(m.reliability, self.health.success_rate(p.provider_id)), rank + 1, reasons) for rank, (score, p, m, cost, reasons) in enumerate(raw))

    def route(self, req: TaskRequirements, ledger: BudgetLedger | None = None) -> RouteEvidence:
        candidates = self.candidates(req)
        if not candidates:
            raise RoutingError("no eligible route satisfies capability, context, quota, health, circuit, cost, and latency constraints")
        selected = candidates[0]
        if ledger is not None:
            ledger.reserve(selected.estimated_cost)
        attempts = self.policy.max_attempts
        worst = selected.estimated_cost * sum(self.policy.retry_multiplier ** i for i in range(attempts))
        return RouteEvidence(infer_complexity(req), selected, len(candidates), 0, 1, None, selected.estimated_cost, worst)

    def fallback(self, evidence: RouteEvidence, req: TaskRequirements, *, retryable_failure: str) -> RouteEvidence:
        candidates = self.candidates(req)
        remaining = [candidate for candidate in candidates if (candidate.provider_id, candidate.model_id) != (evidence.selected.provider_id, evidence.selected.model_id)]
        if not remaining:
            raise RoutingError("no fallback route remains")
        next_candidate = remaining[0]
        escalation = evidence.escalation_level
        if next_candidate.score < evidence.selected.score and req.allow_downgrade:
            escalation -= 1
        elif next_candidate.score > evidence.selected.score and req.allow_escalation:
            escalation += 1
        attempt = evidence.attempt + 1
        if attempt > self.policy.max_attempts:
            raise RoutingError("retry budget exhausted")
        return RouteEvidence(infer_complexity(req), next_candidate, len(candidates), escalation, attempt, retryable_failure, next_candidate.estimated_cost, next_candidate.estimated_cost * sum(self.policy.retry_multiplier ** i for i in range(self.policy.max_attempts - attempt + 1)))

    def record_outcome(self, provider_id: str, *, success: bool, latency_ms: float, rate_limited: bool = False) -> None:
        from core.provider_intelligence.health import HealthObservation
        self.health.record(HealthObservation(provider_id, success, latency_ms))
        if rate_limited or not success:
            self.circuit(provider_id).record_failure()
        else:
            self.circuit(provider_id).record_success()

    def estimate(self, req: TaskRequirements, attempts: int | None = None) -> float:
        candidates = self.candidates(req)
        if not candidates:
            raise RoutingError("cannot estimate without an eligible route")
        count = attempts or self.policy.max_attempts
        if count <= 0:
            raise ValueError("attempts must be positive")
        return candidates[0].estimated_cost * sum(self.policy.retry_multiplier ** i for i in range(count))

    @staticmethod
    def forecast_token_budget(req: TaskRequirements, models: Iterable[ModelProfile]) -> int:
        """Return a conservative output reservation across the supplied candidates."""
        maximum = max((model.max_output_tokens for model in models), default=0)
        return max(req.estimated_output_tokens, ceil(maximum * 0.05))

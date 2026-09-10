"""Capability-aware, cost-aware model selection with deterministic fallback ranking."""

from core.provider_intelligence.circuit import CircuitBreaker
from core.provider_intelligence.models import (
    ModelProfile,
    ProviderProfile,
    RoutingDecision,
    RoutingRequest,
)
from core.provider_intelligence.quota import QuotaTracker
from core.provider_intelligence.registry import ProviderRegistry


class NoSuitableModelError(RuntimeError):
    """Raised when no registered model satisfies the routing constraints."""


class ModelRouter:
    """Rank eligible models without performing provider calls."""

    def __init__(self, registry: ProviderRegistry, quota: QuotaTracker | None = None) -> None:
        self.registry = registry
        self.quota = quota or QuotaTracker()
        self._circuits: dict[str, CircuitBreaker] = {}

    def circuit(self, provider_id: str) -> CircuitBreaker:
        return self._circuits.setdefault(provider_id, CircuitBreaker())

    @staticmethod
    def _cost(model: ModelProfile, request: RoutingRequest) -> float:
        return (
            request.estimated_input_tokens * model.input_cost_per_million
            + request.estimated_output_tokens * model.output_cost_per_million
        ) / 1_000_000

    def route(self, request: RoutingRequest) -> RoutingDecision:
        candidates: list[tuple[float, ProviderProfile, ModelProfile, float, tuple[str, ...]]] = []
        for provider, model in self.registry.models():
            if provider.provider_id in request.excluded_providers:
                continue
            if not request.required_capabilities.issubset(model.capabilities):
                continue
            if not self.quota.available(provider.provider_id):
                continue
            if not self.circuit(provider.provider_id).allow():
                continue
            cost = self._cost(model, request)
            if request.max_cost is not None and cost > request.max_cost:
                continue
            if request.max_latency_ms is not None and model.latency_ms > request.max_latency_ms:
                continue
            reasons = ["capabilities satisfied"]
            score = model.reliability * 100.0 - model.latency_ms * 0.01 - cost * 10.0
            if request.prefer_free:
                score += 20.0 if provider.free else -20.0
                reasons.append("free-first preference" if provider.free else "paid provider deprioritized")
            score -= provider.priority * 0.01
            candidates.append((score, provider, model, cost, tuple(reasons)))
        if not candidates:
            raise NoSuitableModelError("no model satisfies capability, quota, circuit, cost, and latency constraints")
        score, provider, model, cost, reasons = max(
            candidates, key=lambda item: (item[0], -item[1].priority, item[1].provider_id, item[2].model_id)
        )
        return RoutingDecision(provider.provider_id, model.model_id, score, cost, reasons)

    def record_success(self, provider_id: str) -> None:
        self.circuit(provider_id).record_success()

    def record_failure(self, provider_id: str) -> None:
        self.circuit(provider_id).record_failure()

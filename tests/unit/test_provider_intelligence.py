"""Adversarial tests for Phase 14 model/provider intelligence."""

from datetime import UTC, datetime, timedelta

import pytest

from core.provider_intelligence.circuit import CircuitBreaker
from core.provider_intelligence.health import HealthObservation, HealthTracker
from core.provider_intelligence.models import Capability, ModelProfile, ProviderProfile, QuotaSnapshot, RoutingRequest
from core.provider_intelligence.quota import QuotaTracker
from core.provider_intelligence.registry import ProviderRegistry
from core.provider_intelligence.router import ModelRouter, NoSuitableModelError


def model(model_id: str, *, free: bool = True, cost: float = 0.0, latency: float = 100.0) -> ModelProfile:
    return ModelProfile(
        model_id=model_id,
        capabilities=frozenset({Capability.CHAT, Capability.CODE}),
        input_cost_per_million=cost,
        output_cost_per_million=cost,
        latency_ms=latency,
    )


def test_registry_rejects_duplicate_provider() -> None:
    registry = ProviderRegistry()
    provider = ProviderProfile("p", (model("m"),))
    registry.register(provider)
    with pytest.raises(ValueError, match="already registered"):
        registry.register(provider)


def test_router_enforces_required_capabilities() -> None:
    registry = ProviderRegistry()
    registry.register(ProviderProfile("p", (model("m"),)))
    router = ModelRouter(registry)
    with pytest.raises(NoSuitableModelError):
        router.route(RoutingRequest(frozenset({Capability.VISION})))


def test_router_prefers_free_model() -> None:
    registry = ProviderRegistry()
    registry.register(ProviderProfile("paid", (model("paid", cost=1.0),), free=False))
    registry.register(ProviderProfile("free", (model("free"),), free=True))
    decision = ModelRouter(registry).route(RoutingRequest(frozenset({Capability.CHAT})))
    assert decision.provider_id == "free"


def test_router_enforces_cost_ceiling() -> None:
    registry = ProviderRegistry()
    registry.register(ProviderProfile("paid", (model("paid", cost=2.0),), free=False))
    request = RoutingRequest(frozenset({Capability.CHAT}), estimated_input_tokens=1_000_000, max_cost=1.0)
    with pytest.raises(NoSuitableModelError):
        ModelRouter(registry).route(request)


def test_router_enforces_latency_ceiling() -> None:
    registry = ProviderRegistry()
    registry.register(ProviderProfile("slow", (model("slow", latency=500),)))
    with pytest.raises(NoSuitableModelError):
        ModelRouter(registry).route(RoutingRequest(frozenset({Capability.CHAT}), max_latency_ms=100))


def test_quota_zero_blocks_provider_and_unknown_is_available() -> None:
    quota = QuotaTracker()
    assert quota.available("unknown")
    quota.observe(QuotaSnapshot("p", remaining_requests=0))
    assert not quota.available("p")


def test_quota_keeps_newest_observation() -> None:
    quota = QuotaTracker()
    now = datetime.now(UTC)
    quota.observe(QuotaSnapshot("p", remaining_requests=0, observed_at=now))
    quota.observe(QuotaSnapshot("p", remaining_requests=3, observed_at=now + timedelta(seconds=1)))
    assert quota.get("p").remaining_requests == 3


def test_circuit_opens_after_threshold() -> None:
    circuit = CircuitBreaker(failure_threshold=2, cooldown_seconds=60)
    circuit.record_failure()
    assert circuit.allow()
    circuit.record_failure()
    assert not circuit.allow()


def test_circuit_success_resets_failures() -> None:
    circuit = CircuitBreaker(failure_threshold=2)
    circuit.record_failure()
    circuit.record_success()
    circuit.record_failure()
    assert circuit.allow()


def test_router_skips_open_circuit() -> None:
    registry = ProviderRegistry()
    registry.register(ProviderProfile("bad", (model("m"),)))
    router = ModelRouter(registry)
    for _ in range(3):
        router.record_failure("bad")
    with pytest.raises(NoSuitableModelError):
        router.route(RoutingRequest(frozenset({Capability.CHAT})))


def test_router_fallback_preserves_exclusions() -> None:
    registry = ProviderRegistry()
    registry.register(ProviderProfile("p1", (model("m1"),)))
    registry.register(ProviderProfile("p2", (model("m2"),)))
    request = RoutingRequest(frozenset({Capability.CHAT}), excluded_providers=frozenset({"p1"}))
    assert ModelRouter(registry).route(request).provider_id == "p2"


def test_health_window_is_bounded() -> None:
    tracker = HealthTracker(window=2)
    for success in (False, False, True):
        tracker.record(HealthObservation("p", success, 10))
    assert tracker.success_rate("p") == 0.5


def test_model_rejects_negative_cost() -> None:
    with pytest.raises(ValueError, match="cost"):
        ModelProfile("m", frozenset({Capability.CHAT}), input_cost_per_million=-1)


def test_provider_rejects_duplicate_models() -> None:
    with pytest.raises(ValueError, match="unique"):
        ProviderProfile("p", (model("m"), model("m")))


def test_router_cost_calculation_uses_both_token_directions() -> None:
    registry = ProviderRegistry()
    registry.register(ProviderProfile("p", (model("m", cost=2.0),)))
    request = RoutingRequest(
        frozenset({Capability.CHAT}), estimated_input_tokens=100_000, estimated_output_tokens=50_000
    )
    decision = ModelRouter(registry).route(request)
    assert decision.estimated_cost == pytest.approx(0.3)

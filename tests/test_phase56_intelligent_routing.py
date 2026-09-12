from datetime import UTC, datetime

import pytest

from core.provider_intelligence import (
    Capability,
    ModelProfile,
    ProviderProfile,
    ProviderRegistry,
    QuotaSnapshot,
)
from core.provider_intelligence.health import HealthObservation, HealthTracker
from core.provider_intelligence.intelligent_router import (
    BudgetExceededError,
    BudgetLedger,
    FailureClass,
    IntelligentRouter,
    RoutePolicy,
    RoutingError,
    TaskComplexity,
    TaskRequirements,
    classify_failure,
    infer_complexity,
)


def model(name, *, caps=None, cost=1.0, latency=100, quality=0.8, reliability=0.9):
    return ModelProfile(
        name,
        frozenset(caps or {Capability.CHAT}),
        context_tokens=32_000,
        max_output_tokens=8_000,
        input_cost_per_million=cost,
        output_cost_per_million=cost,
        latency_ms=latency,
        quality=quality,
        reliability=reliability,
    )


def router():
    registry = ProviderRegistry()
    registry.register(
        ProviderProfile("cheap", (model("cheap-model", cost=0.1, quality=0.6),), priority=20)
    )
    registry.register(
        ProviderProfile("best", (model("best-model", cost=2.0, quality=1.0, latency=300),), priority=10)
    )
    return registry, IntelligentRouter(registry, policy=RoutePolicy(cost_weight=0.7))


def test_complexity_is_deterministic_and_capability_driven():
    assert infer_complexity(TaskRequirements(prompt="hello")) is TaskComplexity.SIMPLE
    req = TaskRequirements(
        prompt="debug architecture",
        capabilities=frozenset({Capability.CODE, Capability.REASONING}),
        estimated_input_tokens=5000,
    )
    assert infer_complexity(req) in {TaskComplexity.COMPLEX, TaskComplexity.CRITICAL}


def test_capability_context_streaming_and_structured_matching():
    registry = ProviderRegistry()
    registry.register(
        ProviderProfile(
            "rich",
            (
                model(
                    "rich-model",
                    caps={Capability.CHAT, Capability.VISION, Capability.STREAMING, Capability.STRUCTURED_OUTPUT},
                ),
            ),
        )
    )
    engine = IntelligentRouter(registry)
    evidence = engine.route(
        TaskRequirements(
            require_vision=True,
            require_streaming=True,
            require_structured_output=True,
            context_tokens=10_000,
            estimated_output_tokens=10,
        )
    )
    assert evidence.selected.model_id == "rich-model"


def test_cost_and_budget_reservation():
    _, engine = router()
    ledger = BudgetLedger(0.001)
    evidence = engine.route(
        TaskRequirements(estimated_input_tokens=100, estimated_output_tokens=100, max_cost=0.0001),
        ledger,
    )
    assert evidence.selected.provider_id == "cheap"
    assert ledger.reservations > 0
    ledger.settle(evidence.estimated_attempt_cost, actual=evidence.estimated_attempt_cost)
    assert ledger.reservations == 0
    with pytest.raises(BudgetExceededError):
        engine.route(
            TaskRequirements(estimated_input_tokens=6000, estimated_output_tokens=6000),
            BudgetLedger(0.001),
        )


def test_preference_can_override_small_economic_difference():
    registry = ProviderRegistry()
    registry.register(ProviderProfile("preferred", (model("p", cost=0.5, quality=0.7),), priority=100))
    registry.register(ProviderProfile("other", (model("o", cost=0.1, quality=0.71),), priority=1))
    engine = IntelligentRouter(registry)
    evidence = engine.route(TaskRequirements(preferred_providers=("preferred",)))
    assert evidence.selected.provider_id == "preferred"
    assert "preferred provider" in evidence.selected.reasons


def test_quota_health_and_circuit_are_fail_closed_for_unusable_provider():
    registry = ProviderRegistry()
    registry.register(ProviderProfile("bad", (model("b"),)))
    registry.register(ProviderProfile("good", (model("g"),)))
    engine = IntelligentRouter(registry)
    engine.quota.observe(QuotaSnapshot("bad", remaining_requests=0))
    assert engine.route(TaskRequirements()).selected.provider_id == "good"
    for _ in range(3):
        engine.record_outcome("good", success=False, latency_ms=500)
    with pytest.raises(RoutingError):
        engine.route(TaskRequirements(excluded_providers=frozenset({"bad"})))
    engine.recover("good")
    assert engine.route(TaskRequirements(excluded_providers=frozenset({"bad"}))).selected.provider_id == "good"


def test_health_history_reduces_reliability():
    registry = ProviderRegistry()
    registry.register(ProviderProfile("p", (model("m", reliability=1.0),)))
    health = HealthTracker()
    for _ in range(3):
        health.record(HealthObservation("p", False, 100))
    engine = IntelligentRouter(registry, health=health)
    with pytest.raises(RoutingError):
        engine.route(TaskRequirements(minimum_reliability=0.5))


def test_failure_classification_is_safe_and_deterministic():
    assert classify_failure(429) is FailureClass.RATE_LIMIT
    assert classify_failure(503) is FailureClass.TRANSIENT
    assert classify_failure(401) is FailureClass.AUTHORIZATION
    assert classify_failure(422) is FailureClass.INVALID_REQUEST
    assert classify_failure(message="too many requests") is FailureClass.RATE_LIMIT
    assert classify_failure(message="provider disappeared") is FailureClass.UNKNOWN


def test_retry_economics_and_fallback_are_bounded():
    registry = ProviderRegistry()
    registry.register(ProviderProfile("a", (model("a", cost=1.0, quality=0.9),)))
    registry.register(ProviderProfile("b", (model("b", cost=1.2, quality=0.8),)))
    engine = IntelligentRouter(registry, policy=RoutePolicy(max_attempts=2, retry_multiplier=2.0))
    req = TaskRequirements()
    first = engine.route(req)
    assert first.estimated_worst_case_cost == pytest.approx(first.selected.estimated_cost * 3)
    second = engine.fallback(first, req, retryable_failure="429 rate limited")
    assert second.attempt == 2
    assert second.retryable_failure == "rate_limit"
    with pytest.raises(RoutingError):
        engine.fallback(second, req, retryable_failure="503")
    with pytest.raises(RoutingError):
        engine.fallback(first, req, retryable_failure="401 unauthorized")


def test_escalation_and_downgrade_controls():
    registry = ProviderRegistry()
    registry.register(ProviderProfile("a", (model("a", quality=0.7),)))
    registry.register(ProviderProfile("b", (model("b", quality=1.0, cost=0.5),)))
    policy = RoutePolicy(preference_bonus=15.0, escalation_margin=0.15)
    engine = IntelligentRouter(registry, policy=policy)
    req = TaskRequirements(preferred_models=("a",))
    first = engine.route(req)
    second = engine.fallback(first, req, retryable_failure="503 transient")
    assert second.escalation_level == 1
    assert second.selected.model_id == "b"


def test_estimate_and_token_forecast_are_conservative():
    registry, engine = router()
    req = TaskRequirements(estimated_input_tokens=100, estimated_output_tokens=100)
    assert engine.estimate(req, attempts=2) > 0
    assert engine.forecast_token_budget(req, [registry.get("cheap").models[0]]) >= 100


def test_stale_quota_observation_does_not_replace_newer_state():
    registry = ProviderRegistry()
    registry.register(ProviderProfile("p", (model("m"),)))
    from core.provider_intelligence.quota import QuotaTracker

    quota = QuotaTracker()
    newer = datetime(2026, 1, 1, 0, 0, 1, tzinfo=UTC)
    quota.observe(QuotaSnapshot("p", remaining_requests=0, observed_at=newer))
    quota.observe(
        QuotaSnapshot("p", remaining_requests=10, observed_at=datetime(2026, 1, 1, tzinfo=UTC))
    )
    assert not quota.available("p")

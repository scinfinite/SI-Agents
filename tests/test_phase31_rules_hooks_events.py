from __future__ import annotations

from pathlib import Path

import pytest

from core.events import Event, EventBus, EventName, EventSource, EventStore
from core.hooks import Hook, HookDecision, HookEngine, HookPhase, HookRegistry
from core.rules import Rule, RuleEffect, RuleEngine, RuleMatch, RuleRegistry, load_rules

ROOT = Path(__file__).resolve().parents[1]


def test_event_redacts_secret_like_payload_keys() -> None:
    event = Event(
        EventName.TOOL_BEFORE.value,
        EventSource.TOOL,
        "tool:git",
        {"token": "secret", "safe": "value"},
    )
    assert event.payload["token"] == "<redacted>"
    assert event.payload["safe"] == "value"


def test_event_rejects_unsupported_payload_values() -> None:
    with pytest.raises(TypeError, match="unsupported value"):
        Event(EventName.TASK_STARTED.value, EventSource.CORE, "task:1", {"value": object()})


def test_rule_registry_rejects_duplicates() -> None:
    registry = RuleRegistry()
    rule = Rule("r1", "rule", RuleMatch(events=(EventName.TASK_STARTED.value,)), RuleEffect.ALLOW)
    registry.register(rule)
    with pytest.raises(ValueError, match="duplicate"):
        registry.register(rule)


def test_rule_catalog_is_safe_and_deterministic() -> None:
    registry = load_rules(ROOT / "config" / "rules.v1.json")
    assert [rule.id for rule in registry.all()] == [
        "dangerous-tool-requires-approval",
        "credential-tool-requires-approval",
        "publication-requires-approval",
        "destructive-handoff-requires-approval",
    ]


def test_dangerous_events_fail_closed_without_a_rule() -> None:
    event = Event(EventName.TOOL_BEFORE.value, EventSource.TOOL, "tool:rm", {"dangerous": True})
    result = RuleEngine().evaluate(event)
    assert not result.allowed
    assert result.reasons == ("fail-closed: dangerous event has no matching rule",)


def test_event_bus_requires_approval_for_dangerous_tool() -> None:
    rules = RuleEngine(load_rules(ROOT / "config" / "rules.v1.json"))
    bus = EventBus(rules=rules)
    event = Event(EventName.TOOL_BEFORE.value, EventSource.TOOL, "tool:deploy", {"dangerous": True})
    blocked = bus.publish(event)
    assert not blocked.dispatched
    assert blocked.reason == "approval required"

    approved = bus.publish(
        Event(
            EventName.TOOL_BEFORE.value,
            EventSource.TOOL,
            "tool:deploy",
            {"dangerous": True, "approval_granted": True},
        )
    )
    assert approved.dispatched


def test_hooks_are_ordered_and_observer_failures_do_not_block() -> None:
    calls: list[str] = []

    def first(event: Event) -> None:
        calls.append("first")

    def second(event: Event) -> None:
        calls.append("second")
        raise RuntimeError("observer failed")

    registry = HookRegistry()
    registry.register(Hook("first", (EventName.TASK_STARTED.value,), first, priority=10))
    registry.register(Hook("second", (EventName.TASK_STARTED.value,), second, priority=20))
    reports = HookEngine(registry).run(
        Event(EventName.TASK_STARTED.value, EventSource.CORE, "task:1"), HookPhase.BEFORE
    )
    assert calls == ["first", "second"]
    assert [report.hook_id for report in reports] == ["first", "second"]
    assert reports[-1].error == "observer failed"


def test_gate_hook_denies_and_event_bus_stops_dispatch() -> None:
    def gate(event: Event) -> HookDecision:
        return HookDecision.DENY

    hooks = HookRegistry()
    hooks.register(Hook("deny", (EventName.TOOL_BEFORE.value,), gate, gate=True))
    bus = EventBus(hooks=HookEngine(hooks))
    result = bus.publish(Event(EventName.TOOL_BEFORE.value, EventSource.TOOL, "tool:test"))
    assert not result.dispatched
    assert result.reason == "blocked by gate hook"


def test_gate_hook_failure_fails_closed() -> None:
    def gate(event: Event) -> HookDecision:
        raise RuntimeError("boom")

    hooks = HookRegistry()
    hooks.register(Hook("broken", (EventName.TOOL_BEFORE.value,), gate, gate=True))
    bus = EventBus(hooks=HookEngine(hooks))
    result = bus.publish(Event(EventName.TOOL_BEFORE.value, EventSource.TOOL, "tool:test"))
    assert not result.dispatched
    assert "failed closed" in (result.reason or "")


def test_event_store_is_bounded() -> None:
    store = EventStore(max_events=2)
    for index in range(3):
        store.append(Event(EventName.TASK_STARTED.value, EventSource.CORE, f"task:{index}"))
    assert [event.subject for event in store.all()] == ["task:1", "task:2"]

from __future__ import annotations

from dataclasses import dataclass

from core.events.models import Event
from core.events.store import EventStore
from core.hooks.engine import HookEngine, HookExecutionError, HookReport
from core.hooks.models import HookDecision, HookPhase
from core.rules.engine import RuleEngine, RuleEvaluation


@dataclass(frozen=True)
class EventDispatchResult:
    event: Event
    rules: RuleEvaluation
    before_hooks: tuple[HookReport, ...]
    after_hooks: tuple[HookReport, ...]
    dispatched: bool
    reason: str | None = None


class EventBus:
    """Central event boundary connecting rules, hooks, and the bounded event journal."""

    def __init__(
        self,
        *,
        store: EventStore | None = None,
        rules: RuleEngine | None = None,
        hooks: HookEngine | None = None,
    ) -> None:
        self.store = store or EventStore()
        self.rules = rules or RuleEngine()
        self.hooks = hooks or HookEngine()

    def publish(self, event: Event) -> EventDispatchResult:
        self.store.append(event)
        evaluation = self.rules.evaluate(event)
        approval_granted = bool(event.payload.get("approval_granted", False))
        if not evaluation.allowed and not (evaluation.approval_required and approval_granted):
            return EventDispatchResult(
                event, evaluation, (), (), False,
                "approval required" if evaluation.approval_required else "blocked by rule",
            )

        try:
            before = self.hooks.run(event, HookPhase.BEFORE)
        except HookExecutionError as exc:
            return EventDispatchResult(event, evaluation, (), (), False, str(exc))
        if any(report.decision is not HookDecision.ALLOW for report in before):
            return EventDispatchResult(event, evaluation, before, (), False, "blocked by gate hook")

        try:
            after = self.hooks.run(event, HookPhase.AFTER)
        except HookExecutionError as exc:
            return EventDispatchResult(event, evaluation, before, (), False, str(exc))
        return EventDispatchResult(event, evaluation, before, after, True)

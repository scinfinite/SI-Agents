from __future__ import annotations

from dataclasses import dataclass

from core.events.models import Event
from core.rules.models import Rule, RuleEffect
from core.rules.registry import RuleRegistry


@dataclass(frozen=True)
class RuleEvaluation:
    """Deterministic policy signal; it does not grant permissions."""

    matched: tuple[str, ...]
    effects: tuple[RuleEffect, ...]
    allowed: bool
    approval_required: bool
    reasons: tuple[str, ...]


class RuleEngine:
    """Evaluate registered rules with deny/approval precedence and fail-closed defaults."""

    def __init__(self, registry: RuleRegistry | None = None) -> None:
        self.registry = registry or RuleRegistry()

    def evaluate(self, event: Event) -> RuleEvaluation:
        matched_rules = [rule for rule in self.registry.all() if rule.matches(event)]
        effects = tuple(rule.effect for rule in matched_rules)
        reasons = tuple(f"{rule.id}: {rule.description}" for rule in matched_rules)
        denied = any(effect is RuleEffect.DENY for effect in effects)
        approval = any(effect is RuleEffect.REQUIRE_APPROVAL for effect in effects)
        allowed = not denied and not approval
        if event.dangerous and not matched_rules:
            denied = True
            allowed = False
            reasons = ("fail-closed: dangerous event has no matching rule",)
        return RuleEvaluation(
            matched=tuple(rule.id for rule in matched_rules),
            effects=effects,
            allowed=allowed,
            approval_required=approval and not denied,
            reasons=reasons,
        )

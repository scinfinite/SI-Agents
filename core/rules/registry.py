from __future__ import annotations

from threading import RLock

from core.rules.models import Rule


class RuleRegistry:
    """Explicit process-local registration; duplicates are rejected."""

    def __init__(self) -> None:
        self._rules: dict[str, Rule] = {}
        self._lock = RLock()

    def register(self, rule: Rule) -> None:
        with self._lock:
            if rule.id in self._rules:
                raise ValueError(f"duplicate rule: {rule.id}")
            self._rules[rule.id] = rule

    def register_many(self, rules: tuple[Rule, ...] | list[Rule]) -> None:
        for rule in rules:
            self.register(rule)

    def get(self, rule_id: str) -> Rule:
        with self._lock:
            try:
                return self._rules[rule_id]
            except KeyError as exc:
                raise KeyError(f"unknown rule: {rule_id}") from exc

    def all(self) -> tuple[Rule, ...]:
        with self._lock:
            return tuple(sorted(self._rules.values(), key=lambda item: (item.priority, item.id)))

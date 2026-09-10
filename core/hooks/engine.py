from __future__ import annotations

from dataclasses import dataclass
from time import monotonic

from core.events.models import Event
from core.hooks.models import Hook, HookDecision, HookPhase
from core.hooks.registry import HookRegistry


class HookExecutionError(RuntimeError):
    """Raised when a gate hook fails closed or violates its execution budget."""


@dataclass(frozen=True)
class HookReport:
    hook_id: str
    decision: HookDecision
    duration_ms: float
    error: str | None = None


class HookEngine:
    """Invoke only registered in-process handlers; shell/command hooks are unsupported."""

    def __init__(self, registry: HookRegistry | None = None) -> None:
        self.registry = registry or HookRegistry()

    def run(self, event: Event, phase: HookPhase) -> tuple[HookReport, ...]:
        reports: list[HookReport] = []
        for hook in self.registry.matching(event.name, phase.value):
            started = monotonic()
            try:
                result = hook.handler(event)
                decision = result if isinstance(result, HookDecision) else HookDecision.ALLOW
                duration_ms = (monotonic() - started) * 1000
                if duration_ms > hook.max_runtime_ms:
                    raise HookExecutionError(
                        f"hook {hook.id} exceeded runtime budget ({duration_ms:.1f}ms > {hook.max_runtime_ms}ms)"
                    )
                if not hook.gate:
                    decision = HookDecision.ALLOW
                report = HookReport(hook.id, decision, duration_ms)
                reports.append(report)
                if hook.gate and decision is not HookDecision.ALLOW:
                    return tuple(reports)
            except Exception as exc:
                duration_ms = (monotonic() - started) * 1000
                report = HookReport(hook.id, HookDecision.DENY, duration_ms, str(exc))
                reports.append(report)
                if hook.gate:
                    raise HookExecutionError(f"gate hook failed closed: {hook.id}") from exc
        return tuple(reports)

from collections.abc import Iterable

from core.orchestrator.plan_models import Plan, PlanStep


class PlanValidationError(ValueError):
    """Raised when a plan is structurally unsafe or inconsistent."""


def topological_order(steps: Iterable[PlanStep]) -> tuple[PlanStep, ...]:
    items = tuple(steps)
    by_id = {step.id: step for step in items}
    if len(by_id) != len(items):
        raise PlanValidationError("Plan contains duplicate step IDs")
    indegree = {step.id: len(step.dependencies) for step in items}
    dependents: dict[str, list[str]] = {step.id: [] for step in items}
    for step in items:
        for dependency in step.dependencies:
            if dependency not in by_id:
                raise PlanValidationError(f"Unknown plan dependency: {dependency}")
            dependents[dependency].append(step.id)
    ready = sorted(step_id for step_id, degree in indegree.items() if degree == 0)
    ordered: list[PlanStep] = []
    while ready:
        current = ready.pop(0)
        ordered.append(by_id[current])
        for dependent in sorted(dependents[current]):
            indegree[dependent] -= 1
            if indegree[dependent] == 0:
                ready.append(dependent)
        ready.sort()
    if len(ordered) != len(items):
        raise PlanValidationError("Plan contains a dependency cycle")
    return tuple(ordered)


def validate_plan(plan: Plan) -> Plan:
    topological_order(plan.steps)
    return plan

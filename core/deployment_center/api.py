"""Transport-neutral deployment projections used by operator surfaces."""

from __future__ import annotations

from .service import DeploymentCenter


def snapshot(center: DeploymentCenter) -> dict[str, object]:
    return {
        "targets": [target.as_dict() for target in center.targets()],
        "plans": [plan.as_dict() for plan in center.all()],
        "authority": "planning-only; deployment execution is a separate governed boundary",
    }


def create(center: DeploymentCenter, payload: dict[str, object]) -> dict[str, object]:
    def strings(key: str) -> tuple[str, ...]:
        value = payload.get(key, [])
        if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
            raise ValueError(f"{key} must be a list of strings")
        return tuple(value)

    plan_id = payload.get("id")
    harness_id = payload.get("harness_id")
    if not isinstance(plan_id, str) or not plan_id.strip():
        raise ValueError("id is required")
    if not isinstance(harness_id, str) or not harness_id.strip():
        raise ValueError("harness_id is required")
    return center.plan(plan_id, harness_id, strings("agents"), strings("teams"), strings("skills"),
                       strings("capabilities"), strings("permissions")).as_dict()

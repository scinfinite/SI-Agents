"""Deployment planning and validation without execution authority."""

from __future__ import annotations

from pathlib import Path
from threading import RLock

from core.runtime.deployment import HarnessDeploymentManifest, build_manifest

from .models import DeploymentPlan, DeploymentState, HarnessTarget


class DeploymentCenter:
    """Inspect, validate, and prepare harness deployment plans.

    Applying a plan is intentionally outside this service. This boundary can
    produce a manifest, but cannot enable adapters, invoke workers, or move credentials.
    """

    def __init__(self, root: str | Path):
        self.root = Path(root).resolve()
        self._lock = RLock()
        self._plans: dict[str, DeploymentPlan] = {}

    def targets(self) -> tuple[HarnessTarget, ...]:
        adapters = self.root / "adapters"
        if not adapters.exists():
            return ()
        result = []
        for path in sorted(adapters.iterdir()):
            if path.is_dir() and not path.name.startswith("."):
                result.append(HarnessTarget(path.name, "unknown", str(path.relative_to(self.root))))
        return tuple(result)

    def plan(
        self,
        plan_id: str,
        harness_id: str,
        agents: tuple[str, ...],
        teams: tuple[str, ...],
        skills: tuple[str, ...] = (),
        capabilities: tuple[str, ...] = (),
        permissions: tuple[str, ...] = (),
    ) -> DeploymentPlan:
        target_ids = {target.id for target in self.targets()}
        reasons: list[str] = []
        if harness_id not in target_ids:
            reasons.append("harness target is not registered")
        if capabilities:
            reasons.append("requested capabilities require existing governance authorization")
        if permissions:
            reasons.append("requested permissions require existing governance authorization")
        state = DeploymentState.BLOCKED if reasons else DeploymentState.VALID
        result = DeploymentPlan(
            plan_id, harness_id, tuple(sorted(set(agents))), tuple(sorted(set(teams))),
            tuple(sorted(set(skills))), tuple(sorted(set(capabilities))), tuple(sorted(set(permissions))),
            state, tuple(reasons),
        )
        with self._lock:
            self._plans[plan_id] = result
        return result

    def get(self, plan_id: str) -> DeploymentPlan:
        with self._lock:
            if plan_id not in self._plans:
                raise KeyError(plan_id)
            return self._plans[plan_id]

    def all(self) -> tuple[DeploymentPlan, ...]:
        with self._lock:
            return tuple(self._plans[key] for key in sorted(self._plans))

    def manifest(self, plan_id: str, *, agent_definitions=(), team_definitions=()) -> HarnessDeploymentManifest:
        plan = self.get(plan_id)
        if plan.state is not DeploymentState.VALID:
            raise PermissionError("deployment plan is not valid")
        if plan.requested_capabilities or plan.requested_permissions:
            raise PermissionError("deployment plan contains authority-bearing requests")
        return build_manifest(plan.harness_id, tuple(agent_definitions), tuple(team_definitions), skills=plan.skills)

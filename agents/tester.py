from __future__ import annotations

from collections.abc import Callable

from agents.base import AgentContext, AgentResult, AgentSpec
from core.policies.permission_engine import PermissionEngine


class TesterAgent:
    spec = AgentSpec(
        name="tester",
        responsibility="Validate repaired behavior, attack likely regressions, and report only observed results.",
        deliverables=("verification result", "red-team result", "regression result"),
        success_criteria=("target test passes", "negative/adversarial checks pass", "regression suite passes"),
        boundaries=("does not modify production code", "does not convert failures into success", "does not bypass evidence recording"),
        required_permissions=("test_execute",),
    )

    def run(self, context: AgentContext, verify: Callable[[], bool], red_team: Callable[[], bool], regression: Callable[[], bool], *, permissions: PermissionEngine, agent_name: str = "tester") -> AgentResult:
        permissions.require("local_command", agent=agent_name)
        for name, check in (("verification", verify), ("red_team", red_team), ("regression", regression)):
            if not check():
                context.values[name] = False
                raise RuntimeError(f"Tester stage failed: {name}")
            context.values[name] = True
        return AgentResult(self.spec.name, "succeeded", "Verification, red-team, and regression checks passed", handoff={"verified": True})

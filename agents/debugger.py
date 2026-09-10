from __future__ import annotations

from collections.abc import Callable

from agents.base import AgentContext, AgentResult, AgentSpec
from core.policies.permission_engine import PermissionEngine


class DebuggerAgent:
    spec = AgentSpec(
        name="debugger",
        responsibility="Reproduce failures, test causal hypotheses, and identify the smallest justified repair.",
        deliverables=("reproduction result", "ranked root-cause hypothesis", "repair recommendation"),
        success_criteria=("failure reproduced when expected", "hypothesis is evidence-backed", "repair scope is minimal"),
        boundaries=("does not silently modify files", "does not bypass permissions", "does not claim unverified fixes"),
        required_permissions=("repository_read",),
    )

    def run(self, context: AgentContext, reproduce: Callable[[], bool], diagnose: Callable[[], str], *, permissions: PermissionEngine, agent_name: str = "debugger") -> AgentResult:
        permissions.require("repository_read", agent=agent_name)
        if not reproduce():
            raise RuntimeError("Debugger could not reproduce the expected failure")
        diagnosis = diagnose().strip()
        if not diagnosis:
            raise RuntimeError("Debugger produced no root-cause hypothesis")
        context.values["failure_reproduced"] = True
        context.values["root_cause"] = diagnosis
        return AgentResult(self.spec.name, "succeeded", "Failure reproduced and root cause identified", handoff={"root_cause": diagnosis})

from __future__ import annotations

from collections.abc import Callable

from agents.base import AgentContext, AgentResult, AgentSpec
from core.policies.permission_engine import PermissionEngine


class DeveloperAgent:
    spec = AgentSpec(
        name="developer",
        responsibility="Apply the smallest maintainable repair justified by inspection and diagnosis.",
        deliverables=("minimal code change", "repair summary", "changed behavior"),
        success_criteria=("repair addresses the diagnosed cause", "scope remains minimal", "execution uses approved tooling"),
        boundaries=("does not ignore the debugger handoff", "does not grant itself permissions", "does not declare verification complete"),
        required_permissions=("workspace_write",),
    )

    def run(self, context: AgentContext, repair: Callable[[str], str], *, permissions: PermissionEngine, agent_name: str = "developer") -> AgentResult:
        permissions.require("workspace_write", agent=agent_name)
        root_cause = str(context.require("root_cause"))
        change = repair(root_cause).strip()
        if not change:
            raise RuntimeError("Developer produced no repair result")
        context.values["repair"] = change
        return AgentResult(self.spec.name, "succeeded", "Minimal repair applied", handoff={"repair": change})

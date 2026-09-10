from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum

from core.organization.models import AgentDefinition, Division


class WorkflowStepKind(StrEnum):
    DISCOVERY = "discovery"
    PLANNING = "planning"
    EXECUTION = "execution"
    REVIEW = "review"
    VERIFICATION = "verification"
    HANDOFF = "handoff"


@dataclass(frozen=True)
class TeamDefinition:
    id: str
    name: str
    purpose: str
    division_ids: tuple[str, ...]
    member_agent_ids: tuple[str, ...]
    lead_agent_id: str

    def __post_init__(self) -> None:
        _require_id(self.id, "team id")
        if not self.name.strip() or not self.purpose.strip():
            raise ValueError("Team name and purpose are required")
        if not self.division_ids or not self.member_agent_ids:
            raise ValueError("Team must declare divisions and members")
        if len(self.division_ids) != len(set(self.division_ids)):
            raise ValueError(f"Team {self.id} has duplicate divisions")
        if len(self.member_agent_ids) != len(set(self.member_agent_ids)):
            raise ValueError(f"Team {self.id} has duplicate members")
        if self.lead_agent_id not in self.member_agent_ids:
            raise ValueError(f"Team {self.id} lead must be a member")


@dataclass(frozen=True)
class WorkflowStep:
    id: str
    kind: WorkflowStepKind
    team_id: str
    agent_id: str
    purpose: str
    depends_on: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        _require_id(self.id, "workflow step id")
        if not self.purpose.strip():
            raise ValueError("Workflow step purpose is required")
        if len(self.depends_on) != len(set(self.depends_on)):
            raise ValueError(f"Workflow step {self.id} has duplicate dependencies")


@dataclass(frozen=True)
class WorkflowDefinition:
    id: str
    name: str
    purpose: str
    steps: tuple[WorkflowStep, ...]

    def __post_init__(self) -> None:
        _require_id(self.id, "workflow id")
        if not self.name.strip() or not self.purpose.strip():
            raise ValueError("Workflow name and purpose are required")
        if len(self.steps) < 2:
            raise ValueError(f"Workflow {self.id} must contain at least two steps")
        step_ids = tuple(step.id for step in self.steps)
        if len(step_ids) != len(set(step_ids)):
            raise ValueError(f"Workflow {self.id} has duplicate step ids")
        if not any(step.kind is WorkflowStepKind.VERIFICATION for step in self.steps):
            raise ValueError(f"Workflow {self.id} must include a verification step")


@dataclass(frozen=True)
class DivisionAssignment:
    division_id: str
    team_id: str
    rationale: str

    def __post_init__(self) -> None:
        _require_id(self.division_id, "division id")
        _require_id(self.team_id, "team id")
        if not self.rationale.strip():
            raise ValueError("Division assignment rationale is required")


@dataclass(frozen=True)
class OrganizationExpansion:
    version: int
    teams: tuple[TeamDefinition, ...]
    division_assignments: tuple[DivisionAssignment, ...]
    workflows: tuple[WorkflowDefinition, ...]

    def validate(
        self,
        divisions: tuple[Division, ...],
        agents: tuple[AgentDefinition, ...],
    ) -> tuple[str, ...]:
        errors: list[str] = []
        if self.version != 1:
            errors.append(f"unsupported organization expansion version: {self.version}")

        division_ids = {division.id for division in divisions}
        agent_ids = {agent.id for agent in agents}
        team_ids = {team.id for team in self.teams}
        assignment_by_division = {assignment.division_id: assignment.team_id for assignment in self.division_assignments}

        if len(team_ids) != len(self.teams):
            errors.append("duplicate team ids")

        assigned = [assignment.division_id for assignment in self.division_assignments]
        if len(assigned) != len(set(assigned)):
            errors.append("duplicate division assignments")
        missing_divisions = sorted(division_ids - set(assigned))
        extra_divisions = sorted(set(assigned) - division_ids)
        if missing_divisions:
            errors.append("unassigned divisions: " + ", ".join(missing_divisions))
        if extra_divisions:
            errors.append("unknown assigned divisions: " + ", ".join(extra_divisions))

        for team in self.teams:
            missing_team_divisions = sorted(set(team.division_ids) - division_ids)
            missing_members = sorted(set(team.member_agent_ids) - agent_ids)
            if missing_team_divisions:
                errors.append(f"team {team.id} references unknown divisions: {', '.join(missing_team_divisions)}")
            if missing_members:
                errors.append(f"team {team.id} references unknown agents: {', '.join(missing_members)}")
            for division_id in team.division_ids:
                assigned_team = assignment_by_division.get(division_id)
                if assigned_team is not None and assigned_team != team.id:
                    errors.append(
                        f"team {team.id} lists division {division_id}, but it is assigned to {assigned_team}"
                    )

        for assignment in self.division_assignments:
            if assignment.team_id not in team_ids:
                errors.append(f"division {assignment.division_id} references unknown team {assignment.team_id}")
            elif assignment.division_id in division_ids:
                team = next(team for team in self.teams if team.id == assignment.team_id)
                if assignment.division_id not in team.division_ids:
                    errors.append(
                        f"division {assignment.division_id} is assigned to {assignment.team_id}, "
                        "but that team does not declare the division"
                    )

        for workflow in self.workflows:
            step_ids = {step.id for step in workflow.steps}
            seen: set[str] = set()
            for step in workflow.steps:
                if step.team_id not in team_ids:
                    errors.append(f"workflow {workflow.id} step {step.id} references unknown team {step.team_id}")
                if step.agent_id not in agent_ids:
                    errors.append(f"workflow {workflow.id} step {step.id} references unknown agent {step.agent_id}")
                elif step.team_id in team_ids:
                    team = next(team for team in self.teams if team.id == step.team_id)
                    if step.agent_id not in team.member_agent_ids:
                        errors.append(f"workflow {workflow.id} step {step.id} agent is not a member of {step.team_id}")
                unknown_dependencies = sorted(set(step.depends_on) - step_ids)
                if unknown_dependencies:
                    errors.append(
                        f"workflow {workflow.id} step {step.id} has unknown dependencies: "
                        + ", ".join(unknown_dependencies)
                    )
                if step.id in step.depends_on:
                    errors.append(f"workflow {workflow.id} step {step.id} cannot depend on itself")
                if any(dependency not in seen for dependency in step.depends_on):
                    errors.append(f"workflow {workflow.id} step {step.id} depends on a later step")
                seen.add(step.id)

        return tuple(errors)


def _require_id(value: str, label: str) -> None:
    if not value or value != value.strip() or any(char not in "abcdefghijklmnopqrstuvwxyz0123456789-_" for char in value):
        raise ValueError(f"Invalid {label}: {value!r}")

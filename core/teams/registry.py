from __future__ import annotations

from core.teams.models import TeamDefinition


class TeamRegistry:
    """Canonical registry for declarative teams; registration never grants execution authority."""

    def __init__(self) -> None:
        self._teams: dict[str, TeamDefinition] = {}

    def register(self, team: TeamDefinition) -> TeamDefinition:
        if team.id in self._teams:
            raise ValueError(f"Duplicate team id: {team.id}")
        if any(existing.name == team.name for existing in self._teams.values()):
            raise ValueError(f"Duplicate team name: {team.name}")
        self._teams[team.id] = team
        return team

    def get(self, team_id: str) -> TeamDefinition:
        try:
            return self._teams[team_id]
        except KeyError as exc:
            raise KeyError(f"Unknown team: {team_id}") from exc

    def all(self) -> tuple[TeamDefinition, ...]:
        return tuple(self._teams.values())

    def validate(self) -> tuple[str, ...]:
        errors: list[str] = []
        for team in self._teams.values():
            task_ids = {task.id for task in team.tasks}
            for task in team.tasks:
                missing = set(task.depends_on) - task_ids
                if missing:
                    errors.append(f"team {team.id} task {task.id} has missing dependencies: {sorted(missing)}")
        return tuple(errors)

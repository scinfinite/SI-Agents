from __future__ import annotations

from collections.abc import Callable
from concurrent.futures import ThreadPoolExecutor, as_completed
from copy import deepcopy
from threading import Event

from agents.base import AgentContext, AgentResult, AgentWorker
from core.teams.models import (
    ContextMode,
    TaskDefinition,
    TaskStatus,
    TeamDefinition,
    TeamExecution,
    WorkflowEventType,
)
from core.teams.registry import TeamRegistry

WorkerResolver = Callable[[str], AgentWorker]


class TeamEngine:
    """Execute bounded, dependency-aware agent teams without owning agent permissions."""

    def __init__(self, registry: TeamRegistry | None = None) -> None:
        self.registry = registry or TeamRegistry()

    def run(
        self,
        team_id: str,
        *,
        initial_context: dict[str, object] | None = None,
        resolve_worker: WorkerResolver,
        cancellation: Event | None = None,
    ) -> TeamExecution:
        team = self.registry.get(team_id)
        self._validate_acyclic(team)
        cancel_event = cancellation or Event()
        execution = TeamExecution(team_id=team.id, context=deepcopy(initial_context or {}))
        execution.task_status = {task.id: TaskStatus.PENDING for task in team.tasks}
        execution.attempts = {task.id: 0 for task in team.tasks}
        execution.status = TaskStatus.RUNNING
        execution.emit(WorkflowEventType.WORKFLOW_STARTED, data={"team": team.id})

        task_map = {task.id: task for task in team.tasks}
        while True:
            if cancel_event.is_set():
                self._cancel_pending(execution)
                execution.status = TaskStatus.CANCELLED
                execution.emit(WorkflowEventType.WORKFLOW_CANCELLED)
                return execution

            ready = self._ready_tasks(execution, task_map)
            if not ready:
                self._skip_blocked(execution, task_map)
                if all(status.terminal for status in execution.task_status.values()):
                    break
                if not any(status is TaskStatus.RUNNING for status in execution.task_status.values()):
                    execution.errors.append("workflow made no progress; dependency graph is unsatisfied")
                    execution.status = TaskStatus.FAILED
                    execution.emit(WorkflowEventType.WORKFLOW_FAILED, data={"reason": execution.errors[-1]})
                    return execution
                continue

            for task in ready:
                execution.emit(WorkflowEventType.TASK_READY, task_id=task.id)

            batch = ready[: team.max_parallelism]
            for task in batch:
                execution.task_status[task.id] = TaskStatus.RUNNING
            with ThreadPoolExecutor(max_workers=team.max_parallelism) as pool:
                futures = {
                    pool.submit(self._run_task, task, execution, resolve_worker, cancel_event): task
                    for task in batch
                }
                for future in as_completed(futures):
                    task = futures[future]
                    result = future.result()
                    execution.task_status[task.id] = result[0]
                    execution.results[task.id] = result[1]
                    if result[2]:
                        execution.errors.append(result[2])
                    if result[3]:
                        execution.context.update(result[3])

        if any(status is TaskStatus.FAILED for status in execution.task_status.values()):
            execution.status = TaskStatus.FAILED
            execution.emit(WorkflowEventType.WORKFLOW_FAILED, data={"errors": tuple(execution.errors)})
            return execution
        if any(status is TaskStatus.CANCELLED for status in execution.task_status.values()):
            execution.status = TaskStatus.CANCELLED
            execution.emit(WorkflowEventType.WORKFLOW_CANCELLED)
            return execution

        if team.required_evidence and not self._has_evidence(execution):
            execution.errors.append("team completed without required evidence")
            execution.status = TaskStatus.FAILED
            execution.emit(WorkflowEventType.WORKFLOW_FAILED, data={"reason": execution.errors[-1]})
            return execution

        execution.status = TaskStatus.SUCCEEDED
        execution.checkpoints.append("final-gate")
        execution.emit(
            WorkflowEventType.CHECKPOINT,
            data={"name": "final-gate", "evidence": self._evidence_ids(execution)},
        )
        execution.emit(WorkflowEventType.WORKFLOW_COMPLETED, data={"evidence": self._evidence_ids(execution)})
        return execution

    def _run_task(
        self,
        task: TaskDefinition,
        execution: TeamExecution,
        resolve_worker: WorkerResolver,
        cancellation: Event,
    ) -> tuple[TaskStatus, AgentResult | None, str | None, dict[str, object]]:
        if cancellation.is_set():
            return TaskStatus.CANCELLED, None, "workflow cancelled", {}

        context_values = deepcopy(execution.context)
        context = AgentContext(task_id=task.id, values=context_values)
        last_error: str | None = None
        execution.emit(WorkflowEventType.TASK_STARTED, task_id=task.id)
        for attempt in range(1, task.max_attempts + 1):
            execution.attempts[task.id] = attempt
            try:
                worker = resolve_worker(task.agent_id)
                result = worker(context)
                self._validate_result(task, result)
                handoff = dict(result.handoff)
                if task.context_mode is ContextMode.SHARED:
                    handoff = {**context.values, **handoff}
                execution.emit(
                    WorkflowEventType.TASK_SUCCEEDED,
                    task_id=task.id,
                    data={"attempt": attempt, "agent": result.agent},
                )
                return TaskStatus.SUCCEEDED, result, None, handoff
            except Exception as exc:  # noqa: BLE001 - worker boundary normalizes arbitrary failures
                last_error = str(exc) or exc.__class__.__name__
                if attempt < task.max_attempts:
                    execution.emit(
                        WorkflowEventType.TASK_RETRY,
                        task_id=task.id,
                        data={"attempt": attempt, "reason": last_error},
                    )

        if task.escalate_to is not None and not cancellation.is_set():
            try:
                escalation_context = AgentContext(task_id=f"{task.id}:escalation", values=deepcopy(context.values))
                escalation = resolve_worker(task.escalate_to)(escalation_context)
                self._validate_result(task, escalation, allow_verification=False)
                execution.emit(
                    WorkflowEventType.TASK_ESCALATED,
                    task_id=task.id,
                    data={"to": task.escalate_to, "agent": escalation.agent},
                )
                return TaskStatus.ESCALATED, escalation, last_error, dict(escalation.handoff)
            except Exception as exc:  # noqa: BLE001 - escalation is an agent boundary
                last_error = f"{last_error}; escalation failed: {exc}"

        execution.emit(WorkflowEventType.TASK_FAILED, task_id=task.id, data={"reason": last_error})
        return TaskStatus.FAILED, None, f"task {task.id} failed: {last_error}", {}

    @staticmethod
    def _validate_result(
        task: TaskDefinition,
        result: AgentResult,
        *,
        allow_verification: bool = True,
    ) -> None:
        if result.status != "succeeded":
            raise RuntimeError(f"agent returned non-success status: {result.status}")
        if task.requires_evidence and not result.evidence_ids:
            raise RuntimeError("task requires evidence but agent returned none")
        if allow_verification and task.verification_gate and not bool(result.handoff.get("verified")):
            raise RuntimeError("verification gate requires handoff['verified'] == true")

    @staticmethod
    def _ready_tasks(execution: TeamExecution, task_map: dict[str, TaskDefinition]) -> list[TaskDefinition]:
        ready: list[TaskDefinition] = []
        for task in task_map.values():
            if execution.task_status[task.id] is not TaskStatus.PENDING:
                continue
            dependency_statuses = [execution.task_status[dep] for dep in task.depends_on]
            if all(status in {TaskStatus.SUCCEEDED, TaskStatus.ESCALATED} for status in dependency_statuses):
                ready.append(task)
        return ready

    @staticmethod
    def _skip_blocked(execution: TeamExecution, task_map: dict[str, TaskDefinition]) -> None:
        for task in task_map.values():
            if execution.task_status[task.id] is not TaskStatus.PENDING:
                continue
            dependency_statuses = [execution.task_status[dep] for dep in task.depends_on]
            if any(status in {TaskStatus.FAILED, TaskStatus.CANCELLED, TaskStatus.SKIPPED} for status in dependency_statuses):
                execution.task_status[task.id] = TaskStatus.SKIPPED
                execution.emit(
                    WorkflowEventType.TASK_SKIPPED,
                    task_id=task.id,
                    data={"reason": "dependency did not complete successfully"},
                )

    @staticmethod
    def _cancel_pending(execution: TeamExecution) -> None:
        for task_id, status in tuple(execution.task_status.items()):
            if status is TaskStatus.PENDING:
                execution.task_status[task_id] = TaskStatus.CANCELLED

    @staticmethod
    def _validate_acyclic(team: TeamDefinition) -> None:
        task_map = {task.id: task for task in team.tasks}
        visiting: set[str] = set()
        visited: set[str] = set()

        def visit(task_id: str) -> None:
            if task_id in visiting:
                raise ValueError(f"workflow dependency cycle detected at {task_id}")
            if task_id in visited:
                return
            visiting.add(task_id)
            for dependency in task_map[task_id].depends_on:
                visit(dependency)
            visiting.remove(task_id)
            visited.add(task_id)

        for task_id in task_map:
            visit(task_id)

    @staticmethod
    def _evidence_ids(execution: TeamExecution) -> tuple[str, ...]:
        evidence: list[str] = []
        for result in execution.results.values():
            if isinstance(result, AgentResult):
                evidence.extend(result.evidence_ids)
        return tuple(dict.fromkeys(evidence))

    @staticmethod
    def _has_evidence(execution: TeamExecution) -> bool:
        return bool(TeamEngine._evidence_ids(execution))

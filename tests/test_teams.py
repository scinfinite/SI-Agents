from __future__ import annotations

# isort: skip_file

import threading
import time
import unittest

from agents.base import AgentResult
from core.teams.engine import TeamEngine
from core.teams.models import ContextMode, TaskDefinition, TaskStatus, TeamDefinition, WorkflowEventType
from core.teams.registry import TeamRegistry


class TeamEngineTests(unittest.TestCase):
    def make_team(self, *tasks: TaskDefinition, parallelism: int = 1, evidence: bool = True) -> TeamDefinition:
        members = tuple(dict.fromkeys([task.agent_id for task in tasks] + [task.escalate_to for task in tasks if task.escalate_to]))
        return TeamDefinition(
            id="test-team",
            name="Test Team",
            description="team engine acceptance fixture",
            members=members,
            tasks=tasks,
            max_parallelism=parallelism,
            required_evidence=evidence,
        )

    @staticmethod
    def resolver(workers: dict[str, object]):
        return lambda agent_id: workers[agent_id]

    def test_dependency_handoff_and_final_evidence_gate(self) -> None:
        def planner(context):
            return AgentResult("planner", "succeeded", "planned", evidence_ids=("plan-1",), handoff={"plan": "approved"})

        def builder(context):
            self.assertEqual(context.require("plan"), "approved")
            return AgentResult("builder", "succeeded", "built", evidence_ids=("build-1",), handoff={"verified": True})

        team = self.make_team(
            TaskDefinition("plan", "planner", context_mode=ContextMode.SHARED, requires_evidence=True),
            TaskDefinition("build", "builder", depends_on=("plan",), context_mode=ContextMode.SHARED, requires_evidence=True),
        )
        registry = TeamRegistry()
        registry.register(team)
        execution = TeamEngine(registry).run(
            team.id,
            resolve_worker=self.resolver({"planner": planner, "builder": builder}),
        )
        self.assertEqual(execution.status, TaskStatus.SUCCEEDED)
        self.assertEqual(execution.task_status["plan"], TaskStatus.SUCCEEDED)
        self.assertEqual(execution.task_status["build"], TaskStatus.SUCCEEDED)
        self.assertIn("final-gate", execution.checkpoints)
        self.assertEqual(execution.context["plan"], "approved")
        self.assertIn(WorkflowEventType.WORKFLOW_COMPLETED, [event.type for event in execution.events])

    def test_parallelism_is_bounded(self) -> None:
        active = 0
        peak = 0
        lock = threading.Lock()

        def worker(context):
            nonlocal active, peak
            with lock:
                active += 1
                peak = max(peak, active)
            time.sleep(0.03)
            with lock:
                active -= 1
            return AgentResult("worker", "succeeded", context.task_id, evidence_ids=(context.task_id,))

        tasks = tuple(TaskDefinition(f"task-{index}", "worker", context_mode=ContextMode.ISOLATED) for index in range(5))
        registry = TeamRegistry()
        registry.register(self.make_team(*tasks, parallelism=2))
        execution = TeamEngine(registry).run("test-team", resolve_worker=self.resolver({"worker": worker}))
        self.assertEqual(execution.status, TaskStatus.SUCCEEDED)
        self.assertLessEqual(peak, 2)
        self.assertEqual(len([status for status in execution.task_status.values() if status is TaskStatus.SUCCEEDED]), 5)

    def test_retry_then_success(self) -> None:
        calls = 0

        def flaky(context):
            nonlocal calls
            calls += 1
            if calls < 2:
                raise RuntimeError("transient")
            return AgentResult("flaky", "succeeded", "recovered", evidence_ids=("retry-ok",))

        registry = TeamRegistry()
        registry.register(self.make_team(TaskDefinition("retry", "flaky", max_attempts=2)))
        execution = TeamEngine(registry).run("test-team", resolve_worker=self.resolver({"flaky": flaky}))
        self.assertEqual(execution.status, TaskStatus.SUCCEEDED)
        self.assertEqual(execution.attempts["retry"], 2)
        self.assertTrue(any(event.type is WorkflowEventType.TASK_RETRY for event in execution.events))

    def test_escalation_recovers_failed_task(self) -> None:
        def primary(context):
            raise RuntimeError("primary failed")

        def escalation(context):
            return AgentResult("senior", "succeeded", "escalated recovery", evidence_ids=("escalated-ok",))

        registry = TeamRegistry()
        registry.register(self.make_team(TaskDefinition("work", "primary", escalate_to="senior")))
        execution = TeamEngine(registry).run(
            "test-team",
            resolve_worker=self.resolver({"primary": primary, "senior": escalation}),
        )
        self.assertEqual(execution.status, TaskStatus.SUCCEEDED)
        self.assertEqual(execution.task_status["work"], TaskStatus.ESCALATED)
        self.assertTrue(any(event.type is WorkflowEventType.TASK_ESCALATED for event in execution.events))

    def test_verification_gate_rejects_unverified_result(self) -> None:
        def worker(context):
            return AgentResult("worker", "succeeded", "done", evidence_ids=("evidence",))

        registry = TeamRegistry()
        registry.register(self.make_team(TaskDefinition("verify", "worker", verification_gate=True)))
        execution = TeamEngine(registry).run("test-team", resolve_worker=self.resolver({"worker": worker}))
        self.assertEqual(execution.status, TaskStatus.FAILED)
        self.assertEqual(execution.task_status["verify"], TaskStatus.FAILED)
        self.assertIn("verification gate", execution.errors[0])

    def test_failed_dependency_skips_downstream_task(self) -> None:
        def fail(context):
            raise RuntimeError("blocked")

        def downstream(context):
            raise AssertionError("must not run")

        registry = TeamRegistry()
        registry.register(
            self.make_team(
                TaskDefinition("first", "fail"),
                TaskDefinition("second", "downstream", depends_on=("first",)),
                evidence=False,
            )
        )
        execution = TeamEngine(registry).run(
            "test-team",
            resolve_worker=self.resolver({"fail": fail, "downstream": downstream}),
        )
        self.assertEqual(execution.status, TaskStatus.FAILED)
        self.assertEqual(execution.task_status["second"], TaskStatus.SKIPPED)

    def test_cancellation_prevents_dispatch(self) -> None:
        cancellation = threading.Event()
        cancellation.set()
        called = False

        def worker(context):
            nonlocal called
            called = True
            return AgentResult("worker", "succeeded", "unexpected", evidence_ids=("x",))

        registry = TeamRegistry()
        registry.register(self.make_team(TaskDefinition("work", "worker")))
        execution = TeamEngine(registry).run(
            "test-team", resolve_worker=self.resolver({"worker": worker}), cancellation=cancellation
        )
        self.assertEqual(execution.status, TaskStatus.CANCELLED)
        self.assertFalse(called)
        self.assertEqual(execution.task_status["work"], TaskStatus.CANCELLED)

    def test_cycle_is_rejected(self) -> None:
        registry = TeamRegistry()
        registry.register(
            self.make_team(
                TaskDefinition("a", "worker", depends_on=("b",)),
                TaskDefinition("b", "worker", depends_on=("a",)),
                evidence=False,
            )
        )
        with self.assertRaisesRegex(ValueError, "cycle"):
            TeamEngine(registry).run("test-team", resolve_worker=self.resolver({"worker": lambda context: None}))

    def test_registry_rejects_duplicate_team_name(self) -> None:
        registry = TeamRegistry()
        team = self.make_team(TaskDefinition("one", "worker"), evidence=False)
        registry.register(team)
        with self.assertRaisesRegex(ValueError, "Duplicate team name"):
            registry.register(
                TeamDefinition(
                    id="other-team",
                    name=team.name,
                    description=team.description,
                    members=team.members,
                    tasks=team.tasks,
                )
            )


if __name__ == "__main__":
    unittest.main()

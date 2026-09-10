from dataclasses import dataclass

from core.capabilities.models import Capability
from core.capabilities.registry import CapabilityRegistry
from core.orchestrator.brain_models import Decomposition, Problem, Subtask
from core.orchestrator.capability_selector import CapabilitySelector
from core.orchestrator.plan_engine import validate_plan
from core.orchestrator.plan_models import Plan, PlanStep, StepKind


@dataclass(frozen=True)
class BrainResult:
    problem: Problem
    decomposition: Decomposition
    plan: Plan
    selected_capabilities: tuple[Capability, ...] = ()


class EngineeringBrain:
    """Deterministic engineering-planning substrate with explicit validation boundaries."""

    def __init__(self, capabilities: CapabilityRegistry | None = None) -> None:
        self.capabilities = capabilities or CapabilityRegistry()
        self.selector = CapabilitySelector(self.capabilities)

    def decompose(self, problem: Problem) -> Decomposition:
        subtasks = tuple(
            Subtask(
                description=criterion,
                acceptance_criteria=(criterion,),
                rationale="Derived directly from a declared acceptance criterion.",
            )
            for criterion in problem.acceptance_criteria
        )
        return Decomposition(
            problem_id=problem.id,
            subtasks=subtasks,
            strategy="acceptance-criteria decomposition",
            assumptions=problem.context,
        )

    def plan(self, problem: Problem, decomposition: Decomposition | None = None) -> Plan:
        decomposition = decomposition or self.decompose(problem)
        steps: list[PlanStep] = []
        for subtask in decomposition.subtasks:
            inspect = PlanStep(
                description=f"Inspect evidence relevant to: {subtask.description}",
                kind=StepKind.INSPECT,
                expected_evidence=subtask.acceptance_criteria,
            )
            steps.append(inspect)
            research = PlanStep(
                description=f"Research alternatives and constraints for: {subtask.description}",
                kind=StepKind.RESEARCH,
                dependencies=(inspect.id,),
            )
            steps.append(research)
            execute = PlanStep(
                description=f"Implement the smallest justified change for: {subtask.description}",
                kind=StepKind.EXECUTE,
                dependencies=(research.id,),
            )
            steps.append(execute)
            test = PlanStep(
                description=f"Test: {subtask.description}",
                kind=StepKind.TEST,
                dependencies=(execute.id,),
                expected_evidence=subtask.acceptance_criteria,
            )
            steps.append(test)
        verify = PlanStep(
            description="Verify every acceptance criterion and record evidence",
            kind=StepKind.VERIFY,
            dependencies=tuple(step.id for step in steps if step.kind is StepKind.TEST),
            expected_evidence=problem.acceptance_criteria,
        )
        steps.append(verify)
        document = PlanStep(
            description="Document decisions, evidence, limitations, and reusable lessons",
            kind=StepKind.DOCUMENT,
            dependencies=(verify.id,),
        )
        steps.append(document)
        return validate_plan(Plan(
            objective=problem.description,
            steps=tuple(steps),
            success_criteria=problem.acceptance_criteria,
            assumptions=problem.constraints,
        ))

    def build(self, problem: Problem, *, category: str | None = None) -> BrainResult:
        decomposition = self.decompose(problem)
        plan = self.plan(problem, decomposition)
        selected = self.selector.select(category=category) if category else ()
        return BrainResult(problem, decomposition, plan, selected)

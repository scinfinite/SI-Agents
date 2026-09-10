from collections.abc import Callable

from core.learning.evaluator import ImprovementEvaluator
from core.learning.models import ImprovementProposal, ImprovementStatus
from core.learning.registry import ImprovementRegistry

Apply = Callable[[ImprovementProposal], None]
Rollback = Callable[[ImprovementProposal], None]


class ImprovementEngine:
    """Fail-closed improvement workflow: propose -> evaluate -> approve -> apply -> verify."""

    def __init__(
        self,
        registry: ImprovementRegistry,
        evaluator: ImprovementEvaluator,
        *,
        minimum_verified_evidence: int = 2,
    ) -> None:
        if minimum_verified_evidence < 1:
            raise ValueError("Minimum verified evidence must be positive")
        self.registry = registry
        self.evaluator = evaluator
        self.minimum_verified_evidence = minimum_verified_evidence

    def propose(self, proposal: ImprovementProposal) -> ImprovementProposal:
        if proposal.verified_evidence_count < self.minimum_verified_evidence:
            raise ValueError("Improvement proposal lacks required verified evidence")
        return self.registry.register(proposal)

    def evaluate(self, proposal_id: str, *, score_before: float) -> ImprovementProposal:
        proposal = self.registry.get(proposal_id)
        result = self.evaluator.evaluate(proposal, score_before=score_before)
        return self.registry.transition(
            proposal_id,
            ImprovementStatus.EVALUATED,
            evaluation=result,
        )

    def approve(self, proposal_id: str) -> ImprovementProposal:
        proposal = self.registry.get(proposal_id)
        if proposal.evaluation is None or not proposal.evaluation.passed:
            raise ValueError("Only fully passing evaluations can be approved")
        if proposal.evaluation.score_after < proposal.evaluation.score_before:
            raise ValueError("Improvement cannot reduce benchmark score")
        return self.registry.transition(proposal_id, ImprovementStatus.APPROVED)

    def apply(self, proposal_id: str, apply_change: Apply) -> ImprovementProposal:
        proposal = self.registry.get(proposal_id)
        if proposal.status is not ImprovementStatus.APPROVED:
            raise ValueError("Only approved improvements can be applied")
        apply_change(proposal)
        return self.registry.transition(proposal_id, ImprovementStatus.APPLIED)

    def rollback(self, proposal_id: str, rollback_change: Rollback) -> ImprovementProposal:
        proposal = self.registry.get(proposal_id)
        if proposal.status is not ImprovementStatus.APPLIED:
            raise ValueError("Only applied improvements can be rolled back")
        rollback_change(proposal)
        return self.registry.transition(proposal_id, ImprovementStatus.ROLLED_BACK)

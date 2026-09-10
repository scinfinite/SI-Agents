from core.learning.models import ImprovementProposal, ImprovementStatus


class ImprovementRegistry:
    """In-memory proposal registry with explicit lifecycle transitions."""

    _ALLOWED = {
        ImprovementStatus.CANDIDATE: {ImprovementStatus.EVALUATED, ImprovementStatus.REJECTED},
        ImprovementStatus.EVALUATED: {ImprovementStatus.APPROVED, ImprovementStatus.REJECTED},
        ImprovementStatus.APPROVED: {ImprovementStatus.APPLIED, ImprovementStatus.REJECTED},
        ImprovementStatus.APPLIED: {ImprovementStatus.ROLLED_BACK},
        ImprovementStatus.REJECTED: set(),
        ImprovementStatus.ROLLED_BACK: set(),
    }

    def __init__(self) -> None:
        self._items: dict[str, ImprovementProposal] = {}

    def register(self, proposal: ImprovementProposal) -> ImprovementProposal:
        if proposal.id in self._items:
            raise ValueError(f"Improvement ID already registered: {proposal.id}")
        self._items[proposal.id] = proposal
        return proposal

    def get(self, proposal_id: str) -> ImprovementProposal:
        try:
            return self._items[proposal_id]
        except KeyError as exc:
            raise KeyError(f"Unknown improvement proposal: {proposal_id}") from exc

    def all(self) -> tuple[ImprovementProposal, ...]:
        return tuple(self._items.values())

    def transition(self, proposal_id: str, status: ImprovementStatus, **changes: object) -> ImprovementProposal:
        current = self.get(proposal_id)
        if status not in self._ALLOWED[current.status]:
            raise ValueError(f"Invalid improvement transition: {current.status.value} -> {status.value}")
        updated = ImprovementProposal(**{**current.__dict__, **changes, "status": status})
        self._items[proposal_id] = updated
        return updated

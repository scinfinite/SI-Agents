"""Legal and provenance policy evaluation; not legal advice."""

from core.governance.models import GovernanceRequest


class LegalPolicy:
    """Require review for actions whose legality depends on external terms or rights."""

    def evaluate(self, request: GovernanceRequest) -> list[str]:
        reasons: list[str] = []
        if request.legal_review_required and request.approval is None:
            reasons.append("required legal/compliance review is missing")
        if request.publication and not request.provenance:
            reasons.append("publication requires provenance evidence")
        return reasons

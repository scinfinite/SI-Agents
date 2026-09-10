from __future__ import annotations

from core.orchestrator.orchestrator import Orchestrator
from core.verification.claims import Claim
from core.verification.red_team import RedTeamChallenge, RedTeamSuite
from core.verification.regression import RegressionCase, RegressionSuite
from core.verification.verification_engine import VerificationCheck, VerificationOutcome


def test_orchestrator_registers_and_verifies_claim_with_all_gates() -> None:
    orchestrator = Orchestrator()
    claim = orchestrator.register_claim(
        Claim(
            statement="release candidate is acceptable",
            scope="phase 7 fixture",
            acceptance_criteria=("tests pass", "attack does not find a flaw"),
        )
    )
    report = orchestrator.verify_claim(
        claim.id,
        (VerificationCheck("tests", lambda: True),),
        regression=RegressionSuite((RegressionCase("regression", lambda: True),)),
        red_team=RedTeamSuite((RedTeamChallenge("attack", lambda: False),)),
    )
    assert report.outcome is VerificationOutcome.VERIFIED
    assert orchestrator.claims.get(claim.id).confidence == 1.0


def test_orchestrator_exposes_readiness_evaluation() -> None:
    orchestrator = Orchestrator()
    readiness = orchestrator.evaluate_readiness(())
    assert not readiness.ready

from __future__ import annotations

import pytest

from core.verification.claim_store import ClaimStore
from core.verification.claims import Claim
from core.verification.confidence import ConfidenceLevel, assess
from core.verification.evidence import Evidence, VerificationStatus
from core.verification.evidence_store import EvidenceStore
from core.verification.production_readiness import ReadinessGate, ReadinessStatus, evaluate
from core.verification.red_team import RedTeamChallenge, RedTeamStatus, RedTeamSuite
from core.verification.regression import RegressionCase, RegressionStatus, RegressionSuite
from core.verification.verification_engine import (
    VerificationCheck,
    VerificationEngine,
    VerificationOutcome,
)


def make_claim() -> Claim:
    return Claim(
        statement="the change satisfies the acceptance criteria",
        scope="unit test fixture",
        acceptance_criteria=("result is correct",),
    )


def test_claim_validation_and_evidence_attachment() -> None:
    store = ClaimStore()
    claim = store.record(make_claim())
    evidence = Evidence("result is correct", "unit-test", VerificationStatus.VERIFIED)
    EvidenceStore().record(evidence)
    updated = store.attach_evidence(claim.id, (evidence.id,), 0.9)
    assert updated.evidence_ids == (evidence.id,)
    assert updated.confidence == 0.9


def test_confidence_boundaries() -> None:
    assert assess(0.49, "weak evidence").level is ConfidenceLevel.LOW
    assert assess(0.50, "some evidence").level is ConfidenceLevel.MEDIUM
    assert assess(0.80, "strong evidence").level is ConfidenceLevel.HIGH
    with pytest.raises(ValueError):
        assess(1.01, "invalid")


def test_evidence_store_is_append_only_and_queryable() -> None:
    store = EvidenceStore()
    verified = store.record(Evidence("claim", "test", VerificationStatus.VERIFIED))
    failed = store.record(Evidence("claim", "test", VerificationStatus.FAILED, "broken"))
    assert store.get(verified.id) == verified
    assert store.for_claim("claim") == (verified, failed)
    assert store.verified() == (verified,)
    assert store.failed() == (failed,)
    with pytest.raises(ValueError, match="already exists"):
        store.record(verified)


def test_regression_suite_fails_closed_on_false_and_exception() -> None:
    suite = RegressionSuite()
    suite.add(RegressionCase("passes", lambda: True))
    suite.add(RegressionCase("fails", lambda: False))
    suite.add(RegressionCase("raises", lambda: 1 / 0))
    result = suite.run()
    assert result.status is RegressionStatus.FAILED
    assert len(result.results) == 3
    assert not result.passed


def test_regression_suite_with_no_cases_is_blocked() -> None:
    assert RegressionSuite().run().status is RegressionStatus.BLOCKED


def test_red_team_marks_successful_attack_as_flaw() -> None:
    suite = RedTeamSuite()
    suite.add(RedTeamChallenge("resists", lambda: False))
    suite.add(RedTeamChallenge("attack succeeds", lambda: True))
    results = suite.run()
    assert results[0].status is RedTeamStatus.RESISTED
    assert results[1].status is RedTeamStatus.FOUND_FLAW
    assert not RedTeamSuite.passed(results)


def test_red_team_attack_exception_fails_closed() -> None:
    suite = RedTeamSuite((RedTeamChallenge("raises", lambda: 1 / 0),))
    result = suite.run()
    assert result[0].status is RedTeamStatus.FOUND_FLAW
    assert not RedTeamSuite.passed(result)


def test_verification_engine_requires_registered_claim() -> None:
    claims = ClaimStore()
    engine = VerificationEngine(claims, EvidenceStore())
    with pytest.raises(ValueError, match="registered"):
        engine.verify(make_claim(), (VerificationCheck("ok", lambda: True),))


def test_verification_engine_blocks_without_checks() -> None:
    claims = ClaimStore()
    claim = claims.record(make_claim())
    evidence = EvidenceStore()
    report = VerificationEngine(claims, evidence).verify(claim, ())
    assert report.outcome is VerificationOutcome.BLOCKED
    assert report.confidence == 0.0
    assert evidence.all()[0].verification_status is VerificationStatus.UNVERIFIED


def test_verification_engine_requires_regression_and_red_team_when_supplied() -> None:
    claims = ClaimStore()
    claim = claims.record(make_claim())
    engine = VerificationEngine(claims, EvidenceStore())
    report = engine.verify(
        claim,
        (VerificationCheck("acceptance", lambda: True),),
        regression=RegressionSuite((RegressionCase("regression", lambda: True),)),
        red_team=RedTeamSuite((RedTeamChallenge("attack", lambda: False),)),
    )
    assert report.outcome is VerificationOutcome.VERIFIED
    assert report.confidence == 1.0
    assert report.regression is not None and report.regression.passed
    assert report.red_team[0].status is RedTeamStatus.RESISTED


def test_verification_engine_fails_closed_on_check_exception() -> None:
    claims = ClaimStore()
    claim = claims.record(make_claim())
    report = VerificationEngine(claims, EvidenceStore()).verify(
        claim,
        (VerificationCheck("broken", lambda: 1 / 0),),
    )
    assert report.outcome is VerificationOutcome.FAILED
    assert "broken" in report.failed_checks
    assert report.confidence < 1.0


def test_verification_engine_fails_when_red_team_finds_flaw() -> None:
    claims = ClaimStore()
    claim = claims.record(make_claim())
    report = VerificationEngine(claims, EvidenceStore()).verify(
        claim,
        (VerificationCheck("acceptance", lambda: True),),
        red_team=RedTeamSuite((RedTeamChallenge("find flaw", lambda: True),)),
    )
    assert report.outcome is VerificationOutcome.FAILED
    assert "red-team suite" in report.failed_checks


def test_production_readiness_requires_evidence_and_all_gates() -> None:
    evidence_id = "evidence-1"
    ready = evaluate((ReadinessGate("tests", True, (evidence_id,)),))
    assert ready.status is ReadinessStatus.READY
    not_ready = evaluate((ReadinessGate("security", False, details="security review failed"),))
    assert not_ready.status is ReadinessStatus.NOT_READY
    assert not evaluate(()).ready


def test_readiness_gate_rejects_unsupported_pass_or_failure() -> None:
    with pytest.raises(ValueError, match="requires evidence"):
        ReadinessGate("tests", True)
    with pytest.raises(ValueError, match="requires details"):
        ReadinessGate("tests", False)

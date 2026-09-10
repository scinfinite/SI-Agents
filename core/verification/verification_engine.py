from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field
from enum import Enum

from core.verification.claim_store import ClaimStore
from core.verification.claims import Claim
from core.verification.confidence import assess
from core.verification.evidence import Evidence, VerificationStatus
from core.verification.evidence_store import EvidenceStore
from core.verification.red_team import RedTeamResult, RedTeamSuite
from core.verification.regression import RegressionStatus, RegressionSuite, RegressionSuiteResult


class VerificationOutcome(str, Enum):
    VERIFIED = "verified"
    FAILED = "failed"
    BLOCKED = "blocked"


@dataclass(frozen=True)
class VerificationCheck:
    name: str
    check: Callable[[], bool] = field(repr=False, compare=False)

    def __post_init__(self) -> None:
        if not self.name.strip():
            raise ValueError("Verification check name must not be empty")


@dataclass(frozen=True)
class VerificationReport:
    claim_id: str
    outcome: VerificationOutcome
    confidence: float
    evidence_ids: tuple[str, ...]
    failed_checks: tuple[str, ...] = ()
    regression: RegressionSuiteResult | None = None
    red_team: tuple[RedTeamResult, ...] = ()


class VerificationEngine:
    """Fail-closed verification coordinator for claims and engineering results."""

    def __init__(self, claims: ClaimStore, evidence: EvidenceStore) -> None:
        self.claims = claims
        self.evidence = evidence

    def verify(
        self,
        claim: Claim,
        checks: tuple[VerificationCheck, ...],
        *,
        regression: RegressionSuite | None = None,
        red_team: RedTeamSuite | None = None,
        source_prefix: str = "verification",
    ) -> VerificationReport:
        if claim.id not in {item.id for item in self.claims.all()}:
            raise ValueError("Claim must be registered before verification")
        if not checks:
            evidence = self.evidence.record(
                Evidence(
                    claim=claim.statement,
                    source=source_prefix,
                    verification_status=VerificationStatus.UNVERIFIED,
                    details="No verification checks supplied",
                )
            )
            self.claims.attach_evidence(claim.id, (evidence.id,), 0.0)
            return VerificationReport(claim.id, VerificationOutcome.BLOCKED, 0.0, (evidence.id,))

        failed: list[str] = []
        evidence_ids: list[str] = []
        for item in checks:
            try:
                passed = bool(item.check())
            except Exception as exc:
                passed = False
                detail = f"check raised: {exc}"
            else:
                detail = "check passed" if passed else "check returned false"
            status = VerificationStatus.VERIFIED if passed else VerificationStatus.FAILED
            if not passed:
                failed.append(item.name)
            evidence_ids.append(
                self.evidence.record(
                    Evidence(
                        claim=f"{claim.statement} :: {item.name}",
                        source=f"{source_prefix}:{item.name}",
                        verification_status=status,
                        details=detail if not passed else "Independent verification check passed",
                    )
                ).id
            )

        regression_result = regression.run() if regression is not None else None
        regression_ok = regression_result is None or regression_result.status is RegressionStatus.PASSED
        if regression_result is not None and not regression_ok:
            failed.append("regression suite")

        red_results = red_team.run() if red_team is not None else ()
        red_team_ok = red_team is None or RedTeamSuite.passed(red_results)
        if red_results and not red_team_ok:
            failed.append("red-team suite")
        elif red_team is not None and not red_results:
            failed.append("red-team suite (no challenges)")

        passed = not failed
        outcome = VerificationOutcome.VERIFIED if passed else VerificationOutcome.FAILED
        confidence = 1.0 if passed else max(0.0, 1.0 - len(failed) / (len(checks) + 2))
        rationale = (
            "all checks, regressions, and attacks passed"
            if passed
            else f"failed: {', '.join(failed)}"
        )
        assessment = assess(confidence, rationale)
        self.claims.attach_evidence(claim.id, tuple(evidence_ids), assessment.value)
        return VerificationReport(
            claim.id,
            outcome,
            assessment.value,
            tuple(evidence_ids),
            tuple(failed),
            regression_result,
            tuple(red_results),
        )

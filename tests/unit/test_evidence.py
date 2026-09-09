import pytest

from core.verification.evidence import Evidence, VerificationStatus


def test_evidence_records_unique_instance_metadata() -> None:
    first = Evidence("tests pass", "github-actions", VerificationStatus.VERIFIED)
    second = Evidence("tests pass", "github-actions", VerificationStatus.VERIFIED)

    assert first.id != second.id
    assert first.recorded_at.tzinfo is not None


def test_failed_evidence_requires_details() -> None:
    with pytest.raises(ValueError, match="must include details"):
        Evidence("tests failed", "ci", VerificationStatus.FAILED)


def test_evidence_requires_claim_and_source() -> None:
    with pytest.raises(ValueError, match="claim must not be empty"):
        Evidence(" ", "ci", VerificationStatus.VERIFIED)

    with pytest.raises(ValueError, match="source must not be empty"):
        Evidence("tests pass", " ", VerificationStatus.VERIFIED)

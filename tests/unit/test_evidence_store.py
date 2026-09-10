import pytest

from core.verification.evidence import Evidence, VerificationStatus
from core.verification.evidence_store import EvidenceStore


def test_record_and_get_evidence() -> None:
    store = EvidenceStore()
    evidence = Evidence("tests pass", "ci", VerificationStatus.VERIFIED)

    assert store.record(evidence) == evidence
    assert store.get(evidence.id) == evidence


def test_duplicate_evidence_id_is_rejected() -> None:
    store = EvidenceStore()
    evidence = Evidence("claim", "test", VerificationStatus.VERIFIED)
    store.record(evidence)

    with pytest.raises(ValueError, match="already exists"):
        store.record(evidence)


def test_all_returns_recorded_evidence() -> None:
    store = EvidenceStore()
    first = Evidence("one", "test", VerificationStatus.UNVERIFIED)
    second = Evidence("two", "test", VerificationStatus.VERIFIED)

    store.record(first)
    store.record(second)

    assert store.all() == (first, second)

from core.hardening.health import HealthStatus, ReadinessChecker
from core.hardening.limits import ResourceLimits
from core.hardening.redaction import redact
from core.hardening.release import ReleaseGate


def test_readiness_is_deterministic_and_fail_closed() -> None:
    report = ReadinessChecker({"z": lambda: True, "a": lambda: False}).check()
    assert report.status is HealthStatus.UNHEALTHY
    assert [item[0] for item in report.checks] == ["a", "z"]


def test_readiness_exception_is_unhealthy() -> None:
    def broken() -> bool:
        raise RuntimeError("boom")

    report = ReadinessChecker({"dependency": broken}).check()
    assert report.checks[0][1] is HealthStatus.UNHEALTHY
    assert report.checks[0][2] == "check failed"


def test_limits_accept_boundary_values() -> None:
    limits = ResourceLimits(max_input_bytes=10, max_output_bytes=20, max_events=3, max_metadata_items=2,
                            max_timeout_seconds=5)
    limits.validate(input_bytes=10, output_bytes=20, events=3, metadata_items=2, timeout_seconds=5)


def test_limits_reject_overflow() -> None:
    limits = ResourceLimits(max_input_bytes=10)
    try:
        limits.validate(input_bytes=11, output_bytes=0, events=0, metadata_items=0, timeout_seconds=None)
    except ValueError as exc:
        assert "input" in str(exc)
    else:
        raise AssertionError("expected input limit failure")


def test_limits_reject_negative_measurement() -> None:
    limits = ResourceLimits()
    try:
        limits.validate(input_bytes=-1, output_bytes=0, events=0, metadata_items=0, timeout_seconds=None)
    except ValueError as exc:
        assert "non-negative" in str(exc)
    else:
        raise AssertionError("expected negative measurement failure")


def test_redaction_handles_secret_keys_and_bearer_tokens() -> None:
    result = redact({"api_key": "secret", "nested": {"password": "pw"}, "message": "Bearer abc.def"})
    assert result["api_key"] == "[REDACTED]"
    assert result["nested"]["password"] == "[REDACTED]"
    assert result["message"] == "Bearer [REDACTED]"


def test_redaction_preserves_non_secret_values() -> None:
    assert redact({"status": "ok", "count": 2}) == {"status": "ok", "count": 2}


def test_release_gate_requires_all_evidence() -> None:
    result = ReleaseGate().evaluate(
        tests_passed=True, lint_passed=True, build_passed=True,
        security_reviewed=True, migration_reviewed=False, rollback_tested=True,
    )
    assert not result.ready
    assert result.reasons == ("migration_review evidence missing",)


def test_release_gate_passes_only_when_complete() -> None:
    result = ReleaseGate().evaluate(
        tests_passed=True, lint_passed=True, build_passed=True,
        security_reviewed=True, migration_reviewed=True, rollback_tested=True,
    )
    assert result.ready
    assert result.reasons == ()

"""Evidence-based release readiness gate."""

from dataclasses import dataclass


@dataclass(frozen=True)
class ReleaseResult:
    ready: bool
    reasons: tuple[str, ...]


class ReleaseGate:
    """Require all declared release evidence before production readiness."""

    def evaluate(self, *, tests_passed: bool, lint_passed: bool, build_passed: bool,
                 security_reviewed: bool, migration_reviewed: bool, rollback_tested: bool) -> ReleaseResult:
        checks = (
            ("tests", tests_passed),
            ("lint", lint_passed),
            ("build", build_passed),
            ("security_review", security_reviewed),
            ("migration_review", migration_reviewed),
            ("rollback_test", rollback_tested),
        )
        reasons = tuple(name + " evidence missing" for name, passed in checks if not passed)
        return ReleaseResult(not reasons, reasons)

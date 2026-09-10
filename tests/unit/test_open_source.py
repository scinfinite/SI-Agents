from datetime import UTC, datetime, timedelta

import pytest

from core.open_source.archaeology import activity_window, summarize_history
from core.open_source.health import assess_health
from core.open_source.intelligence import analyze
from core.open_source.license import assess_license
from core.open_source.models import (
    CommitSummary,
    HealthAssessment,
    IntelligenceStatus,
    IssueSummary,
    OpenSourceSnapshot,
    PullRequestSummary,
    ReleaseSummary,
    RepositorySummary,
    SecurityAdvisory,
)
from core.open_source.provider import collect
from core.open_source.registry import OpenSourceRegistry


class FakeProvider:
    def repository(self, full_name):
        return RepositorySummary(full_name, default_branch="main", open_issues=4, source="fixture")

    def commits(self, full_name):
        return (CommitSummary("abc", "fix: parser", authored_at=datetime(2026, 1, 2, tzinfo=UTC)),)

    def issues(self, full_name):
        return (IssueSummary(1, "bug", "open"),)

    def pull_requests(self, full_name):
        return (PullRequestSummary(2, "fix", "closed", merged=True),)

    def releases(self, full_name):
        return (ReleaseSummary("v1.0", "First"),)

    def advisories(self, full_name):
        return (SecurityAdvisory("CVE-X", "high", "fixture advisory"),)


def make_snapshot(**kwargs):
    repository = kwargs.pop("repository", RepositorySummary("example/project", open_issues=4))
    return OpenSourceSnapshot(repository, sources=("fixture",), **kwargs)


def test_models_cover_repository_history_issues_prs_releases_security():
    snapshot = make_snapshot(
        commits=(CommitSummary("abc", "fix: parser"),),
        issues=(IssueSummary(1, "bug", "open"),),
        pull_requests=(PullRequestSummary(2, "fix", "closed", merged=True),),
        releases=(ReleaseSummary("v1", "release"),),
        advisories=(SecurityAdvisory("GHSA-x", "high", "issue"),),
    )
    assert snapshot.commits[0].sha == "abc"
    assert snapshot.pull_requests[0].merged
    assert snapshot.advisories[0].severity == "high"


def test_provider_collection_is_read_only_and_provenance_bearing():
    snapshot = collect(FakeProvider(), "example/project")
    assert snapshot.repository.source == "fixture"
    assert snapshot.sources
    assert len(snapshot.issues) == len(snapshot.pull_requests) == 1


def test_registry_rejects_duplicate_snapshot():
    registry = OpenSourceRegistry()
    snapshot = make_snapshot()
    registry.record(snapshot)
    with pytest.raises(ValueError):
        registry.record(snapshot)
    assert registry.for_repository("example/project") == (snapshot,)


def test_archaeology_is_deterministic_and_reports_activity_window():
    first = datetime(2026, 1, 1, tzinfo=UTC)
    second = datetime(2026, 2, 1, tzinfo=UTC)
    commits = (
        CommitSummary("a", "feat: x", authored_at=first),
        CommitSummary("b", "fix: y", authored_at=second),
    )
    report = summarize_history("example/project", commits)
    assert report.themes == ("feat", "fix")
    assert activity_window(commits) == (first, second)


def test_health_does_not_treat_missing_signals_as_negative_quality():
    repository = RepositorySummary("example/project", open_issues=10)
    snapshot = make_snapshot(repository=repository, releases=())
    health = assess_health(snapshot)
    assert health.score is not None
    assert "no releases observed in supplied snapshot" in health.limitations
    assert health.status is IntelligenceStatus.OBSERVED


def test_stale_snapshot_is_not_reported_as_fresh():
    snapshot = make_snapshot(captured_at=datetime.now(UTC) - timedelta(days=10))
    result = analyze(snapshot, max_age=timedelta(days=1))
    assert result.status is IntelligenceStatus.STALE
    assert result.limitations


def test_license_unknown_is_fail_closed():
    assessment = assess_license(None)
    assert assessment.status is IntelligenceStatus.UNKNOWN
    assert assessment.redistribution_allowed is None


def test_license_permissive_still_requires_text_review():
    assessment = assess_license("MIT")
    assert assessment.redistribution_allowed is True
    assert assessment.attribution_required is True
    assert "license-text" in assessment.notes


def test_validated_snapshot_requires_provenance():
    with pytest.raises(ValueError):
        OpenSourceSnapshot(RepositorySummary("example/project"), status=IntelligenceStatus.VERIFIED)


def test_health_rejects_invalid_score():
    with pytest.raises(ValueError):
        HealthAssessment(1.1, IntelligenceStatus.OBSERVED)

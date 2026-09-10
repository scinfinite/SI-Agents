from typing import Protocol

from core.open_source.models import (
    CommitSummary,
    IssueSummary,
    OpenSourceSnapshot,
    PullRequestSummary,
    ReleaseSummary,
    RepositorySummary,
    SecurityAdvisory,
)


class OpenSourceProvider(Protocol):
    """Read-only provider contract. Implementations must preserve source provenance."""

    def repository(self, full_name: str) -> RepositorySummary: ...

    def commits(self, full_name: str) -> tuple[CommitSummary, ...]: ...

    def issues(self, full_name: str) -> tuple[IssueSummary, ...]: ...

    def pull_requests(self, full_name: str) -> tuple[PullRequestSummary, ...]: ...

    def releases(self, full_name: str) -> tuple[ReleaseSummary, ...]: ...

    def advisories(self, full_name: str) -> tuple[SecurityAdvisory, ...]: ...


def collect(provider: OpenSourceProvider, full_name: str) -> OpenSourceSnapshot:
    """Collect read-only signals through an injected provider; no network is hidden here."""
    repository = provider.repository(full_name)
    return OpenSourceSnapshot(
        repository=repository,
        commits=provider.commits(full_name),
        issues=provider.issues(full_name),
        pull_requests=provider.pull_requests(full_name),
        releases=provider.releases(full_name),
        advisories=provider.advisories(full_name),
        sources=(repository.source, "provider contract"),
    )

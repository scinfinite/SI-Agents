from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import Enum
from uuid import uuid4


class IntelligenceStatus(str, Enum):
    UNKNOWN = "unknown"
    OBSERVED = "observed"
    VERIFIED = "verified"
    STALE = "stale"
    BLOCKED = "blocked"


@dataclass(frozen=True)
class RepositorySummary:
    full_name: str
    default_branch: str | None = None
    description: str | None = None
    archived: bool = False
    fork: bool = False
    stars: int | None = None
    forks: int | None = None
    open_issues: int | None = None
    license_spdx: str | None = None
    topics: tuple[str, ...] = ()
    source: str = "github"

    def __post_init__(self) -> None:
        if not self.full_name.strip():
            raise ValueError("Repository name must not be empty")
        for value in (self.stars, self.forks, self.open_issues):
            if value is not None and value < 0:
                raise ValueError("Repository counters must not be negative")


@dataclass(frozen=True)
class CommitSummary:
    sha: str
    message: str
    author: str | None = None
    authored_at: datetime | None = None
    files_changed: int | None = None


@dataclass(frozen=True)
class IssueSummary:
    number: int
    title: str
    state: str
    labels: tuple[str, ...] = ()
    comments: int = 0
    created_at: datetime | None = None
    updated_at: datetime | None = None

    def __post_init__(self) -> None:
        if self.number <= 0 or not self.title.strip():
            raise ValueError("Issue number and title must be valid")
        if self.comments < 0:
            raise ValueError("Issue comments must not be negative")


@dataclass(frozen=True)
class PullRequestSummary:
    number: int
    title: str
    state: str
    merged: bool = False
    draft: bool = False
    changed_files: int | None = None
    additions: int | None = None
    deletions: int | None = None

    def __post_init__(self) -> None:
        if self.number <= 0 or not self.title.strip():
            raise ValueError("Pull request number and title must be valid")
        for value in (self.changed_files, self.additions, self.deletions):
            if value is not None and value < 0:
                raise ValueError("Pull request counters must not be negative")


@dataclass(frozen=True)
class ReleaseSummary:
    tag: str
    name: str
    published_at: datetime | None = None
    prerelease: bool = False
    draft: bool = False
    source: str = "github"

    def __post_init__(self) -> None:
        if not self.tag.strip() or not self.name.strip():
            raise ValueError("Release tag and name must not be empty")


@dataclass(frozen=True)
class SecurityAdvisory:
    identifier: str
    severity: str
    summary: str
    affected_versions: tuple[str, ...] = ()
    patched_versions: tuple[str, ...] = ()
    source: str = "github"

    def __post_init__(self) -> None:
        if not self.identifier.strip() or not self.summary.strip():
            raise ValueError("Security advisory identifier and summary are required")


@dataclass(frozen=True)
class LicenseAssessment:
    identifier: str
    spdx_id: str | None
    status: IntelligenceStatus
    redistribution_allowed: bool | None
    attribution_required: bool | None
    source: str
    notes: str = ""

    def __post_init__(self) -> None:
        if not self.identifier.strip() or not self.source.strip():
            raise ValueError("License identifier and source are required")


@dataclass(frozen=True)
class HealthAssessment:
    score: float | None
    status: IntelligenceStatus
    signals: tuple[str, ...] = ()
    limitations: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if self.score is not None and not 0.0 <= self.score <= 1.0:
            raise ValueError("Health score must be between 0 and 1")


@dataclass(frozen=True)
class OpenSourceSnapshot:
    repository: RepositorySummary
    commits: tuple[CommitSummary, ...] = ()
    issues: tuple[IssueSummary, ...] = ()
    pull_requests: tuple[PullRequestSummary, ...] = ()
    releases: tuple[ReleaseSummary, ...] = ()
    advisories: tuple[SecurityAdvisory, ...] = ()
    license: LicenseAssessment | None = None
    health: HealthAssessment | None = None
    status: IntelligenceStatus = IntelligenceStatus.OBSERVED
    sources: tuple[str, ...] = ()
    captured_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    id: str = field(default_factory=lambda: uuid4().hex)

    def __post_init__(self) -> None:
        if not self.sources:
            raise ValueError("Open-source snapshot requires at least one provenance source")

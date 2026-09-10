from dataclasses import dataclass
from datetime import datetime

from core.open_source.models import CommitSummary


@dataclass(frozen=True)
class ArchaeologyReport:
    repository: str
    commits: tuple[CommitSummary, ...]
    themes: tuple[str, ...] = ()
    limitations: tuple[str, ...] = ()


def summarize_history(repository: str, commits: tuple[CommitSummary, ...]) -> ArchaeologyReport:
    """Produce deterministic history observations; it does not infer intent from commit text."""
    messages = [c.message.strip() for c in commits if c.message.strip()]
    themes = tuple(dict.fromkeys(message.split(":", 1)[0].lower() for message in messages))
    return ArchaeologyReport(repository=repository, commits=commits, themes=themes)


def activity_window(commits: tuple[CommitSummary, ...]) -> tuple[datetime | None, datetime | None]:
    dates = [c.authored_at for c in commits if c.authored_at is not None]
    return (min(dates), max(dates)) if dates else (None, None)

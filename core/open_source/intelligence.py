from dataclasses import dataclass
from datetime import UTC, datetime, timedelta

from core.open_source.health import assess_health
from core.open_source.models import IntelligenceStatus, OpenSourceSnapshot


@dataclass(frozen=True)
class IntelligenceResult:
    snapshot_id: str
    status: IntelligenceStatus
    findings: tuple[str, ...]
    limitations: tuple[str, ...]
    generated_at: datetime


def analyze(snapshot: OpenSourceSnapshot, max_age: timedelta | None = None) -> IntelligenceResult:
    """Aggregate repository signals without presenting missing data as negative evidence."""
    health = snapshot.health or assess_health(snapshot)
    findings = [f"health_score={health.score:.3f}" for _ in [0] if health.score is not None]
    findings.extend(health.signals)
    limitations = list(health.limitations)
    status = snapshot.status
    if max_age is not None and datetime.now(UTC) - snapshot.captured_at > max_age:
        status = IntelligenceStatus.STALE
        limitations.append("snapshot is older than the requested freshness window")
    return IntelligenceResult(snapshot.id, status, tuple(findings), tuple(limitations), datetime.now(UTC))

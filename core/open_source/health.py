from core.open_source.models import HealthAssessment, IntelligenceStatus, OpenSourceSnapshot


def assess_health(snapshot: OpenSourceSnapshot) -> HealthAssessment:
    """Score only observable signals; absence of data lowers confidence, not repository quality."""
    signals: list[str] = []
    limitations: list[str] = []
    score_parts: list[float] = []
    repo = snapshot.repository

    if repo.archived:
        signals.append("repository is archived")
        score_parts.append(0.0)
    else:
        signals.append("repository is not archived")
        score_parts.append(1.0)

    if repo.open_issues is not None:
        score_parts.append(1.0 if repo.open_issues < 100 else 0.5 if repo.open_issues < 500 else 0.25)
        signals.append("open-issue count observed")
    else:
        limitations.append("open-issue count unavailable")

    if snapshot.releases:
        signals.append("release history observed")
        score_parts.append(1.0)
    else:
        limitations.append("no releases observed in supplied snapshot")

    if not score_parts:
        return HealthAssessment(None, IntelligenceStatus.UNKNOWN, tuple(signals), tuple(limitations))
    status = IntelligenceStatus.VERIFIED if not limitations else IntelligenceStatus.OBSERVED
    return HealthAssessment(sum(score_parts) / len(score_parts), status, tuple(signals), tuple(limitations))

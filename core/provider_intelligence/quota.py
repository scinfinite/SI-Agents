"""Quota observations and conservative availability checks."""

from core.provider_intelligence.models import QuotaSnapshot


class QuotaTracker:
    """Keeps the freshest observed quota per provider; unknown is not exhausted."""

    def __init__(self) -> None:
        self._snapshots: dict[str, QuotaSnapshot] = {}

    def observe(self, snapshot: QuotaSnapshot) -> None:
        current = self._snapshots.get(snapshot.provider_id)
        if current is None or snapshot.observed_at >= current.observed_at:
            self._snapshots[snapshot.provider_id] = snapshot

    def get(self, provider_id: str) -> QuotaSnapshot | None:
        return self._snapshots.get(provider_id)

    def available(self, provider_id: str) -> bool:
        snapshot = self.get(provider_id)
        if snapshot is None:
            return True
        if snapshot.remaining_requests == 0 or snapshot.remaining_tokens == 0:
            return False
        return True

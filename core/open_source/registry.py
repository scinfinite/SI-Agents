from core.open_source.models import IntelligenceStatus, OpenSourceSnapshot


class OpenSourceRegistry:
    """In-memory, duplicate-safe store for provenance-bearing OSS snapshots."""

    def __init__(self) -> None:
        self._snapshots: dict[str, OpenSourceSnapshot] = {}

    def record(self, snapshot: OpenSourceSnapshot) -> OpenSourceSnapshot:
        if snapshot.id in self._snapshots:
            raise ValueError(f"Open-source snapshot already exists: {snapshot.id}")
        self._snapshots[snapshot.id] = snapshot
        return snapshot

    def get(self, snapshot_id: str) -> OpenSourceSnapshot:
        try:
            return self._snapshots[snapshot_id]
        except KeyError as exc:
            raise KeyError(f"Unknown open-source snapshot: {snapshot_id}") from exc

    def all(self) -> tuple[OpenSourceSnapshot, ...]:
        return tuple(self._snapshots.values())

    def for_repository(self, full_name: str) -> tuple[OpenSourceSnapshot, ...]:
        return tuple(s for s in self._snapshots.values() if s.repository.full_name == full_name)

    def by_status(self, status: IntelligenceStatus) -> tuple[OpenSourceSnapshot, ...]:
        return tuple(s for s in self._snapshots.values() if s.status is status)

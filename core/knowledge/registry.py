from core.knowledge.models import KnowledgeEntry, KnowledgeKind, KnowledgeStatus


class KnowledgeRegistry:
    """Deterministic registry for versioned, provenance-aware technical knowledge."""

    def __init__(self) -> None:
        self._entries_by_id: dict[str, KnowledgeEntry] = {}
        self._ids_by_name: dict[str, str] = {}

    def register(self, entry: KnowledgeEntry) -> KnowledgeEntry:
        if entry.id in self._entries_by_id:
            raise ValueError(f"Knowledge entry id already registered: {entry.id}")
        key = entry.name.casefold()
        if key in self._ids_by_name:
            raise ValueError(f"Knowledge entry name already registered: {entry.name}")
        self._entries_by_id[entry.id] = entry
        self._ids_by_name[key] = entry.id
        return entry

    def get(self, entry_id: str) -> KnowledgeEntry:
        try:
            return self._entries_by_id[entry_id]
        except KeyError as exc:
            raise KeyError(f"Unknown knowledge entry: {entry_id}") from exc

    def get_by_name(self, name: str) -> KnowledgeEntry:
        try:
            return self.get(self._ids_by_name[name.casefold()])
        except KeyError as exc:
            raise KeyError(f"Unknown knowledge entry: {name}") from exc

    def all(self) -> tuple[KnowledgeEntry, ...]:
        return tuple(self._entries_by_id.values())

    def by_kind(self, kind: KnowledgeKind) -> tuple[KnowledgeEntry, ...]:
        return tuple(item for item in self.all() if item.kind is kind)

    def by_status(self, status: KnowledgeStatus) -> tuple[KnowledgeEntry, ...]:
        return tuple(item for item in self.all() if item.status is status)

    def validated(self, *, kind: KnowledgeKind | None = None) -> tuple[KnowledgeEntry, ...]:
        entries = self.by_status(KnowledgeStatus.VALIDATED)
        if kind is not None:
            entries = tuple(item for item in entries if item.kind is kind)
        return entries

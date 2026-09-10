from __future__ import annotations

import json
import os
from pathlib import Path
from tempfile import NamedTemporaryFile

from core.handoff.models import HandoffEnvelope, HandoffStatus


class HandoffStore:
    """Read/write portable handoff files without executing or importing their contents."""

    def __init__(self, directory: Path | None = None) -> None:
        self.directory = directory or Path.home() / ".config" / "si-agents" / "handoffs"

    def path_for(self, handoff_id: str) -> Path:
        if not handoff_id or any(char not in "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_" for char in handoff_id):
            raise ValueError("invalid handoff id")
        return self.directory / f"{handoff_id}.json"

    def save(self, envelope: HandoffEnvelope) -> Path:
        self.directory.mkdir(parents=True, exist_ok=True)
        self.directory.chmod(0o700)
        target = self.path_for(envelope.handoff_id)
        with NamedTemporaryFile("w", encoding="utf-8", dir=self.directory, delete=False) as handle:
            json.dump(envelope.as_dict(), handle, indent=2, sort_keys=True, ensure_ascii=False)
            handle.write("\n")
            temporary = Path(handle.name)
        temporary.chmod(0o600)
        temporary.replace(target)
        return target

    def load(self, path: Path) -> HandoffEnvelope:
        target = path.expanduser().resolve()
        data = json.loads(target.read_text(encoding="utf-8"))
        return HandoffEnvelope.from_dict(data)

    def import_file(self, path: Path, *, target_environment: str) -> HandoffEnvelope:
        envelope = self.load(path)
        if envelope.target_environment not in (None, target_environment):
            raise ValueError(
                f"handoff targets {envelope.target_environment!r}, not {target_environment!r}"
            )
        if envelope.source_environment == target_environment:
            raise ValueError("handoff source and target environments must differ")
        imported = HandoffEnvelope(**{**envelope.__dict__, "target_environment": target_environment, "status": HandoffStatus.IMPORTED})
        return imported

    @staticmethod
    def safe_export_path(path: Path) -> Path:
        """Reject paths that are obviously unsafe for a portable handoff artifact."""
        resolved = path.expanduser().resolve()
        if resolved.name.startswith("."):
            raise ValueError("hidden handoff export filenames are not allowed")
        return resolved

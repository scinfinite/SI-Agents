from __future__ import annotations

import json
from pathlib import Path
from uuid import uuid4


class ArtifactStore:
    """Durable workspace-external artifact metadata store.

    Files are copied into an artifact directory; metadata is JSON and uses atomic writes.
    """

    def __init__(self, root: str | Path) -> None:
        self.root = Path(root).resolve()
        self.root.mkdir(parents=True, exist_ok=True)

    def put(self, source: str | Path, *, name: str | None = None) -> str:
        source_path = Path(source).resolve()
        if not source_path.is_file():
            raise ValueError(f"Artifact source is not a file: {source_path}")
        artifact_id = uuid4().hex
        filename = name or source_path.name
        destination = self.root / f"{artifact_id}-{filename}"
        destination.write_bytes(source_path.read_bytes())
        metadata = self.root / f"{artifact_id}.json"
        temporary = metadata.with_suffix(".tmp")
        temporary.write_text(
            json.dumps({"id": artifact_id, "name": filename, "path": str(destination)}, indent=2),
            encoding="utf-8",
        )
        temporary.replace(metadata)
        return artifact_id

    def get_metadata(self, artifact_id: str) -> dict[str, str]:
        path = self.root / f"{artifact_id}.json"
        if not path.is_file():
            raise KeyError(f"Unknown artifact: {artifact_id}")
        return json.loads(path.read_text(encoding="utf-8"))

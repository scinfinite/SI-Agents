import json
from dataclasses import asdict
from datetime import datetime
from pathlib import Path
from typing import Any

from core.capabilities.models import Capability, CapabilityStatus
from core.capabilities.registry import CapabilityRegistry


class CapabilityStore:
    """Durable JSON persistence for capability definitions."""

    def __init__(self, path: str | Path) -> None:
        self.path = Path(path)

    def save(self, registry: CapabilityRegistry) -> None:
        payload = [self._serialize(item) for item in registry.all()]
        self.path.parent.mkdir(parents=True, exist_ok=True)
        temporary = self.path.with_suffix(self.path.suffix + ".tmp")
        temporary.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
        temporary.replace(self.path)

    def load(self, registry: CapabilityRegistry) -> tuple[Capability, ...]:
        if not self.path.exists():
            return ()
        payload = json.loads(self.path.read_text(encoding="utf-8"))
        if not isinstance(payload, list):
            raise TypeError("Capability store must contain a JSON list")
        loaded: list[Capability] = []
        for raw in payload:
            if not isinstance(raw, dict):
                raise TypeError("Capability record must be a JSON object")
            data = dict(raw)
            data["status"] = CapabilityStatus(data["status"])
            data["registered_at"] = datetime.fromisoformat(data["registered_at"])
            for key in ("skills", "tools", "permissions", "inputs", "outputs", "verification", "evidence"):
                data[key] = tuple(data.get(key, ()))
            item = Capability(**data)
            registry.register(item)
            loaded.append(item)
        return tuple(loaded)

    @staticmethod
    def _serialize(capability: Capability) -> dict[str, Any]:
        data = asdict(capability)
        data["status"] = capability.status.value
        data["registered_at"] = capability.registered_at.isoformat()
        return data

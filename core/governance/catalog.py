"""Validated loader for declarative governance configuration."""

import json
from pathlib import Path

from core.governance.models import Capability, Policy, RiskLevel
from core.governance.store import GovernanceStore


class GovernanceCatalogError(ValueError):
    pass


def load_catalog(path: str | Path) -> GovernanceStore:
    source = Path(path)
    try:
        payload = json.loads(source.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise GovernanceCatalogError(f"cannot load governance catalog: {source}") from exc
    if payload.get("schema_version") != 1:
        raise GovernanceCatalogError("unsupported governance schema")
    store = GovernanceStore()
    for item in payload.get("capabilities", []):
        store.add_capability(Capability(item["name"], item.get("description", ""), RiskLevel(item.get("risk", "low"))))
    for item in payload.get("policies", []):
        store.add_policy(
            Policy(
                name=item["name"],
                description=item["description"],
                deny_capabilities=tuple(item.get("deny_capabilities", [])),
                approval_risks=tuple(RiskLevel(value) for value in item.get("approval_risks", ["high", "critical"])),
                max_cost=item.get("max_cost"),
                allow_external_egress=bool(item.get("allow_external_egress", False)),
            )
        )
    return store

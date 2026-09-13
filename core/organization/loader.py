from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from core.organization.models import AgentDefinition, AgentStatus, Division
from core.organization.registry import AgentCatalog


def load_catalog(path: str | Path) -> AgentCatalog:
    """Load the canonical catalog plus independently authored repository extensions."""
    catalog_path = Path(path)
    payload = json.loads(catalog_path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict) or payload.get("version") != 1:
        raise ValueError("Unsupported or missing agent catalog version")

    catalog = AgentCatalog()
    for raw in payload.get("divisions", []):
        catalog.register_division(Division(**_required(raw, "id", "name", "description")))
    for raw in payload.get("agents", []):
        catalog.register(AgentDefinition(**_agent_kwargs(raw)))

    extension_path = catalog_path.with_name("agent-catalog-extensions.json")
    if extension_path.exists():
        extension = json.loads(extension_path.read_text(encoding="utf-8"))
        if not isinstance(extension, dict) or extension.get("version") != 1:
            raise ValueError("Unsupported agent catalog extension version")
        if extension.get("schema") != "si-agents.agent-catalog-extension.v1":
            raise ValueError("Unsupported agent catalog extension schema")
        for raw in extension.get("agents", []):
            catalog.register(AgentDefinition(**_agent_kwargs(raw)))

    errors = catalog.validate()
    if errors:
        raise ValueError("Invalid agent catalog: " + "; ".join(errors))
    return catalog


def _required(raw: Any, *keys: str) -> dict[str, Any]:
    if not isinstance(raw, dict):
        raise TypeError("Catalog entries must be objects")
    missing = [key for key in keys if key not in raw]
    if missing:
        raise ValueError(f"Catalog entry missing required fields: {', '.join(missing)}")
    return {key: raw[key] for key in keys}


def _agent_kwargs(raw: Any) -> dict[str, Any]:
    values = _required(
        raw,
        "id",
        "name",
        "division",
        "description",
        "responsibilities",
        "deliverables",
        "success_criteria",
        "boundaries",
    )
    for key in ("skills", "capabilities", "permissions", "harnesses", "environments"):
        values[key] = tuple(raw.get(key, ()))
    values["responsibilities"] = tuple(values["responsibilities"])
    values["deliverables"] = tuple(values["deliverables"])
    values["success_criteria"] = tuple(values["success_criteria"])
    values["boundaries"] = tuple(values["boundaries"])
    values["status"] = AgentStatus(raw.get("status", AgentStatus.CATALOGED))
    values["implementation"] = raw.get("implementation")
    return values

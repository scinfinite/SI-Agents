from pathlib import Path

import pytest

from core.organization import AgentStatus, load_catalog


CATALOG = Path(__file__).parents[1] / "config" / "agent-catalog.json"


def test_canonical_catalog_loads_and_validates() -> None:
    catalog = load_catalog(CATALOG)

    assert len(catalog.all_divisions()) == 7
    assert len(catalog.all()) == 12
    assert catalog.validate() == ()
    assert catalog.get("developer").status is AgentStatus.IMPLEMENTED
    assert catalog.get("developer").implementation == "agents.developer.DeveloperAgent"


def test_catalog_selection_is_capability_and_permission_aware() -> None:
    catalog = load_catalog(CATALOG)

    writable = catalog.select(
        division="engineering",
        required_capabilities=("filesystem", "terminal"),
        required_permissions=("workspace_write",),
        environment="codespace",
    )

    assert [agent.id for agent in writable] == ["developer", "backend-engineer", "frontend-engineer"]


def test_catalog_selection_can_require_skill_and_harness() -> None:
    catalog = load_catalog(CATALOG)

    selected = catalog.select(
        required_skills=("verify-change",),
        harness="opencode",
        environment="termux",
    )

    assert {agent.id for agent in selected} == {
        "developer",
        "tester",
        "backend-engineer",
        "security-engineer",
        "code-reviewer",
        "reality-checker",
        "release-engineer",
    }


def test_duplicate_division_and_agent_are_rejected() -> None:
    from core.organization.models import AgentDefinition, Division
    from core.organization.registry import AgentCatalog

    catalog = AgentCatalog()
    division = Division("engineering", "Engineering", "Build software")
    catalog.register_division(division)
    with pytest.raises(ValueError, match="Duplicate division"):
        catalog.register_division(division)

    agent = AgentDefinition(
        id="developer",
        name="Developer",
        division="engineering",
        description="Build software",
        responsibilities=("implement",),
        deliverables=("change",),
        success_criteria=("tested",),
        boundaries=("no bypass",),
    )
    catalog.register(agent)
    with pytest.raises(ValueError, match="Duplicate agent id"):
        catalog.register(agent)


def test_invalid_catalog_status_is_rejected(tmp_path: Path) -> None:
    path = tmp_path / "catalog.json"
    path.write_text(
        '{"version":1,"divisions":[{"id":"engineering","name":"Engineering","description":"Build"}],'
        '"agents":[{"id":"bad","name":"Bad","division":"engineering","description":"Bad",'
        '"responsibilities":["x"],"deliverables":["x"],"success_criteria":["x"],"boundaries":["x"],'
        '"status":"unknown"}]}',
        encoding="utf-8",
    )
    with pytest.raises(ValueError, match="unknown is not a valid AgentStatus"):
        load_catalog(path)

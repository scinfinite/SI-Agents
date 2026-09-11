import pytest

from agents.builder import AgentDefinition, AgentRegistry, BuilderError, ResourceLimits, TeamBuilder
from core.runtime.omniroute import OmniRoutePolicy


def make_registry() -> AgentRegistry:
    return AgentRegistry(
        (
            AgentDefinition(
                "architect",
                "architecture",
                "Design system structure",
                skills=("architecture",),
                capabilities=("repo.read", "repo.write"),
                model_policy=OmniRoutePolicy(required_capabilities=frozenset({"reasoning"})),
                resources=ResourceLimits(max_parallel=2, max_tokens=8000),
                boundaries=("no.deploy",),
            ),
            AgentDefinition(
                "reviewer",
                "verification",
                "Review evidence",
                skills=("testing",),
                capabilities=("repo.read",),
            ),
        )
    )


def test_agent_definition_is_deterministic_and_validates_limits():
    registry = make_registry()
    assert registry.get("architect").canonical()["skills"] == ["architecture"]
    assert registry.digest() == registry.digest()
    with pytest.raises(BuilderError):
        ResourceLimits(max_parallel=0)
    with pytest.raises(BuilderError):
        AgentDefinition("Bad ID", "role", "description")


def test_registry_rejects_conflicting_duplicate_ids():
    registry = make_registry()
    with pytest.raises(BuilderError, match="already registered"):
        registry.register(AgentDefinition("architect", "different", "different"))


def test_team_builder_requires_registered_members_and_builds_manifest():
    builder = TeamBuilder(make_registry())
    team = builder.build(
        "delivery-team",
        "Build and verify a change",
        ("architect", "reviewer"),
        handoffs=(("architect", "reviewer"),),
        max_parallel=3,
    )
    assert builder.capabilities(team) == ("repo.read", "repo.write")
    assert builder.effective_parallelism(team) == 3
    manifest = builder.manifest(team)
    assert manifest["team"]["team_id"] == "delivery-team"
    assert len(manifest["manifest_sha256"]) == 64
    assert builder.manifest(team) == manifest

    with pytest.raises(BuilderError, match="unknown agent"):
        builder.build("broken", "broken", ("missing",))


def test_team_rejects_invalid_handoffs_and_duplicate_members():
    builder = TeamBuilder(make_registry())
    with pytest.raises(BuilderError):
        builder.build("bad", "bad", ("architect", "architect"))
    with pytest.raises(BuilderError):
        builder.build("bad", "bad", ("architect", "reviewer"), handoffs=(("architect", "missing"),))
    with pytest.raises(BuilderError):
        builder.build("bad", "bad", ("architect",), handoffs=(("architect", "architect"),))


def test_catalog_order_and_team_capabilities_are_stable():
    registry = make_registry()
    assert [agent.agent_id for agent in registry.list()] == ["architect", "reviewer"]
    team = TeamBuilder(registry).build("stable", "stable", ("reviewer", "architect"))
    assert TeamBuilder(registry).manifest(team) == TeamBuilder(registry).manifest(team)

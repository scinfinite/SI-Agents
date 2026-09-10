# isort: skip_file

import tempfile
import unittest
from pathlib import Path

from core.organization import AgentStatus, load_catalog
from core.organization.models import AgentDefinition, Division
from core.organization.registry import AgentCatalog


CATALOG = Path(__file__).parents[1] / "config" / "agent-catalog.json"


class AgentCatalogTests(unittest.TestCase):
    def test_canonical_catalog_loads_and_validates(self) -> None:
        catalog = load_catalog(CATALOG)
        self.assertEqual(len(catalog.all_divisions()), 7)
        self.assertEqual(len(catalog.all()), 279)
        self.assertEqual(catalog.validate(), ())
        self.assertTrue(all(agent.status is AgentStatus.CATALOGED for agent in catalog.all()))

    def test_catalog_selection_is_capability_and_permission_aware(self) -> None:
        catalog = load_catalog(CATALOG)
        selected = catalog.select(
            division="engineering",
            required_capabilities=("filesystem",),
            required_permissions=("repository_read",),
            environment="codespace",
        )
        self.assertGreater(len(selected), 0)
        self.assertTrue(all("filesystem" in agent.capabilities for agent in selected))
        self.assertTrue(all("repository_read" in agent.permissions for agent in selected))

    def test_catalog_selection_can_require_skill_and_harness(self) -> None:
        catalog = load_catalog(CATALOG)
        selected = catalog.select(
            required_skills=("verify-change",),
            harness="opencode",
            environment="termux",
        )
        self.assertEqual(len(selected), 279)

    def test_duplicate_division_and_agent_are_rejected(self) -> None:
        catalog = AgentCatalog()
        division = Division("engineering", "Engineering", "Build software")
        catalog.register_division(division)
        with self.assertRaisesRegex(ValueError, "Duplicate division"):
            catalog.register_division(division)

        agent = AgentDefinition(
            id="example-agent",
            name="Example Agent",
            division="engineering",
            description="Build software",
            responsibilities=("implement",),
            deliverables=("change",),
            success_criteria=("tested",),
            boundaries=("no bypass",),
        )
        catalog.register(agent)
        with self.assertRaisesRegex(ValueError, "Duplicate agent id"):
            catalog.register(agent)

    def test_invalid_catalog_status_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "catalog.json"
            path.write_text(
                '{"version":1,"divisions":[{"id":"engineering","name":"Engineering","description":"Build"}],'
                '"agents":[{"id":"bad","name":"Bad","division":"engineering","description":"Bad",'
                '"responsibilities":["x"],"deliverables":["x"],"success_criteria":["x"],"boundaries":["x"],'
                '"status":"unknown"}]}',
                encoding="utf-8",
            )
            with self.assertRaisesRegex(ValueError, "'unknown' is not a valid AgentStatus"):
                load_catalog(path)


if __name__ == "__main__":
    unittest.main()

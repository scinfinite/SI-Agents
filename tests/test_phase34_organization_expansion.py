import json
import tempfile
import unittest
from pathlib import Path

from core import organization


ROOT = Path(__file__).parents[1]
CATALOG = ROOT / "config" / "agent-catalog.json"
EXPANSION = ROOT / "config" / "organization-expansion.v1.json"


class OrganizationExpansionTests(unittest.TestCase):
    def test_canonical_expansion_covers_catalog(self) -> None:
        catalog = organization.load_catalog(CATALOG)
        expansion = organization.load_expansion(EXPANSION, CATALOG)
        self.assertEqual(len(expansion.teams), 5)
        self.assertEqual(len(expansion.division_assignments), 18)
        self.assertEqual(len(expansion.workflows), 4)
        self.assertEqual(expansion.validate(catalog.all_divisions(), catalog.all()), ())

    def test_every_division_has_exactly_one_home_team(self) -> None:
        expansion = organization.load_expansion(EXPANSION, CATALOG)
        assignments = [item.division_id for item in expansion.division_assignments]
        self.assertEqual(len(assignments), len(set(assignments)))
        self.assertEqual(set(assignments), {division.id for division in organization.load_catalog(CATALOG).all_divisions()})

    def test_workflow_agents_must_belong_to_the_declared_team(self) -> None:
        expansion = organization.load_expansion(EXPANSION, CATALOG)
        workflow = expansion.workflows[0]
        invalid_step = organization.WorkflowStep(
            id="invalid",
            kind=organization.WorkflowStepKind.EXECUTION,
            team_id="security-verification",
            agent_id="si-engineering-senior-developer",
            purpose="invalid cross-team membership",
            depends_on=(),
        )
        malformed = organization.WorkflowDefinition(
            id="malformed",
            name="Malformed",
            purpose="Test invalid team membership",
            steps=(
                workflow.steps[0],
                invalid_step,
                organization.WorkflowStep(
                    id="verify",
                    kind=organization.WorkflowStepKind.VERIFICATION,
                    team_id="security-verification",
                    agent_id="si-verification-evidence-collector",
                    purpose="verify",
                    depends_on=("invalid",),
                ),
            ),
        )
        candidate = organization.OrganizationExpansion(
            version=1,
            teams=expansion.teams,
            division_assignments=expansion.division_assignments,
            workflows=expansion.workflows + (malformed,),
        )
        errors = candidate.validate(organization.load_catalog(CATALOG).all_divisions(), organization.load_catalog(CATALOG).all())
        self.assertTrue(any("is not a member" in error for error in errors))

    def test_later_step_dependency_is_rejected(self) -> None:
        step_a = organization.WorkflowStep(
            id="a",
            kind=organization.WorkflowStepKind.PLANNING,
            team_id="engineering-delivery",
            agent_id="si-delivery-project-manager-senior",
            purpose="plan",
            depends_on=("b",),
        )
        step_b = organization.WorkflowStep(
            id="b",
            kind=organization.WorkflowStepKind.VERIFICATION,
            team_id="engineering-delivery",
            agent_id="si-verification-reality-checker",
            purpose="verify",
        )
        workflow = organization.WorkflowDefinition(
            "bad-order", "Bad order", "dependency regression", (step_a, step_b)
        )
        expansion = organization.load_expansion(EXPANSION, CATALOG)
        candidate = organization.OrganizationExpansion(
            version=1,
            teams=expansion.teams,
            division_assignments=expansion.division_assignments,
            workflows=(workflow,),
        )
        errors = candidate.validate(organization.load_catalog(CATALOG).all_divisions(), organization.load_catalog(CATALOG).all())
        self.assertTrue(any("depends on a later step" in error for error in errors))

    def test_unknown_agent_in_expansion_is_rejected(self) -> None:
        expansion = organization.load_expansion(EXPANSION, CATALOG)
        broken_team = organization.TeamDefinition(
            id="broken",
            name="Broken",
            purpose="test",
            division_ids=("si-engineering",),
            member_agent_ids=("does-not-exist",),
            lead_agent_id="does-not-exist",
        )
        candidate = organization.OrganizationExpansion(
            version=1,
            teams=expansion.teams + (broken_team,),
            division_assignments=expansion.division_assignments,
            workflows=expansion.workflows,
        )
        errors = candidate.validate(organization.load_catalog(CATALOG).all_divisions(), organization.load_catalog(CATALOG).all())
        self.assertTrue(any("references unknown agents" in error for error in errors))

    def test_loader_rejects_wrong_version(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "expansion.json"
            payload = json.loads(EXPANSION.read_text(encoding="utf-8"))
            payload["version"] = 2
            path.write_text(json.dumps(payload), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "version"):
                organization.load_expansion(path, CATALOG)

    def test_organization_layer_does_not_contain_authority_fields(self) -> None:
        payload = json.loads(EXPANSION.read_text(encoding="utf-8"))
        serialized = json.dumps(payload).lower()
        self.assertNotIn('"permissions"', serialized)
        self.assertNotIn('"capabilities"', serialized)
        self.assertNotIn('"credentials"', serialized)


if __name__ == "__main__":
    unittest.main()

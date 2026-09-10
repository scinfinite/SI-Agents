# Phase 34 — Organization Expansion

**Status:** Implementation complete; pending merge and final mainline CI.

## Scope

Phase 34 turns the 279-agent catalog into an inspectable operating organization without importing an external persona roster or creating a second permission authority.

The organization layer answers four questions:

1. Which operating team owns a division's organizational home?
2. Which small set of existing SI agents form the core of that team?
3. Which repeatable workflows coordinate those responsibilities?
4. Where are verification gates explicit?

Agent capabilities, permissions, credentials, and governance remain owned by their existing SI Core systems. Organization metadata cannot grant authority.

## Implementation

- `core/organization/expansion.py` defines immutable Team, DivisionAssignment, Workflow, and WorkflowStep contracts.
- `core/organization/expansion_loader.py` loads the declarative organization layer and validates every reference against `config/agent-catalog.json`.
- `config/organization-expansion.v1.json` defines five operating teams, a single organizational home for all 18 divisions, and four evidence-gated workflows.
- `core/organization/__init__.py` exposes the expansion contracts and loader.
- `pyproject.toml` packages the expansion catalog with distributions.

## Operating model

```text
18 divisions
     ↓ one organizational home each
5 operating teams
     ↓ bounded workflow roles
4 reusable workflows
     ↓ explicit verification gates
Evidence-backed handoff
```

The five operating teams are:

- Engineering & Delivery
- Security & Governance Assurance
- Research & Strategy
- Product & Experience
- Operations & Support

The teams are deliberately small coordination units. The 279-agent catalog remains the canonical source for individual agent identity and responsibilities; the expansion layer does not duplicate every persona into a new team-specific definition.

## Workflows

The initial workflow set covers:

- Governed Change Delivery
- Security Assurance
- Evidence-Backed Discovery
- Product Discovery to Delivery

Every workflow contains an explicit verification step. Dependencies are ordered and validated, and a workflow step may only name an agent that belongs to its declared team.

## Security and authority boundary

Organization configuration is coordination metadata. It cannot declare or inherit `permissions`, `capabilities`, `credentials`, or other authority fields. Existing Governance remains the only authorization boundary.

The loader validates unknown agents, unknown divisions, unknown teams, duplicate IDs, invalid workflow dependencies, later-step dependencies, and cross-team agent references. It never executes workflow steps.

## External pattern review

Current ECC guidance emphasizes focused specialized workers, explicit workflows, tests, review, verification, and evidence rather than simply increasing the number of agents. Current Agency Agents material similarly demonstrates that useful organizations are assembled from small teams and repeatable multi-agent workflows, with division consistency treated as a source-of-truth concern. SI-Agents uses these engineering patterns independently and does not copy external prompts, code, branding, or architecture. citeturn0search1turn0search6turn0search9

## Verification plan

Exit gates require:

- canonical 279-agent catalog remains valid;
- all 18 divisions have exactly one organizational home;
- all team and workflow references resolve to canonical agents;
- every workflow has a verification gate;
- adversarial malformed organization data is rejected;
- distribution packaging includes the expansion catalog;
- Ruff and full pytest pass;
- documentation is synchronized;
- implementation is merged to `main`;
- final mainline CI is green on the documentation-synchronized merge commit.

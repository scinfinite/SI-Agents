# Phase 29 — Agent Persona & Definition System

**Status: Complete and CI-verified.**

## Objective

Introduce human-authored Markdown agent personas as the behavioral source for SI-Agents while retaining typed machine contracts as the authority for capabilities, permissions, harness compatibility, environments, lifecycle, and execution.

## Canonical model

```text
agents/**/agent.md
        |
        v
 deterministic Markdown parser
        |
        v
 AgentPersona (behavioral data)
        |
        +---- validation
        |
        v
 compile with existing AgentDefinition
        |
        v
 governed organization registry/runtime
```

The repository currently uses one Markdown file per canonical persona under `agents/<division>/`. The filename and path are organizational metadata; the stable identity is the frontmatter `id`.

## Contract

Persona files use `si-agents.agent-persona.v1` frontmatter with:

- `version`
- `id`
- `name`
- `division`
- `description`

Required Markdown sections are:

1. Identity
2. Personality
3. Core Mission
4. Expertise
5. Responsibilities
6. Workflow
7. Critical Rules
8. Boundaries
9. Deliverables
10. Failure Behavior
11. Escalation Behavior
12. Verification Expectations
13. Evidence Requirements

List sections require Markdown bullets. Scalar sections require exactly one paragraph. Duplicate keys/sections/items, malformed frontmatter, missing sections, invalid IDs, and unsupported schema/version values fail closed.

## Governance boundary

Personas are data. They are never executable instructions, permission manifests, tool manifests, or credential stores. The parser rejects privilege/execution fields including capabilities, permissions, harnesses, environments, tools, commands, shell, network, credentials, and secrets.

`compile_persona()` requires an existing typed `AgentDefinition` with matching stable identity, name, and division. Governance fields are copied unchanged from that typed contract. Persona text can refine behavioral fields only; it cannot grant privileges or change implementation authority.

## Canonical personas

The initial canonical persona set is:

- Engineering: Developer, Backend Engineer, Infrastructure Engineer
- Debugging: Debugger
- Verification: Tester, Code Reviewer
- Security: Security Engineer

Infrastructure Engineer is also registered in the canonical agent catalog as a cataloged agent. Existing catalog entries remain authoritative for machine-facing permissions/capabilities and implementation status.

## Provenance and independent design

Current ECC and Agency Agents repositories were inspected as external references. Reusable concepts were generalized rather than copied:

- ECC: specialized agent roles, reusable engineering workflows, explicit verification, security scanning, and separation of behavioral assets from harness integration.
- Agency Agents: human-readable identity/personality, mission, workflow, deliverables, and success-oriented specialist definitions.

No external prompt text, distinctive prose, implementation, or repository architecture is copied into SI-Agents. External material remains untrusted reference data and cannot override SI governance.

## Verification

Phase 29 tests cover:

- deterministic parsing and typed conversion
- malformed and unterminated frontmatter
- duplicate keys and sections
- missing required sections
- malformed list sections
- rejected privilege/execution frontmatter
- stable identity/name/division matching
- compilation preserving capabilities, permissions, harnesses, environments, and implementation
- duplicate registry identities/names
- catalog conflict detection
- directory discovery
- all seven canonical personas parsing and matching the catalog
- persona content containing command-like text remaining inert data
- catalog JSON validity
- semantic validation

Canonical Markdown files are included in distributions through setuptools package data.

## Completion gate

Phase 29 is complete only when implementation, security boundaries, tests, distribution packaging, documentation, and CI all pass. The next phase is Phase 30 — first-class portable Skills.

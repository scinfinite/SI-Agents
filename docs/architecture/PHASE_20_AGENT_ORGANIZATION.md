# Phase 20 — Agent Organization & Catalog

**Status: Complete — canonical catalog, typed registry, selection, and CI tests implemented.**

## Purpose

Phase 20 establishes the missing organization layer identified by the Phase 19 reality audit. SI-Agents now has a machine-readable source of truth for divisions and agent roles without pretending that every cataloged role already has an executable worker.

## Design

- `config/agent-catalog.json` is the canonical catalog source.
- `core/organization/models.py` defines typed `Division`, `AgentDefinition`, and lifecycle status.
- `core/organization/registry.py` provides duplicate-safe registration, lookup, division grouping, capability/permission/skill/harness/environment selection, and consistency validation.
- `core/organization/loader.py` loads the catalog with the Python standard library only; no YAML/runtime dependency is introduced.
- Existing executable workers remain under `agents/`. The catalog references implemented workers explicitly and keeps catalog-only roles declarative.
- Catalog membership never grants execution permission. Runtime permission checks remain the responsibility of the existing governance/runtime layers.

## Initial organization

The catalog contains 7 divisions and 12 roles:

- Engineering: Developer, Backend Engineer, Frontend Engineer
- Debugging: Debugger
- Verification: Tester, Code Reviewer, Reality Checker
- Architecture: Software Architect
- Security: Security Engineer
- Research: Technology Researcher
- Operations: Release Engineer, Cost Governance Engineer

Three roles are executable today: Developer, Debugger, and Tester. The remaining roles are intentionally `cataloged` rather than falsely marked implemented.

## Selection contract

Agents can be selected by:

- division
- required skills
- required capabilities
- required permissions
- harness
- environment
- lifecycle status

Selection is declarative. It does not spawn an agent, grant a permission, invoke a harness, or bypass governance.

## Evidence and limitations

Phase 20 does not implement:

- multi-agent orchestration or team execution
- external harness adapters
- OpenCode integration
- OmniRoute integration
- Termux/Codespace installers
- automatic prompt/persona generation
- automatic agent promotion or self-modification
- dynamic remote agent discovery

Those remain separate workstreams so that organization, execution, transport, and governance stay independently testable.

## Reference-derived decisions

ECC's current source separates agents, skills, rules, and harness surfaces, while its team-builder dynamically discovers agents rather than relying on hard-coded lists. Agency Agents similarly treats a division catalog as a source of truth, with CI checking directory/catalog consistency. SI-Agents adopts the useful source-of-truth and discovery principles, but adds typed capabilities, permissions, environments, lifecycle status, and explicit implementation references so catalog membership cannot be confused with execution authority.

## Acceptance criteria

1. Catalog parses with no third-party runtime dependency.
2. Every agent references a declared division.
3. IDs and names are unique.
4. Required identity, responsibilities, deliverables, success criteria, and boundaries are mandatory.
5. Implemented agents declare their executable implementation path.
6. Selection can filter by capability and permission without granting either.
7. Existing agent implementations remain compatible.
8. Tests cover loading, validation, duplicate rejection, selection, and invalid status handling.
9. CI runs the new tests together with the existing full suite.
10. Documentation records the actual implemented boundary and future exclusions.

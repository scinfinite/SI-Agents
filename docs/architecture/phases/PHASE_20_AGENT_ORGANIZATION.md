# Phase 20 — Agent Organization & Catalog

**Status: Complete — canonical catalog, typed registry, selection, and CI-verified tests implemented.**

## Purpose

Phase 20 establishes the organization layer identified by the Phase 19 reality audit. SI-Agents has a machine-readable source of truth for divisions and agent roles without pretending that every cataloged role already has an executable worker.

## Design

- `config/agent-catalog.json` is the canonical catalog source.
- `core/organization/models.py` defines typed `Division`, `AgentDefinition`, and lifecycle status.
- `core/organization/registry.py` provides duplicate-safe registration, lookup, division grouping, capability/permission/skill/harness/environment selection, and consistency validation.
- `core/organization/loader.py` loads the catalog with the Python standard library only.
- Existing executable workers remain under `agents/`. The catalog references implemented workers explicitly and keeps catalog-only roles declarative.
- Catalog membership never grants execution permission.

## Initial organization at Phase 20 completion

The Phase 20 catalog contained 7 divisions and 12 roles. Three roles were executable at that phase; the remainder were intentionally cataloged rather than falsely marked implemented.

## Selection contract

Agents can be selected by division, required skills, required capabilities, required permissions, harness, environment, and lifecycle status. Selection is declarative and does not spawn an agent, grant permission, invoke a harness, or bypass governance.

## Independent design lesson

General patterns from external specialist-organization research reinforced the usefulness of explicit source-of-truth catalogs and dynamic discovery. SI-Agents independently implemented typed capabilities, permissions, environments, lifecycle status, and explicit implementation references.

## Verification

Phase 20 acceptance covered catalog parsing, division consistency, unique IDs/names, required identity fields, implementation references, selection filtering, compatibility, and invalid-status handling. The final Phase 20 CI evidence is retained as the historical verification for this phase.

## Current-state addendum

Phase 20 is a historical organization baseline. Later phases expanded the canonical organization and added human-authored personas. As of Phase 29, persona files live under `agents/<division>/`, compile only against typed `AgentDefinition` contracts, and cannot grant privileges. Current catalog/status truth is maintained in `PHASES.md` and the repository's current organization files; the Phase 20 counts above describe the catalog **at Phase 20 completion**, not today's final organization.

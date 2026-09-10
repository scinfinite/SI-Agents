# Phase 29 — SI Agent Persona System

**Status:** Complete — 279 SI-native specialist personas represented, validated, packaged, and tested.

## 1. Purpose

Phase 29 establishes the complete specialist persona layer for SI-Agents. Personas are human-readable behavioral data; typed SI contracts remain authoritative for capabilities, permissions, harness compatibility, environments, lifecycle, execution, and governance.

The phase expanded the initial persona machinery into a complete 279-definition corpus and made deterministic identity, security, packaging, provenance, and verification requirements explicit.

## 2. Completion snapshot

- Immutable reference snapshot: `6d29a9b08785a0e49ffc9818bbdd381164c2df5f`
- Definitions represented: **279**
- Domain divisions represented: **18**
- SI persona files: **279**
- Missing mappings: **0**
- Duplicate identities: **0**
- Invalid personas: **0**
- Governance leakage: **0**
- Hidden Unicode control characters: **0**

The snapshot identifier is provenance evidence only. It is not a governance authority or a permanent future count.

## 3. SI-native organization

The persona corpus is organized under SI-owned divisions rather than preserving an external directory taxonomy. Current persona directories are:

- `agents/si-cognition/`
- `agents/si-creative/`
- `agents/si-delivery/`
- `agents/si-engineering/`
- `agents/si-finance/`
- `agents/si-game/`
- `agents/si-geospatial/`
- `agents/si-growth/`
- `agents/si-health/`
- `agents/si-market/`
- `agents/si-product/`
- `agents/si-research/`
- `agents/si-revenue/`
- `agents/si-security/`
- `agents/si-spatial/`
- `agents/si-specialized/`
- `agents/si-support/`
- `agents/si-verification/`

Every persona has an SI-specific identity, identifier, filename, and division. For example, the engineering AI specialist is `si-engineering-ai-engineer` in `agents/si-engineering/si-ai-engineer.md`.

The four legacy Python modules in `agents/` are runtime compatibility/model modules, not the persona corpus. Markdown persona artifacts are the canonical specialist definitions.

## 4. Canonical persona model

The flow is:

```text
specialist inventory
      |
      v
file-level audit
      |
      v
SI-native persona definition
      |
      v
deterministic Markdown parser
      |
      v
AgentPersona
      |
      +---- semantic/security validation
      |
      v
compile with AgentDefinition
      |
      v
governed organization registry/runtime
```

Persona frontmatter uses `si-agents.agent-persona.v1` with `version`, `id`, `name`, `division`, and `description`. Behavioral sections cover identity, personality, mission, expertise, responsibilities, workflow, critical rules, boundaries, deliverables, failure behavior, escalation behavior, verification expectations, and evidence requirements.

## 5. Governance and security boundary

Persona Markdown is configuration data, not executable authority. Importing, editing, or selecting a persona never grants permissions, tools, credentials, environments, commands, network access, or execution authority.

The parser rejects privilege/execution-bearing frontmatter. `compile_persona()` requires a matching typed `AgentDefinition` and preserves typed governance fields. Persona text can refine behavior but cannot change implementation authority.

Imported material is untrusted reference data. Command-like text remains inert until an independently authorized execution path interprets an instruction.

Hidden Unicode/control-character checks are part of the persona corpus audit.

## 6. Provenance and independent design

The implementation records only generalized engineering lessons from inspected specialist-agent and automation systems. SI-Agents uses its own schema, identifiers, divisions, behavioral vocabulary, governance boundaries, parser, registry, catalog, tests, and packaging.

The provenance workflow is:

`inspect → identify reusable concept → record provenance → design independently → implement → verify → record evidence`

`config/persona-source-index.json` retains the immutable snapshot identifier and aggregate inventory facts. Provenance establishes lineage; it does not grant authority.

## 7. Verification and packaging

Phase 29 requires all of the following:

- exactly 279 discoverable persona Markdown files
- exactly 279 catalog entries
- unique SI-native identities
- deterministic parsing and validation
- security-boundary enforcement
- hidden Unicode/control-character checks
- provenance validation
- package inclusion of the complete persona corpus
- distribution build success
- isolated wheel installation/import success
- CLI smoke checks
- Ruff success
- full pytest success
- repository hygiene success
- final CI success on the final repository head

The completed verification run recorded **358 tests passed** together with successful distribution build, wheel installation/import, CLI smoke checks, and Ruff.

## 8. CI modernization

GitHub Actions uses Node 24-compatible action majors:

- `actions/checkout@v5`
- `actions/setup-python@v6`

This removes the repository's use of the deprecated Node 20 action majors and prevents the corresponding CI deprecation warning.

## 9. Documentation consolidation

This file is the single canonical Phase 29 architecture record. The former separate Phase 29 audit, persona, and provenance documents are consolidated here so Phase 29 has one authoritative Markdown record.

Current-state phase status belongs here and in the phase index; historical phase records remain historical where appropriate.

## 10. Exit gate

Phase 30 — First-Class Portable Skills may begin only after this Phase 29 state is accepted and the final CI gate remains green.

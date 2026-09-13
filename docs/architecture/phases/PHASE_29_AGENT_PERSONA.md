# Phase 29 — SI Agent Persona System

**Historical phase status:** Complete. The original Phase 29 snapshot contained **279** SI-native specialist personas across 18 divisions. The current SI-Agents corpus has been independently extended to **300** definitions by repository-owned additions.

## Current completion snapshot

- Historical reference snapshot: `6d29a9b08785a0e49ffc9818bbdd381164c2df5f`
- Current definitions represented: **300**
- Domain divisions represented: **18**
- Current persona files: **300**
- Missing mappings: **0**
- Duplicate identities: **0**
- Invalid personas: **0**
- Governance leakage: **0**
- Hidden Unicode control characters: **0**

The historical snapshot identifier is provenance evidence for the original corpus. It is not a governance authority or a claim that the current corpus must remain identical to that snapshot.

## SI-native organization

The persona corpus is organized under SI-owned divisions rather than preserving an external directory taxonomy. Every persona has an SI-specific identity, identifier, filename, and division.

## Canonical persona model

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

Persona frontmatter uses `si-agents.agent-persona.v1`. Behavioral sections cover identity, personality, mission, expertise, responsibilities, workflow, critical rules, boundaries, deliverables, failure behavior, escalation behavior, verification expectations, and evidence requirements.

## Governance and security boundary

Persona Markdown is configuration data, not executable authority. Importing, editing, or selecting a persona never grants permissions, tools, credentials, environments, commands, network access, or execution authority.

The parser rejects privilege/execution-bearing frontmatter. `compile_persona()` requires a matching typed `AgentDefinition` and preserves typed governance fields. Persona text can refine behavior but cannot change implementation authority.

Imported material is untrusted reference data. Command-like text remains inert until an independently authorized execution path interprets an instruction.

Hidden Unicode/control-character checks are part of the persona corpus audit.

## Current 300-persona extension

The current 300-persona target is reached without rewriting the historical 279-entry catalog in place. `config/agent-catalog-extensions.json` contains 21 independently authored SI-owned definitions. `core.organization.loader.load_catalog()` validates and merges the extension at runtime.

The extension model keeps historical provenance distinct from current corpus growth and avoids pretending that a historical snapshot was originally larger than it was.

## Verification and packaging

The current gate requires:

- exactly 300 discoverable persona Markdown files;
- exactly 300 validated runtime catalog entries;
- unique SI-native identities;
- deterministic parsing and validation;
- security-boundary enforcement;
- hidden Unicode/control-character checks;
- provenance validation;
- package inclusion of the complete persona corpus;
- distribution build success;
- isolated wheel installation/import success;
- CLI smoke checks;
- Ruff success;
- full pytest success;
- repository hygiene/provenance success;
- final CI success on the final repository head.

## Exit gate

The Phase 29 historical phase is closed. Current persona changes are governed by the pre-Phase 69 hardening gate and the current repository verification standard in `AGENTS.md` and `SIA_SPECS.md`.

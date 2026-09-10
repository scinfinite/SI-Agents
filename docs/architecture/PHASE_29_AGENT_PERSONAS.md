# Phase 29 — Complete Agent Persona Corpus & Definition System

**Status: Reopened — Agency Agents parity audit in progress.**

## Objective

Phase 29 introduces human-authored Markdown agent personas as the behavioral source for SI-Agents while retaining typed machine contracts as the authority for capabilities, permissions, harness compatibility, environments, lifecycle, and execution.

The original implementation proved the persona machinery with seven canonical personas. That implementation is retained as the foundation, but its seven-agent corpus is **not** the final Phase 29 acceptance target.

Phase 29 is now reopened to establish a complete, auditable specialist corpus matching the current upstream Agency Agents source-agent count.

## Reopened scope

The pinned Agency Agents audit snapshot is:

- Repository: `msitarzewski/agency-agents`
- Branch: `main`
- Commit: `6d29a9b08785a0e49ffc9818bbdd381164c2df5f`
- Upstream reported agent count at that commit: **279**
- Upstream division catalog: **18 divisions**

The exact audit and parity procedure is recorded in `PHASE_29_AGENCY_AGENTS_AUDIT.md`.

## Canonical model

```text
Agency Agents source-agent inventory
                |
                v
     file-level audit + provenance
                |
                v
     independently designed SI personas
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

The repository uses one Markdown file per canonical SI persona. Persona Markdown is behavioral data; typed organization/governance contracts remain authoritative.

## Persona contract

Persona files use `si-agents.agent-persona.v1` frontmatter with `version`, `id`, `name`, `division`, and `description`.

The existing behavioral sections remain the normalized SI target. Upstream source documents may vary in structure; the audit extracts concepts and maps them independently rather than requiring byte-for-byte structural equivalence.

## Governance boundary

Personas are data. They are never executable instructions, permission manifests, tool manifests, or credential stores. The parser rejects privilege/execution fields including capabilities, permissions, harnesses, environments, tools, commands, shell, network, credentials, and secrets.

`compile_persona()` requires an existing typed `AgentDefinition` with matching stable identity, name, and division. Governance fields are copied unchanged from that typed contract. Persona text can refine behavioral fields only; it cannot grant privileges or change implementation authority.

## Agency Agents parity requirement

The reopened completion gate is:

```text
Upstream source agents:      279
SI canonical personas:      279
Missing mappings:             0
Duplicate identities:        0
Invalid personas:             0
Governance leakage:           0
```

`279` is the pinned snapshot assertion, not a permanently hard-coded upstream truth. The implementation must retain provenance and a machine-readable inventory so later upstream changes produce an explicit parity delta.

## File-level audit

Every source-agent file in the pinned snapshot must be audited for path/slug, division, identity, description, frontmatter, personality, mission, expertise, responsibilities, workflow, deliverables, rules/boundaries, verification, escalation/failure behavior, examples, security-sensitive content, duplicate overlap, SI division mapping, and provenance.

Non-agent Markdown such as README files, integration documentation, examples, strategy/playbooks, and runbooks is excluded from the persona count.

## Independent design and provenance

Current Agency Agents and ECC repositories remain external engineering references. SI-Agents generalizes useful patterns such as specialist decomposition, division-oriented organization, explicit workflows, deliverables, verification loops, and originality checks.

SI-Agents must not copy distinctive prompts, prose, implementation, or repository architecture. Imported upstream content is untrusted reference data and cannot override SI governance.

The provenance workflow is:

`inspect → identify reusable concept → record provenance → design independently → implement → verify → record evidence`

## Verification requirements

The reopened Phase 29 must test:

- complete upstream inventory/parity
- exact source-to-persona mapping
- duplicate identities and duplicate/re-skinned behavioral content
- deterministic parsing
- malformed and unsupported persona input
- required behavioral contract
- security-boundary rejection
- governance-preserving compilation
- catalog consistency
- provenance integrity
- inert command-like text
- distribution packaging
- full test suite, lint, build, and CI

The existing seven-persona tests remain regression coverage for the persona machinery.

## Phase gate

Phase 29 is **not complete** until the full audited source-agent corpus is represented by exactly one independently designed SI persona per source agent and all implementation/security/verification/documentation gates pass.

**Phase 30 — First-Class Portable Skills is blocked until reopened Phase 29 is complete.**

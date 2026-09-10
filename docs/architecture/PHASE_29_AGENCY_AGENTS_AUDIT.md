# Phase 29 — Agency Agents Parity Audit

**Status: Audit in progress. Phase 29 is intentionally reopened.**

## Purpose

The original Phase 29 implementation introduced the persona system but stopped at seven canonical personas. That is not the intended Phase 29 scope. SI-Agents must first establish the full specialist roster represented by the current `msitarzewski/agency-agents` source corpus, then independently model that roster inside SI governance.

This document records the upstream audit baseline before expanding the SI-Agent corpus.

## Upstream snapshot

- Repository: `msitarzewski/agency-agents`
- Branch: `main`
- Audited tree commit: `6d29a9b08785a0e49ffc9818bbdd381164c2df5f`
- Upstream commit message reports: **279 agents** and verification of converted outputs across 14 tools.
- Division catalog: `divisions.json`
- Current division count: **18**

The upstream commit itself is the authoritative snapshot for this parity effort. The upstream README contains older roster/count material and must not be treated as the live count source.

## Current upstream divisions

1. Academic
2. Design
3. Engineering
4. Finance
5. Game Development
6. GIS
7. Healthcare
8. Marketing
9. Paid Media
10. Product
11. Project Management
12. Research
13. Sales
14. Security
15. Spatial Computing
16. Specialized
17. Support
18. Testing

## What counts as an agent

SI-Agents will **not** count every Markdown file in the upstream repository.

The upstream repository contains non-agent Markdown under documentation, integrations, examples, strategy, playbooks, and runbooks. Those files are not specialist-agent definitions.

The parity corpus is the set of source agent Markdown files under the authoritative division set that satisfy the upstream agent-file/frontmatter contract.

Therefore the target is:

> **One SI persona per upstream source-agent definition, not one persona per arbitrary `.md` file.**

## Upstream observations

### 1. The roster is substantially larger than the previous SI catalog

The previous SI Phase 29 corpus contained only seven personas. The audited upstream snapshot reports **279 agents**. This means the previous completion claim did not satisfy roster parity and Phase 29 must be reopened.

### 2. The roster is heterogeneous

The source corpus contains short and long specialist definitions, broad roles and highly technical specialists, nested subdirectories, market/platform specialists, verification roles, business roles, and specialized roles. SI's persona schema therefore needs to normalize behavioral concepts without requiring every upstream source document to have identical section structure.

### 3. Division membership is explicit

`divisions.json` is the upstream division source of truth. The repository's own validation tooling checks division-directory consistency. SI will record the upstream division and an SI canonical division mapping rather than infer organization membership from prose alone.

### 4. Generated integrations are not source personas

The upstream repository contains tool-specific integration outputs. These must not be imported as additional agents. The source corpus is the division-organized agent definitions; generated integration copies remain deployment artifacts.

### 5. Originality is explicitly guarded upstream

The upstream repository has an originality checker based on normalized shingle overlap. SI will use the engineering lesson—detect duplicate/re-skinned roles—but will implement its own independent validator and thresholds.

### 6. Persona content is untrusted data

Upstream Markdown will be treated as reference data. It does not grant SI capabilities, permissions, tools, commands, network access, credentials, harnesses, or execution authority. SI typed governance remains authoritative.

## File-level audit procedure

Before generating the expanded SI corpus, every source-agent file in the 279-agent snapshot will be audited for:

- path and stable slug
- upstream division
- display name
- description
- frontmatter fields
- identity/personality material
- mission and responsibilities
- expertise/specialization
- workflow/process material
- deliverables/output expectations
- rules and boundaries
- verification/success criteria
- escalation/failure behavior where present
- examples and implementation-specific material
- potentially executable or privilege-bearing text
- duplicate/re-skin overlap
- proposed SI division mapping
- proposed SI persona identity
- provenance reference to the pinned upstream file SHA

The audit must preserve the distinction between **behavioral concepts** and **machine/governance authority**.

## SI implementation target

The reopened Phase 29 target is:

```text
Agency Agents source definitions: 279
SI canonical personas:             279
Missing mappings:                   0
Duplicate SI identities:            0
Unvalidated personas:               0
Governance leakage:                 0
```

The numeric target is a snapshot assertion, not a permanent hard-coded upstream truth. The implementation will retain the pinned upstream SHA and a machine-readable inventory so a future upstream update can produce an explicit parity delta.

## Implementation sequence

1. Freeze and record the upstream snapshot.
2. Produce the complete 279-entry source inventory.
3. Complete file-level structural/semantic/security audit.
4. Define the independent SI division mapping.
5. Expand the SI persona corpus to exactly one persona per audited source agent.
6. Preserve typed `AgentDefinition` governance authority.
7. Add deterministic parity, duplicate, provenance, and security regression tests.
8. Verify packaging/distribution and the complete test suite.
9. Update Phase 29 status only after all gates pass.
10. Do not begin Phase 30 until the reopened Phase 29 completion gate is satisfied.

## Provenance rule

Agency Agents is an external reference corpus. SI-Agents may generalize useful concepts such as specialist decomposition, division organization, explicit workflows, deliverables, and verification loops. SI-Agents must not copy distinctive prompts, prose, implementation, or repository architecture.

The provenance workflow remains:

`inspect → identify reusable concept → record provenance → design independently → implement → verify → record evidence`

## Current state

This audit has established the authoritative upstream snapshot and corrected the Phase 29 scope. The previous seven-persona completion record is historical evidence of the first implementation of the persona machinery; it is no longer the completion gate for Phase 29.

**Phase 30 remains blocked until this reopened Phase 29 is complete.**

# Phase 32 — Memory & Knowledge

**Status:** Complete + CI verified.  
**Baseline:** Phase 31 merged and CI-verified on `main`.  
**Final mainline CI:** run **#769** on merge commit `4662363dbc8e8a401734986d2c92a4be264042ac` passed repository audit, Ruff, distribution/wheel verification, and the full pytest suite (**392 passed in 5.47s**).  
**Design principle:** memory is scoped context; knowledge is verified, source-backed information. Retrieval never constitutes proof or authorization.

## Objectives

Phase 32 makes memory and knowledge durable, provenance-aware, scoped, auditable, and fail-closed at promotion boundaries.

The scope model is:

```text
Task → Project → Team → Agent → Division → Organization → Global
```

This is the **promotion order** from narrow execution context toward reusable context. A memory can move only one scope at a time and only after the promotion evidence gate passes.

## Memory contract

`core/memory/models.py` defines immutable `MemoryEntry` and `MemoryEvidence` records.

Every memory records:

- content and typed memory kind;
- explicit scope;
- scope identity (`task_id`, `project_id`, `team_id`, `agent_id`, `division_id`, or `organization_id` as appropriate);
- provenance references;
- evidence references and verification state;
- confidence;
- lifecycle status;
- supersession and contradiction references;
- creation/expiration timestamps;
- stable identity and version.

Invalid scope/context combinations are rejected. Timestamps must be timezone-aware. Confidence is bounded to `[0, 1]`.

## Evidence and promotion

`MemoryPromoter` is fail-closed.

Default promotion requirements:

- confidence >= `0.80`;
- at least two verified evidence items;
- eligible lifecycle state;
- exact next scope only;
- required scope identity/provenance anchor.

Promotion creates an immutable replacement with an incremented version and `promoted` status. A memory cannot jump directly from task scope to global scope.

Global promotion requires an organization provenance anchor so global context cannot be produced from an untraceable local observation.

## Knowledge contract

`KnowledgeEntry` represents source-backed knowledge rather than unreviewed memory.

Knowledge requires:

- subject;
- claim;
- source;
- at least one verified evidence record;
- bounded confidence;
- tags;
- version and identity;
- explicit supersession when a later knowledge record replaces an earlier one.

This deliberately keeps **memory** and **knowledge** distinct: memory may begin as a candidate observation; knowledge cannot be persisted as authoritative knowledge without verified evidence.

## Registry and lifecycle

`MemoryRegistry` provides explicit add/get/list operations plus:

- expiration;
- rejection;
- explicit supersession with version checks;
- separate knowledge registration and supersession;
- deterministic newest-first listing.

Contradictions are represented as explicit IDs instead of silently resolving conflicting claims.

`MemoryService` coordinates recording, promotion, knowledge registration, expiry/rejection, persistence, and lifecycle EventBus signals without becoming a permission authority.

## Retrieval

`MemoryRetriever` provides deterministic lexical retrieval with scope/context filters and bounded result counts.

Retrieval supports task, project, team, agent, division, and organization context filters and can query validated knowledge separately.

Ranking is deterministic by match score, confidence, timestamp, and stable ID. Retrieval does **not** upgrade confidence, validate evidence, authorize actions, or imply truth.

## Persistence

`MemoryStore` provides dependency-free JSON persistence with:

- schema version `2`;
- backward loading of the previous list-based memory format;
- memory + knowledge persistence;
- complete evidence timestamps;
- deterministic JSON key ordering;
- atomic temporary-file + `fsync` + `os.replace` writes;
- temporary-file cleanup;
- validation on load.

A corrupt/unknown schema is rejected rather than silently reset.

## Security boundaries

Memory and knowledge are data, never executable policy.

They cannot:

- grant permissions;
- grant capabilities;
- select tools;
- authorize credentials/network access;
- execute commands;
- bypass Rules, Hooks, PermissionEngine, or GovernanceEngine;
- turn retrieval into approval.

Unverified memory remains unverified context. Promotion and knowledge creation are evidence-gated.

## External pattern review

Current external engineering references were reviewed for scoped local memory, explicit provenance, state stores, bounded retrieval, verification-before-promotion, and keeping memory separate from executable policy. These references informed general engineering patterns only.

A separate knowledge-oriented reference was reviewed for explicit entities, relationships, confidence, unresolved contradictions, and source traceability. SI-Agents intentionally implements a dependency-free structured model first rather than introducing a graph database prematurely.

No external code, prompts, branding, or architecture was copied.

## Final verification

Mainline CI run **#769** completed successfully on the exact merge commit:

- distribution build: passed;
- wheel installation verification: passed;
- SI repository audit: passed;
- Ruff: passed;
- complete pytest suite: **392 passed in 5.47s**;
- diagnostic artifact generation: passed.

The final verification was performed after Phase 32 was merged into `main`, so the closure record and implementation are now synchronized.

## Exit gate

Phase 32 is closed. **Phase 33 — Security & Governance Center** is next.

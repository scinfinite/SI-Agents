# Phase 52 — Context / Memory Economics

## Status

Implemented on the Phase 52 branch; mainline closure is gated by the final exact-tree CI.

## Architecture

Phase 52 adds a deterministic context-economics layer under `core/context_economics/`.
It is deliberately below SI Core orchestration and above model invocation: it decides what
already-authorized context is worth carrying into a request, but it does not grant
permissions, select providers, or become the execution authority.

### Contracts

- `ContextItem` carries bounded content metadata, scope, importance, relevance, provenance,
  lineage, sensitivity, and an optional cost/token estimate.
- `ContextBudget` expresses token and optional cost limits at user/project/session/workflow/
  team/task/agent scopes.
- `ModelContextProfile` describes the target context window and reserved output capacity.
- `ContextSelection` is an auditable immutable decision containing selected/dropped context,
  accounting, deterministic decision identity, and evidence.
- `ContextSnapshotStore` persists an atomic JSON snapshot for recovery and provenance.

### Selection policy

1. Deduplicate normalized content by SHA-256 fingerprint.
2. Exclude sensitive context unless explicitly allowed by the caller's already-authorized
   policy boundary.
3. Redact secret-like context by default; callers may instead fail closed by dropping it.
4. Rank by deterministic importance/relevance score with ID tie-breaking.
5. Enforce the smallest active scope budget and model input capacity.
6. Compact oversized items deterministically, or use an explicitly supplied summarizer.
7. Enforce token and cost limits before inclusion.
8. Emit a stable decision ID and accounting evidence.

This layer is intentionally deterministic so decisions can be tested, replayed, audited,
and compared without requiring an LLM to decide whether its own context fits.

## Memory relationship

The existing `core/memory` subsystem remains the durable memory authority. Phase 52 treats
memory, execution state, artifacts, evidence, and handoff material as context candidates;
retrieval remains scope-aware and provenance-bearing. Context economics controls injection
into a model request rather than silently promoting or mutating durable memory.

## External reference synthesis

Current external engineering references consistently emphasize bounded context windows,
inspectable memory, scoped recall, explicit handoffs, shared state, durable summaries,
separation of recent and persistent memory, and token/cost-aware context injection.
SI-Agents generalizes these patterns while keeping SI Core authority, capability
authorization, and provenance boundaries intact; external systems are references only and
are not runtime dependencies or governance authorities.

## Security and adversarial coverage

Tests cover invalid budgets, deterministic ordering, duplicate-context amplification,
sensitive-context isolation, secret redaction/fail-closed handling, oversized-context
compaction, cost ceilings, custom summarizer behavior, and snapshot schema rejection.

## Closure evidence

Final completion requires repository audit, distribution/wheel verification, integration
verification, Ruff, compileall, full pytest, documentation synchronization, and a green
mainline exact-tree CI run.

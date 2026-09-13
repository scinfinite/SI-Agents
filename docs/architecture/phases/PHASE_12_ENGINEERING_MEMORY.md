# Phase 12 — Engineering Memory

## Purpose

Engineering Memory preserves useful, auditable experience without turning every observation into permanent system knowledge. Memory is explicitly scoped to a task, project, or global system context.

## Model

A memory entry contains content, type, scope, provenance, evidence, confidence, lifecycle status, tags, timestamps, and optional supersession metadata. Task and project scopes require their corresponding anchors. Expiry is first-class so temporary operational facts do not silently become permanent knowledge.

## Promotion policy

Promotion is fail-closed and moves exactly one scope at a time: task → project → global. Promotion requires at least 0.80 confidence and two verified evidence records by default. A global promotion also requires a project provenance anchor. Rejected, expired, or already-promoted entries cannot be promoted. Promotion increments the memory version.

The memory layer does not automatically infer truth from repetition. Evidence remains attributable to its source, and callers remain responsible for producing valid verification evidence.

## Retrieval

Retrieval is deterministic and scope-aware. It filters by task/project/scope/tags and ranks matching terms with confidence and recency as tie-breakers. A retrieval result is a memory candidate, not proof that its contents are correct.

## Persistence

The dependency-free JSON store preserves the complete entry shape, including evidence and lifecycle metadata. Persistence is deliberately simple and auditable; it is not a concurrency-safe distributed database.

## Safety boundaries

- No automatic global promotion.
- No uncontrolled self-modification.
- No secrets should be stored as ordinary memory content.
- Expired memories are excluded from normal retrieval.
- Supersession is explicit and versioned.
- Memory does not override security, legal, cost, permission, or verification policies.

## Acceptance criteria

1. Task/project/global scopes are represented and validated.
2. Provenance and evidence are mandatory.
3. Promotion is evidence- and confidence-gated and fail-closed.
4. Promotion advances only one scope at a time.
5. Retrieval is deterministic and scope-aware.
6. Expiration and supersession are supported.
7. Memory survives a JSON persistence round trip.
8. Unit tests cover adversarial promotion and lifecycle behavior.
9. CI builds, lints, and tests the complete repository.

## Limitations

This phase provides the memory domain and a local persistence implementation. Distributed locking, encrypted-at-rest storage, vector/semantic retrieval, retention automation, and cross-process event sourcing are intentionally deferred to later hardening work.

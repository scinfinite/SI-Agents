# Context and Memory Architecture

SI-Agents separates **durable memory** from **request context economics**.

- `core/memory` owns memory entries, knowledge, evidence, lifecycle, retrieval, and durable JSON persistence.
- `core/context_economics` owns deterministic context selection, budgets, token/cost accounting, compaction, deduplication, sensitivity handling, and decision evidence.
- Capability authorization remains the authority for whether a source may be accessed.
- SI Core remains authoritative for execution lifecycle and governance.
- Model/provider selection remains outside this layer and is owned by the routing boundary.

Context is never permission by implication. Retrieved memory is untrusted informational input;
important claims require provenance/evidence and policy checks before consequential use.

## Budget hierarchy

A request may carry budgets for user, project, session, workflow, team, task, and agent scopes.
The effective limit is the minimum applicable scope limit and the target model's available input
capacity after reserving output tokens.

## Selection invariants

- Duplicate content is counted once.
- Sensitive content is excluded unless an already-authorized caller explicitly permits it.
- Secret-like values are redacted by default; callers may choose fail-closed dropping.
- Selection is deterministic and stable for the same inputs.
- Token and cost ceilings are enforced before inclusion.
- Oversized context is compacted or explicitly summarized before it is admitted.
- Every selection has a stable decision ID and accounting evidence.
- Snapshots are written atomically for recovery/audit.

## Phase 52 evidence

Phase 52 is complete on main. Mainline CI #1015 (`34673115687`) passed distribution build,
wheel verification, repository audit, integration verification, Ruff, and the full test suite.
The implementation is covered by deterministic/adversarial tests for budget validation,
deduplication, sensitivity, secret handling, compaction/summarization, cost ceilings,
and snapshot serialization/schema handling.

## Memory quality

Future phases can add richer retrieval, utilization metrics, persistent sessions, and model-aware
routing without changing the authority boundary established here.

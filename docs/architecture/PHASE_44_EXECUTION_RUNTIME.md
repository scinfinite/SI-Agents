# Phase 44 — Execution Runtime Foundation

**Status:** Complete and CI-verified
**Roadmap:** V4 Phase 44
**Authority:** `docs/architecture/PHASES.md` and `docs/architecture/SI_AGENTS_V4_PLAN.md`

## Objective

Establish a durable execution foundation underneath the existing SI governance and Control API contracts. Phase 44 owns execution mechanics; it does not grant authority, bypass governance, change provenance, or become a provider/model policy layer.

## Implemented foundation

- Canonical execution lifecycle: `accepted → queued → running → terminal`.
- Terminal outcomes: `succeeded`, `failed`, `cancelled`, `expired`.
- Stable `task_id`, `execution_id`, and `attempt_id` identity.
- SQLite durable execution and attempt persistence.
- Atomic lifecycle transitions and terminal idempotence.
- Idempotency-key reuse with conflict detection.
- Explicit retry attempts under the same execution.
- Runtime cancellation signal plus adapter cancellation callback.
- Runtime deadline checks and normalized expiry outcome.
- Adapter failure normalization without leaking exception payloads.
- Adapter pause/resume capability boundary.
- Restart recovery of interrupted `running` work back to `queued` while preserving attempt identity.
- Re-openable persistence across process/store instances.
- Inline secret-like payload rejection so raw credentials are not persisted in runtime state.
- Terminal-state immutability under cancellation/pause requests.
- Concurrency coverage for competing terminal writers.
- Exported runtime contracts from `core.runtime`.

## Authority boundary

The runtime receives an already-authorized task. The runtime does not decide caller identity, permissions, governance, approvals, provenance, model policy, or provider selection. Harness/provider adapters are downstream mechanics and cannot grant authority.

The existing `RuntimeEngine` remains the cross-harness governance coordinator. `ExecutionRuntime` is the durable execution primitive and is intentionally separate from provider/harness policy.

## Verification evidence

The final mainline CI run was **#916 (`34609972530`)**, on commit `e48fd1d0722c4aa7b70879961294f296e5aff662`.

All CI gates passed:

- distribution build;
- wheel installation/import smoke tests;
- repository audit;
- integration verification;
- Ruff;
- Python compileall;
- complete pytest suite.

The final suite included **484 passing tests** after a CI-discovered hygiene regression was corrected. The regression was caused by V4 planning documentation explicitly naming external engineering references; both the repository audit and hygiene test were aligned so reference-only documentation is permitted while executable/package surfaces remain protected.

## Phase 44 gate result

Phase 44 is closed. The runtime foundation is implemented on `main`, tested, documented, security/adversarial checked, packaging-verified, and final-CI verified. Phase 45 is the next implementation phase.

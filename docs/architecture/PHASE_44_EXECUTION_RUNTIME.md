# Phase 44 — Execution Runtime Foundation

**Status:** Implementation in progress
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
- Exported runtime contracts from `core.runtime`.

## Authority boundary

The runtime receives an already-authorized task. The runtime does not decide caller identity, permissions, governance, approvals, provenance, model policy, or provider selection. Harness/provider adapters are downstream mechanics and cannot grant authority.

The existing `RuntimeEngine` remains the cross-harness governance coordinator. `ExecutionRuntime` is the new durable execution primitive and is intentionally separate from provider/harness policy.

## Verification requirements

Phase 44 cannot close until all of the following are green:

1. Runtime lifecycle tests.
2. Idempotency and retry tests.
3. Cancellation/deadline tests.
4. Restart/persistence recovery tests.
5. Pause/resume capability-boundary tests.
6. Secret-isolation/adversarial tests.
7. Existing V3 test suite.
8. Repository audit and static checks.
9. Packaging/distribution checks.
10. Final GitHub Actions CI run on `main`.

## Remaining gate

This document deliberately remains **Implementation in progress** until final CI provides evidence for the complete Phase 44 contract. No downstream Phase 45 implementation should be treated as started merely because this runtime exists.

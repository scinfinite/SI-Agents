# Phase 46 — Parallel Scheduler + Executor

**Status:** Advanced-hardening complete; final verification pending documentation-tree CI
**Roadmap:** V4 Phase 46

## Advanced-level audit result

The original Phase 46 implementation was functional and CI-verified, but the audit found two production-hardening gaps: explicit execution identities could surface as raw runtime uniqueness failures, and scheduler idempotency needed to be authoritative at the orchestration boundary. These are now fixed. The dependency graph is also defensively checked for cycles and existing schedules are never mutated by a conflicting resubmission.

## Implemented

- Durable SQLite schedule records and dependency edges.
- Priority scheduling with bounded aging to reduce starvation.
- Dependency-aware dispatch: successors wait for successful predecessors.
- Failure/cancellation propagation to blocked descendants.
- Bounded parallel execution using a thread pool.
- Durable waiting/running/terminal schedule state.
- Restart recovery of scheduler-owned running records back to waiting, with runtime recovery.
- Explicit cancellation of queued/running work through the Phase 44 runtime.
- Scheduler lifecycle events emitted through the Phase 45 event bus.
- Deterministic synchronous `drain()` plus background `start()`/`stop()` operation.
- Fail-closed validation for worker count, timing configuration, duplicate/unknown dependencies, and invalid priorities.
- Queued cancellation and dependency blocking finalize the corresponding authoritative runtime execution as cancelled.
- **Idempotent schedule submission:** runtime idempotency and explicit `execution_id` reuse return the existing schedule only when task/dependency/priority metadata is identical.
- **Conflict protection:** a conflicting reuse is rejected before runtime insertion and cannot mutate the existing schedule.
- **DAG defense:** dependency insertion performs a graph reachability cycle check in addition to immutable dependency creation semantics.
- **Deterministic dependency ordering:** persisted dependency edges are returned in stable order.

## Authority and safety invariants

1. The Control API remains the authority for caller identity, admission, policy, capability, approvals, and provenance.
2. The scheduler only schedules executions already accepted by `ExecutionRuntime`.
3. Adapter invocation remains exclusively inside the execution runtime; scheduler code cannot grant adapter authority.
4. Runtime lifecycle state remains authoritative; scheduler state is orchestration metadata.
5. A dependency must be known before it can gate another execution.
6. A failed/cancelled/blocked dependency prevents its descendants from executing.
7. Worker concurrency is bounded by the configured `max_workers`.
8. Restart never silently treats an interrupted running schedule as successfully completed.
9. Scheduler events are facts and cannot be used as authorization signals.
10. Scheduler cancellation uses the runtime cancellation boundary; it does not directly mutate runtime lifecycle state.
11. A duplicate execution identity cannot create a second schedule or overwrite dependency metadata.
12. A scheduler graph cannot introduce a dependency cycle through resubmission.

## Verification coverage

`tests/test_phase46_scheduler.py` covers bounded parallelism, dependency ordering, failure propagation, priority ordering, queued cancellation, persistence/reopen, durable scheduler events, invalid configuration/dependency handling, terminal runtime state for blocked/cancelled executions, explicit identity conflict safety, and runtime-idempotent resubmission.

## Baseline evidence

Original final Phase 46 implementation commit: `772716428868a7597540a0bea72f715dfd46a224`. Original final CI: **#938 (`34615157829`)**.

## Advanced-hardening evidence

Advanced hardening is being verified as part of the combined Phase 46/47/49/50 audit branch. CI **#984 (`34671292491`)** passed distribution, wheel verification, repository audit, integration verification, Ruff, and the complete pytest suite after the scheduler fixes.

## Gate result

The Phase 46 implementation is now advanced-hardened. Final status becomes immutable on `main` only after the documentation synchronization commit also passes exact-tree CI.

Phase 47 — OpenCode Bridge remains part of this combined advanced audit.

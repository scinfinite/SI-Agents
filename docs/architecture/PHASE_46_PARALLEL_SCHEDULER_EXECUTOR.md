# Phase 46 — Parallel Scheduler + Executor

**Status:** Implementation complete; final CI gate required before closure.
**Roadmap:** V4 Phase 46

## Objective

Add a durable, dependency-aware parallel scheduler above the Phase 44 execution runtime and Phase 45 event/state layer. The scheduler decides **when** already-authorized executions run. It does not authorize work, change provenance, or become a second control plane.

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
- Deterministic synchronous `drain()` for tests/operators plus background `start()`/`stop()` operation.
- Fail-closed validation for worker count, timing configuration, duplicate/unknown dependencies, and invalid priorities.

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

## Verification coverage

`tests/test_phase46_scheduler.py` covers bounded parallelism, dependency ordering, failure propagation, priority ordering, queued cancellation, persistence/reopen, durable scheduler events, and invalid configuration/dependency handling.

## CI gate

Closure requires a green final CI run on the exact `main` tree containing this implementation, tests, documentation, and status update. The phase must not be treated as complete until distribution, installation/import smoke tests, repository audit/integration verification, Ruff, compileall, and the full pytest suite pass.

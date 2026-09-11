# Phase 45 — Event Bus + State Architecture

**Status:** Complete and CI-verified
**Roadmap:** V4 Phase 45

## Objective

Establish the durable event/state layer beneath the Phase 44 execution runtime. Phase 45 owns append-only runtime events, correlation/causation metadata, per-aggregate ordering, replay, live in-process subscriptions, projections, and durable projection checkpoints.

It does **not** become an authorization or governance plane. Control API authorization remains authoritative; events record execution facts and projections materialize queryable state.

## Implemented

- SQLite-backed append-only runtime event log.
- Stable event IDs with idempotent re-publication and conflict detection.
- Per-aggregate monotonic sequence numbers.
- Correlation and causation identifiers.
- Durable event timestamps and stable event metadata.
- Aggregate stream reads and correlation queries.
- Deterministic durable-log replay.
- Live in-process subscriptions after successful event commit.
- Explicit unsubscribe lifecycle for subscriptions.
- Projection reducers with durable checkpoints.
- Projection state persisted independently from the source event log.
- Re-openable persistence across process/store instances.
- Concurrent append coverage proving unique ordered sequences.
- Invalid-input and event-ID conflict fail-closed tests.
- Canonical Phase 44 execution lifecycle events emitted into the Phase 45 bus.

## Design invariants

1. Source events are append-only; projections are disposable materialized state.
2. An event ID may be retried idempotently only with the same event identity/content.
3. Sequence numbers are unique and monotonic within an aggregate stream.
4. Every event carries correlation identity; causation is optional for root events.
5. Consumers must tolerate replay and never infer authority from event payloads.
6. Projection checkpoints advance only after the reducer and projection write succeed.
7. Runtime lifecycle events preserve the execution authority boundary and never grant permissions.
8. Subscriber failures cannot roll back an already committed durable event.

## Final verification evidence

The exact final `main` tree is commit **`ccc115b2448a40c1a815216ed692c24d5be8dd9a`**. Final CI run **#932 (`34612277732`)** completed successfully.

All CI gates passed:

- distribution build;
- wheel installation/import smoke tests;
- repository audit;
- integration verification;
- Ruff;
- complete pytest suite;
- diagnostics and post-job steps.

The immediately preceding implementation CI #930 (`34612083838`) was also green for the runtime/event implementation. The final #932 run verifies the exact documented closing tree.

## Phase 45 gate result

Phase 45 is closed. The event bus/state architecture is implemented on `main`, integrated with the Phase 44 runtime, tested for durability/order/replay/projection/concurrency/security-boundary behavior, documented, packaging-verified, and final-CI verified.

Phase 46 — Parallel Scheduler + Executor is the next implementation phase.

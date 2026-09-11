# Phase 45 — Event Bus + State Architecture

**Status:** Implementation in progress
**Roadmap:** V4 Phase 45

## Scope

Phase 45 establishes the durable event/state layer beneath the Phase 44 execution runtime. It owns append-only runtime events, correlation/causation metadata, per-aggregate ordering, replay, projections, and durable projection checkpoints.

It does **not** become an authorization or governance plane. Control API authorization remains authoritative; events record execution facts and projections materialize queryable state.

## Implemented

- SQLite-backed append-only runtime event log.
- Stable event IDs with idempotent re-publication.
- Per-aggregate monotonic sequence numbers.
- Correlation and causation identifiers.
- Durable event timestamps and typed event metadata.
- Aggregate stream reads and correlation queries.
- Deterministic replay from the durable log.
- Projection reducers with durable checkpoints.
- Projection state persisted independently from the source event log.
- Re-openable persistence across process/store instances.
- Concurrent append coverage proving unique ordered sequences.
- Invalid-input and event-ID conflict fail-closed tests.

## Design invariants

1. Source events are append-only; projections are disposable materialized state.
2. An event ID may be retried idempotently only with the same event identity/content.
3. Sequence numbers are unique and monotonic within an aggregate stream.
4. Every event carries correlation identity; causation is optional for root events.
5. Consumers must tolerate replay and never infer authority from event payloads.
6. Projection checkpoints make repeated projection runs no-ops after successful processing.
7. Runtime state and event state remain durable across process restarts.

## Remaining Phase 45 gate

Before closure, integration with the execution runtime must emit canonical lifecycle events, state projection behavior must be verified against runtime transitions, event ordering/terminality must be tested end-to-end, and the complete repository CI/security/package gates must be green.

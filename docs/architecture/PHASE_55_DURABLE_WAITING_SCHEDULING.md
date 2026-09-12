# Phase 55 — Durable Waiting + Scheduling

## Status

**Implementation complete; final synchronized-tree CI pending.**

## Scope delivered

- durable WAIT records backed by SQLite;
- timer and delayed waits that do not occupy execution workers;
- recurring interval schedules with bounded occurrence counts;
- five-field UTC cron schedules with validation and next-occurrence calculation;
- event/resource/human/external wake-up triggers;
- approval-compatible wait kind for durable governance pauses;
- deadlines and deterministic fail-closed expiry;
- restart-safe recovery through durable state and ordered wait events;
- priority plus bounded age-based fairness to reduce starvation;
- bounded queue and payload sizes;
- optimistic revision protection for completion/rescheduling;
- idempotent wake/cancel behavior;
- Control API routes for create/list/get/events/wake/claim/complete/cancel;
- subject/project isolation on every wait operation;
- secret-like field rejection and JSON-safe payload enforcement.

## Authority boundaries

SI Core owns wait state, schedule calculation, lifecycle, fairness, expiry, and recovery.
The Control API is a transport/control surface only. A ready or claimed wait does not grant
capabilities, credentials, provider authorization, or execution authority. Downstream execution
must independently authorize the work before running it.

## State contract

`waiting` is durable and consumes no worker. `ready` means the wake condition is satisfied and
is claimable. `completed` records a claimed occurrence; recurring schedules atomically return the
record to `waiting` for the next occurrence. `cancelled` and `expired` are terminal. Deadlines
always fail closed. Wake-up of an already-terminal record is idempotent and cannot resurrect it.

## Scheduling contract

One-shot timers use an absolute UTC wake time. Recurring schedules use bounded positive intervals.
Cron schedules use standard five-field UTC expressions. Queue ordering combines explicit priority
with bounded age credit, preventing a permanently high-priority stream from starving older waits.
The implementation is intentionally a durable ledger rather than a background worker pool: restart
requires only the SQLite state and a subsequent promotion/claim call.

## API surface

- `GET /api/v1/waits` — identity-bound wait queue;
- `GET /api/v1/waits/{wait_id}` — inspect a wait;
- `GET /api/v1/waits/{wait_id}/events` — inspect lifecycle events;
- `POST /api/v1/waits` — create a timer/schedule/event wait;
- `POST /api/v1/waits/{wait_id}/wake` — record an external wake trigger;
- `POST /api/v1/waits/{wait_id}/claim` — claim ready work;
- `POST /api/v1/waits/{wait_id}/complete` — finish/reschedule an occurrence;
- `POST /api/v1/waits/{wait_id}/cancel` — cancel a pending/ready wait.

All routes require `X-SI-Subject` and `X-SI-Project`. The wait layer never becomes a second
business authority for execution or authorization.

## Safety invariants

1. Missing or mismatched identity fails closed.
2. Cross-project reads and mutations fail closed.
3. Waiting records never occupy execution workers.
4. Deadlines cannot be bypassed by late wake-up.
5. Terminal waits cannot be resurrected.
6. Stale revisions cannot overwrite concurrent changes.
7. Queue and payload limits are enforced before persistence.
8. Secret-like payload fields are rejected before persistence.
9. Recurrence is bounded by explicit occurrence limits and the one-year interval limit.
10. Cron calculation is bounded to one year when searching for the next occurrence.
11. Restart preserves state and event history.
12. A wait transition never grants execution capability.

## Testing

Adversarial tests cover restart recovery, deadline expiry, event wake-up, recurring rescheduling,
cron validation, fairness/starvation resistance, cross-project isolation, stale revisions, secret
rejection, oversized payloads, idempotent cancellation, and JSON-safe persistence. CI must also
cover distribution installation, repository audit, integration verification, Ruff, and full pytest.

## Engineering-reference synthesis

Generalized scheduling patterns used here are durable state machines, worker-free waiting, explicit
wake conditions, bounded retries/schedules, fairness/aging, restart recovery, and separation of
control-plane scheduling from execution authority. No external runtime is treated as SI Core
authority.

## Closure evidence

- Phase 54 was verified complete on `main` before Phase 55 implementation.
- Phase 54 final synchronized-tree CI #1051 (`34676632475`) passed all required gates.
- Phase 55 implementation commits add `core/waiting`, adversarial tests, and Control API routes.
- Final completion requires synchronized documentation and an exact-tree mainline CI success.

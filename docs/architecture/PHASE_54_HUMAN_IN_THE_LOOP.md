# Phase 54 — Human-in-the-Loop

## Status

**Complete on main.**

## Scope delivered

- durable approval, human-input, and review requests;
- explicit gate classification for risk, cost, egress, destructive, security, and deployment decisions;
- subject/project identity binding and fail-closed missing/mismatched identity;
- pause-at-gate semantics represented by pending approval state;
- human outcomes: approve, reject, modify, retry, reassign, and authorized alternative;
- bounded decision metadata and secret-like field rejection;
- expiry with deterministic fail-closed transition;
- optimistic revision protection against stale decisions;
- immutable terminal decisions and ordered audit events;
- SHA-256 evidence digests linking request and decision history;
- durable SQLite persistence and restart-safe recovery;
- bounded outstanding approval queues;
- Control API queue/get/decide/audit-event controls for Web/TUI/CLI clients;
- notification intent recorded as an auditable queue fact without creating a second authority.

## Authority boundaries

SI Core owns approval state, lifecycle, identity/project isolation, audit history, and evidence.
The Control API is a transport/control surface. A human decision is governance evidence, not a
credential, capability grant, provider authorization, or execution instruction. Downstream runtime
execution must re-authorize the intended action after an approval and must independently enforce
capability, identity, egress, cost, and risk policy.

## State contract

`pending` is the only actionable gate state. A request may transition exactly once to one of the
terminal outcomes `approved`, `rejected`, `modified`, `retry`, `reassigned`, `alternative`,
`expired`, or `cancelled`. Expiry is automatic when a pending request is observed after its deadline.
Terminal requests cannot be decided again. Revision checks reject stale concurrent mutations.

`modified`, `retry`, `reassigned`, and `alternative` carry bounded structured decision payloads so
the downstream orchestrator can interpret the human instruction under its own authorization rules.
The HITL layer never executes the requested change itself.

## Safety invariants

1. Missing or mismatched subject/project identity fails closed.
2. Requesters cannot create a gate for a different subject through the public service.
3. Cross-project access and decisions fail closed.
4. Pending requests alone never authorize execution.
5. Expired requests cannot be approved after expiry.
6. Terminal requests cannot be replay-decided.
7. Stale revisions cannot overwrite a concurrent decision.
8. Secret-like fields are rejected rather than persisted.
9. Metadata and queue sizes are bounded.
10. Audit event order is monotonic per approval.
11. Evidence digests are deterministic from the prior evidence and recorded decision.
12. Restart preserves approval state and terminal decisions.
13. Notification facts do not create an independent delivery or execution authority.

## API surface

- `GET /api/v1/approvals` — identity-bound outstanding queue;
- `POST /api/v1/approvals` — create approval/input/review gate;
- `GET /api/v1/approvals/{approval_id}` — inspect a gate;
- `GET /api/v1/approvals/{approval_id}/events` — inspect audit history;
- `POST /api/v1/approvals/{approval_id}/decide` — record a human decision.

The control surface supplies `X-SI-Subject` and `X-SI-Project` for protected queue/read operations.
Decision payloads repeat identity fields so a replayed or cross-project request cannot silently bind
to another subject. The API remains localhost-first under the existing Control API transport.

## Testing

Adversarial coverage verifies lifecycle decisions, identity/project isolation, stale revisions,
secret rejection, oversized metadata, expiry and restart persistence, and HTTP queue/decision/event
controls. Final mainline CI #1050 (`34676573634`) passed distribution build, wheel verification,
repository audit, integration verification, Ruff, and the full pytest suite.

## Engineering-reference synthesis

Generalized patterns used here include explicit human gates, resumable operator decisions, durable
audit history, bounded context, and separation between a user-facing harness/control surface and
the authoritative execution/governance layer. No external system is treated as SI Core authority.

## Closure evidence

- Phase 53 final exact-tree mainline CI #1041 (`34675322458`) was verified before Phase 54 work.
- Phase 54 implementation was merged to `main` and then hardened through repository CI.
- Mainline CI #1050 (`34676573634`) passed all required gates on commit `a28b86e4bc461530cb863369c4c18da220eb4d34`.
- The synchronized documentation closure is committed on `main`; its final exact-tree CI is required before this documentation commit is itself considered the closure point.

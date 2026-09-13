# Phase 53 — Persistent Sessions

## Status

**Complete on main.** Phase 53 implementation, adversarial coverage, documentation synchronization, merge, and final mainline verification are complete.

## Scope delivered

- durable session IDs and lifecycle states: active, paused, archived, expired, closed;
- ownership and project/workspace isolation;
- harness binding for OpenCode and other clients;
- optimistic revision checks for concurrent updates;
- durable session state/context and token/cost history;
- ordered immutable event history and replay;
- session artifacts with SHA-256 evidence digests;
- expiry and archival;
- export/import with schema and ownership validation;
- cloning/branch lineage;
- bounded session search/filtering;
- restart/recovery through durable storage;
- `PersistentSessionAdapter` for runtime/harness continuity.

## Authority boundaries

SI Core owns session lifecycle, persistence, ownership checks, history, artifacts, and recovery.
The session store never restores or grants credentials, capability grants, provider authorization,
or identity. Every operation re-checks subject/project ownership; the runtime adapter additionally
checks harness binding. Authorization remains outside the persistence layer.

## Safety invariants

1. Cross-subject/project access fails closed.
2. Revision conflicts prevent lost concurrent updates.
3. Archived sessions cannot be reopened through ordinary lifecycle mutation.
4. Secret-like fields are rejected rather than persisted.
5. JSON/event/artifact/search inputs are bounded.
6. Event sequence is monotonic per session.
7. Export/import requires a supported schema and matching owner.
8. Clones receive a new session identity and explicit parent lineage.
9. Replay is read-only and cannot grant authority.
10. Expiry is deterministic and restart-safe.
11. Artifact export retains evidence metadata/digest but never invents or restores file content.

## Testing

Adversarial tests cover isolation, stale revision updates, secret leakage, malformed schemas,
export ownership, expiry, archive immutability, artifact size bounds, deterministic event replay,
search bounds, JSON safety, clone lineage, restart persistence, and OpenCode/harness mismatch.

## Engineering-reference synthesis

External systems were reviewed for general patterns around durable sessions, bounded context,
shared execution state, resumable history, and runtime/harness separation. SI-Agents generalizes
those patterns into its own contracts and tests without making an external runtime the authority
for session state or governance.

## Closure evidence

- Phase 52 final exact-tree mainline CI #1020 (`34673411916`) was verified before Phase 53 started.
- Phase 53 implementation was merged into `main` as commit `671458a47dc6a3ce6ff79dfdc5acb4ffdb32fc09`.
- Mainline Phase 53 verification CI: **#1021 / `34674234547`**.
- Final documentation-synchronized mainline CI: **#1037 / `34675239106`** — passed distribution, wheel verification, repository audit, integration verification, Ruff, and full pytest.
- The final hardening also corrected the recurring Web oversized-request client race by boundedly draining rejected bodies and handling disconnects safely while retaining the 1 MiB request limit.

Phase 53 is closed. The phase is not reopened by subsequent roadmap work; **Phase 54 — Human-in-the-Loop** is the next phase.
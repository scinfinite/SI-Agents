# Phase 53 — Persistent Sessions

## Status

**Implementation complete; final closure is gated on green CI and merge to `main`.**

## Scope

Phase 53 makes sessions durable SI Core state rather than process-local harness state.
The implementation provides:

- durable session IDs and lifecycle states: active, paused, archived, expired, closed;
- ownership and project/workspace isolation;
- harness binding for OpenCode and other clients;
- optimistic revision checks for concurrent updates;
- durable session state and token/cost history;
- ordered immutable event history and replay;
- session artifacts with SHA-256 evidence digests;
- expiry and archival;
- export/import with schema and ownership validation;
- cloning/branch lineage;
- bounded session search/filtering;
- restart/recovery through the durable store;
- `PersistentSessionAdapter` for runtime/harness continuity.

## Authority boundaries

SI Core owns session lifecycle, persistence, ownership checks, history, artifacts, and recovery.
The session store never restores credentials, capability grants, provider authorization, or identity.
Every operation re-checks the caller's subject/project boundary; the runtime adapter additionally
checks the harness binding. Authorization remains outside the persistence layer.

## Safety invariants

1. Cross-subject/project access fails closed.
2. Revision conflicts prevent lost concurrent updates.
3. Archived sessions cannot be reopened through ordinary lifecycle mutation.
4. Secret-like fields are rejected rather than persisted.
5. JSON/event/artifact/session search inputs are bounded.
6. Event sequence is monotonic per session.
7. Export/import requires a supported schema and matching owner.
8. Clones receive a new session identity and explicit parent lineage.
9. Replay is read-only and cannot grant authority.
10. Expiry is deterministic and restart-safe.
11. Artifact exports retain evidence metadata/digest but never invent or restore file content.

## Testing

Adversarial tests cover isolation, stale revision updates, secret leakage, malformed schemas,
export ownership, expiry, archive immutability, artifact size bounds, deterministic event replay,
search bounds, JSON safety, clone lineage, restart persistence, and OpenCode/harness mismatch.

## External-reference synthesis

Current ECC and Agency Agents patterns reinforce explicit context/memory boundaries and reusable
agent/session state; OpenCode emphasizes durable user-facing session continuity; n8n demonstrates
persistent execution records and resumable history; OmniRoute's role remains model/provider routing.
SI-Agents generalizes these patterns without making any external runtime the authority for session
state or governance.

## Closure evidence

Final evidence will be recorded here after the exact synchronized `main` tree passes the final
mainline CI gate. Phase 52 remains historically closed and is not renumbered or reopened.

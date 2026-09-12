# Architecture

SI-Agents V4 uses a single authoritative SI Core. Web, TUI, CLI, OpenCode, runtime adapters, schedulers, agents, teams, workflows, and integrations are clients/adapters of that authority rather than independent state owners.

## V4 target architecture

```text
OpenCode → SI OpenCode Bridge → SI Core / Control API
        → Scheduler / Orchestrator → Tasks / Agents / Teams / Workflows
        → Authorization → OmniRoute → Models / Providers / APIs
        → Results / Artifacts / Evidence → SI Core
        → OpenCode / Web / TUI / CLI
```

OmniRoute owns model/provider/API routing. SI Core owns execution, orchestration, governance, evidence, lifecycle, persistence, and recovery.

## Verified V4 phases

| Phase | Capability | Status | Evidence |
|---:|---|---|---|
| 44 | Execution Runtime Foundation | Complete | CI #919 / `34610448789` |
| 45 | Event Bus + State Architecture | Complete | CI #935 / `34612616978` |
| 46 | Parallel Scheduler + Executor | **Advanced hardened** | Hardening CI #984 / `34671292491` |
| 47 | OpenCode Bridge | **Advanced hardened** | Hardening CI #984 / `34671292491` |
| 48 | OmniRoute Integration | Complete | CI #949 / `34623762921` |
| 49 | Agent + Team Builder | **Advanced hardened** | Hardening CI #984 / `34671292491` |
| 50 | Capability Authorization | **Advanced hardened** | Hardening CI #984 / `34671292491` |
| 51 | Checkpoints + Resume | Complete | CI #977 / `34627956634` |
| 52 | Context / Memory Economics | **Complete** | Final exact-tree CI #1020 / `34673411916` |
| 53 | Persistent Sessions | **Complete** | Final synchronized-tree mainline CI #1041 / `34675322458` |
| 54 | Human-in-the-Loop | **Complete** | Final synchronized-tree mainline CI pending |

## Phase 53 persistent sessions

`core/sessions` is the durable session authority. `SessionStore` persists session identity, ownership, lifecycle, state/context, token/cost history, ordered events, artifacts, expiry, archival, and lineage. `PersistentSessionAdapter` binds durable sessions to an authorized runtime/harness identity. Session persistence never restores credentials, capabilities, grants, provider authorization, or identity.

## Phase 54 human-in-the-loop

`core/hitl` is the durable human-gate authority. `HumanApprovalService` supports approval, human-input, and review gates; risk/cost/egress/destructive/security/deployment gate classification; identity/project binding; bounded metadata; expiry; optimistic revision checks; immutable terminal decisions; audited evidence digests; and controlled outcomes for approve, reject, modify, retry, reassign, and authorized alternatives.

The Control API exposes the outstanding approval queue, individual approval records, audit events, and decision endpoint. Identity is supplied explicitly by the control surface and checked against the persisted project/subject boundary. Missing identity fails closed. Approval decisions are governance evidence only: downstream execution must re-authorize and may not treat a stored decision as a credential or capability grant.

Web, TUI, and CLI remain clients of this shared Control API. Notifications are represented as an auditable queued notification fact; delivery infrastructure is intentionally not made a second authority. Approval expiry is fail-closed and restart-safe through SQLite persistence.

See `PHASE_54_HUMAN_IN_THE_LOOP.md` and `SI_AGENTS_V4_PLAN.md` for the full contract.

## Advanced hardening status

- **Phase 46:** execution identity conflict safety, idempotency, DAG cycle defense, bounded parallelism, recovery and cancellation.
- **Phase 47:** timeout propagation, bounded SSE frames, terminal semantics, session filtering, cancellation and endpoint security.
- **Phase 49:** deterministic versioned catalogs/manifests, validation, acyclic handoffs and execution layers.
- **Phase 50:** request-bound approvals, replay prevention, metadata rejection, egress/capability/scope controls and cost/risk policy.

Combined hardening CI **#984 (`34671292491`)** passed distribution, wheel verification, repository audit, integration verification, Ruff, and full pytest.

## V4 surface contract

### Web

Localhost-first and richest interface: live execution/agent/task/team status, DAG/workflow canvas, timelines, events, logs, evidence, artifacts, code/Markdown/JSON/diff viewers, routing/cost/health, approvals, search, global navigation, command palette, keyboard shortcuts, responsive layouts, accessibility, and state-oriented animation.

### TUI

Terminal-native operator cockpit with live refresh/streams, split panes, trees, DAG/progress views, fuzzy search/filtering, inspection, approvals, pause/resume/stop/retry/cancel/reconnect, and degraded-mode operation.

### CLI

Stable human and machine interface with normal commands, JSON schemas, exit codes, streaming, CI/non-interactive mode, profiles, authentication, local/remote control, session/execution attachment, and scripting.

All surfaces operate on the same SI Core authority.

## Next

**Phase 55 — Durable Waiting + Scheduling** is next after Phase 54 final closure.

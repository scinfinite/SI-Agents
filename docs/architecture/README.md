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
| 53 | Persistent Sessions | **Complete** | Final synchronized-tree mainline CI #1037 / `34675239106` |

## Phase 52 context / memory economics

`core/context_economics` is a deterministic policy layer between already-authorized context retrieval and model invocation. It provides scoped token/cost budgets, model capacity awareness, deterministic relevance/importance selection, deduplication, sensitive-context isolation, secret handling, compaction/summarization, accounting, stable decision IDs, evidence, and atomic snapshots.

## Phase 53 persistent sessions

`core/sessions` is the durable session authority. `SessionStore` persists session identity, ownership, lifecycle, state/context, token/cost history, ordered events, artifacts, expiry, archival, and lineage. `PersistentSessionAdapter` binds durable sessions to an authorized runtime/harness identity.

Key invariants:

- session operations require subject and project ownership;
- OpenCode/other harness operations additionally require the expected harness binding;
- optimistic revisions prevent stale concurrent writes;
- secret-like fields are rejected instead of persisted;
- state/events/artifacts/search inputs are bounded;
- replay is read-only;
- export/import requires schema and owner validation;
- clones receive a new identity and explicit parent lineage;
- session persistence never restores credentials, capabilities, grants, provider authorization, or identity.

The session layer is persistence/lifecycle infrastructure, not a competing execution or authorization authority.

See `PHASE_53_PERSISTENT_SESSIONS.md` and `SI_AGENTS_V4_PLAN.md` for the full contract.

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

**Phase 54 — Human-in-the-Loop** is the next implementation phase.
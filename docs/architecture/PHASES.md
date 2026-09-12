# V4 Phases

43. Final v3 Integration & Hardening — historical V3 close

## V4 status

Phases 44–63 are closed. Phase 64 is merged and awaiting its exact synchronized-tree mainline closure gate. **Phase 65 — Workflow + Automation is active.** Phases 46, 47, 49, 50, 58, 59, and 60 received advanced hardening.

The active roadmap explicitly spans **Phase 44 — Execution Runtime Foundation** through **Phase 71 — Final Production Hardening**.

## Status legend

- **Complete** — implementation, tests, documentation, and final CI evidence verified.
- **Advanced hardened** — a closed phase received additional production/security invariants and green hardening CI.
- **Active** — current implementation phase; closure gate is still pending.
- **Next** — next implementation phase.
- **Planned** — future roadmap phase.

## V4 sequence

| Phase | Name | Status | Evidence |
|---:|---|---|---|
| 44 | Execution Runtime Foundation | Complete | CI #919 / `34610448789` |
| 45 | Event Bus + State Architecture | Complete | CI #935 / `34612616978` |
| 46 | Parallel Scheduler + Executor | Advanced hardened | CI #984 / `34671292491` |
| 47 | OpenCode Bridge | Advanced hardened | CI #984 / `34671292491` |
| 48 | OmniRoute Integration | Complete | CI #949 / `34623762921` |
| 49 | Agent + Team Builder | Advanced hardened | CI #984 / `34671292491` |
| 50 | Capability Authorization | Advanced hardened | CI #984 / `34671292491` |
| 51 | Checkpoints + Resume | Complete | CI #977 / `34627956634` |
| 52 | Context / Memory Economics | Complete | CI #1020 / `34673411916` |
| 53 | Persistent Sessions | Complete | CI #1041 / `34675322458` |
| 54 | Human-in-the-Loop | Complete | CI #1051 / `34676632475` |
| 55 | Durable Waiting + Scheduling | Complete | CI #1080 / `34678317246` |
| 56 | Intelligent Routing + Economics | Complete | CI #1099 / `34682849381` |
| 57 | Security Platform | Complete | CI #1113 / `34684260315` |
| 58 | Workspace / Worktree Lifecycle | Advanced hardened | PR #74 / CI #1144 / `34691176676` |
| 59 | Observability | Advanced hardened | PR #74 / CI #1144 / `34691176676` |
| 60 | Evaluation + Benchmarking | Advanced hardened | PR #74 / CI #1144 / `34691176676` |
| 61 | Continuous Improvement | Complete | PR #75 / CI #1157 / `34692165853` |
| 62 | Cross-Runtime / Cross-Harness | Complete | PR #76 / CI #1166 / `34692621358`; final mainline #1186 / `34693756693` |
| 63 | Ecosystem / Marketplace | Complete | PR #77 / CI #1189 / `34694186010`; final mainline #1198 / `34694418960` |
| 64 | SDK / Developer Platform | Active closure | PR #78 merged; synchronized-tree mainline closure pending |
| 65 | Workflow + Automation | **Active** | Workflow engine + acceptance/adversarial tests implemented; final closure pending |
| 66 | Advanced Web Control Plane | Planned | Planned |
| 67 | Advanced TUI Control Center | Planned | Planned |
| 68 | Advanced CLI Platform | Planned | Planned |
| 69 | npm Distribution + Setup | Planned | Planned |
| 70 | End-to-End Production Validation | Planned | Planned |
| 71 | Final Production Hardening | Planned | Planned |

## Phase 65 implementation

`core/automation/workflows.py` provides versioned declarative DAGs, conditional branching, durable waits, human gates, bounded fan-out/loops, delegation, retries, event/webhook/interval triggers, request-fingerprint-bound idempotency, cancellation, runtime limits, durable JSON checkpoints, templates, and reverse-order compensation. `core/automation/__init__.py` exports the workflow contracts.

`tests/unit/test_phase65_workflows.py` provides acceptance and adversarial coverage for the workflow state machine and failure boundaries.

Documentation: `docs/architecture/PHASE_65_WORKFLOW_AUTOMATION.md`.

## Phase 64 closure

Phase 64 delivers typed Python and TypeScript SDKs, versioned REST/SSE/WebSocket access, stable errors, optional bearer authentication, header-bound identity, filter-bound cursor pagination, bounded idempotent run creation, bounded client concurrency, explicit event subscriptions, signed webhook delivery primitives, OpenAPI updates, examples, package metadata, and dedicated SDK CI. SDKs remain clients; SI Core retains governance and execution authority.

Implementation: `sdk/python/si_agents`, `sdk/typescript`, `core/control_api/pagination.py`, `core/control_api/subscriptions.py`, `core/control_api/server.py`, and `core/control_api/openapi.py`.

Documentation: `docs/architecture/PHASE_64_SDK_DEVELOPER_PLATFORM.md`.

PR #78 was merged into `main`. The final synchronized-tree mainline CI remains the closure gate.

## Closure gate

A phase is not complete until implementation, unit/integration tests, adversarial/security tests, edge/failure tests, documentation synchronization, repository audit, distribution/wheel verification, integration verification, Ruff, compileall, full pytest, and final exact-tree mainline CI are green.

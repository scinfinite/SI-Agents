# V4 Phases

43. Final v3 Integration & Hardening — historical V3 close

## V4 status

Phases 44–63 are closed. Phases 46, 47, 49, 50, 58, 59, and 60 received advanced hardening. Phase 64 is in implementation pending final closure CI.

The active roadmap explicitly spans **Phase 44 — Execution Runtime Foundation** through **Phase 71 — Final Production Hardening**.

## Status legend

- **Complete** — implementation, tests, documentation, and final CI evidence verified.
- **Advanced hardened** — a closed phase received additional production/security invariants and green hardening CI.
- **In implementation** — implementation is merged but final closure CI is pending.
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
| 64 | SDK / Developer Platform | **In implementation** | PR #78 |
| 65 | Workflow + Automation | Planned | Planned |
| 66 | Advanced Web Control Plane | Planned | Planned |
| 67 | Advanced TUI Control Center | Planned | Planned |
| 68 | Advanced CLI Platform | Planned | Planned |
| 69 | npm Distribution + Setup | Planned | Planned |
| 70 | End-to-End Production Validation | Planned | Planned |
| 71 | Final Production Hardening | Planned | Planned |

## Phase 64 implementation

Phase 64 adds typed Python and TypeScript SDKs, versioned REST access, stable errors, optional bearer authentication, query-bound cursor pagination/filtering, bounded idempotent run creation, bounded client concurrency, SSE/WebSocket event transports, explicit subscription lifecycle, signed webhook delivery primitives, OpenAPI updates, package metadata, and adversarial transport tests. SDKs remain clients; SI Core retains governance and execution authority.

Implementation: `sdk/python/si_agents`, `sdk/typescript`, `core/control_api/pagination.py`, `core/control_api/subscriptions.py`, and the SDK-facing transport extensions in `core/control_api/server.py` / `openapi.py`.

Documentation: `docs/architecture/PHASE_64_SDK_DEVELOPER_PLATFORM.md`.

Closure gate: PR #78 must pass the complete repository gate, then the documentation-synchronized exact tree must pass final mainline CI before Phase 64 is marked Complete.

## Phase 63 closure

Phase 63 provides governed ecosystem metadata and lifecycle contracts through `MarketplaceManifest`, `MarketplaceRegistry`, and `EcosystemManager`: strict semver, dependencies, compatibility, declared permissions, provenance/trust, exact manifest identity, templates, install/update/uninstall/rollback, bounded history, and drift detection. Marketplace lifecycle never grants execution authority; SI Core remains authoritative for authorization and execution.

Merged PR #77 as `19be0c14774e7073871a21fde42132a73c2a77d4`. PR CI #1189 / `34694186010` passed wheel verification, repository audit, integration verification, Ruff, and full pytest. Final exact-tree mainline CI #1198 / `34694418960` on `633af3e9a5b1a106fafee37c4c95d0b18e19743e` passed the complete repository closure suite.

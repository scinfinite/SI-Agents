# V4 Phases

43. Final v3 Integration & Hardening — historical V3 close

## V4 roadmap: Phase 44 through Phase 71

Phases **44–70 are closed**. Phase 71 is the final production-hardening gate and is pending final mainline verification.

## Status legend

- **Complete** — implementation, tests, documentation, and final CI evidence verified.
- **Advanced hardened** — a closed phase received additional production/security invariants and green hardening CI.
- **Next** — next implementation phase after the current closed phase.
- **Planned** — future roadmap phase.
- **Pending final verification** — implementation is complete, but final mainline closure evidence is still required.

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
| 62 | Cross-Runtime / Cross-Harness | Complete | PR #76 / final mainline #1186 / `34693756693` |
| 63 | Ecosystem / Marketplace | Complete | PR #77 / final mainline #1198 / `34694418960` |
| 64 | SDK / Developer Platform | Complete | PR #78 / closure CI #1239 / `34697885027` |
| 65 | Workflow + Automation | Complete / 100% | final synchronized-tree CI #1249 / `34698187600` |
| 66 | Advanced Web Control Plane | Complete / 100% | PR #79 / final synchronized-tree CI #1284 / `34701494501` |
| 67 | Advanced TUI Control Center | Complete / 100% | PR #80 / final PR CI #1288 / `34702115990` |
| 68 | Advanced CLI Platform | Complete / 100% | PR #81 / PR CI #1319 / `34703142494` / SDK #111 / `34703142515` / final mainline #1320 / `34703212232` |
| 69 | npm Distribution + Setup | Complete / 100% | final mainline CI #1363 / `34742449609` |
| 70 | End-to-End Production Validation | **Complete / 100%** | final mainline CI #1372 / `34742931329` + SDK #164 / `34742931334` |
| 71 | Final Production Hardening | **Pending final verification** | Phase 71 lifecycle/idempotency/concurrency hardening + final mainline CI pending |

## Phase 71 implementation

Phase 71 hardens the authoritative RuntimeEngine lifecycle without adding a second authority. `InvocationLedger` is thread-safe and bounded, keys state by `(harness_id, request_id)`, caches terminal responses for idempotent replay, rejects request-ID payload confusion, prevents concurrent duplicate execution, and makes cancellation terminal.

Implementation: `core/runtime/lifecycle.py`, `core/runtime/engine.py`, `core/runtime/__init__.py`.

Acceptance coverage: `tests/integration/test_phase71_final_hardening.py`.

Detailed contract: `docs/architecture/phases/PHASE_71_FINAL_PRODUCTION_HARDENING.md`.

## Closure evidence

Phase 71 is complete only when the hardening implementation is present on canonical `main`, documentation is synchronized, the full existing repository gates remain green, SDK CI is green, and final mainline CI is green on the exact final Phase 71 tree. Post-merge branch cleanup must leave only canonical `main`.

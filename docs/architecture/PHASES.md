# V4 Phases

43. Final v3 Integration & Hardening — historical V3 close

## V4 roadmap markers

- **Phase 44 — Execution Runtime Foundation**
- **Phase 45 — Event Bus + State Architecture**
- **Phase 46 — Parallel Scheduler + Executor**
- **Phase 47 — OpenCode Bridge**
- **Phase 48 — OmniRoute Integration**
- **Phase 49 — Agent + Team Builder**
- **Phase 50 — Capability Authorization**
- **Phase 51 — Checkpoints + Resume**
- **Phase 52 — Context / Memory Economics**
- **Phase 53 — Persistent Sessions** through **Phase 70 — End-to-End Production Validation**
- **Phase 71 — Final Production Hardening**

## Status legend

- **Complete** — implementation, tests, documentation, and final CI evidence verified.
- **Advanced hardened** — a closed phase was re-audited with additional production/security invariants and green hardening CI.
- **In implementation** — active phase implementation/tests/docs are in progress; final mainline CI is still required.
- **Next** — planned next implementation phase.
- **Planned** — future roadmap phase.

## V4 sequence and current status

| Phase | Name | Status | Evidence |
|---:|---|---|---|
| 44 | Execution Runtime Foundation | Complete | CI #919 / `34610448789` |
| 45 | Event Bus + State Architecture | Complete | CI #935 / `34612616978` |
| 46 | Parallel Scheduler + Executor | Advanced hardened | Hardening CI #984 / `34671292491` |
| 47 | OpenCode Bridge | Advanced hardened | Hardening CI #984 / `34671292491` |
| 48 | OmniRoute Integration | Complete | CI #949 / `34623762921` |
| 49 | Agent + Team Builder | Advanced hardened | Hardening CI #984 / `34671292491` |
| 50 | Capability Authorization | Advanced hardened | Hardening CI #984 / `34671292491` |
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
| 62 | Cross-Runtime / Cross-Harness | **In implementation** | PR pending |
| 63 | Ecosystem / Marketplace | Next | Planned |
| 64 | SDK / Developer Platform | Planned | Planned |
| 65 | Workflow + Automation | Planned | Planned |
| 66 | Advanced Web Control Plane | Planned | Planned |
| 67 | Advanced TUI Control Center | Planned | Planned |
| 68 | Advanced CLI Platform | Planned | Planned |
| 69 | npm Distribution + Setup | Planned | Planned |
| 70 | End-to-End Production Validation | Planned | Planned |
| 71 | Final Production Hardening | Planned | Planned |

Phase 58–60 are fully closed at advanced-hardening level by PR #74 / PR CI #1143 (`34691131729`) and final mainline CI #1144 (`34691176676`). Phase 61 is fully closed by merged PR #75 / PR CI #1157 (`34692165853`).

Phase 62 adds portable resource adapter contracts, deterministic harness discovery and capability filtering, health/quarantine/recovery, project+harness session isolation, explicit migration, and safe pre-start fallback. Its closure remains gated on PR CI and final synchronized-tree mainline CI.

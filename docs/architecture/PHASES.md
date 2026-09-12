# V4 Phases

43. Final v3 Integration & Hardening — historical V3 close

## V4 roadmap: Phase 44 through Phase 71

Phases **44–67 are closed**. **Phase 68 — Advanced CLI Platform is implementation-complete pending its final synchronized-tree closure gate.** Phase 71 is the final production-hardening gate.

## Status legend

- **Complete** — implementation, tests, documentation, and final CI evidence verified.
- **Advanced hardened** — a closed phase received additional production/security invariants and green hardening CI.
- **In progress / closure gate** — implementation is complete but final CI/documentation closure is still pending.
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
| 62 | Cross-Runtime / Cross-Harness | Complete | PR #76 / final mainline #1186 / `34693756693` |
| 63 | Ecosystem / Marketplace | Complete | PR #77 / final mainline #1198 / `34694418960` |
| 64 | SDK / Developer Platform | Complete | PR #78 / closure CI #1239 / `34697885027` |
| 65 | Workflow + Automation | Complete / 100% | final synchronized-tree CI #1249 / `34698187600` |
| 66 | Advanced Web Control Plane | Complete / 100% | PR #79 / final synchronized-tree CI #1284 / `34701494501` |
| 67 | Advanced TUI Control Center | **Complete / 100%** | PR #80 / final PR CI #1288 / `34702115990` |
| 68 | Advanced CLI Platform | **Implementation complete / closure gate** | PR #81 / CI pending final green |
| 69 | npm Distribution + Setup | Planned | Planned |
| 70 | End-to-End Production Validation | Planned | Planned |
| 71 | Final Production Hardening | Planned | Planned |

## Phase 68 implementation

Phase 68 introduces the advanced transport-neutral `si` CLI platform over SI Core's Control API. The surface covers governed run/task/execution operations, agent/team/workflow navigation, identity-bound approvals, sessions, events/streaming, models/providers delegation, attachment inspection, non-secret configuration/auth status, and bounded declarative pipelines. Local mode calls `ControlApiService`; remote mode uses authenticated HTTP. The CLI remains an adapter and cannot become a second execution or governance authority.

Implementation: `core/cli/platform.py`, `core/cli/aliases.py`, and `core/cli/dispatch.py`.

Acceptance coverage: `tests/test_phase68_cli.py` plus the full existing repository suite.

Detailed contract: `docs/architecture/PHASE_68_ADVANCED_CLI_PLATFORM.md`.

## Closure gate

Phase 68 closes only after PR CI passes wheel installation, repository audit, integration verification, Ruff, compileall, full pytest, SDK verification, security/adversarial coverage, documentation synchronization, merge, and a final exact-tree mainline CI run on the merged documentation state.

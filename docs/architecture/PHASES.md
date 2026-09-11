# V4 Phases

## Status legend

- **Complete** — implementation, tests, documentation, and final CI evidence verified.
- **Next** — planned next phase.
- **Planned** — not started.

## V4 sequence

| Phase | Name | Status | Evidence |
|---:|---|---|---|
| 44 | Execution Runtime Foundation | Complete | CI #919 / `34610448789` |
| 45 | Event Bus + State Architecture | Complete | CI #935 / `34612616978` |
| 46 | Parallel Scheduler + Executor | Complete | CI #938 / `34615157829` |
| 47 | OpenCode Bridge | Complete | CI #942 / `34615862860` |
| 48 | OmniRoute Integration | Complete | CI #949 / `34623762921` |
| 49 | Agent + Team Builder | Complete | CI #954 / `34625018676` |
| 50 | Capability Authorization | Complete | CI #970 / `34625819419` |
| 51 | Checkpoints + Resume | Complete after final exact-tree CI |
| 52 | Context / Memory Economics | Next |
| 53 | Persistent Sessions | Planned |
| 54 | Human-in-the-Loop | Planned |
| 55 | Durable Waiting + Scheduling | Planned |
| 56 | Intelligent Routing + Economics | Planned |
| 57 | Security Platform | Planned |
| 58 | Workspace / Worktree Lifecycle | Planned |
| 59 | Observability | Planned |
| 60 | Evaluation + Benchmarking | Planned |
| 61 | Continuous Improvement | Planned |
| 62 | Cross-Runtime / Cross-Harness | Planned |
| 63 | Ecosystem / Marketplace | Planned |
| 64 | SDK / Developer Platform | Planned |
| 65 | Workflow + Automation | Planned |
| 66 | Advanced Web Control Plane | Planned |
| 67 | Advanced TUI Control Center | Planned |
| 68 | Advanced CLI Platform | Planned |
| 69 | npm Distribution + Setup | Planned |
| 70 | End-to-End Production Validation | Planned |
| 71 | Final Production Hardening | Planned |

## Phase 51 integration markers

Phase 51 integrates with the Phase 44 authoritative execution runtime and Phase 45 EventBus. It does not bypass authorization, scheduler ownership, or adapter boundaries. Resume creates a new authoritative runtime attempt rather than restoring state directly.

## Phase 51 acceptance checklist

- [x] Durable SQLite checkpoint persistence.
- [x] Ordered per-execution sequence and parent lineage.
- [x] Canonical SHA-256 integrity verification.
- [x] Secret-like field rejection.
- [x] Bounded serialized checkpoint size.
- [x] Cross-execution lineage rejection.
- [x] Terminal-only resume.
- [x] Fresh authoritative attempt creation.
- [x] Authority is not restored from checkpoint metadata.
- [x] Reopen/persistence and tamper tests.
- [ ] Final exact-tree CI after this documentation synchronization.

## Closure rule

Do not mark a phase complete until the implementation and tests pass repository audit, distribution/wheel verification, integration verification, Ruff, compileall, full pytest, and the final exact-tree CI. Update README, docs index, architecture index, V4 plan, this phase index, the phase record, and affected cross-cutting documents after every phase.

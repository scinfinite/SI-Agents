# V4 Phases

43. Final v3 Integration & Hardening — historical V3 close

## Status legend

- **Complete** — implementation, tests, documentation, and final CI evidence verified.
- **Advanced hardened** — closed phase re-audited with additional production/security invariants and green hardening CI; final documentation-tree CI is required before merge.
- **Next** — planned next phase.
- **Planned** — not started.

## V4 sequence

| Phase | Name | Status | Evidence |
|---:|---|---|---|
| 44 | Execution Runtime Foundation | Complete | CI #919 / `34610448789` |
| 45 | Event Bus + State Architecture | Complete | CI #935 / `34612616978` |
| 46 | Parallel Scheduler + Executor | **Advanced hardened** | Hardening CI #984 / `34671292491` |
| 47 | OpenCode Bridge | **Advanced hardened** | Hardening CI #984 / `34671292491` |
| 48 | OmniRoute Integration | Complete | CI #949 / `34623762921` |
| 49 | Agent + Team Builder | **Advanced hardened** | Hardening CI #984 / `34671292491` |
| 50 | Capability Authorization | **Advanced hardened** | Hardening CI #984 / `34671292491` |
| 51 | Checkpoints + Resume | Complete | CI #977 / `34627956634` |
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

## Advanced hardening audit

- Phase 46: scheduler idempotency, explicit execution identity conflict safety, dependency DAG cycle defense, bounded concurrency/recovery/cancellation.
- Phase 47: request timeout propagation, bounded SSE frame buffering, terminal stream semantics, cancellation/error normalization.
- Phase 49: schema-versioned catalogs/manifests, stronger definition validation, acyclic handoff topology, deterministic execution layers.
- Phase 50: request-fingerprint-bound approvals, replay prevention, secret-like metadata rejection, bounded governance inputs, fail-closed egress.

Combined hardening CI **#984 (`34671292491`)** passed distribution, wheel verification, repository audit, integration verification, Ruff, and full pytest. The final mainline CI after merge is the authoritative exact-tree closure gate for these hardening changes.

## Phase 51 integration markers

Phase 51 integrates with the Phase 44 authoritative execution runtime and Phase 45 EventBus. It does not bypass authorization, scheduler ownership, or adapter boundaries. Resume creates a new authoritative runtime attempt rather than restoring state directly.

## Next-phase marker

Phase 52 is the next implementation phase: Context / Memory Economics.

## V4 integration marker

Phase 71 is the final production-hardening gate for the V4 roadmap; all advanced hardening remains subject to that roadmap's same evidence and authority rules.

## Closure rule

Do not mark a phase or hardening audit complete until implementation and tests pass repository audit, distribution/wheel verification, integration verification, Ruff, compileall, full pytest, and the final exact-tree CI. Update README, docs index, architecture index, V4 plan, this phase index, phase records, and affected cross-cutting documents after every phase and hardening audit.

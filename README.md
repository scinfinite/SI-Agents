# SI-Agents

SI-Agents is the governed execution and agent platform for Project-SI. V4 is built around one authoritative SI Core exposed through Web, TUI, CLI, OpenCode, SDKs, workflows, and runtime/integration adapters.

## Current V4 status

- **Phases 44–67 are complete on `main`.**
- **Phase 67 — Advanced TUI Control Center** is fully implemented, audited, documented, merged through PR #80, and verified by final PR CI #1288 (`34702115990`).
- **Phase 66 — Advanced Web Control Plane** is fully implemented, audited, documented, merged through PR #79, and verified by final synchronized-tree mainline CI #1284 (`34701494501`).
- **Phase 65 — Workflow + Automation** is fully implemented, audited, documented, and verified by final synchronized-tree CI #1249 (`34698187600`).
- **Phase 68 — Advanced CLI Platform** is implementation-complete and in its final CI/documentation closure gate on PR #81.
- **Phases 46, 47, 49, 50, 58, 59, and 60 passed dedicated advanced hardening.**

## Phase 68 — Advanced CLI Platform

Phase 68 adds a transport-neutral, machine-friendly `si` platform over SI Core. It provides governed run/task/execution commands, agent/team/workflow navigation, identity-bound approvals, bounded client sessions, event/state observation and run streaming, model/provider discovery delegation, attachment inspection, non-secret config/auth status, and bounded declarative pipelines.

Local mode calls the existing `ControlApiService`; remote mode uses authenticated HTTP against the existing Control API. The CLI is an adapter rather than a second execution/governance authority. It never invokes arbitrary shells or providers directly, never persists authentication secrets, and fail-closes when downstream execution owns a lifecycle transition such as resume.

Safety/automation contracts include deterministic JSON envelopes and exit classes, 1 MiB remote payload limits, 10 MiB attachment inspection, 256 KiB pipeline files, 100 pipeline steps, 100 retained client sessions, bounded streaming, and path-safe identifiers. See `docs/architecture/PHASE_68_ADVANCED_CLI_PLATFORM.md` and `tests/test_phase68_cli.py`.

## Phase 67 — Advanced TUI Control Center

Phase 67 provides a dependency-free, keyboard-first terminal operator cockpit over the existing Control API. It preserves the historical 14-view contract while adding bounded selection, filtering, deterministic sorting, detail inspection, pause/live state, direct view navigation, bounded JSON status export, non-interactive rendering, governed run creation, and identity-bound approval controls.

The TUI is a client of SI Core rather than a second authority. It owns only ephemeral presentation/navigation state, never executes shell commands, never invokes providers directly, and routes mutations through the existing governed Control API methods. Page size is bounded to 1–100, unknown commands are inert, `NO_COLOR` is respected, and CI/non-TTY rendering is deterministic.

Acceptance coverage: `tests/test_phase67_tui.py` plus the Phase 41 regression suite `tests/test_phase41_tui.py`. See `docs/architecture/PHASE_67_ADVANCED_TUI_CONTROL_CENTER.md` for the complete contract.

## V4 roadmap

See `docs/architecture/SI_AGENTS_V4_PLAN.md` for the authoritative roadmap and `docs/architecture/PHASES.md` for phase evidence.

| Phase | Name | Status |
|---:|---|---|
| 44 | Execution Runtime Foundation | Complete |
| 45 | Event Bus + State Architecture | Complete |
| 46 | Parallel Scheduler + Executor | Advanced hardened |
| 47 | OpenCode Bridge | Advanced hardened |
| 48 | OmniRoute Integration | Complete |
| 49 | Agent + Team Builder | Advanced hardened |
| 50 | Capability Authorization | Advanced hardened |
| 51 | Checkpoints + Resume | Complete |
| 52 | Context / Memory Economics | Complete |
| 53 | Persistent Sessions | Complete |
| 54 | Human-in-the-Loop | Complete |
| 55 | Durable Waiting + Scheduling | Complete |
| 56 | Intelligent Routing + Economics | Complete |
| 57 | Security Platform | Complete |
| 58 | Workspace / Worktree Lifecycle | Advanced hardened |
| 59 | Observability | Advanced hardened |
| 60 | Evaluation + Benchmarking | Advanced hardened |
| 61 | Continuous Improvement | Complete |
| 62 | Cross-Runtime / Cross-Harness | Complete |
| 63 | Ecosystem / Marketplace | Complete |
| 64 | SDK / Developer Platform | Complete |
| 65 | Workflow + Automation | Complete / 100% |
| 66 | Advanced Web Control Plane | Complete / 100% |
| 67 | Advanced TUI Control Center | **Complete / 100%** |
| 68 | Advanced CLI Platform | **Implementation complete / closure gate** |
| 69 | npm Distribution + Setup | Planned |
| 70 | End-to-End Production Validation | Planned |
| 71 | Final Production Hardening | Planned |

## Engineering gate

A phase is not complete until implementation, unit/integration tests, security/adversarial tests, edge/failure tests, documentation synchronization, repository audit, distribution/wheel verification, integration verification, Ruff, compileall, full pytest, SDK verification, merge, and final exact-tree mainline CI are green. **Phase 68 is not declared complete until that final mainline gate passes on the synchronized merged tree.**

## Current phase

**Phase 68 — Advanced CLI Platform is implementation-complete and undergoing its final closure gate.**
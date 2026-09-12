# V4 Phases

43. Final v3 Integration & Hardening — historical V3 close

## V4 status

Phases **44–66 are closed**. Phases 46, 47, 49, 50, 58, 59, and 60 received advanced hardening. **Phase 67 — Advanced TUI Control Center is next.**

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
| 64 | SDK / Developer Platform | Complete | PR #78 merged; implementation closure CI #1239 / `34697885027` |
| 65 | Workflow + Automation | Complete / 100% | Final synchronized-tree CI #1249 / `34698187600` |
| 66 | Advanced Web Control Plane | **Complete / 100%** | PR #79 merged; PR closure CI #1275 / `34699632473` passed; final synchronized-tree mainline gate follows this documentation state |
| 67 | Advanced TUI Control Center | **Next** | Planned |
| 68 | Advanced CLI Platform | Planned | Planned |
| 69 | npm Distribution + Setup | Planned | Planned |
| 70 | End-to-End Production Validation | Planned | Planned |
| 71 | Final Production Hardening | Planned | Planned |

## Phase 66 implementation

The web control plane is a same-origin client layered directly on the existing WebServer and versioned Control API. `core/web/advanced.py` installs the Phase 66 handler; `web/control/index.html`, `web/control/app.js`, and `web/control/styles.css` provide the dependency-free responsive UI.

The surface includes overview/health, live activity, workflows/runs, topology/DAG, evidence, identity-bound approvals, governed run-request controls, resources/settings, and bounded repository source/search/diff inspection. It uses semantic navigation, keyboard-accessible controls, a skip link, live status announcements, responsive layouts, and a text-first graph representation.

Security boundaries include inherited WebServer authentication/audit, restrictive CSP, `nosniff`, safe static/repository path resolution, no third-party runtime assets, bounded five-second refresh, bounded repository search/source/diff, `.git` exclusion, and explicit identity headers for approval visibility. Governed run requests remain ordinary Control API requests and cannot bypass SI Core authorization. The UI does not become an execution or authorization authority.

Acceptance tests: `tests/unit/test_phase66_web_control.py` and `tests/unit/test_phase66_advanced_web.py`.

Documentation: `docs/architecture/PHASE_66_ADVANCED_WEB_CONTROL_PLANE.md`.

## Closure gate

Phase 66 implementation and PR closure gates are green. The final synchronized-tree mainline CI for this documentation state is the authoritative last gate before Phase 66 is considered fully closed.

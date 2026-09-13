# V4 Phases

43. Final v3 Integration & Hardening — historical V3 close

## V4 roadmap: Phase 44 through Phase 71

Phases **44–68 are closed**. Phase 69 adds the npm distribution/bootstrap surface. Phase 70 validates the complete product end-to-end. Phase 71 is the final production-hardening gate.

## Status legend

- **Complete** — implementation, tests, documentation, and final CI evidence verified.
- **Advanced hardened** — a closed phase received additional production/security invariants and green hardening CI.
- **Next** — next implementation phase after the current closed phase.
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
| 68 | Advanced CLI Platform | **Complete / 100%** | PR #81 / PR CI #1319 / `34703142494` / SDK #111 / `34703142515` / final mainline #1320 / `34703212232` |
| 69 | npm Distribution + Setup | **Complete / 100%** | npm package verification + final mainline CI |
| 70 | End-to-End Production Validation | Planned | Planned |
| 71 | Final Production Hardening | Planned | Planned |

## Phase 69 implementation

Phase 69 adds a deliberately thin npm distribution surface. `package.json` declares the npm package and executable; `bin/si-agents.js` discovers a supported Python executable and forwards commands to `core.cli.dispatch`, preserving SI Core as the runtime authority. `si-agents setup` provides an explicit bootstrap path for the matching Python package. The launcher is shell-independent, supports an explicit `SI_AGENTS_PYTHON` override, and returns actionable prerequisite errors.

The npm package is content-allowlisted to the launcher, `LICENSE`, `NOTICE`, and `README.npm.md`. `scripts/verify-npm-package.mjs` checks npm/Python version parity, license metadata, required files, exact `npm pack` contents, and launcher version/help smoke behavior. CI runs this verifier after the existing Python distribution, audit, integration, lint, compile, and pytest gates.

Detailed contract: `docs/architecture/phases/PHASE_69_NPM_DISTRIBUTION_SETUP.md`.

## Closure evidence

Phase 69 is complete only when the implementation is present on canonical `main`, npm packaging verification is green, the full existing repository gates remain green, and final mainline CI is green on the exact Phase 69 tree. npm registry publication itself is a maintainer-controlled release operation and is not performed automatically by the repository CI.

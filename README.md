# SI-Agents

SI-Agents is an evidence-driven AI engineering system designed to inspect software, diagnose problems, execute controlled changes, verify results, and learn reusable engineering patterns.

## Current status

**v3 is complete and closed. V4 is active through Phase 47; Phases 44–47 are complete and final-CI verified. Phase 48 — OmniRoute Integration — is next.**

The verified v3 foundation includes 279 SI-native specialist personas across 18 divisions, portable Skills, Rules/Hooks/Events, scoped Memory/Knowledge, Security/Governance, organization teams/workflows, Control API v1, localhost-first Web, Control Center, visual organization/workflow inspection, Agent Builder, evidence-first observability, TUI, the governed Harness Deployment Center, and final cross-cutting integration hardening.

V4 is now extending that foundation into a real agent operating system with durable execution state, parallel task orchestration, live events/control, first-class OpenCode + OmniRoute integration, richer agent/team/workflow capabilities, security and economics controls, advanced Web/TUI/CLI surfaces, and a simple npm-based installation experience.

## V4 roadmap

The complete v4 plan is `docs/architecture/SI_AGENTS_V4_PLAN.md` and covers Phases 44–71.

```text
44 Runtime Foundation       [complete]
 → 45 Event + State         [complete]
 → 46 Scheduler / Executor  [complete]
 → 47 OpenCode Bridge       [complete]
 → 48 OmniRoute             [next]
 → 49 Agent + Team Builder
 → 50 Capability Authorization
 → 51 Checkpoints + Resume
 → 52 Context / Memory Economics
 → 53 Persistent Sessions
 → 54 Human-in-the-Loop
 → 55 Durable Waiting + Scheduling
 → 56 Intelligent Routing + Economics
 → 57 Security Platform
 → 58 Workspace / Worktree Lifecycle
 → 59 Observability
 → 60 Evaluation + Benchmarking
 → 61 Continuous Improvement
 → 62 Cross-Runtime / Cross-Harness
 → 63 Ecosystem / Marketplace
 → 64 SDK / Developer Platform
 → 65 Workflow + Automation
 → 66 Advanced Web Control Plane
 → 67 Advanced TUI Control Center
 → 68 Advanced CLI Platform
 → 69 npm Distribution + Setup
 → 70 End-to-End Production Validation
 → 71 Final Production Hardening
```

The roadmap deliberately builds the runtime, state, scheduling, governance, security and developer foundations before the final workflow, Web, TUI, CLI and distribution layers. Web is the richest localhost-first interface; TUI is the fastest terminal operator interface; CLI is the strongest automation/scripting interface. All three share the same SI Core, Control API and authoritative state.

## Target installation

```bash
npm install -g @scinfinite/si
si setup
```

This remains a V4 target and is not a claim of a currently released npm contract.

## Architecture principles

- One SI Core and one authoritative Control API.
- Web, TUI and CLI are control surfaces, not competing authorities.
- OpenCode remains the interactive coding harness.
- OmniRoute remains the model/provider routing layer.
- Runtime execution mechanics cannot grant authority or bypass governance.
- Evidence is required before completion claims.
- Secrets remain isolated from execution state wherever possible.
- Surface parity means operationally important capabilities remain available consistently across Web/TUI/CLI where appropriate.
- External engineering reference systems are used for pattern research only, not as copied dependencies or authorities over SI governance.

## Current verification baseline

Phase 43 final correction merged as `52588921c0956f091fb569c4b51e9fd741790744`. Final mainline CI #886 (`34558002476`) passed the V3 release gates.

V4 verification:
- Phase 44 final CI #919 (`34610448789`) passed.
- Phase 45 final exact-tree CI #935 (`34612616978`) passed.
- Phase 46 final CI #938 (`34615157829`) passed.
- Phase 47 implementation CI #941 (`34615709124`) passed, followed by final documentation exact-tree CI #942 (`34615862860`) on `main`.

## Documentation

- `docs/README.md` — documentation navigation and current baseline.
- `docs/architecture/PHASES.md` — authoritative current status.
- `docs/architecture/README.md` — architecture index and phase navigation.
- `docs/architecture/SI_AGENTS_V4_PLAN.md` — V4 roadmap and acceptance gates through Phase 71.
- `docs/architecture/SI_AGENTS_V3.md` — completed V3 architecture.
- `docs/architecture/PHASE_44_EXECUTION_RUNTIME.md` — Phase 44 evidence.
- `docs/architecture/PHASE_45_EVENT_BUS_STATE.md` — Phase 45 evidence.
- `docs/architecture/PHASE_46_PARALLEL_SCHEDULER_EXECUTOR.md` — Phase 46 evidence.
- `docs/architecture/PHASE_47_OPENCODE_BRIDGE.md` — Phase 47 evidence.

## Engineering loop

```text
OBSERVE → UNDERSTAND → RESEARCH → PLAN → EXECUTE → MEASURE
→ TEST → ATTACK THE SOLUTION → VERIFY → DOCUMENT → LEARN → GENERALIZE → REUSE
```

## Documentation rule

Historical phase Markdown preserves phase-time evidence. Current/index Markdown must reflect the latest verified status. After every completed phase, current status, navigation/index, roadmap state, verification baseline, and relevant cross-cutting documentation must be updated. Documentation must never claim implementation that has not been implemented and CI-verified.

# SI-Agents

SI-Agents is an evidence-driven AI engineering system designed to inspect software, diagnose problems, execute controlled changes, verify results, and learn reusable engineering patterns.

## Current status

**V3 is complete and closed. V4 is active through Phase 50; Phases 44–50 are complete and final-CI verified. Phase 51 — Checkpoints + Resume — is next.**

V4 is extending the verified V3 governance/control foundation into a real agent operating system with durable execution state, parallel orchestration, live events/control, first-class OpenCode and OmniRoute integration, richer agents/teams/workflows, security/economics controls, advanced Web/TUI/CLI surfaces, and distribution.

## V4 roadmap

```text
44 Runtime Foundation       [complete]
 → 45 Event + State         [complete]
 → 46 Scheduler / Executor  [complete]
 → 47 OpenCode Bridge       [complete]
 → 48 OmniRoute             [complete]
 → 49 Agent + Team Builder  [complete]
 → 50 Capability Authorization [complete]
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

The roadmap builds runtime/state/scheduling/governance foundations before the final workflow, Web, TUI, CLI and distribution layers. Web is the richest localhost-first interface; TUI is the fastest terminal operator interface; CLI is the strongest automation interface. All share the same SI Core, Control API and authoritative state.

## Architecture principles

- One SI Core and one authoritative Control API.
- Web, TUI and CLI are control surfaces, not competing authorities.
- OpenCode remains the interactive coding harness.
- OmniRoute remains downstream model/provider routing infrastructure.
- Runtime and provider adapters cannot grant authority or bypass governance.
- Model selection is policy-bounded; it cannot create permissions.
- Agent/team builders declare capabilities but cannot grant them.
- Capability authorization is explicit, scoped, fail-closed, and audit-evidenced.
- Credentials remain references and are resolved at transport time.
- Evidence is required before completion claims.
- Surface parity means operationally important capabilities share authoritative state.
- External engineering systems are pattern references, not copied authorities or dependencies.

## Current verification baseline

V3 final correction merged as `52588921c0956f091fb569c4b51e9fd741790744`; final V3 mainline CI #886 (`34558002476`) passed.

V4:
- Phase 44 final CI #919 (`34610448789`) passed.
- Phase 45 final exact-tree CI #935 (`34612616978`) passed.
- Phase 46 final CI #938 (`34615157829`) passed.
- Phase 47 implementation CI #941 (`34615709124`) passed, followed by documentation exact-tree CI #942 (`34615862860`).
- Phase 48 implementation/final CI run 949 (`34623762921`) passed; merge commit `f670563c7df06c05d269fe714e63abfe518036e0` is on `main`.
- Phase 49 implementation CI run 954 (`34625018676`) passed; merged to `main` as `de06398f2abefe24b58e52a7629dc5af3c191428`.
- Phase 50 implementation CI run 962 (`34625560602`) passed; merged to `main` as `03029d301f77ff6931bfa68415893686a849201b`.

## Documentation

- `docs/README.md` — documentation navigation and current baseline.
- `docs/architecture/PHASES.md` — authoritative current status.
- `docs/architecture/README.md` — architecture index and phase navigation.
- `docs/architecture/SI_AGENTS_V4_PLAN.md` — V4 roadmap and acceptance gates.
- `docs/architecture/MODEL_ROUTING.md` — model/provider routing contract.
- `docs/architecture/PHASE_44_EXECUTION_RUNTIME.md` through `PHASE_50_CAPABILITY_AUTHORIZATION.md` — phase evidence.

## Engineering loop

```text
OBSERVE → UNDERSTAND → RESEARCH → PLAN → EXECUTE → MEASURE
→ TEST → ATTACK THE SOLUTION → VERIFY → DOCUMENT → LEARN → GENERALIZE → REUSE
```

## Documentation rule

Historical phase Markdown preserves phase-time evidence. Current/index Markdown must reflect the latest verified status. After every completed phase, update the phase record, `PHASES.md`, architecture index, project/documentation navigation, roadmap status, verification references, and affected cross-cutting contracts before the final exact-tree CI gate. Documentation must never claim implementation that has not been implemented and CI-verified.

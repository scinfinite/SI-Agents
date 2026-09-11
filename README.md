# SI-Agents

SI-Agents is an evidence-driven AI engineering system designed to inspect software, diagnose problems, execute controlled changes, verify results, and learn reusable engineering patterns.

## Current status

**v3 is complete and closed. v4 planning is established through Phase 71; Phase 44 implementation has not started on `main`.**

The verified v3 foundation includes 279 SI-native specialist personas across 18 divisions, portable Skills, Rules/Hooks/Events, scoped Memory/Knowledge, Security/Governance, organization teams/workflows, Control API v1, localhost-first Web, Control Center, visual organization/workflow inspection, Agent Builder, evidence-first observability, TUI, the governed Harness Deployment Center, and final cross-cutting integration hardening.

The v4 goal is to evolve this foundation into a real agent operating system with persistent execution state, parallel task orchestration, live events/control, first-class OpenCode + OmniRoute integration, richer agent/team/workflow capabilities, security and economics controls, advanced Web/TUI/CLI surfaces, and a simple npm-based installation experience.

## V4 roadmap

The complete v4 plan is `docs/architecture/SI_AGENTS_V4_PLAN.md` and covers Phases 44–71.

```text
44 Runtime Foundation
 → 45 Event + State
 → 46 Scheduler / Executor
 → 47 OpenCode Bridge
 → 48 OmniRoute
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
- ECC, Agency Agents, OpenCode, OmniRoute and n8n are external reference systems for engineering patterns, not copied dependencies or authorities over SI governance.

## Current verification baseline

Phase 43 final correction merged as `52588921c0956f091fb569c4b51e9fd741790744`. Final mainline CI #886 (`34558002476`) passed the repository release gates, including distribution, wheel installation, repository audit, Ruff, and the complete pytest suite.

## Documentation

- `docs/README.md` — documentation navigation and current baseline.
- `docs/architecture/PHASES.md` — authoritative current status.
- `docs/architecture/README.md` — architecture index.
- `docs/architecture/SI_AGENTS_V4_PLAN.md` — V4 roadmap and acceptance gates through Phase 71.
- `docs/architecture/SI_AGENTS_V3.md` — completed V3 architecture record.
- `docs/architecture/PHASE_43_INTEGRATION_HARDENING.md` — final V3 phase evidence.

## Engineering loop

```text
OBSERVE → UNDERSTAND → RESEARCH → PLAN → EXECUTE → MEASURE
→ TEST → ATTACK THE SOLUTION → VERIFY → DOCUMENT → LEARN → GENERALIZE → REUSE
```

## Documentation rule

Historical phase Markdown preserves phase-time evidence. Current/index Markdown must reflect the latest verified status. Documentation must never claim implementation that has not been implemented and CI-verified.

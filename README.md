# SI-Agents

SI-Agents is an evidence-driven AI engineering system designed to inspect software, diagnose problems, execute controlled changes, verify results, and learn reusable engineering patterns.

## Current status

**v3 is complete and closed. v4 planning is established; Phase 44 has not started.**

The verified v3 foundation includes 279 SI-native specialist personas across 18 divisions, portable Skills, Rules/Hooks/Events, scoped Memory/Knowledge, Security/Governance, organization teams/workflows, Control API v1, localhost-first Web, Control Center, visual organization/workflow inspection, Agent Builder, evidence-first observability, TUI, the governed Harness Deployment Center, and final cross-cutting integration hardening.

The v4 goal is to evolve this foundation into a real agent operating system with persistent execution state, parallel task orchestration, live events/control, first-class OpenCode + OmniRoute integration, substantially improved Web/TUI/CLI surfaces, workflow automation, and a simple npm-based installation experience.

## v4 planning

The complete v4 plan is `docs/architecture/SI_AGENTS_V4_PLAN.md` and covers Phases 44–55.

```text
44 Runtime
 → 45 Event + State
 → 46 Scheduler / Executor
 → 47 OpenCode Bridge
 → 48 OmniRoute
 → 49 Web 2.0
 → 50 TUI 2.0
 → 51 CLI 2.0
 → 52 Agent / Team Builder
 → 53 Workflow / Automation
 → 54 npm Distribution / Setup
 → 55 End-to-End Validation
```

The target public installation experience is:

```bash
npm install -g @scinfinite/si
si setup
```

This is a v4 target, not a currently released npm contract.

## Current architecture principle

There is one SI Core and one Control API. Web, TUI and CLI are control surfaces, not competing authorities. OpenCode remains the interactive coding harness, and OmniRoute remains the model/provider routing layer.

The v4 implementation order deliberately starts with the execution runtime and state/event contracts before rebuilding presentation surfaces. This prevents Web/TUI/CLI from becoming sophisticated dashboards over incomplete execution semantics.

## Current verification baseline

Phase 43 final correction merged as `52588921c0956f091fb569c4b51e9fd741790744`. Final mainline CI #886 (`34558002476`) passed the repository release gates, including distribution, wheel installation, repository audit, Ruff, and the complete pytest suite.

## Documentation

- `docs/README.md` — documentation navigation and current baseline.
- `docs/architecture/PHASES.md` — authoritative current status.
- `docs/architecture/README.md` — architecture index.
- `docs/architecture/SI_AGENTS_V4_PLAN.md` — v4 planning baseline.
- `docs/architecture/SI_AGENTS_V3.md` — completed v3 architecture record.
- `docs/architecture/PHASE_43_INTEGRATION_HARDENING.md` — final v3 phase evidence.

## Engineering loop

```text
OBSERVE → UNDERSTAND → RESEARCH → PLAN → EXECUTE → MEASURE
→ TEST → ATTACK THE SOLUTION → VERIFY → DOCUMENT → LEARN → GENERALIZE → REUSE
```

## Documentation rule

Historical phase Markdown preserves phase-time evidence. Current/index Markdown must reflect the latest verified status. Documentation must never claim implementation that has not been implemented and CI-verified.
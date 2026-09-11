# SI-Agents v4 — Agent Operating System Roadmap

**Status:** Active implementation
**Baseline:** V3 Phases 1–43 complete and CI-verified
**Implemented:** V4 Phases 44–47 complete and final-CI verified
**Current phase:** Phase 48 — OmniRoute Integration (implementation complete; final CI pending)
**Planned sequence:** Phases 44–71

> A phase is complete only after implementation, tests, security/adversarial checks, documentation, packaging where relevant, and final CI verification. Current/index documentation must be synchronized before the final exact-tree gate.

## Vision

SI-Agents v4 evolves the V3 governance/control foundation into an agent operating system with durable execution, parallel orchestration, live events/control, first-class OpenCode and OmniRoute integration, richer agents/teams/workflows, security/economics controls, advanced Web/TUI/CLI surfaces, and production-grade distribution.

## Target architecture

```text
User / External System
  ├── Web ───────┐
  ├── TUI ───────┤
  ├── CLI ───────┤
  └── OpenCode ──┤
                 ▼
           SI Control API
           single authority
                 │
        Workflow / Orchestrator
                 │
        Runtime / Scheduler
          ┌──────┼───────────┐
          ▼      ▼           ▼
      OpenCode OmniRoute Native/MCP
          │      │           │
          └──────┼───────────┘
                 ▼
            Models / Tools
```

Control API owns identity, authorization, admission, policy, authority scope, provenance, approvals, audit and externally visible intent. Runtime owns execution mechanics. OpenCode is a harness/protocol adapter. OmniRoute is downstream model/provider routing infrastructure. Neither downstream layer can grant SI authority.

## Product principles

1. One Core and one authoritative Control API.
2. Web is the richest localhost-first surface.
3. TUI is the terminal operator cockpit.
4. CLI is the stable automation surface.
5. OpenCode remains the interactive coding harness.
6. OmniRoute remains downstream routing infrastructure.
7. Parallel execution is dependency/resource/governance bounded.
8. State and events are durable, correlated and replayable.
9. Control operations are typed transitions.
10. Evidence is required before completion.
11. Secrets stay out of runtime state.
12. V3 contracts remain intact.
13. Surface parity uses shared authoritative state.
14. Animation communicates state rather than hiding it.
15. External projects are research references, not copied authorities or dependencies.

## Phase status and roadmap

| Phase | Scope | State |
|---:|---|---|
| 44 | Execution Runtime Foundation | **Complete + final-CI verified** |
| 45 | Event Bus + State Architecture | **Complete + final-CI verified** |
| 46 | Parallel Scheduler + Executor | **Complete + final-CI verified** |
| 47 | OpenCode Bridge | **Complete + final-CI verified** |
| 48 | OmniRoute Integration | **Implementation complete; final CI pending** |
| 49 | Agent + Team Builder | Planned |
| 50 | Capability Authorization | Planned |
| 51 | Checkpoints + Resume | Planned |
| 52 | Context / Memory Economics | Planned |
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
| 71 | Final Production Hardening | Planned / final gate |

## Completed V4 evidence

### Phase 44 — Execution Runtime Foundation

Durable execution/attempt identity, lifecycle transitions, persistence, idempotency, cancellation, pause/resume boundaries, deadlines, retries, restart recovery, adapter isolation and secret isolation. Final CI `34610448789` passed.

### Phase 45 — Event Bus + State Architecture

Durable append-only events, aggregate ordering, correlation/causation, replay, subscriptions, projections/checkpoints and lifecycle integration. Final exact-tree CI `34612616978` passed.

### Phase 46 — Parallel Scheduler + Executor

Durable dependency-aware scheduling, priority/aging, bounded parallel execution, cancellation/failure propagation, restart recovery and runtime-authoritative finalization. Final CI `34615157829` passed.

### Phase 47 — OpenCode Bridge

Health/session discovery, blocking and streaming invocation, cancellation, SSE filtering, loopback-default endpoint policy, remote opt-in and transport-error normalization. Implementation CI `34615709124` and documentation exact-tree CI `34615862860` passed.

## Phase 48 — OmniRoute Integration

**Objective:** Use OmniRoute as the model/provider access layer without creating a competing router.

**Implemented scope:** health/status; model catalog; typed capability metadata; capability-aware preferred/fallback selection; OpenAI-compatible chat completion; usage metadata; rate-limit and upstream-error classification; credential references; loopback-default endpoint policy; deterministic injectable transport; explicit unsupported-cancellation behavior.

**Authority invariants:** model selection cannot grant authority; governance metadata is not forwarded as provider authority; credentials are resolved at transport time; upstream response bodies are not exposed; no silent unauthorized fallback occurs.

**Acceptance:** SI can discover usable configured models through OmniRoute and invoke the canonical OpenAI-compatible workload through the runtime adapter while preserving SI authority. Final acceptance additionally requires repository CI and synchronized documentation.

## Phase 49 — Agent + Team Builder

Typed, composable SI-native agents and teams with capabilities, skills, model policy, resource limits, governance, evidence and deterministic/auditable builder output.

## Phases 50–71

50 Capability Authorization; 51 Checkpoints + Resume; 52 Context/Memory Economics; 53 Persistent Sessions; 54 Human-in-the-Loop; 55 Durable Waiting + Scheduling; 56 Intelligent Routing + Economics; 57 Security Platform; 58 Workspace/Worktree Lifecycle; 59 Observability; 60 Evaluation + Benchmarking; 61 Continuous Improvement; 62 Cross-Runtime/Cross-Harness; 63 Ecosystem/Marketplace; 64 SDK/Developer Platform; 65 Workflow + Automation; 66 Advanced Web Control Plane; 67 Advanced TUI Control Center; 68 Advanced CLI Platform; 69 npm Distribution + Setup; 70 End-to-End Production Validation; 71 Final Production Hardening.

Phase 71 is the final V4 production-hardening gate. No later phase may be marked complete without evidence from implementation, tests, security/adversarial checks, documentation, packaging where relevant, and final CI.

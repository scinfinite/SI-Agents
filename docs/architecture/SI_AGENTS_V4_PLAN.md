# SI-Agents v4 — Agent Operating System Roadmap

**Status:** Active implementation
**Baseline:** V3 Phases 1–43 complete and CI-verified
**Implemented:** V4 Phases 44–50 complete and final-CI verified
**Current phase:** Phase 51 — Checkpoints + Resume
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

Control API owns identity, authorization, admission, policy, authority scope, provenance, approvals, audit and externally visible intent. Runtime owns execution mechanics. OpenCode is a harness/protocol adapter. OmniRoute is downstream model/provider routing infrastructure. Agent/team composition is declarative. Capability authorization is the explicit admission boundary. None of these downstream layers can self-grant SI authority.

## Product principles

1. One Core and one authoritative Control API.
2. Web is the richest localhost-first surface.
3. TUI is the terminal operator cockpit.
4. CLI is the stable automation surface.
5. OpenCode remains the interactive coding harness.
6. OmniRoute remains downstream routing infrastructure.
7. Agent/team builders declare capabilities; authorization decides whether they may use them.
8. Authorization is explicit, scoped, deny-first and fail-closed.
9. Parallel execution is dependency/resource/governance bounded.
10. State and events are durable, correlated and replayable.
11. Control operations are typed transitions.
12. Evidence is required before completion.
13. Secrets stay out of runtime state.
14. V3 contracts remain intact.
15. Surface parity uses shared authoritative state.
16. Animation communicates state rather than hiding it.
17. External projects are research references, not copied authorities or dependencies.

## Phase status and roadmap

| Phase | Scope | State |
|---:|---|---|
| 44 | Execution Runtime Foundation | **Complete + final-CI verified** |
| 45 | Event Bus + State Architecture | **Complete + final-CI verified** |
| 46 | Parallel Scheduler + Executor | **Complete + final-CI verified** |
| 47 | OpenCode Bridge | **Complete + final-CI verified** |
| 48 | OmniRoute Integration | **Complete + final-CI verified** |
| 49 | Agent + Team Builder | **Complete + final-CI verified** |
| 50 | Capability Authorization | **Complete + final-CI verified** |
| 51 | Checkpoints + Resume | Planned / next |
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

### Phase 48 — OmniRoute Integration

Health/model discovery, typed capability metadata, capability-aware preferred/fallback selection, OpenAI-compatible inference, usage normalization, rate-limit/upstream/transient transport classification, credential references, endpoint security, deterministic transport tests and authority-boundary enforcement. Final CI run 949 (`34623762921`) passed; merged to `main` as `f670563c7df06c05d269fe714e63abfe518036e0`.

### Phase 49 — Agent + Team Builder

Typed immutable agent definitions, deterministic registry/catalog digests, explicit team membership and handoffs, bounded parallelism, aggregate capability declarations, model/resource policy metadata, deterministic manifests, conflict-safe registration, and governance-boundary tests. CI run 954 (`34625018676`) passed; merged to `main` as `de06398f2abefe24b58e52a7629dc5af3c191428`.

### Phase 50 — Capability Authorization

Fail-closed authorization over existing governance `Permission`/`Policy` primitives, with explicit scoped grants, deny precedence, declared-capability enforcement, subject identity binding, condition checks, high/critical-risk approval gates, explicit egress policy, cost constraints, deterministic evidence identifiers, and request fingerprints that exclude secrets. CI run 962 (`34625560602`) passed; merged to `main` as `03029d301f77ff6931bfa68415893686a849201b`.

## Phase 51 — Checkpoints + Resume

Next objective: durable execution checkpoints, safe state snapshots, restart/resume semantics, compaction boundaries, and replay-aware recovery without violating authorization or provenance.

## Phases 52–71

52 Context/Memory Economics; 53 Persistent Sessions; 54 Human-in-the-Loop; 55 Durable Waiting + Scheduling; 56 Intelligent Routing + Economics; 57 Security Platform; 58 Workspace/Worktree Lifecycle; 59 Observability; 60 Evaluation + Benchmarking; 61 Continuous Improvement; 62 Cross-Runtime/Cross-Harness; 63 Ecosystem/Marketplace; 64 SDK/Developer Platform; 65 Workflow + Automation; 66 Advanced Web Control Plane; 67 Advanced TUI Control Center; 68 Advanced CLI Platform; 69 npm Distribution + Setup; 70 End-to-End Production Validation; 71 Final Production Hardening.

Phase 71 is the final V4 production-hardening gate. No later phase may be marked complete without evidence from implementation, tests, security/adversarial checks, documentation, packaging where relevant, and final CI.
# Architecture

SI-Agents V4 uses a single authoritative SI Core. Web, TUI, CLI, OpenCode, runtime adapters, schedulers, agents, teams, workflows, and integrations are clients/adapters of that authority rather than independent state owners.

## V4 target architecture

```text
OpenCode → SI OpenCode Bridge → SI Core / Control API
        → Scheduler / Orchestrator → Tasks / Agents / Teams / Workflows
        → Authorization → OmniRoute → Models / Providers / APIs
        → Results / Artifacts / Evidence → SI Core
        → OpenCode / Web / TUI / CLI
```

OmniRoute owns model/provider/API routing. SI Core owns execution, orchestration, governance, evidence, lifecycle, persistence, recovery, and durable waiting state. Phase 56 adds SI-side routing intelligence without taking over OmniRoute authority.

## Verified V4 phases

| Phase | Capability | Status | Evidence |
|---:|---|---|---|
| 44 | Execution Runtime Foundation | Complete | CI #919 / `34610448789` |
| 45 | Event Bus + State Architecture | Complete | CI #935 / `34612616978` |
| 46 | Parallel Scheduler + Executor | **Advanced hardened** | Hardening CI #984 / `34671292491` |
| 47 | OpenCode Bridge | **Advanced hardened** | Hardening CI #984 / `34671292491` |
| 48 | OmniRoute Integration | Complete | CI #949 / `34623762921` |
| 49 | Agent + Team Builder | **Advanced hardened** | Hardening CI #984 / `34671292491` |
| 50 | Capability Authorization | **Advanced hardened** | Hardening CI #984 / `34671292491` |
| 51 | Checkpoints + Resume | Complete | CI #977 / `34627956634` |
| 52 | Context / Memory Economics | **Complete** | Final exact-tree CI #1020 / `34673411916` |
| 53 | Persistent Sessions | **Complete** | Final synchronized-tree mainline CI #1041 / `34675322458` |
| 54 | Human-in-the-Loop | **Complete** | Final synchronized-tree mainline CI #1051 / `34676632475` |
| 55 | Durable Waiting + Scheduling | **Complete** | Final synchronized-tree closure CI #1080 / `34678317246` |
| 56 | Intelligent Routing + Economics | **Complete** | Final synchronized-tree mainline CI #1095 / `34682748193` |

## Phase 56 intelligent routing

`core/provider_intelligence/intelligent_router.py` provides deterministic SI-side routing intelligence over explicit task requirements and existing provider/model profiles. It matches capabilities, context, output limits, streaming, structured output, vision, coding, reasoning, and tool use; ranks by quality, reliability history, latency, cost, and preference; gates on provider/model enablement, quota, and circuit state; and produces non-secret route evidence.

Economics are guarded through `BudgetLedger` reservations/settlement, cost estimation, retry forecasting, bounded retry attempts, and transient/rate-limit fallback. Escalation and downgrade are explicit policy decisions. Provider outcomes update health/circuit state, and recovery probes can restore eligibility. Routing never grants authorization or credentials.

## Phase 55 durable waiting

`core/waiting` is the SI Core durable wait/scheduling authority. `WaitingService` persists timer, delayed, recurring, cron, approval, human, dependency, resource, and external waits with explicit `waiting → ready → claimed → completed` lifecycle, deadline expiry, event wake-up, restart recovery, priority plus age-based fairness, optimistic revisions, bounded queue/payload limits, secret-like field rejection, and ordered lifecycle events.

Recurring schedules use bounded positive intervals and explicit occurrence limits. Cron uses validated five-field UTC expressions and bounded next-occurrence search. Waiting never consumes execution-worker capacity. A claim is an execution handoff state, not an authorization grant; downstream execution must independently authorize capabilities, credentials, providers, and identity.

The Control API exposes identity-bound create/list/get/events/wake/claim/complete/cancel routes under `/api/v1/waits`. Missing identity and cross-project access fail closed.

## Phase 54 human-in-the-loop

`core/hitl` is the durable human-gate authority. Approval, human-input, and review gates remain governance evidence only; downstream execution must re-authorize.

## Surface contract

Web, TUI, CLI, and OpenCode remain clients of shared SI Core authority. No interface creates competing execution, session, approval, or waiting state ownership.

## Next

**Phase 57 — Security Platform** follows Phase 56 final synchronized-tree mainline CI closure.

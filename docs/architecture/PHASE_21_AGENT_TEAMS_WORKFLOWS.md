# Phase 21 — Agent Teams & Workflows

## Status

**Complete pending final CI verification.**

Phase 21 turns the Phase 20 agent catalog into an executable, bounded team/workflow control plane. It deliberately remains harness-neutral: the engine executes injected `AgentWorker` implementations and does not depend on OpenCode, Claude Code, Codex, Cline, Antigravity, or OmniRoute.

## Goals

Phase 21 acceptance requires:

1. Canonical team/workflow definitions separate from execution authority.
2. Typed team membership, task definitions, dependencies, lifecycle states, and execution events.
3. Deterministic dependency-aware scheduling.
4. Bounded parallel execution.
5. Explicit shared versus isolated task context.
6. Structured handoffs through `AgentResult.handoff`.
7. Bounded retry attempts.
8. Explicit escalation to a declared team member.
9. Verification gates and evidence requirements.
10. Dependency failure propagation without executing blocked work.
11. Cooperative cancellation before dispatch and cancellation of pending work.
12. Checkpoints and auditable workflow events.
13. No permission or governance bypass through team membership.
14. Canonical JSON team catalog with stdlib-only loading and validation.

## Implementation

- `core/teams/models.py` — typed team/task/execution/event contracts.
- `core/teams/registry.py` — duplicate-safe team registry.
- `core/teams/loader.py` — canonical JSON loader and validation.
- `core/teams/engine.py` — dependency-aware bounded executor, retry/escalation, context isolation, evidence/verification gates, cancellation, and checkpoints.
- `config/team-catalog.json` — canonical declarative engineering repair workflow.
- `tests/test_teams.py` — orchestration acceptance suite.

## Scheduling model

The workflow is a dependency DAG. A task becomes runnable only when all dependencies are `succeeded` or `escalated`. Ready tasks are dispatched in deterministic catalog order up to `max_parallelism`. A task failure blocks downstream dependents; blocked work is marked `skipped` rather than executed.

Parallelism is bounded by the team definition. The engine uses a standard-library thread pool and does not create unbounded agent processes or hidden workers.

## Context and handoff model

`ContextMode.SHARED` allows successful task context/handoff values to become available to downstream tasks. `ContextMode.ISOLATED` receives a snapshot and does not publish arbitrary context mutations. Explicit `AgentResult.handoff` remains the portable handoff surface.

This avoids implicit cross-agent memory and keeps the team layer separate from the persistent memory system from earlier phases.

## Failure and escalation model

Each task declares `max_attempts`. Failed attempts emit retry events until the limit is reached. If `escalate_to` is declared, the escalation worker receives the failed task's local context. A successful escalation produces `TaskStatus.ESCALATED`, which is treated as a successful dependency outcome while preserving the fact that escalation occurred.

Escalation targets must be declared team members. Team membership does not grant permissions; the injected worker remains responsible for enforcing its own required permissions and the existing governance/runtime layers remain authoritative.

## Evidence and verification gates

A task may require evidence (`requires_evidence`) and/or a verification handoff (`verification_gate`, requiring `handoff["verified"] == true`). A team with `required_evidence=true` cannot finish successfully without at least one evidence identifier across successful/escalated results.

The engine records a `final-gate` checkpoint containing the evidence identifiers before emitting `workflow_completed`.

## Cancellation

Cancellation is cooperative. A cancellation event prevents new work from being dispatched and marks pending work as cancelled. Already-running workers are not force-killed by the team layer because arbitrary `AgentWorker` implementations are outside its process-control authority. Harness-specific cancellation remains a later integration concern.

## External reference patterns

The design generalizes useful patterns from current ECC and Agency Agents without copying their implementation. ECC's current team-builder emphasizes dynamic discovery, bounded parallel dispatch, explicit failure reporting, and synthesis; its dynamic workflow guidance emphasizes observable checkpoints, eval gates, handoffs, and stopping on unsafe or unclear states. Agency Agents' NEXUS workflow emphasizes explicit role sequencing, quality gates, evidence, Dev↔QA loops, retries, and handoffs. citeturn1view0turn2view0turn1view1

SI-Agents intentionally adds typed contracts, explicit permissions/governance boundaries, evidence identifiers, deterministic DAG scheduling, isolated context, and a harness-neutral execution boundary rather than adopting a prompt-only orchestration model.

## Explicit non-goals

Phase 21 does **not** implement:

- external harness adapters;
- OpenCode integration;
- OmniRoute integration;
- Claude Code/Codex/Cline/Antigravity adapters;
- Termux/Codespace installers;
- model selection or quota routing;
- automatic persona generation;
- self-modifying agent promotion;
- forced process termination of arbitrary workers.

Those remain later phases or deployment responsibilities.

## Verification

The acceptance suite covers:

- dependency ordering and structured handoff;
- shared versus isolated context;
- bounded parallelism;
- retry behavior;
- escalation recovery;
- verification gates;
- evidence gates;
- blocked downstream work;
- cancellation before dispatch;
- cycle rejection;
- duplicate team rejection;
- canonical catalog loading and validation.

Phase completion is only declared after the final main CI run verifies distribution build, isolated wheel installation/import, Ruff, and the complete pytest suite.

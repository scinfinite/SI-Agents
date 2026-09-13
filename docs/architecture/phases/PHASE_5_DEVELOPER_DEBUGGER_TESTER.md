# Phase 5 — Developer / Debugger / Tester

## Status

**Complete — CI verified on 2026-09-10.** Phase 5 completes the Alpha release target (Phases 1–5).

## Objective

Deliver the first real engineering execution loop after the Engineering Brain: inspect, reproduce, diagnose, checkpoint, repair, test, red-team, regress, verify, and document through explicit agent contracts.

## Implemented

- `DebuggerAgent`: reproduction and evidence-backed root-cause handoff.
- `DeveloperAgent`: minimal repair driven by the debugger handoff and protected by the permission engine.
- `TesterAgent`: verification, adversarial/red-team, and regression gates; it cannot declare success without all checks passing.
- `EngineeringWorkflow`: deterministic orchestration of the three agents with task-local context, checkpoints, evidence, and failure propagation.
- Optional Engineering Brain integration validates that the generated plan contains inspect/research/execute/test/verify/document stages before agent execution begins.
- Agent contracts explicitly declare responsibility, deliverables, success criteria, required permissions, and boundaries.
- Adversarial coverage for permission-denial and invalid workflow/agent handoff paths.

## Security and control boundaries

Agents are workers, not policy authorities. Registering or invoking an agent does not grant permissions. Stage entry is checked through `PermissionEngine`; destructive operations remain approval-gated. Code mutation should be performed through the existing orchestrator/tool execution path rather than an agent bypassing policy.

The local command backend remains a development executor, not a security boundary. Untrusted projects must use the isolated execution backend established in the tool-system phase.

## Handoffs

`DebuggerAgent` produces `root_cause` → `DeveloperAgent` consumes it and produces `repair` → `TesterAgent` consumes the repaired state and produces verified/red-team/regression outcomes. Task context is isolated by task ID and the evidence ledger records each gate.

## Alpha acceptance target

The existing broken-project fixture intentionally implements subtraction in `add()`. Phase 5 exercises the failure lifecycle and permission-denial path through deterministic workflow contracts. The workflow is adapter-based so execution can route repairs and tests through `Orchestrator.execute()` and registered tools without creating an alternate permission path.

## Verification standard

Phase 5 is complete only when project installation, distribution build, Ruff, the full pytest suite, and adversarial permission tests pass in GitHub Actions. The latest verified CI run is **#165**, with **108 tests passing**.

## Completion boundary

Phase 5 establishes the first complete controlled engineering workflow. It does not claim reusable skill evolution, broad technical knowledge, technology discovery, open-source intelligence, memory promotion, provider intelligence, automation, or self-improvement; those remain later roadmap phases.

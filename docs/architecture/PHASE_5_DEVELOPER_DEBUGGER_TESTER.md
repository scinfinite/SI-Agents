# Phase 5 — Developer / Debugger / Tester

## Objective

Deliver the first real engineering execution loop after the Engineering Brain: inspect, reproduce, diagnose, checkpoint, repair, test, red-team, regress, verify, and document through explicit agent contracts.

## Implemented

- `DebuggerAgent`: reproduction and evidence-backed root-cause handoff.
- `DeveloperAgent`: minimal repair driven by the debugger handoff and protected by the permission engine.
- `TesterAgent`: verification, adversarial/red-team, and regression gates; it cannot declare success without all checks passing.
- `EngineeringWorkflow`: deterministic orchestration of the three agents with task-local context, checkpoints, evidence, and failure propagation.
- Optional Engineering Brain integration validates that the generated plan contains inspect/research/execute/test/verify/document stages before agent execution begins.
- Agent contracts explicitly declare responsibility, deliverables, success criteria, required permissions, and boundaries.

## Security and control boundaries

Agents are workers, not policy authorities. Registering or invoking an agent does not grant permissions. Stage entry is checked through `PermissionEngine`; destructive operations remain approval-gated. Code mutation should be performed through the existing orchestrator/tool execution path rather than an agent bypassing policy.

The local command backend remains a development executor, not a security boundary. Untrusted projects must use the isolated execution backend established in the tool-system phase.

## Handoffs

`DebuggerAgent` produces `root_cause` → `DeveloperAgent` consumes it and produces `repair` → `TesterAgent` consumes the repaired state and produces verified/red-team/regression outcomes. Task context is isolated by task ID and the evidence ledger records each gate.

## Alpha acceptance target

The existing broken-project fixture intentionally implements subtraction in `add()`. Phase 5 tests exercise the equivalent failure lifecycle and permission-denial path. The workflow itself is adapter-based so production execution can route repairs and tests through `Orchestrator.execute()` and the registered tools.

## Verification standard

Phase 5 is complete only when project installation, distribution build, Ruff, the full pytest suite, and adversarial permission tests pass in GitHub Actions. CI failures must be fixed and rerun before declaring completion.

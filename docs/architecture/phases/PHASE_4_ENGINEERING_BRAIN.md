# Phase 4 — Engineering Brain

## Status

**Complete — CI verified.** Phase 4 is part of the completed Alpha baseline (Phases 1–5).

Phase 4 adds a deterministic reasoning and planning substrate to SI-Agents. It is deliberately separated from model/provider routing: these components represent explicit engineering state and validation, not simulated intelligence.

## Scope

- Problem normalization with task kind, constraints, context, and acceptance criteria.
- Acceptance-criteria-driven task decomposition.
- Dependency-aware plans with inspect → research → execute → test → verify → document stages.
- Topological plan validation with cycle and unknown-dependency rejection.
- Explicit reasoning steps with confidence propagation.
- Falsifiable hypothesis lifecycle and evidence-driven confidence updates.
- Root-cause analysis structures with causal chains, evidence, and alternative-cause tracking.
- Trade-off analysis with explicit options, benefits, costs, risks, scores, and rationale.
- Uncertainty assessment with assumptions and missing-evidence tracking.
- Risk/impact assessment with mitigations.
- Capability-aware planning through the existing capability registry and selector.
- Orchestrator integration through a non-executing `build_plan()` boundary.
- Downstream consumption by the Phase 5 Developer/Debugger/Tester workflow without bypassing execution policy.

## Safety boundaries

The Engineering Brain does not silently execute a plan, grant permissions, bypass approvals, or claim that evidence exists. Execution remains behind the existing permission/tool/execution boundaries. A plan is a proposed sequence until its steps are independently executed and verified.

## Verification

The Phase 4 tests cover decomposition, complete planning, dependency ordering, cycle rejection, hypothesis updates, reasoning confidence, RCA confidence classification, trade-off selection, uncertainty classification, risk classification, and validated capability selection. CI verifies installation, distribution build, Ruff, and the complete pytest suite.

## Current role in the architecture

Phase 4 is the planning/intelligence boundary immediately before controlled engineering execution. Phase 5 consumes its validated plan structure and applies the Developer/Debugger/Tester workflow while preserving task state, permissions, checkpoints, execution records, and evidence.

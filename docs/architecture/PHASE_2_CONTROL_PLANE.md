# Phase 2 — Control Plane

**Status: Complete — historical Phase 2 contract, with current boundary notes.**

> **Current-state note:** SI-Agents has completed **Phases 1–29**. `PHASES.md` is authoritative for current implementation/status, while `SI_AGENTS_V3.md` covers Phases 30–43. This document preserves the Phase 2 contract and incorporates the important execution-boundary material formerly duplicated in `CONTROL_PLANE.md`.

## Objective

Provide a deterministic control plane that can create, schedule, persist, coordinate, authorize, execute, checkpoint, and verify engineering tasks without conflating capability selection with permission to act.

## Implemented

- Task lifecycle: pending, running, succeeded, failed, cancelled.
- Task priority and dependency ordering.
- Retry budget and explicit retry transition.
- Durable JSON task state with atomic replacement.
- Explicit execution lifecycle state and durable execution state storage.
- Task-local context isolation.
- Named agent registration and delegation.
- Dependency-aware workflow execution and cycle detection.
- Detection of tasks blocked by failed or cancelled dependencies.
- Deny-by-default permission evaluation.
- Agent/tool-scoped permission restrictions.
- Separate approval request lifecycle for high-risk actions.
- Capability registry integration and validated-capability selection.
- Command execution correlation with task and execution state.
- Evidence recording for command results.
- Control-plane checkpoints.
- Durable checkpoint metadata.
- Filesystem-backed snapshots and approval-gated restore.

## Execution contract

The verified Phase 2 execution path is:

```text
Task
  → permission decision
  → checkpoint marker
  → task-aware command execution
  → immutable execution record
  → evidence ledger
```

`PermissionEngine` is deny-by-default. Known low-risk capabilities are explicitly configured, repository writes remain denied by default, and high-risk capabilities return `approval_required` until an approval is supplied. Permission evaluation is an application policy layer, not an OS security boundary.

Every command executed through `CommandRunner` is associated with a task ID and records its workspace, command, exit status, output, timeout state, policy decision, and execution identity. The execution record is immutable. The evidence ledger records a verification claim referencing that execution record; failed executions remain failed evidence and are never presented as success.

`CheckpointStore` records an immutable control-plane checkpoint marker. `FilesystemSnapshotStore` provides an actual workspace snapshot and restore mechanism when rollback protection is required. Restore is destructive and therefore requires explicit approval.

A checkpoint marker alone is **not** a rollback guarantee. Callers must create a filesystem snapshot (or a future Git-backed snapshot) before treating a checkpoint as workspace protection.

## Execution backend boundary

`CommandRunner` depends on an `ExecutionBackend`, not a concrete sandbox. `LocalSandbox` is a development executor using the host process environment and `shell=True`; it is not a security boundary. `DockerSandbox` provides a stronger container boundary with disabled networking, dropped Linux capabilities, `no-new-privileges`, a read-only container root filesystem, and resource limits, subject to the Docker daemon and host trust boundary.

The control plane must not silently generalize backend-specific security properties. Untrusted workloads require an actually isolated backend appropriate to the deployment.

## Security boundaries

Capability selection is a planning decision. It does not grant permission. Permission evaluation remains an independent gate, and high-risk actions require explicit approval. Agents and later organization/team layers remain workers rather than policy authorities.

## Alpha integration and later evolution

Phase 2 became the base for the Alpha Developer/Debugger/Tester workflow and all later control-plane evolution. Subsequent phases added skills, evidence, memory, governance, runtime/harness interoperability, organization/catalogs, teams/workflows, OpenCode, OmniRoute, environment runtimes, CLI/setup, handoff, and personas without replacing the core separation between orchestration, execution, authorization, and evidence.

## Verification requirements

Phase 2 was completed only after the relevant CI gates and complete test suite passed. Current CI status for the repository is recorded in `PHASES.md`; this document intentionally does not substitute later CI evidence for the historical Phase 2 record.

## Deliberate non-goals

- A graphical approval UI is outside the core control-plane package.
- Hard preemption of arbitrary running Python callables is not claimed; cancellation is cooperative at the task-control level.
- Distributed scheduling and multi-process locking are future work unless explicitly implemented by a later phase.
- Capability execution authorization remains separate from capability selection.

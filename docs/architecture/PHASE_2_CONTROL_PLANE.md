# Phase 2 — Control Plane

## Status

**Complete — CI verified as part of the Alpha baseline.**

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

## Security boundaries

Capability selection is a planning decision. It does not grant permission. Permission evaluation remains an independent gate, and high-risk actions require explicit approval. The local shell backend is trusted development execution, not a security boundary; isolated execution uses the Docker backend when untrusted code must be contained.

## Verification requirements

Phase 2 is considered complete only when CI verifies build, Ruff, and the complete test suite. The completed Alpha baseline includes coverage for task persistence, dependency scheduling, retries, context isolation, agent delegation, workflow cycle detection, scoped permissions, approvals, execution state persistence, checkpoints, and downstream integration with the tool and agent phases.

## Deliberate non-goals

- A graphical approval UI is outside the core control-plane package.
- Hard preemption of arbitrary running Python callables is not claimed; cancellation is cooperative at the task-control level.
- Distributed scheduling and multi-process locking are future work.
- Capability execution authorization remains separate from capability selection.

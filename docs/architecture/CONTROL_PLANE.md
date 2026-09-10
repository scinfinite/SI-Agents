# Control Plane Execution Contract

## Status

**Phase 2 — Control Plane complete.** This contract remains the authoritative execution and policy boundary for the completed Alpha phases.

The current control plane establishes this verified path:

```text
Task
  -> permission decision
  -> checkpoint marker
  -> task-aware command execution
  -> immutable execution record
  -> evidence ledger
```

## Permission semantics

`PermissionEngine` is deny-by-default. Known low-risk capabilities are explicitly configured, repository writes remain denied, and high-risk capabilities return `approval_required` until an approval is supplied.

The engine is an application policy layer. It is not an OS security boundary.

## Execution records

Every command executed through `CommandRunner` is associated with a task ID and records its workspace, command, exit status, output, timeout state, policy decision, and execution identity. The record is immutable.

The evidence ledger records a verification claim referencing the execution record. Failed executions are recorded as failed evidence rather than being presented as success.

## Checkpoints

`CheckpointStore` records an immutable control-plane checkpoint marker. `FilesystemSnapshotStore` provides an actual workspace snapshot and restore mechanism when rollback protection is required. Restore is a destructive filesystem operation and therefore requires explicit approval.

A checkpoint marker alone is **not** a rollback guarantee. Callers must create a filesystem snapshot (or a future Git-backed snapshot) before treating a checkpoint as workspace protection.

## Execution backend boundary

`CommandRunner` depends on an `ExecutionBackend`, not a concrete sandbox. `LocalSandbox` is a development executor: it uses the host process environment and `shell=True`, so it is not a security boundary. `DockerSandbox` provides a stronger container boundary with disabled networking, dropped Linux capabilities, `no-new-privileges`, a read-only container root filesystem, and resource limits.

The Docker daemon remains a trust boundary. Backend-specific security properties must not be generalized to other execution environments.

## Alpha integration

The control plane is now consumed by the Phase 5 Developer/Debugger/Tester workflow. Agents remain workers: permission evaluation, approvals, execution backends, task state, checkpoints, and evidence remain control-plane responsibilities.

## Alpha fixture

`tests/fixtures/broken_project` is a deterministic intentionally broken project. Its acceptance case is executed by an integration harness so the normal repository test suite remains green while the fixture can demonstrate reproducible failure. The Phase 5 workflow builds on the ordered inspection, reproduction, checkpointing, repair, verification, red-team, and regression stages.

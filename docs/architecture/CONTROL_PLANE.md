# Control Plane Execution Contract

The current Alpha control plane establishes this verified path:

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

The current checkpoint implementation is a control-plane marker only. It does not snapshot, revert, or restore workspace state. Git-backed or filesystem-backed rollback must be implemented separately before checkpoints are described as rollback protection.

## Sandbox boundary

`LocalSandbox` is a development executor. It currently uses the host process environment and `shell=True`; its command policy blocks a small set of obviously destructive prefixes. This is insufficient for untrusted code execution. A production executor must use a real isolation boundary such as a container, VM, or equivalent OS sandbox, with explicit resource and network controls.

## Alpha fixture

`tests/fixtures/broken_project` is a deterministic intentionally broken project. Its acceptance case is executed by an integration harness so the normal repository test suite remains green while the fixture can demonstrate reproducible failure.

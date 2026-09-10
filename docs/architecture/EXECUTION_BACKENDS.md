# Execution Backends

SI-Agents separates task orchestration from command execution through the `ExecutionBackend` contract.

## Backends

- `LocalSandbox`: development executor. It runs on the host and uses `shell=True`; it is **not** a security boundary and must not be used for untrusted code.
- `DockerSandbox`: isolated execution backend for environments with a trusted Docker daemon. It disables networking, drops Linux capabilities, enables `no-new-privileges`, makes the container root filesystem read-only, limits memory/CPU/PIDs, and mounts only the requested workspace.

The Docker daemon is itself a trust boundary. SI-Agents must not describe Docker execution as a complete host-security guarantee, especially when the daemon/socket is controlled by an untrusted party.

## Design rule

`CommandRunner` depends only on `ExecutionBackend`. New backends can therefore be introduced without changing orchestration, task state, or evidence handling.

Before an untrusted workload is executed, the control plane must select an actually isolated backend. A development-only host executor must never be silently upgraded to an isolation guarantee.

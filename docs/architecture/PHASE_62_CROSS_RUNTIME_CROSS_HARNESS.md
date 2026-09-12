# Phase 62 — Cross-Runtime / Cross-Harness

## Status

**Implemented; closure pending final CI.**

Phase 62 establishes a harness-neutral interoperability layer without creating a second execution authority. Existing SI Core remains authoritative for execution, sessions, capabilities, security, evidence, workspaces, evaluation, and continuous improvement.

## Contract

The portable boundary covers the V4 resource families:

- runtime
- session
- tool
- model
- event
- capability
- context
- checkpoint
- artifact

`PortableAdapterDescriptor` and `PortableAdapter` provide a common discovery/health contract. `PortableAdapterRegistry` is deny-by-default, deterministic, and does not grant permissions or mutate state.

Harnesses continue to implement `HarnessAdapter`. `CrossRuntimeGateway` adds the cross-harness authority for:

1. deterministic capability-aware discovery;
2. enabled/disabled harness state;
3. health probing and bounded quarantine/recovery;
4. deterministic preferred-harness selection;
5. streaming capability filtering;
6. project + harness session binding;
7. explicit session migration;
8. safe fallback only when a failure is retryable and no execution-start event was emitted;
9. non-secret routing decisions with bounded retention;
10. fail-closed behavior when no eligible harness exists.

## Security and authority invariants

- Registration and discovery never grant execution capability.
- Disabled or quarantined harnesses are never selected.
- Session identity is bound to both project and harness; cross-project/cross-harness use fails closed.
- Migration is explicit and creates a replacement session; it never silently rewrites an existing session binding.
- Fallback is prohibited after `started`, `delta`, `tool_call`, or `tool_result` events to prevent duplicate side effects.
- Request input is excluded from route-decision fingerprints, preventing arbitrary payloads from entering decision evidence.
- Health failures are bounded and quarantine duration is bounded.
- Transport exceptions are isolated; a failed transport does not become an authorization grant.
- Runtime authorization remains outside the adapter registry/gateway.

## Compatibility

The existing OpenCode bridge, OmniRoute bridge, local harness, runtime engine, session registry, wire protocol, checkpoints, and deployment manifests remain valid. Phase 62 composes with these contracts rather than replacing them.

OpenCode is therefore a supported harness, not the definition of the runtime protocol. Future CLI, IDE, API, embedded, or agent harnesses can implement the same `HarnessAdapter` contract and participate through the gateway without creating parallel SI state ownership.

## Failure model

| Condition | Behavior |
|---|---|
| No enabled harness | fail closed |
| Missing streaming capability | candidate excluded |
| Session project mismatch | reject |
| Session harness mismatch | reject |
| Transport failure before response | try next eligible harness |
| Retryable failure before execution start | safe fallback |
| Retryable failure after execution starts | no fallback |
| Repeated harness failures | degrade, then bounded quarantine |
| Successful health probe | restore healthy state |
| Duplicate portable adapter | reject |

## Verification

Dedicated adversarial coverage is in `tests/unit/test_phase62_cross_runtime.py`, including deterministic discovery, capability filtering, safe/unsafe fallback, quarantine and recovery, session isolation, explicit migration, deny-by-default selection, portable resource-kind coverage, duplicate registration protection, and non-secret decision fingerprints.

Closure requires the normal repository gate: distribution/wheel verification, repository audit, integration verification, Ruff, compileall, full pytest, and final synchronized-tree mainline CI.

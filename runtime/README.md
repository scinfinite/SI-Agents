# Runtime & Harness Interoperability

Phase 17 defines one transport-neutral invocation boundary so CLI, API, IDE, agent, embedded, and future harnesses can share SI-Agents policy and capability semantics without coupling the core to a vendor SDK.

## Boundary

`HarnessAdapter` is an integration boundary, not a policy authority. Registration is explicit and disabled by default. Adapters report capabilities, accept an `InvocationRequest`, return a correlated `InvocationResponse`, and expose cooperative cancellation.

`RuntimeEngine` is the governed entry point. It resolves only enabled adapters, validates optional session identity against both project and harness, checks requested runtime capabilities, evaluates the existing Phase 13 `GovernanceEngine`, invokes the adapter, and validates the returned envelope. Adapter failures are normalized without exposing implementation exception text.

## Interoperability guarantees

- deterministic metadata normalization;
- stable request/response correlation;
- normalized typed events with ordered sequence numbers;
- structured, transport-neutral error categories;
- capability negotiation with fail-closed unsupported features;
- project-scoped, harness-bound sessions;
- explicit harness enablement;
- dependency-free adapter conformance checks;
- no credentials in runtime envelopes or runtime policy;
- a deterministic local reference adapter for testing and development.

Timeouts are a **cooperative contract** at this layer: the request carries a deadline declaration and adapters are responsible for enforcing it without unsafe forced termination. The local adapter detects overrun after the supplied function returns; it is not a hard process-isolation boundary.

## Adapter lifecycle

1. Define immutable metadata and advertised capabilities.
2. Register the adapter explicitly; leave it disabled until trusted configuration enables it.
3. Run the transport-neutral conformance suite.
4. Add transport-specific tests for streaming, timeout enforcement, disconnects, partial output, cancellation races, malformed payloads, and resource cleanup.
5. Route production calls through `RuntimeEngine`, never directly from an untrusted transport.

## Governance and security

Every runtime invocation has a mandatory project identity. The reference local adapter and `RuntimeEngine` both require a `GovernanceRequest`; deny and approval-required decisions do not execute. Phase 13 remains authoritative for security, legal, cost, data-egress, and approval decisions.

Runtime registration and capability negotiation do not grant permissions. Runtime metadata is descriptive only. Adapter exceptions are normalized at the runtime boundary, and credentials must never be placed in metadata, input, output, errors, or policy files.

The local adapter is a reference implementation, not a host security boundary. External runtimes retain their own isolation properties and remain subject to SI-Agents governance.

## Conformance

`run_conformance` verifies request correlation, terminal status, response shape, and cancellation when the adapter advertises cancellation. Conformance is intentionally transport-neutral; adapter implementations must add tests for protocol-specific behavior before production use.

## Scope discipline

Phase 17 does not add OpenCode, Codex, Claude, Cline, MCP, or other vendor SDK dependencies, and it does not add paid runtime services. Those can be integrated later through adapters that implement the same contract and preserve governance and project isolation.

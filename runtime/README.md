# Runtime & Harness Interoperability

Phase 17 defines one transport-neutral invocation boundary so CLI, API, IDE, agent, embedded, and future harnesses can share SI-Agents policy and capability semantics without coupling the core to a vendor SDK.

## Boundary

`HarnessAdapter` is an integration boundary, not a policy authority. Registration is explicit and disabled by default. Adapters report capabilities, accept an `InvocationRequest`, return a correlated `InvocationResponse`, and expose cooperative cancellation.

`RuntimeEngine` is the governed entry point. It resolves only enabled adapters, validates session identity against project and harness, checks requested runtime capabilities, evaluates the existing governance engine, invokes the adapter, and validates the returned envelope.

## Interoperability guarantees

- deterministic metadata normalization;
- stable request/response correlation;
- normalized typed events with ordered sequence numbers;
- structured transport-neutral errors;
- capability negotiation with fail-closed unsupported features;
- project-scoped, harness-bound sessions;
- explicit harness enablement;
- dependency-free adapter conformance checks;
- no credentials in runtime envelopes or runtime policy;
- a deterministic local reference adapter for testing/development.

Timeouts are a cooperative contract. The local adapter is not a hard process-isolation boundary.

## Adapter lifecycle

1. Define immutable metadata and advertised capabilities.
2. Register explicitly and leave disabled until trusted configuration enables it.
3. Run the transport-neutral conformance suite.
4. Add transport-specific tests for streaming, timeouts, disconnects, partial output, cancellation races, malformed payloads, and cleanup.
5. Route production calls through `RuntimeEngine`, never directly from an untrusted transport.

## Governance and security

Every runtime invocation has a mandatory project identity. Runtime and reference-adapter governance checks prevent deny/approval-required execution. Runtime registration and capability negotiation do not grant permissions. Credentials must never be placed in metadata, input, output, errors, or policy files.

OpenCode is a supported harness adapter, while OmniRoute remains the model/provider routing authority. Termux and Codespaces are environment profiles, not policy authorities.

## Current v3 boundary

Phase 29 personas are compiled above the organization/runtime layer; Phase 30 Skills will be composed above this boundary without changing the transport authority. Future Control API, Web, and TUI surfaces must all use the same runtime/governance contracts rather than duplicating them.

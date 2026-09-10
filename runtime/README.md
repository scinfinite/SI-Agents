# Runtime & Harness Interoperability

Phase 17 defines one transport-neutral invocation envelope so CLI, API, IDE, agent, embedded, and future harnesses can share SI-Agents policy and capability semantics.

## Boundary

`HarnessAdapter` is an integration boundary, not a policy authority. Registration is explicit and disabled by default. Adapters report capabilities, accept an `InvocationRequest`, return a correlated `InvocationResponse`, and expose cancellation.

Every invocation carries a project identity and must carry a `GovernanceRequest` before the reference local adapter executes it. Governance remains the Phase 13 authority; adapters cannot grant permissions by themselves.

## Interoperability guarantees

- deterministic metadata normalization;
- request/response correlation;
- normalized typed events and structured errors;
- explicit capability negotiation for streaming;
- project-scoped sessions;
- explicit harness enablement;
- conformance checks independent of transport;
- no credentials in runtime policy or envelopes;
- dependency-free local reference implementation.

External runtimes such as OpenCode, Codex, Claude Code, Cline, Termux, and Codespaces are integration targets, not implicit dependencies. A future adapter must pass the conformance suite and preserve governance, project isolation, and error semantics.

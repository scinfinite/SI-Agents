# Phase 17 — Harness & Runtime Interoperability

## Objective

Make SI-Agents independent of any single developer harness while preserving the existing control-plane, capability, governance, project-isolation, and verification boundaries.

## Architecture

```text
CLI / API / IDE / Agent / Embedded harness
                 |
          HarnessAdapter
                 |
       Invocation envelope
                 |
           RuntimeEngine
                 |
     SI-Agents capability core
                 |
 Governance -> execution -> evidence
```

The adapter is deliberately thin. It translates transport concerns; it does not decide authorization, bypass governance, or silently add capabilities. `RuntimeEngine` is the governed entry point that composes registry, session isolation, capability negotiation, governance, adapter invocation, and response validation.

## Contract

`InvocationRequest` contains a stable request ID, mandatory project ID, optional session ID, capability ID, input, normalized metadata, governance request, cooperative timeout declaration, and streaming preference. `InvocationResponse` preserves request correlation and exposes a terminal status, normalized events, structured error, and non-negative integer usage metadata.

`RuntimeCapabilities` advertises optional streaming, cancellation, tool-call, structured-output, and session-continuity features. Unsupported requested features fail closed.

`RuntimeEvent` gives all transports a common event vocabulary and ordered sequence requirement. `RuntimeError` gives callers stable error categories without exposing transport implementation details. Metadata and usage keys are unique and non-empty.

## Governance and security

`RuntimeEngine` evaluates the existing Phase 13 `GovernanceEngine` before adapter execution. The reference local adapter repeats the governance check as defense in depth. Deny and approval-required decisions do not execute.

Runtime configuration contains no secrets. Harness registration is explicit and disabled by default. Project identity is mandatory on invocations and sessions. A session is bound immutably to both project and harness; cross-project or cross-harness reuse fails closed.

Adapter exceptions are normalized to a generic execution error at the engine boundary so transport internals are not exposed. Runtime envelopes must not carry credentials. The local adapter is a reference implementation, not a host security boundary.

Timeouts are cooperative: the request declares a limit and an adapter must enforce it safely. The local reference adapter can detect an overrun after its synchronous function returns, but it cannot forcibly terminate arbitrary Python code and therefore does not claim hard timeout or isolation guarantees.

## Conformance

`run_conformance` checks correlation, terminal status, response shape, and cancellation when advertised. The test suite additionally covers disabled harnesses, duplicate registration, project/session isolation, closed sessions, governance ordering, malformed responses, adapter exception normalization, cancellation, cooperative timeout behavior, unsupported streaming, runtime-checkable protocol conformance, and envelope validation.

Production adapters must add transport-specific tests for disconnects, partial output, duplicate events, streaming backpressure, cancellation races, deadline enforcement, resource cleanup, and credential redaction.

## Scope discipline

Phase 17 intentionally does not add OpenCode, Codex, Claude, Cline, MCP, or other vendor SDK dependencies or paid runtime services. Those are future adapters. The core contracts remain dependency-free so interoperability can be added without coupling the platform to a vendor.

## Acceptance criteria

- [x] typed transport-neutral request/response envelope;
- [x] runtime and harness capability negotiation;
- [x] normalized events and structured errors;
- [x] project/harness session isolation;
- [x] explicit disabled-by-default registry;
- [x] governed local reference adapter;
- [x] centralized runtime engine;
- [x] adapter conformance suite;
- [x] adversarial governance/unsupported-capability/isolation tests;
- [x] cooperative timeout and cancellation contracts;
- [x] runtime policy and architecture documentation;
- [x] CI build, lint, and full test verification on the final phase head.

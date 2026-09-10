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
     SI-Agents capability core
                 |
 Governance -> execution -> evidence
```

The adapter is deliberately thin. It translates transport concerns; it does not decide authorization, bypass governance, or silently add capabilities.

## Contract

`InvocationRequest` contains a stable request ID, project ID, optional session ID, capability ID, input, metadata, governance request, timeout declaration, and streaming preference. `InvocationResponse` preserves request correlation and exposes a terminal status, normalized events, structured error, and integer usage metadata.

`RuntimeCapabilities` advertises optional streaming, cancellation, tool-call, structured-output, and session-continuity features. Unsupported requested features fail closed.

`RuntimeEvent` gives all transports a common event vocabulary and monotonic sequence requirement. `RuntimeError` gives callers stable error categories without leaking transport implementation details.

## Governance and security

The reference local adapter requires a governance request and evaluates it through the existing `GovernanceEngine`. Deny and approval-required decisions do not execute. This preserves Phase 13 as the authoritative policy boundary.

Runtime configuration contains no secrets. Harness registration is explicit and disabled by default. Project identity is mandatory on invocations and sessions. Runtime metadata is normalized but must not be used to transport credentials.

The local adapter is a reference implementation, not a host security boundary. External runtimes remain subject to their own isolation guarantees and to SI-Agents governance.

## Conformance

New adapters should run `run_conformance` and add transport-specific tests. The conformance suite checks correlation, terminal status, and cancellation. Additional adapter-specific suites should cover streaming, timeout semantics, malformed input, disconnects, duplicate events, partial output, and cancellation races before production use.

## Scope discipline

Phase 17 intentionally does not add OpenCode/Codex/Claude/Cline SDK dependencies or paid runtime services. Those are future adapters. The core contracts are dependency-free so interoperability can be added without coupling the platform to a vendor.

## Acceptance criteria

- [x] typed transport-neutral request/response envelope;
- [x] runtime and harness capability negotiation;
- [x] normalized events and structured errors;
- [x] session/project isolation;
- [x] explicit disabled-by-default registry;
- [x] governed local reference adapter;
- [x] adapter conformance suite;
- [x] adversarial governance/unsupported-capability tests;
- [x] runtime policy and architecture documentation;
- [x] CI build, lint, and full test verification.

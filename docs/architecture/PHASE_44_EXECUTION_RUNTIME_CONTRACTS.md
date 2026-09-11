# Phase 44 — Execution Runtime Contract Freeze

**Status:** Frozen for implementation review
**Baseline:** `main` at `b2517d9c5f2fc9cd068c50911bcc4decd10bf280`
**Scope:** Execution Runtime only; no Phase 44 implementation is authorized by this document.

## 1. Preflight decision

The V4 preflight is complete at the contract-review level. The Phase 44 runtime must be built on the existing V3 authority, provenance, governance, Control API, adapter, and routing boundaries rather than replacing them.

The repository baseline also exposes a CI caveat: the latest observed workflow run (`34602495330`) must be treated as a non-green verification gate until its final status is rechecked after this documentation change. A Phase 44 implementation must not be declared complete while the main-branch CI gate is red or indeterminate.

## 2. Boundary freeze

### 2.1 Control plane remains authoritative

The Control API and existing governance layer remain authoritative for:

- authenticated caller identity and authorization;
- task/execution admission and policy decisions;
- authority scope and delegated authority;
- provenance requirements and lineage;
- approval/denial decisions;
- governance/audit records;
- externally visible control intent.

The Execution Runtime **must not** invent, widen, or silently override authority, provenance, or governance decisions.

### 2.2 Execution Runtime owns mechanics

The runtime owns only execution mechanics after an authorized execution has been admitted:

- materializing an execution attempt;
- invoking an execution adapter;
- consuming adapter events/streams;
- enforcing runtime-level deadlines and cancellation once authorized;
- normalizing execution outcomes;
- maintaining execution state transitions;
- emitting runtime telemetry and immutable execution evidence.

The runtime is not a policy engine, identity provider, model router, or source-of-truth for authority.

### 2.3 Provider/router boundary

OmniRoute/provider routing remains a downstream selection/invocation concern. Routing may select an eligible provider/model according to the already-authorized request, but it cannot grant authority, change provenance requirements, or bypass governance.

## 3. Canonical identifiers

Every runtime execution must preserve the caller-supplied or Control-API-issued identity chain:

`task_id -> execution_id -> attempt_id`

The runtime may add internal correlation identifiers, but must never replace the canonical chain or create an unrelated execution identity.

Retries create a new `attempt_id` under the same `execution_id` unless the Control API explicitly requests a new execution.

## 4. Execution state machine

The canonical lifecycle is:

`accepted -> queued -> running -> {succeeded | failed | cancelled | expired}`

Additional implementation states are allowed only when they are explicitly documented as internal states and map deterministically to the canonical lifecycle.

`accepted` is an admission result, not proof that execution has started.

`cancelled` means cancellation was accepted and the runtime has terminated or is terminating the associated work according to the adapter contract; it must not be reported as `succeeded`.

`expired` is reserved for deadline/TTL termination and must remain distinguishable from ordinary failure.

## 5. Control operations

The runtime-facing control surface must be idempotent by canonical execution identity and operation key.

Required operation semantics:

- **start/dispatch:** execute only an admitted execution;
- **cancel:** safe to repeat; once terminal, it is a no-op with the existing terminal result preserved;
- **pause/resume:** capability-gated. The runtime must report unsupported rather than emulate or silently ignore a requested control operation when the active adapter cannot safely honor it;
- **retry:** creates a new attempt under the existing execution unless policy explicitly denies retry.

Control operations are intents. They do not themselves rewrite provenance or authorization records.

## 6. Adapter contract

Adapters are the only runtime boundary allowed to translate a canonical execution into provider/tool-specific invocation semantics.

An adapter must expose, directly or through a stable wrapper:

1. capability discovery;
2. invocation/start;
3. event/stream consumption;
4. cancellation;
5. normalized terminal result;
6. normalized error classification.

Provider-specific payloads, headers, session identifiers, and transport details must remain inside the adapter boundary.

## 7. OpenCode contract

The OpenCode integration must remain a protocol adapter, not a second control plane.

The integration must:

- preserve the canonical `task_id/execution_id/attempt_id` chain in correlation metadata;
- translate Control-API-approved work into the currently supported OpenCode invocation protocol;
- normalize OpenCode session/message/stream/error events into runtime events;
- keep OpenCode-specific identifiers internal to the adapter unless explicitly required for provenance;
- never treat OpenCode session state as the authoritative SI-Agents execution state.

Protocol evolution must be isolated behind the adapter. The runtime contract is not allowed to depend on undocumented OpenCode internals.

## 8. OmniRoute contract

OmniRoute remains a downstream routing/provider interface.

The runtime must submit only the already-authorized execution envelope. It must not embed provider-selection policy that conflicts with existing routing/governance contracts.

The OmniRoute integration must normalize:

- selected provider/model identity;
- upstream request/response correlation;
- streaming chunks/events;
- rate-limit and transient failures;
- terminal provider failures.

A routing fallback is an implementation detail of the attempt unless governance/provenance policy requires it to become an externally recorded decision; in that case the decision must be emitted through the existing provenance/audit boundary rather than silently changing the authority record.

## 9. Event and provenance contract

Runtime events are append-only evidence. They must be:

- correlated to the canonical execution chain;
- ordered by a monotonic event sequence within an execution/attempt;
- timestamped;
- typed with a stable event type;
- safe to replay without changing authoritative state;
- explicit about terminality.

The runtime must never mutate historical provenance events to make a later outcome appear authoritative.

At minimum, the contract reserves event categories for admission, dispatch, start, output/stream, control request/result, retry/attempt, error, and terminal outcome.

## 10. Idempotency and retries

Duplicate delivery is expected at control and transport boundaries.

The runtime must make these operations idempotent where the contract says they are idempotent and must not accidentally execute the same attempt twice because of a duplicated control request.

Retries must preserve the original execution lineage and must be distinguishable by `attempt_id`. A retry must never erase or overwrite the evidence for the failed attempt.

## 11. Cancellation and deadlines

Cancellation is cooperative first and forceful only where the adapter/runtime can guarantee safe termination semantics.

A deadline is an execution constraint, not an authorization change. Deadline expiry must produce an `expired` terminal outcome and preserve the relevant partial evidence.

The runtime must not claim that downstream work stopped unless the adapter has supplied sufficient evidence for that claim.

## 12. Streaming contract

Streaming output is incremental evidence, not a replacement for the terminal result.

The runtime must preserve ordering and correlation for stream events and must emit exactly one canonical terminal outcome per attempt.

A disconnected stream must be classified as a transport/runtime condition; it must not be silently converted into successful completion.

## 13. Error contract

Errors must retain enough information to distinguish at least:

- authorization/admission rejection;
- invalid execution request;
- adapter/protocol error;
- provider/routing error;
- transient/retryable failure;
- cancellation;
- deadline expiry;
- internal runtime failure.

The runtime must not downgrade an authorization or governance failure into a retryable provider failure.

## 14. Security and secrets

Secrets remain owned by the existing credential/configuration boundary. Runtime events, provenance, and logs must not persist raw credentials, authorization tokens, or provider secrets.

Adapters may receive credentials needed for invocation, but those credentials must not cross into canonical runtime event payloads.

## 15. Compatibility requirements

Phase 44 implementation must preserve existing V3 contracts unless an explicit V4 migration contract is added and approved.

In particular, implementation must not:

- replace the Control API as the authority boundary;
- bypass existing governance checks;
- rewrite provenance semantics;
- make provider routing authoritative;
- couple core runtime state to OpenCode-specific internals;
- couple core runtime state to OmniRoute-specific transport details;
- remove or weaken existing audit evidence.

## 16. Test and verification gates

Before Phase 44 can be declared complete, CI must prove at minimum:

1. existing V3 tests remain green;
2. runtime state-machine tests cover every canonical transition and illegal transition;
3. idempotency tests cover duplicate control delivery;
4. retry tests prove lineage preservation;
5. cancellation/deadline tests prove terminal-state correctness;
6. streaming tests prove ordering and single terminal outcome;
7. adapter contract tests cover OpenCode and OmniRoute normalization;
8. provenance tests prove append-only evidence and authority preservation;
9. secret-redaction tests cover runtime events/logs;
10. full repository CI is green on the final Phase 44 commit.

## 17. Freeze rule

This document is the Phase 44 contract boundary. Implementation may proceed only after review of these contracts. Changes to canonical identifiers, authority ownership, lifecycle semantics, provenance rules, adapter boundaries, or terminal outcome semantics require an explicit contract revision before implementation changes are merged.

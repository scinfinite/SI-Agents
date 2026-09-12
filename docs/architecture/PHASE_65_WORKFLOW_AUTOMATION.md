# Phase 65 — Workflow + Automation

## Status

**Complete.** Phase 65 is implemented, audited, tested, documented, and verified on `main` by the repository-wide CI gate. The final synchronized documentation tree is subject to the same exact-tree mainline CI rule.

## Scope

Phase 65 adds a transport-neutral workflow state machine for declarative automation. SI Core remains the authority for authorization, execution governance, persistence policy, and evidence; workflow adapters never grant capabilities themselves.

## Contracts

`core/automation/workflows.py` provides:

- versioned workflow definitions with deterministic SHA-256 fingerprints;
- DAG dependency validation with cycle rejection and bounded step counts;
- task, condition, wait, human approval, fan-out, loop, delegation, and compensation steps;
- manual, event, webhook, and interval triggers;
- durable JSON checkpoints with atomic replacement and restart/load validation;
- explicit adapter registration for actions, conditions, and delegates;
- bounded payloads, fan-out, loop iterations, retries, run retention, and runtime;
- fail-closed missing adapters/conditions and bounded cancellation errors;
- request-fingerprint-bound idempotency, including conflicting-key rejection;
- durable wait expiry and explicit human-gate approval before continuation;
- reverse-order compensation for completed compensatable steps.

### Adapter boundary

Persisted definitions and runs contain only JSON-safe values. Python callables are registered at process startup and are intentionally not serialized. A restarted process must re-register the adapters required by a workflow before execution can continue.

### Branching

A condition that evaluates false becomes `skipped`. A dependent step is also skipped, preventing accidental execution of a false branch. Executable steps may additionally declare a condition predicate; a false predicate skips that step and its dependent branch. Loop conditions are termination predicates evaluated after each bounded iteration.

### Waiting and approval

A wait stores an absolute `wait_until` timestamp. Restarting before expiry keeps the run waiting; after expiry the wait is completed and execution continues. Human steps remain waiting until the required approval variable is explicitly `True` and `resume()` is invoked.

### Scheduling and events

`due_intervals()` exposes interval definitions that are due according to the latest run timestamp. `trigger_intervals()` atomically creates the due runs. `event()` and `webhook()` provide separate trigger namespaces so an event cannot accidentally activate a webhook definition.

## Security and reliability invariants

- No workflow API bypasses SI Core capability authorization.
- Input and persisted state are bounded to prevent unbounded memory/disk growth.
- Idempotency is atomic under the engine lock and is bound to a request fingerprint.
- Invalid or corrupt persisted state fails closed rather than being silently repaired.
- Adapter failures are captured as run failures and invoke registered compensation in reverse completion order.
- Runtime expiry is a terminal failure and cannot be bypassed by a wait/resume cycle.
- Version identity is immutable after registration; a new definition requires a new version.
- Loop execution is bounded and its termination predicate is never used as a pre-execution branch condition.

## Verification

`tests/unit/test_phase65_workflows.py` provides acceptance and adversarial coverage for DAG branching, durable waits, human gates, fan-out/loops, event/webhook/interval triggers, retry behavior, runtime expiry, concurrent idempotency, cancellation, persistence corruption, templates/versioning, payload limits, and compensation.

The implementation-tree closure run **CI #1239 / `34697885027`** passed distribution build, wheel installation, repository audit, integration verification, Ruff, and the full pytest suite. The subsequent synchronized documentation tree is validated by the final exact-tree mainline CI gate.

## References

The implementation follows the repository's standing engineering-reference policy: current ECC and Agency Agents patterns are used only as generalized guidance for bounded workflows, explicit deliverables, security boundaries, and validation; no external project implementation or prompt is copied as an authority.

## Closure rule

Phase 65 is complete only when implementation, unit/integration tests, adversarial/security tests, edge/failure tests, documentation synchronization, repository audit, distribution/wheel verification, integration verification, Ruff, compileall, full pytest, and final exact-tree mainline CI are green.

# Phase 15 — Automation

## Goal

Provide a dependency-free automation layer for scheduled engineering work without creating a second control plane or bypassing governance.

## Delivered

- Typed one-shot and recurring schedules with timezone-aware timestamps.
- Deterministic due-job selection and interval catch-up without schedule drift.
- Explicit job lifecycle: enabled, paused, cancelled; one-shot jobs become cancelled after triggering.
- Registered-action execution contract; unknown actions fail closed.
- Preconditions/conditional triggers that can skip work without executing it.
- Retry policy with bounded exponential backoff and injected sleeping for deterministic tests.
- Idempotency keys that prevent duplicate successful execution.
- Governance evaluation before every action, including paid-resource and sensitive-egress controls.
- Run history with status, attempts, timing, idempotency key, and governance decision status.
- Dependency-free JSON persistence for job definitions and run records.
- Automation policy configuration covering scheduling, retries, safety, and persistence.

## Architecture

`AutomationRegistry` stores declarative jobs. `AutomationScheduler` selects due work and advances schedules. `AutomationRunner` executes only registered actions, checks optional preconditions, evaluates `GovernanceEngine`, retries failures, and records immutable run results. `AutomationStore` persists definitions/history without credentials.

The scheduler never executes an action. The runner never bypasses governance. Automation is therefore an execution mechanism, not a policy authority.

## Safety invariants

1. Missing actions never execute.
2. Governance denial never executes.
3. Approval-required work never executes without an approved governance request.
4. Paid resources remain subject to Phase 13 approval controls.
5. Sensitive/confidential egress remains subject to governance.
6. Idempotency can prevent duplicate successful runs.
7. Retry attempts are bounded and backoff is capped.
8. Cancelled jobs cannot silently resume.
9. Secrets are not part of the automation model or configuration.
10. Persistence stores definitions and evidence, not credentials.

## Deliberate non-goals

No hosted scheduler, paid queue, external credential store, autonomous publication, or arbitrary shell execution is introduced. Integrations can be added through explicitly registered actions and existing SI-Agents tool/governance boundaries.

## Verification

The Phase 15 suite covers lifecycle, duplicate registration, deterministic scheduling, invalid schedules/retries, retry exhaustion/backoff, idempotency, preconditions, paid-resource approval, sensitive-data egress, persistence round trips, and malformed persistence input. Completion requires the repository CI workflow to pass on the final Phase 15 commit.

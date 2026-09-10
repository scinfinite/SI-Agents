# Phase 31 — Rules, Hooks & Events

**Status:** Complete pending final mainline CI evidence  
**Scope:** explicit policy/event layer spanning agents, Skills, tools, workflows, runtime, handoffs, and verification

## Delivered

Phase 31 adds a deterministic, inspectable Rules/Hooks/Events layer without creating a second authorization system or an unrestricted command-hook mechanism.

### Event contract

`core/events/` provides:

- a version-neutral immutable `Event` envelope;
- a canonical vocabulary including `session.created`, `session.closed`, `task.started`, `task.completed`, `task.failed`, `agent.selected`, `skill.started`, `skill.completed`, `tool.before`, `tool.after`, `handoff.created`, `verification.started`, and `verification.failed`;
- source, subject, correlation, timestamp, and sanitized payload fields;
- secret-like payload-key redaction;
- payload size and nesting bounds;
- a bounded append-only in-process `EventStore`;
- `EventBus` dispatch that evaluates Rules before Hooks and records every published event.

### Rule contract

`core/rules/` provides declarative `Rule`, `RuleMatch`, and `RuleEffect` types, an explicit duplicate-rejecting registry, deterministic priority ordering, and a fail-closed evaluator.

Rules use exact event/source/subject/payload predicates only. They do not execute expressions, import code, run commands, or grant permissions. Effects are `allow`, `deny`, `require_approval`, and `audit`.

The canonical `config/rules.v1.json` catalog currently requires approval for dangerous tool operations, credential-related tool operations, publication operations, and destructive handoffs. Dangerous events with no matching rule fail closed.

### Hook contract

`core/hooks/` provides explicit in-process hook registration with:

- `before` and `after` lifecycle phases;
- deterministic priority ordering;
- observer hooks and explicit gate hooks;
- a bounded per-event registration limit;
- per-hook runtime budgets;
- fail-closed gate-hook failures;
- no shell, subprocess, command-string, dynamic-import, or arbitrary-execution hook surface.

Observer failures are retained in the dispatch report without silently turning observers into policy authorities.

### Skill/runtime integration

`SkillExecutor` now emits `skill.started`, `verification.started`, `verification.failed`, `skill.completed`, and failure telemetry through the EventBus when one is supplied. Skill selection and event registration remain separate from permission evaluation.

### Governance boundary

Rules and Hooks are policy-aware controls around the existing SI governance/permission layers. They do not replace `PermissionEngine` or `GovernanceEngine`, and they never grant capabilities, tools, credentials, network access, or execution authority.

Approval-bearing events require an explicit `approval_granted` signal at dispatch time; a Rule cannot manufacture approval.

## Security / adversarial coverage

Tests cover:

- secret-like event payload redaction;
- unsupported event payload rejection;
- duplicate Rule registration;
- deterministic catalog loading;
- fail-closed dangerous-event behavior;
- approval-gated dangerous operations;
- deterministic hook ordering;
- observer failure isolation;
- gate-hook denial;
- gate-hook fail-closed behavior;
- bounded event storage.

## External pattern review

Current ECC guidance was reviewed for matcher-specific hooks, explicit runtime profiles, actionable hook failures, and rules that remain separate from executable authority. Current Agency Agents guidance was reviewed for explicit lifecycle state, continuous QA loops, evidence-based phase gates, reuse-before-creation, and fail-path handling. SI-Agents independently implements these ideas under its existing typed governance and local-first architecture rather than copying external code or prompts.

## Verification requirements

The Phase 31 gate requires:

- typed event vocabulary and bounded immutable envelopes;
- explicit Rule registration and deterministic evaluation;
- safe declarative Rule loading;
- explicit Hook registration and bounded execution;
- fail-closed dangerous-operation handling;
- Skill event integration;
- regression and adversarial tests;
- distribution/package coverage;
- Ruff and complete pytest;
- documentation/source-of-truth synchronization;
- successful final mainline CI.

## Exit gate

Phase 32 may begin only after final mainline CI is green and current documentation reports the verified Rules/Hooks/Events contract and safety boundaries.

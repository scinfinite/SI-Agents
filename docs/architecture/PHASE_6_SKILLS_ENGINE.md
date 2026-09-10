# Phase 6 — Skills Engine

## Status

**Complete — CI-verified.**

## Objective

Provide reusable, explicit, verifiable engineering procedures that can be selected and executed without turning a skill definition into an implicit permission grant.

## Implemented

- Immutable `Skill` contract describing identity, category, procedure, inputs, outputs, tools, permissions, safety constraints, verification, failure handling, success criteria, lifecycle status, and version.
- `SkillStatus` lifecycle: experimental, validated, deprecated, blocked.
- `SkillRegistry` with duplicate protection, category/status lookup, and validated-only selection.
- `SkillExecutor` with input/output validation, permission enforcement, blocked/deprecated rejection, explicit verifier requirement, and evidence recording.
- Failed skill execution and failed verification are recorded as failed evidence.
- Orchestrator integration for registration, selection, and execution.
- Initial validated engineering skill catalog covering repository inspection, failure reproduction, and change verification.
- Unit tests covering lifecycle invariants, duplicate registration, missing inputs, permission denial, explicit verification, successful evidence, and fail-closed verification.

## Execution contract

A skill is a reusable procedure, not an autonomous authority:

```text
select skill
  -> validate lifecycle status
  -> validate declared inputs
  -> enforce required permissions
  -> execute injected procedure
  -> validate declared outputs
  -> require explicit verification
  -> record evidence
  -> return success/failure
```

Registration and selection do **not** grant permissions. The permission engine remains authoritative and approval-gated capabilities remain approval-gated.

## Verification and safety

A validated skill must declare verification criteria and failure handling. Execution cannot be reported as successful without an explicit verifier. External content and tool output remain untrusted input, and skills requiring execution use the existing permission/tool/execution boundaries.

The skill executor deliberately does not interpret procedure prose as executable code. Executable behavior is supplied through an injected handler, keeping the skill definition auditable and preventing a metadata file from silently acquiring execution authority.

## Initial catalog

`skills/registry.yaml` records the first reusable engineering procedures. It is descriptive metadata and is intentionally not an implicit code loader. Runtime registration remains explicit through `SkillRegistry`.

## Non-goals

- Model-driven autonomous skill generation.
- Uncontrolled skill mutation or self-improvement.
- Implicit permission escalation.
- Dynamic execution of arbitrary procedure text.
- Global promotion of project-specific skills without evidence and validation.

## Acceptance criteria

Phase 6 is complete only when skill contracts, registry, selection, execution, permission boundaries, evidence recording, initial catalog, tests, documentation, distribution build, Ruff, and the complete CI test suite are passing.

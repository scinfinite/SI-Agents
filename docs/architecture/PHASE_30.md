# Phase 30 — Portable Skills

**Status:** Complete + CI verified  
**Scope:** first-class portable `SKILL.md` artifacts

Phase 30 establishes Skills as portable, inspectable data artifacts that sit between agent definitions and governed execution.

## Delivered

Every canonical Skill uses `si-agents.skill.v1` and declares identity/version, purpose, inputs/outputs, prerequisites, workflow, tools, requested capabilities/permissions, verification, failure behavior, evidence, examples, compatibility, provenance, optional dependencies, and lifecycle status.

`skills/**/SKILL.md` is authoritative. Discovery indexes do not grant authority.

```text
SKILL.md
   ↓
Deterministic parser
   ↓
Typed Skill
   ↓
Validation / registry
   ↓
Selection / composition
   ↓
Governance permission check
   ↓
Execution handler
   ↓
Verification + evidence
```

Selecting, importing, registering, or composing a Skill never grants permissions, tools, credentials, network access, or execution authority. The parser rejects authority-bearing frontmatter; execution requires explicit permission evaluation and verification. Composition validates dependencies and rejects cycles. Artifact tooling computes SHA-256 digests.

## Canonical Skills

1. `inspect-repository`
2. `reproduce-failure`
3. `verify-change`
4. `plan-minimal-change`
5. `security-review`
6. `compose-workflow`

## Verification evidence

The Phase 30 acceptance suite covered parsing, validation, deterministic registry discovery/selection, duplicate and malformed input rejection, authority-bearing input rejection, dependency resolution/cycle rejection, stable artifact digests, explicit permission/verification enforcement, failure/evidence behavior, packaging, CLI smoke checks, Ruff, and complete pytest.

PR #17 was merged to `main` as commit `62972acf20a0da53bf81161c2108a506dbdad907`. Mainline CI run **#727** completed successfully, satisfying the Phase 30 exit gate.

Phase 31 builds on this verified Skill boundary rather than replacing or duplicating it.

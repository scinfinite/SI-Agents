# Phase 30 — Portable Skills

**Status:** Complete pending final CI evidence  
**Scope:** first-class portable `SKILL.md` artifacts

## Delivered

Phase 30 establishes Skills as portable, inspectable data artifacts that sit between agent definitions and governed execution.

### Contract

Every canonical Skill uses `si-agents.skill.v1` and declares:

- identity, semantic version, category, and purpose;
- inputs and outputs;
- prerequisites and deterministic workflow;
- tools;
- requested capabilities and permissions;
- verification and failure behavior;
- evidence requirements;
- examples;
- compatibility requirements;
- provenance;
- optional Skill dependencies;
- lifecycle status.

### Source of truth

`skills/**/SKILL.md` is authoritative. `skills/index.json` and `skills/registry.yaml` are discovery indexes and do not grant authority.

### Runtime model

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

Selecting, importing, registering, or composing a Skill never grants permissions, tools, credentials, network access, or execution authority.

### Safety boundaries

The parser rejects authority-bearing frontmatter such as execution, shell, network, credential, secret, and installation fields. Skill execution requires explicit permission evaluation and an explicit verifier. Blocked/deprecated Skills cannot execute. Missing outputs, failed verification, and handler failures remain failures.

Skill composition validates dependencies and rejects cycles. Artifact tooling computes SHA-256 digests so deployment and verification layers can identify exact Skill content.

### Canonical Skills

The initial SI-native library contains six validated Skills:

1. `inspect-repository`
2. `reproduce-failure`
3. `verify-change`
4. `plan-minimal-change`
5. `security-review`
6. `compose-workflow`

They are deliberately procedural and reusable rather than copies of any external persona corpus.

## Verification requirements

The Phase 30 gate requires:

- every canonical `SKILL.md` parses;
- every Skill validates;
- deterministic registry discovery and selection;
- duplicate rejection;
- malformed and dangerous-input rejection;
- dependency resolution and cycle rejection;
- stable artifact digest generation;
- explicit permission enforcement;
- explicit verification enforcement;
- failure/evidence behavior coverage;
- wheel packaging and installed CLI smoke tests;
- Ruff and complete pytest;
- current documentation synchronized with implementation.

## Exit gate

Phase 31 may begin only after final mainline CI is green and the current repository documentation reports the verified Skill inventory and safety model.

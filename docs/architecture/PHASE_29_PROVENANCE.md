# Phase 29 Provenance Record

## External references inspected

### ECC — `affaan-m/ECC`

Observed useful general patterns in the current repository: specialist agent roles, skills-first reusable engineering procedures, explicit verification/review loops, memory/learning as structured engineering support, and security scanning around agent assets. ECC also distinguishes harness-specific integration concerns from reusable engineering content.

Application to SI-Agents: these ideas informed the decision to make persona files human-readable and specialist-oriented while keeping execution, governance, and harness boundaries in SI typed contracts.

### Agency Agents — `msitarzewski/agency-agents`

Observed useful general patterns in the current repository: each specialist is represented as a readable Markdown artifact with identity/personality, mission, workflow, deliverables, and success-oriented behavior, organized by division/domain.

Application to SI-Agents: these ideas informed the persona section structure and division-oriented file organization, but SI-Agents adds deterministic parsing, typed compilation, governance preservation, validation, provenance, and fail-closed handling.

## Independent design decisions

1. Markdown is a human-authored behavioral representation, not executable configuration.
2. A small deterministic parser avoids making a third-party YAML dependency part of the core contract.
3. Privilege-bearing frontmatter is explicitly rejected rather than merely ignored.
4. `AgentPersona` contains behavioral fields only.
5. `AgentDefinition` remains the machine-enforced authority for capabilities, permissions, harnesses, environments, lifecycle, and implementation.
6. Compilation requires stable identity/name/division agreement and copies governance fields unchanged.
7. Registry discovery is deterministic and duplicate-safe.
8. Unsupported schema/version values fail closed.
9. Security and command-like text inside Markdown is inert data; importing a persona never executes it.

## Evidence

Implementation files: `core/personas/`.
Canonical persona artifacts: `agents/engineering/*.md`, `agents/debugging/*.md`, `agents/verification/*.md`, and `agents/security/*.md`.
Tests: `tests/test_personas.py` plus updated catalog regression coverage.
Distribution: `pyproject.toml` includes canonical persona Markdown as package data.

This record documents generalized influence only; it is not a claim of code or prompt reuse from either external project.

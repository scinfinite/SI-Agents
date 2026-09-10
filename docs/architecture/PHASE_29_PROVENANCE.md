# Phase 29 Provenance Record

## External engineering references inspected

Current external specialist-agent and engineering-automation repositories were inspected during Phase 29 as reference material for general engineering patterns.

Observed useful general patterns included specialist decomposition, skills-first reusable procedures, explicit verification/review loops, structured memory and learning support, security scanning around agent assets, readable Markdown role artifacts, division/domain organization, and separation of reusable content from harness-specific integration.

Application to SI-Agents: these generalized ideas informed a human-readable persona layer while execution, governance, and harness boundaries remain in SI typed contracts.

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
10. The completed 279-persona corpus is independently normalized into SI's own behavioral and governance vocabulary.

## Evidence

Implementation files: `core/personas/`.
Canonical persona artifacts: `agents/**/*.md`.
Tests: `tests/test_personas.py` and `tests/test_phase29_persona_parity.py`.
Distribution: `pyproject.toml` includes the complete persona Markdown corpus as package data.

This record documents generalized engineering influence only; it does not claim code, prompt, prose, or repository-architecture reuse.

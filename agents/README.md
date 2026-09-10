# SI-Agents Persona Catalog

This directory contains the canonical Phase 29 behavioral persona corpus.

## Canonical structure

The specialist corpus is organized into 18 SI-owned domain directories under `agents/si-*/`. The corpus contains exactly **279 Markdown persona definitions**. Each persona has an SI-specific ID, name, filename, and division.

The top-level Python modules (`base.py`, `developer.py`, `debugger.py`, and `tester.py`) are retained runtime/model compatibility modules from the existing agent implementation. They are not persona definitions and are not counted in the 279-persona corpus.

## Contract

Persona Markdown is **data**, not executable configuration. It may describe identity, personality, mission, expertise, workflow, boundaries, deliverables, verification, and evidence expectations. It may not grant capabilities, permissions, tools, commands, environments, harness access, network access, credentials, or secrets.

The machine-enforced authority remains `core.organization.AgentDefinition` and the canonical `config/agent-catalog.json`. A persona is compiled against an existing typed contract; compilation cannot add privileges.

## Discovery

Use `core.personas.PersonaRegistry` for deterministic discovery and validation. Non-persona Markdown such as README files is excluded. Do not execute Markdown content during discovery, parsing, compilation, or registration.

## Verification

Phase 29 verifies exact corpus count, unique SI-native identities, deterministic parsing, security boundaries, hidden-Unicode checks, provenance separation, package inclusion, distribution installation, lint, tests, and CI.

Phase 30 builds portable Skills alongside this persona layer. Skills remain separate artifacts and do not become an implicit permission mechanism.

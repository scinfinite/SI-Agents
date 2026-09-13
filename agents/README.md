# SI-Agents Persona Catalog

This directory contains the canonical SI-Agents behavioral persona corpus.

## Canonical structure

The specialist corpus is organized into 18 SI-owned domain directories under `agents/si-*/`. The corpus contains exactly **300 Markdown persona definitions**. Each persona has an SI-specific ID, name, filename, and division.

The top-level Python modules (`base.py`, `developer.py`, `debugger.py`, and `tester.py`) are retained runtime/model compatibility modules. They are not persona definitions and are not counted in the 300-persona corpus.

The catalog is composed of the historical canonical catalog plus the independently authored `config/agent-catalog-extensions.json` definitions. The loader merges them into one validated runtime catalog without changing the authority model.

## Contract

Persona Markdown is **data**, not executable configuration. It may describe identity, personality, mission, expertise, workflow, boundaries, deliverables, verification, and evidence expectations. It may not grant capabilities, permissions, tools, commands, environments, harness access, network access, credentials, or secrets.

Machine-enforced authority remains `core.organization.AgentDefinition` and the validated catalog. A persona is compiled against an existing typed contract; compilation cannot add privileges.

## Discovery

Use `core.personas.PersonaRegistry` for deterministic discovery and validation. Non-persona Markdown such as README files is excluded. Do not execute Markdown content during discovery, parsing, compilation, or registration.

## Verification

The current corpus gate verifies exactly 300 definitions, unique SI-native identities, deterministic parsing, security boundaries, hidden-Unicode checks, provenance separation, package inclusion, distribution installation, lint, tests, and CI.

Skills remain separate artifacts and do not become an implicit permission mechanism.

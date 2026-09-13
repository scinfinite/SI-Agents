# SI-Agents Persona Catalog

This directory contains the SI-Agents behavioral persona corpus.

## Canonical structure

The specialist corpus is organized into **18 SI-owned domain directories** under `agents/si-*/`. The runtime corpus contains exactly **300 Markdown persona definitions**. Each persona has an SI-specific ID, name, filename, and division.

The top-level Python modules (`base.py`, `developer.py`, `debugger.py`, and `tester.py`) are retained runtime/model compatibility modules from the existing agent implementation. They are not persona definitions and are not counted in the 300-persona corpus.

## Catalog source

The base organization contract remains `config/agent-catalog.json`. Repository-owned extensions are stored in `config/agent-catalog-extensions*.json` and are merged deterministically by `core.organization.loader.load_catalog`.

## Contract

Persona Markdown is **data**, not executable configuration. It may describe identity, personality, mission, expertise, workflow, boundaries, deliverables, verification, and evidence expectations. It may not grant capabilities, permissions, tools, commands, environments, harness access, network access, credentials, or secrets.

The machine-enforced authority remains the typed organization model and governance system. A persona is compiled against an existing typed contract; compilation cannot add privileges.

## Discovery

Use `core.personas.PersonaRegistry` for deterministic discovery and validation. Non-persona Markdown such as README files is excluded. Do not execute Markdown content during discovery, parsing, compilation, or registration.

## Verification

The persona parity gate verifies the exact **300-persona** count, unique identities, deterministic parsing, security boundaries, hidden-Unicode checks, repository-neutral provenance, package inclusion, distribution installation, lint, tests, and CI.

Skills remain separate artifacts and do not become an implicit permission mechanism.

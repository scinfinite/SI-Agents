# SI-Agents Personas

This directory contains human-authored Phase 29 behavioral personas.

## Contract

Persona Markdown is **data**, not executable configuration. It may describe identity, personality, mission, expertise, workflow, boundaries, deliverables, verification, and evidence expectations. It may not grant capabilities, permissions, tools, commands, environments, harness access, network access, credentials, or secrets.

The machine-enforced authority remains `core.organization.AgentDefinition` and the canonical `config/agent-catalog.json`. A persona is compiled against an existing typed contract; compilation cannot add privileges.

## Canonical set

- `engineering/developer.md`
- `engineering/backend-engineer.md`
- `engineering/infrastructure-engineer.md`
- `debugging/debugger.md`
- `verification/tester.md`
- `verification/code-reviewer.md`
- `security/security-engineer.md`

Use `core.personas.PersonaRegistry` for deterministic discovery and validation. Do not execute Markdown content during discovery, parsing, compilation, or registration.

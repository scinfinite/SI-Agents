# Phase 22 — Universal Harness Integration

## Status

**Implementation complete pending CI verification.**

Phase 22 turns the Phase 17 harness boundary into a reusable, language-neutral integration surface without making SI-Agents depend on a specific external harness. Phase 21 remains the organization/team execution layer; Phase 22 supplies the bridge that exposes that organization to harness adapters.

## Goals

1. Stable, versioned, JSON-compatible runtime wire envelope.
2. Structural harness adapter bridge for CLI, API, IDE, agent, and embedded harnesses.
3. Capability and metadata discovery without leaking transport details into the core.
4. Harness-neutral organization deployment manifests for agents, teams, skills, permissions, and capabilities.
5. Conformance coverage for correlation, terminal responses, cancellation, wire protocol validation, and deterministic manifests.
6. Preservation of governance, permissions, session isolation, and deny-by-default harness registration.

## Implementation

- `core/runtime/wire.py` defines `si.runtime.v1` serialization helpers and strict protocol-envelope validation. Governance is represented as explicit JSON-compatible primitives rather than serialized Python objects.
- `core/runtime/bridge.py` provides `CallbackHarnessAdapter`, a small structural bridge for harness-specific transport callbacks, plus normalized adapter metadata discovery.
- `core/runtime/deployment.py` provides `HarnessDeploymentManifest` and `build_manifest()`. The manifest describes an exposure surface; it never enables a harness, grants a permission, or executes an agent.
- `core/runtime/__init__.py` exports the universal integration surface.
- `tests/unit/test_universal_harness.py` covers callback adaptation, cancellation capability requirements, wire envelopes, enum/error parsing, capability serialization, deterministic deployment manifests, and duplicate rejection.

## Contract

The core remains authoritative for governance and permissions. A harness adapter is a transport boundary, not a security boundary. The existing `RuntimeEngine` continues to require an enabled registered harness, project/session identity where applicable, supported capabilities, and an allowed governance request before invoking an adapter.

The universal bridge intentionally accepts callbacks rather than importing SDKs. A future OpenCode/Codex/Claude Code/Cline/Antigravity adapter can translate its native transport into `InvocationRequest`/`InvocationResponse` and use the same conformance and governance boundary.

## Organization deployment

`HarnessDeploymentManifest` is the first machine-readable representation of the Phase 20/21 organization surface that can be handed to an external harness integration. It contains agent IDs, team IDs, skill IDs, required permissions, and declared capabilities. Required permissions are descriptive and are never automatically granted by manifest generation.

## External reference patterns

Current ECC demonstrates the value of a harness-neutral session substrate and normalized cross-harness surfaces; its current release notes describe session adapters covering Claude Code, Codex, OpenCode, and dmux. Current Agency Agents reinforces the need for a canonical division source of truth plus generated tool-specific integration outputs and CI consistency checks. SI-Agents adopts the underlying engineering lesson—canonical contracts with adapter-specific projections—without copying those implementations.

## Explicit non-goals

Phase 22 does **not** implement:

- OpenCode-specific integration;
- OmniRoute integration;
- provider credentials or model routing;
- Termux/Codespace installers;
- external harness SDK dependencies;
- automatic installation into user configuration directories;
- permission escalation through deployment manifests;
- self-modifying agent generation.

Those remain later phases or deployment responsibilities.

## Acceptance evidence

A Phase 22 completion claim requires:

- package build and isolated wheel import;
- Ruff clean;
- full pytest suite green;
- universal harness tests green;
- PR CI green;
- mainline CI green after merge;
- documentation/roadmap synchronized with the verified implementation.

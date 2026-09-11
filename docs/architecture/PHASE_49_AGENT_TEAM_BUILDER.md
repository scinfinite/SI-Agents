# Phase 49 — Agent + Team Builder

## Status

**Implementation complete; final CI gate pending.**

## Objective

Provide a typed, deterministic, auditable composition layer for SI-native agents and teams without creating a second execution or governance authority.

## Delivered

- Immutable `AgentDefinition` contracts with role, description, skills, capabilities, model-selection policy, resource limits, boundaries, evidence requirements, and metadata.
- `AgentRegistry` with deterministic ordering, conflict-safe registration, catalog lookup, and SHA-256 catalog digest.
- `TeamDefinition` with explicit membership, handoff edges, bounded parallelism, evidence requirements, and metadata.
- `TeamBuilder` that rejects unknown members and invalid handoffs, calculates aggregate capabilities, derives effective parallelism, and produces a deterministic manifest with digest.
- Existing `agents.base.AgentSpec` remains compatible; Phase 49 adds richer V4 composition contracts rather than silently changing the V3 contract.
- No builder API can grant runtime authority, permissions, credentials, or execution state.

## Security and governance boundary

Agent/team definitions are declarative inputs. Capabilities are declarations only. Actual authorization is deliberately deferred to Phase 50's capability authorization layer. Model policy is selection metadata and cannot grant permissions. Resource limits are declarative until runtime enforcement is connected by later phases.

## Determinism

Catalog ordering, canonical manifests, member ordering, capability aggregation, and manifest hashes are stable for equivalent definitions. Duplicate identifiers with conflicting definitions are rejected.

## Evidence

Tests: `tests/test_phase49_agent_team_builder.py` cover invalid identifiers, resource limits, duplicate conflicts, missing members, invalid handoffs, deterministic catalog output, capability aggregation, and manifest stability.

## Acceptance gate

Phase 49 is not complete until repository audit, integration verification, Ruff, full tests, security/adversarial checks, documentation synchronization, and final exact-tree CI pass on the merged mainline.

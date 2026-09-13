# Phase 49 — Agent + Team Builder

## Status

**Advanced-hardening complete; final verification pending documentation-tree CI.**

## Objective

Provide a typed, deterministic, auditable composition layer for SI-native agents and teams without creating a second execution or governance authority.

## Advanced-level audit result

The original Phase 49 composition layer was structurally sound but lacked explicit schema versioning and deterministic execution planning for team handoffs. The hardening pass adds immutable schema-versioned catalogs/manifests, stronger definition validation, acyclic handoff enforcement, and deterministic topological execution layers.

## Delivered

- Immutable `AgentDefinition` contracts with role, description, skills, capabilities, model-selection policy, resource limits, boundaries, evidence requirements, and metadata.
- Schema-versioned canonical agent manifests for forward-compatible catalog evolution.
- `AgentRegistry` with deterministic ordering, conflict-safe registration, catalog lookup, stable SHA-256 catalog digest, and canonical catalog output.
- `TeamDefinition` with explicit membership, handoff edges, bounded parallelism, evidence requirements, and metadata.
- **Acyclic handoff enforcement** rejects self-handoffs and multi-agent cycles before a team can be built.
- `TeamBuilder` rejects unknown members and invalid handoffs, calculates aggregate capabilities, derives effective parallelism, and produces a deterministic manifest with digest.
- **Deterministic execution layers** expose which agents may run in parallel before each handoff dependency is satisfied.
- Stronger validation rejects duplicate skills/capabilities/boundaries and duplicate metadata keys.
- Existing `agents.base.AgentSpec` remains compatible; Phase 49 adds richer V4 composition contracts rather than silently changing the V3 contract.
- No builder API can grant runtime authority, permissions, credentials, or execution state.

## Security and governance boundary

Agent/team definitions are declarative inputs. Capabilities are declarations only. Actual authorization is owned by Phase 50's capability authorization layer. Model policy is selection metadata and cannot grant permissions. Resource limits are declarative until runtime enforcement is connected by later phases.

## Determinism

Catalog ordering, schema-versioned canonical manifests, member ordering, capability aggregation, execution-layer ordering, and manifest hashes are stable for equivalent definitions. Duplicate identifiers with conflicting definitions are rejected.

## Verification coverage

`tests/test_phase49_agent_team_builder.py` covers invalid identifiers, resource limits, duplicate conflicts, missing members, invalid handoffs, cycle rejection, deterministic catalog output, capability aggregation, execution-layer planning, and manifest stability.

## Baseline evidence

Phase 49 CI run 954 (`34625018676`) passed distribution, wheel installation/import, repository audit, integration verification, Ruff, and the complete pytest suite. The implementation was merged to `main` as `de06398f2abefe24b58e52a7629dc5af3c191428`.

## Advanced-hardening evidence

Combined advanced audit CI **#984 (`34671292491`)** passed distribution, wheel verification, repository audit, integration verification, Ruff, and the complete pytest suite after the topology/schema hardening.

## Acceptance

The Phase 49 composition layer is now advanced-hardened. Final status becomes immutable on `main` only after the documentation synchronization commit also passes exact-tree CI.

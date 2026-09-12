# Architecture

SI-Agents V4 uses a single authoritative SI Core. Web, TUI, CLI, OpenCode, runtime adapters, schedulers, agents, teams, workflows, and integrations are clients/adapters of that authority rather than independent state owners.

## V4 target architecture

```text
OpenCode / Web / TUI / CLI → SI Core / Control API
                          → Scheduler / Orchestrator
                          → Tasks / Agents / Teams / Workflows
                          → Capability Authorization → OmniRoute
                          → Models / Providers / APIs
                          → Results / Artifacts / Evidence
                          → Observability → Evaluation → Continuous Improvement
                          → Cross-Runtime Gateway → Clients / Harnesses
```

OmniRoute owns model/provider/API routing. SI Core owns execution, orchestration, governance, evidence, lifecycle, persistence, recovery, waiting, workspaces, observability, evaluation, continuous improvement, and cross-runtime governance.

## Verified V4 phases

Phases 44–62 are closed. Phases 46, 47, 49, 50, 58, 59, and 60 are advanced-hardened.

## Phase 62 architecture

Phase 62 provides a common portable adapter contract for runtime, session, tool, model, event, capability, context, checkpoint, and artifact resources. `PortableAdapterRegistry` is deny-by-default and discovery-only; it grants no permissions.

`CrossRuntimeGateway` provides deterministic harness discovery, streaming capability filtering, preferred selection, health probes, bounded degradation/quarantine/recovery, project+harness session binding, explicit session migration, and safe pre-start fallback. Fallback is allowed only for retryable failures before execution-start signals. Routing evidence excludes request payloads and is bounded.

OpenCode, CLI, API, IDE, embedded, and agent harnesses can implement the same `HarnessAdapter` protocol. SI Core remains the only execution/governance authority; the gateway never silently changes capabilities, grants, execution state, or authorization.

## Phase 62 closure evidence

- PR #76 merged into `main` as `607085782a75e31a60774afe975edcbd38bf5e4c`.
- PR CI #1166 / `34692621358` passed wheel verification, repository audit, integration verification, Ruff, and full pytest.
- Final synchronized-tree mainline CI is the authoritative post-merge gate.

## Current position

**V4 Phases 44–62 are closed; Phase 63 — Ecosystem / Marketplace is next.**

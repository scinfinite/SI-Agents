# Architecture

SI-Agents V4 uses a single authoritative SI Core. Web, TUI, CLI, OpenCode, SDKs, runtime adapters, schedulers, agents, teams, workflows, and integrations are clients/adapters of that authority rather than independent state owners.

## V4 target architecture

```text
OpenCode / Web / TUI / CLI / SDK → SI Core / Control API
                                 → Scheduler / Orchestrator
                                 → Tasks / Agents / Teams / Workflows
                                 → Capability Authorization → OmniRoute
                                 → Models / Providers / APIs
                                 → Results / Artifacts / Evidence
                                 → Observability → Evaluation → Continuous Improvement
                                 → Cross-Runtime Gateway → Ecosystem / Marketplace → Clients / Harnesses
```

OmniRoute owns model/provider/API routing. SI Core owns execution, orchestration, governance, evidence, lifecycle, persistence, recovery, waiting, workspaces, observability, evaluation, continuous improvement, and cross-runtime governance.

## Verified V4 phases

**Phases 44–68 are closed.** Phases 46, 47, 49, 50, 58, 59, and 60 are advanced-hardened.

## Current system hardening

- **300 agent personas across 18 divisions** are validated by the runtime catalog/parity gate.
- Low / Medium / High capacity policy is implemented. Termux permits Low and bounded Medium work; High work and compilation are blocked locally.
- Desktop/Codespace are the preferred High-capacity targets.
- Termux/OpenCode/OmniRoute integration boundaries are documented and remain separate authorities.
- Repository-neutral provenance hygiene removes unnecessary external project branding from shipped surfaces.
- SI-Agents-owned work is licensed under Apache-2.0; third-party dependencies retain their own licenses.
- `AGENTS.md` is the primary agent instruction contract and `SIA_SPECS.md` is the current complete system specification.
- Phase history is systematically indexed under `docs/phases/` while historical `docs/architecture/PHASE_*.md` paths remain compatible.

## Production Web Control Center

The approved Web Control Center visual system is implemented on `main`. It is the reference visual language for SI-Agents browser operations: compact operator typography, dark navy/light neutral surfaces, restrained semantic accents, responsive navigation, dense but readable cards/tables, status badges, and accessible controls.

The web supports **dark and light modes**, with local theme persistence and operating-system preference fallback. The production navigation preserves the full Control Center read surface: Overview, Runs, Agents, Teams, Workflows, Topology, Skills, Memory, Knowledge, Evidence, Organization, Governance, Environments, Harnesses, and Settings.

The browser remains an adapter of the existing versioned Control API. It does not execute agents, workflows, shell commands, tools, or providers directly. Detailed design contract: `WEB_CONTROL_CENTER_DESIGN.md`.

## Phase 68 architecture

Phase 68 adds an advanced CLI adapter over the existing Control API. Local CLI calls use `ControlApiService`; remote CLI calls use authenticated HTTP. The platform exposes governed runs/tasks/executions, agent/team/workflow resources, identity-bound approvals, bounded client sessions, events and bounded run streaming, model/provider delegation, attachment inspection, non-secret configuration/auth status, transport profiles, and bounded declarative pipelines.

The CLI owns no execution state authority. Run creation is always submitted through SI Core governance. Resume explicitly fails closed when downstream execution owns the transition. Model/provider discovery remains delegated to OmniRoute. Client metadata is bounded and stored separately from SI Core lifecycle state. Authentication tokens are environment-only and never printed or persisted by the CLI. Established legacy commands retain their historical routing contracts.

## Phase 67 architecture

Phase 67 upgrades the dependency-free TUI into an advanced operator control center while preserving the historical 14-view contract. The surface provides bounded list selection, deterministic filtering and sorting, detail inspection, pause/live state, direct navigation, bounded JSON status export, non-interactive rendering, and governed run/identity-bound approval commands.

## Phase 66 architecture

Phase 66 adds a same-origin, dependency-free web control client layered over the existing WebServer and versioned Control API. It does not create a second state or authorization authority.

## Phase 65 architecture

Phase 65 adds a transport-neutral workflow state machine for versioned declarative DAGs. It supports conditional branching, bounded fan-out/loops, delegation, human gates, durable waits, event/webhook/interval triggers, retries, runtime limits, cancellation, request-fingerprint-bound idempotency, durable JSON checkpoints, templates, restart validation, and reverse-order compensation.

## Closure evidence

- Phase 63: PR #77 merged; final exact-tree mainline CI #1198 / `34694418960` passed.
- Phase 64: PR #78 merged; implementation closure CI #1239 / `34697885027` passed.
- Phase 65: final synchronized-tree CI #1249 / `34698187600` completed successfully.
- Phase 66: PR #79 merged; final synchronized-tree mainline CI #1284 / `34701494501` completed successfully.
- Phase 67: PR #80 merged; final synchronized-tree mainline CI #1295 / `34702226193` completed successfully.
- Phase 68: PR #81 merged; final PR CI #1319 / `34703142494`, SDK CI #111 / `34703142515`, and merged-tree mainline CI #1320 / `34703212232` completed successfully.
- Web Control Center design: PR #82 merged; the design/documentation changes are now part of the current hardening baseline.

## Current position

**Phase 68 — Advanced CLI Platform is 100% complete and closed. The approved Web Control Center design is implemented. Current hardening covers 300 personas, capacity safety, Termux guidance, provenance/legal controls, and documentation organization. Phase 69 — npm Distribution + Setup is next.**

# Architecture

SI-Agents V4 uses a single authoritative SI Core. Web, TUI, CLI, OpenCode, SDKs, runtime adapters, schedulers, agents, teams, workflows, and integrations are clients/adapters of that authority rather than independent state owners.

## V4 target architecture

```text
OpenCode / Web / TUI / CLI / SDK → SI Core / Control API
                                 → Scheduler / Orchestrator
                                 → Tasks / Agents / Teams / Workflows
                                 → Capacity + Capability Authorization → OmniRoute
                                 → Models / Providers / APIs
                                 → Results / Artifacts / Evidence
                                 → Observability → Evaluation → Continuous Improvement
                                 → Cross-Runtime Gateway → Ecosystem / Marketplace → Clients / Harnesses
```

OmniRoute owns model/provider/API routing. SI Core owns execution, orchestration, governance, evidence, lifecycle, persistence, recovery, waiting, workspaces, observability, evaluation, continuous improvement, and cross-runtime governance.

## Verified V4 phases

**Phases 44–68 are closed.** Phases 46, 47, 49, 50, 58, 59, and 60 are advanced-hardened.

## Canonical phase archive

Historical Phase records **1–68** now live in `docs/architecture/phases/`. `PHASES.md` remains the current status/index document. New phases must be added to the archive directory.

## Pre-Phase 69 hardening

The repository hardening gate adds:

- exactly **300** SI-native persona definitions;
- repository-owned catalog extensions loaded through `core.organization.loader`;
- Low/Medium/High capacity policy with selectable Termux worker counts;
- Termux High/heavy-workload blocking and Desktop/Codespace escalation;
- strengthened provenance, licensing, contributor, and branding controls;
- `SIA_SPECS.md` as the complete system specification;
- synchronized phase documentation;
- OpenCode and OmniRoute retained as intentional integration boundaries.

## Production Web Control Center

The approved Web Control Center visual system is implemented on `main`. It is the reference visual language for SI-Agents browser operations: compact operator typography, dark navy/light neutral surfaces, restrained semantic accents, responsive navigation, dense but readable cards/tables, status badges, and accessible controls.

The web supports **dark and light modes**, with local theme persistence and operating-system preference fallback. The production navigation preserves the full Control Center read surface: Overview, Runs, Agents, Teams, Workflows, Topology, Skills, Memory, Knowledge, Evidence, Organization, Governance, Environments, Harnesses, and Settings.

The browser remains an adapter of the existing versioned Control API. It does not execute agents, workflows, shell commands, tools, or providers directly. Detailed design contract: `WEB_CONTROL_CENTER_DESIGN.md`.

## Capacity architecture

`core/capacity/policy.py` provides a fail-closed execution profile:

- Low: Termux/mobile 1–2 workers.
- Medium: Termux/mobile 3–5 workers.
- High: Desktop/Codespace only; Termux/mobile is blocked.
- Compile/build/native/container/large-benchmark/release workloads are heavy and blocked on Termux/mobile.

`ParallelScheduler` and `TeamEngine` clamp effective concurrency to the resolved capacity. Capacity controls SI-owned concurrency and does not claim hardware thermal control.

## Phase 68 architecture

Phase 68 adds an advanced CLI adapter over the existing Control API. Local CLI calls use `ControlApiService`; remote CLI calls use authenticated HTTP. The platform exposes governed runs/tasks/executions, agent/team/workflow resources, identity-bound approvals, bounded client sessions, events and bounded run streaming, model/provider delegation, attachment inspection, non-secret configuration/auth status, transport profiles, and bounded declarative pipelines.

The CLI owns no execution state authority. Run creation is always submitted through SI Core governance. Model/provider discovery remains delegated to OmniRoute. Authentication tokens are environment-only and never printed or persisted by the CLI. No command performs arbitrary shell execution.

## Closure evidence

- Phase 63: PR #77 merged; final exact-tree mainline CI #1198 / `34694418960` passed.
- Phase 64: PR #78 merged; implementation closure CI #1239 / `34697885027` passed.
- Phase 65: final synchronized-tree CI #1249 / `34698187600` completed successfully.
- Phase 66: PR #79 merged; final synchronized-tree mainline CI #1284 / `34701494501` completed successfully.
- Phase 67: PR #80 merged; final synchronized-tree mainline CI #1295 / `34702226193` completed successfully.
- Phase 68: PR #81 merged; final PR CI #1319 / `34703142494`, SDK CI #111 / `34703142515`, and merged-tree mainline CI #1320 / `34703212232` completed successfully.
- The Web Control Center design was merged through PR #82; the current hardening branch must complete a fresh exact-tree CI before the pre-Phase 69 gate is closed.

## Current position

**Phase 68 remains closed. Phase 69 is the next roadmap phase, but it must not begin until the pre-Phase 69 hardening branch passes the final verification gate.**

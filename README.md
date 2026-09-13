# SI-Agents

SI-Agents is a governed AI engineering and agent platform. V4 is built around one authoritative SI Core exposed through Web, TUI, CLI, OpenCode, SDKs, workflows, and runtime/integration adapters.

## Current status

- **V4 Phases 44–68 are complete on `main`.**
- **300 agent personas across 18 divisions** are now part of the runtime catalog.
- Low / Medium / High capacity controls are implemented; Termux High work and local compilation are blocked.
- Termux, desktop, and Codespace runtime guidance is documented.
- Repository-neutral provenance and license hygiene is implemented.
- `AGENTS.md` is the primary agent operating contract.
- `SIA_SPECS.md` is the current complete system specification.
- Phase documents are systematically indexed under `docs/phases/` while historical architecture paths remain compatible.

## Phase 68 — Advanced CLI Platform

Phase 68 adds a transport-neutral, machine-friendly `si` platform over SI Core. It provides governed run/task/execution commands, agent/team/workflow navigation, identity-bound approvals, bounded client sessions, event/state observation and run streaming, model/provider discovery delegation, attachment inspection, non-secret config/auth status, transport profiles, and bounded declarative pipelines.

Local mode calls the existing Control API service; remote mode uses authenticated HTTP against the existing Control API. The CLI is an adapter rather than a second execution/governance authority. It never invokes arbitrary shells or providers directly, never persists authentication secrets, and fail-closes when downstream execution owns a lifecycle transition such as resume.

## Capacity safety

SI-Agents classifies workloads as Low, Medium, or High.

- **Low:** bounded inspection, status, docs, and short edits.
- **Medium:** bounded tests, lint, review, and short analysis.
- **High:** compilation, large builds, benchmarks, large indexing, code generation, migrations, and other sustained workloads.

On Termux, Low is allowed with one worker, Medium is bounded to two workers, and High is blocked locally. High work should be moved to a desktop or Codespace. This reduces SI-Agents-controlled load but cannot guarantee the thermal behavior of external processes such as OpenCode or OmniRoute.

## OpenCode + OmniRoute

OpenCode is a supported harness/integration boundary. OmniRoute is a supported model/provider routing boundary. SI-Agents owns governance, workflows, evidence, capacity policy, and operator control; it does not silently replace external routing authority.

## Persona organization

The runtime catalog contains **300 personas across 18 divisions**. Persona Markdown is non-executable configuration and cannot grant tools, credentials, permissions, or governance authority.

## Legal and provenance posture

SI-Agents-owned work is licensed under Apache-2.0. External engineering patterns may inform generalized design decisions, but distinctive third-party code, prompts, persona prose, documentation passages, and branding are not intended to be copied. OpenCode and OmniRoute remain named because they are actual supported integrations.

This materially reduces provenance and licensing risk but is not a guarantee that no third party can ever assert a legal claim. See `docs/legal/PROVENANCE_AND_LICENSE.md`.

## V4 roadmap

See `docs/architecture/SI_AGENTS_V4_PLAN.md` for the roadmap and `docs/architecture/PHASES.md` for phase evidence. Current phase status is summarized in `docs/STATUS.md` and `SIA_SPECS.md`.

| Phase | Name | Status |
|---:|---|---|
| 44 | Execution Runtime Foundation | Complete |
| 45 | Event Bus + State Architecture | Complete |
| 46 | Parallel Scheduler + Executor | Advanced hardened |
| 47 | OpenCode Bridge | Advanced hardened |
| 48 | OmniRoute Integration | Complete |
| 49 | Agent + Team Builder | Advanced hardened |
| 50 | Capability Authorization | Advanced hardened |
| 51 | Checkpoints + Resume | Complete |
| 52 | Context / Memory Economics | Complete |
| 53 | Persistent Sessions | Complete |
| 54 | Human-in-the-Loop | Complete |
| 55 | Durable Waiting + Scheduling | Complete |
| 56 | Intelligent Routing + Economics | Complete |
| 57 | Security Platform | Complete |
| 58 | Workspace / Worktree Lifecycle | Advanced hardened |
| 59 | Observability | Advanced hardened |
| 60 | Evaluation + Benchmarking | Advanced hardened |
| 61 | Continuous Improvement | Complete |
| 62 | Cross-Runtime / Cross-Harness | Complete |
| 63 | Ecosystem / Marketplace | Complete |
| 64 | SDK / Developer Platform | Complete |
| 65 | Workflow + Automation | Complete / 100% |
| 66 | Advanced Web Control Plane | Complete / 100% |
| 67 | Advanced TUI Control Center | **Complete / 100%** |
| 68 | Advanced CLI Platform | **Complete / 100%** |
| 69 | npm Distribution + Setup | Planned |
| 70 | End-to-End Production Validation | Planned |
| 71 | Final Production Hardening | Planned |

## Engineering gate

A phase is not complete until implementation, tests, security/adversarial checks, documentation synchronization, repository audit, distribution verification, integration verification, lint/type/build checks, merge, and final exact-tree mainline CI are green.

## npm target

The planned user-facing npm command is:

```bash
npx si-agents
```

Persistent global installation:

```bash
npm install -g si-agents
```

Phase 69 will build and validate the npm distribution. Publishing to the registry requires the project owner's npm authentication/trusted-publishing configuration.

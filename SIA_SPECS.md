# SIA-SPECS — SI-Agents Complete System Specification

**Status:** Pre-Phase 69 hardening baseline

This document is the high-level product and engineering specification for SI-Agents. It is intentionally implementation-neutral where possible; detailed contracts live under `docs/architecture/` and historical phase records live under `docs/architecture/phases/`.

## 1. System identity

SI-Agents is a governed, evidence-driven AI engineering and agent platform. SI Core is the authoritative control plane for execution, governance, authorization, lifecycle, evidence, persistence, recovery, observability, evaluation, and controlled improvement.

External clients/integrations—including Web, TUI, CLI, SDKs, OpenCode, OmniRoute, Termux, Codespaces, and other harness adapters—must not silently become competing execution or authorization authorities.

## 2. Core capabilities

- Agent and persona catalog management.
- 300 repository-owned agent/persona definitions.
- Specialized divisions, teams, workflows, and task graphs.
- Evidence-first engineering workflows.
- Code inspection, debugging, review, architecture, verification, and regression workflows.
- Reusable Skills with validation and indexing.
- Engineering memory and technical knowledge surfaces.
- Security, governance, permissions, approvals, and audit evidence.
- Automation, scheduling, durable waiting, checkpoints, resume, and controlled self-improvement.
- Context/memory economics and model/provider routing delegation.
- Web, TUI, CLI, Python SDK, and TypeScript SDK operator/developer surfaces.
- OpenCode integration and OmniRoute provider/model routing integration.
- Termux/mobile and Codespace/Desktop environment awareness.

## 3. Authority model

1. SI Core owns execution state and lifecycle.
2. Governance owns authorization decisions.
3. OmniRoute owns model/provider/API routing decisions.
4. Adapters transport requests and present results.
5. Evidence records facts; evidence does not grant authority.
6. Imported Markdown/JSON/YAML configuration is data until explicitly validated and authorized.
7. Credentials are never persisted by convenience layers and are never placed in URLs.

## 4. Capacity model

SI-Agents supports three explicit execution levels:

### Low

- Termux/mobile: **1–2 workers**, user-selectable.
- Desktop: bounded low-load profile.
- Intended for normal editing, inspection, small analysis, and lightweight agent tasks.

### Medium

- Termux/mobile: **3–5 workers**, user-selectable.
- Desktop/Codespace: bounded concurrency appropriate to the host.
- Intended for larger multi-agent workflows that remain suitable for the host.

### High

- Desktop/Codespace: allowed with an explicit warning about CPU, memory, battery, and network load.
- Termux/mobile: **blocked by policy** and redirected to Desktop/Codespace.
- Compilation, native builds, large benchmarks, container builds, and full-release builds are treated as heavy workloads and are blocked on Termux/mobile.

Selection can be supplied with `SI_CAPACITY=low|medium|high` and `SI_WORKERS=<n>`. The `si-capacity` command reports the resolved decision.

SI-Agents controls SI-owned concurrency; it cannot guarantee a device temperature because operating-system services, OpenCode, OmniRoute, model providers, and hardware thermal management remain outside its complete authority.

## 5. Termux contract

Termux is a supported lightweight execution environment. The policy is intentionally conservative:

- no implicit high-capacity execution;
- bounded worker count;
- heavy build/compile workloads require a remote/Desktop environment;
- explicit warnings for sustained resource use;
- no claim of guaranteed zero heating;
- Codespace/Desktop is the recommended execution host for high workloads.

See `docs/platforms/TERMUX.md`.

## 6. OpenCode + OmniRoute integration

OpenCode is an execution/harness integration surface. OmniRoute is the model/provider routing authority. SI-Agents does not reimplement OmniRoute's provider routing, quota, pricing, fallback, or circuit-breaker authority.

The supported composition is:

`User → SI-Agents governance/control → OpenCode/harness adapter → OmniRoute routing → model/provider`

Any failure at a governance boundary is fail-closed.

## 7. Web / TUI / CLI

### Web

Dependency-free local Web Control Center with dark/light themes, responsive navigation, resource screens, live operational views, filtering/search/refresh, topology visualization, accessibility and reduced-motion behavior.

### TUI

Dependency-free terminal operator control center with bounded rendering, navigation, inspection, governed mutation routing, deterministic non-interactive mode, and no arbitrary shell execution.

### CLI

Machine-friendly `si` platform with governed run/task/execution resources, sessions, approvals, events, profiles, configuration/auth status, attachments, streaming, pipelines, and compatibility with established legacy commands.

## 8. Security

- Least privilege.
- Fail-closed authorization.
- Identity-bound approvals.
- Secret redaction and non-secret configuration boundaries.
- No arbitrary shell execution from adapter surfaces.
- Bounded payloads, sessions, attachments, pipelines, streams, and concurrency.
- Safe path/identifier handling.
- Integrity-protected handoffs/checkpoints.
- Audit evidence for security-sensitive decisions.

## 9. Provenance and legal-risk controls

SI-Agents is independently authored. Public projects may be consulted for general engineering ideas, but their implementation, prompts, branding, distinctive documentation, or expressive content must not be copied into SI-Agents.

Repository controls include:

- external-branding hygiene checks;
- provenance/license documentation;
- dependency/license review boundaries;
- contributor originality and provenance requirements;
- Apache License 2.0 distribution terms for SI-Agents-owned code;
- separate handling of third-party notices where required;
- no intentional inclusion of third-party secrets or proprietary source material;
- integration names retained only where they identify actual SI-Agents integration boundaries (for example OpenCode and OmniRoute).

These controls reduce risk but cannot provide a legal guarantee that no third party will ever assert a claim. Patent, trademark, copyright, contract, or jurisdiction-specific issues can require professional legal review.

See `docs/legal/PROVENANCE_AND_LICENSE.md` and `CONTRIBUTING.md`.

## 10. Distribution

The Python package currently exposes the `si` CLI and related entry points. The Phase 69 npm distribution target is:

```text
npx si-agents
npm install -g si-agents
```

Phase 69 must establish package contents, cross-platform setup, Termux behavior, smoke tests, provenance/license checks, and publication safety before any release is declared production-ready.

## 11. Verification standard

A feature is not considered complete merely because files exist. Completion requires:

1. evidence inspection;
2. implementation;
3. targeted tests;
4. lint/type/syntax checks where applicable;
5. integration tests;
6. distribution/package verification;
7. repository hygiene/provenance audit;
8. documentation synchronization;
9. final CI;
10. post-merge verification on the exact mainline tree.

## 12. Repository organization

- `agents/` — repository-owned agent/persona definitions.
- `core/` — authoritative runtime, governance, orchestration, adapters, capacity, and services.
- `config/` — canonical machine-readable catalogs and policies.
- `skills/` — reusable validated Skills.
- `sdk/` — developer SDKs.
- `tests/` — regression, unit, integration, security, and phase acceptance tests.
- `docs/architecture/phases/` — canonical historical phase records 1–68.
- `docs/platforms/` — environment-specific operating guidance.
- `docs/legal/` — licensing/provenance policy.
- `SIA_SPECS.md` — this system specification.
- `AGENTS.md` — repository agent operating contract.

## 13. Non-goals

SI-Agents does not promise zero device heating, zero cost, zero legal risk, zero provider failures, or unrestricted execution. It instead provides bounded, auditable, evidence-backed behavior and explicit escalation to a stronger execution environment when the local host is unsuitable.

# SIA_SPECS — SI-Agents System Specification

**Status:** Current repository specification  
**Persona catalog:** 300 personas / 18 divisions  
**Current roadmap:** V4 through Phase 68 closed; Phase 69 npm distribution + setup is the next planned phase.

## 1. System purpose

SI-Agents is a governed AI engineering system that provides an organization of specialized agent personas, reusable skills, engineering memory, technical knowledge, evidence/verification, automation, security/legal/cost controls, cross-runtime interoperability, and operator-facing Web/TUI/CLI control surfaces.

The system is designed for evidence-first engineering rather than autonomous authority. Agents propose and perform bounded work under explicit governance; they do not acquire authority merely by reading a file, prompt, skill, memory entry, or handoff artifact.

## 2. Primary surfaces

- **Web Control Center** — responsive operator console with dark/light themes, navigation, search, live control-plane views, visualization, governance, evidence, environments, and settings.
- **TUI Control Center** — terminal-first control surface for constrained environments.
- **CLI Platform** — stable JSON envelopes, bounded sessions, approvals, profiles, logs, events, pipelines, status, and configuration surfaces.
- **Control API** — versioned localhost-first API used by the operator surfaces.
- **SDKs** — typed Python and TypeScript clients for the Control API.
- **OpenCode integration** — harness/protocol adapter boundary.
- **OmniRoute integration** — provider/model routing boundary; SI-Agents does not replace its routing authority.
- **Termux runtime** — constrained mobile environment with capacity-aware admission rules.
- **Codespace/Desktop runtime** — preferred environments for high-capacity work.

## 3. Agent organization

There are exactly **300** runtime personas across **18** divisions. The base catalog remains `config/agent-catalog.json`; newly authored repository-owned personas are supplied through `config/agent-catalog-extensions*.json` and loaded into the same runtime registry.

Persona files are non-executable configuration. They cannot grant permissions, tools, credentials, provider access, publication rights, or governance overrides.

## 4. Engineering capabilities

SI-Agents supports engineering workflows across multiple languages and ecosystems, including Python, Java, TypeScript/JavaScript, Go, Rust, C/C++, Kotlin, Swift, shell, and repository-specific build systems.

Core engineering capabilities include:

- root-cause debugging;
- code review;
- architecture analysis;
- API contract review;
- testing and regression analysis;
- performance analysis;
- dependency and supply-chain review;
- security review;
- license/provenance review;
- documentation verification;
- release validation;
- workspace/worktree handling;
- evidence and observability;
- controlled self-improvement.

## 5. Capacity model

SI-Agents has three explicit capacity levels:

| Level | Intended work | Termux policy | Preferred heavy-work host |
|---|---|---|---|
| Low | inspection, status, docs, short edits | Allowed; one worker | Any |
| Medium | bounded tests, lint, review, analysis | Allowed; max two workers | Desktop/Codespace when long-running |
| High | builds, compilation, benchmarks, large indexes, code generation, migrations | Blocked locally | Desktop/Codespace |

High-capacity work on Termux must not be bypassed by relabeling. Compilation is specifically treated as high-capacity work.

The policy controls SI-Agents-managed local work. It cannot guarantee the thermal behavior of external processes such as OpenCode, OmniRoute, the operating system, or model providers.

## 6. OpenCode + OmniRoute + SI-Agents

The intended architecture is:

`Operator → SI-Agents Control Surface → SI-Agents Control API → governed workflow → OpenCode/harness boundary → OmniRoute/model-provider routing → external model/provider`

Responsibilities are intentionally separated:

- SI-Agents owns governance, agent organization, workflows, evidence, capacity policy, and operator control.
- OpenCode owns its harness/client behavior.
- OmniRoute owns provider/model routing, fallback, quota, and routing-specific economics.

SI-Agents must not duplicate or silently override OmniRoute routing authority.

## 7. Security model

- localhost-first Control API;
- explicit authentication for protected remote exposure;
- explicit CORS allowlists;
- bounded request and attachment sizes;
- no secret persistence in profiles or personas;
- approval gates for high-risk actions;
- evidence records for material mutations;
- imported content treated as untrusted data;
- fail-closed governance decisions.

## 8. Legal/provenance model

SI-Agents-owned implementation is independently authored. General engineering ideas and methods may be learned from public material, but distinctive third-party expression is not intended to be copied.

The project intentionally avoids unnecessary external project branding in implementation and shipped documentation. OpenCode and OmniRoute remain named because they are actual supported integrations.

The project license for SI-Agents-owned work is Apache-2.0. Third-party dependencies remain under their respective licenses.

This is an engineering/legal-risk control, not a guarantee that no person can ever make a claim. Copyright, trademark, patent, contract, dependency-license, and jurisdictional questions can still require professional legal review.

## 9. Termux requirements

A supported Termux installation should provide Python 3.11+, Git, curl, and SSH where required by the selected workflow. OpenCode and OmniRoute are optional until an integration requiring them is selected.

Termux should be treated as a constrained operator/runtime environment. Heavy compilation, full-suite CI, sustained benchmarks, large indexing, and other high-capacity workloads belong on a desktop or Codespace.

## 10. Verification contract

No phase or feature is complete merely because files exist. Completion requires:

1. implementation inspection;
2. targeted tests;
3. lint/type/build checks where relevant;
4. package/artifact inspection;
5. regression tests;
6. documentation synchronization;
7. final CI verification on the merged tree.

Real physical-device thermal testing cannot be inferred from a Linux CI runner; such testing must be reported separately when performed.

## 11. Distribution

The planned npm user-facing command is:

```bash
npx si-agents
```

Persistent installation is:

```bash
npm install -g si-agents
```

The repository can build and pack the npm artifact in CI. Publishing to npm requires the project owner's npm account/trusted-publishing configuration and is not performed implicitly by normal development CI.

## 12. Documentation map

- `AGENTS.md` — primary agent operating rules.
- `SIA_SPECS.md` — current system specification.
- `docs/STATUS.md` — current implementation and verification status.
- `docs/phases/` — phase history and phase contracts.
- `docs/architecture/README.md` — architecture index.
- `docs/architecture/SI_AGENTS_V4_PLAN.md` — V4 roadmap baseline.
- `docs/architecture/WEB_CONTROL_CENTER_DESIGN.md` — production Web design contract.
- `docs/platforms/TERMUX.md` — Termux installation and capacity guidance.
- `docs/legal/PROVENANCE_AND_LICENSE.md` — provenance and legal-risk controls.

## 13. Non-goals

SI-Agents does not:

- promise zero legal risk;
- promise zero device heating;
- replace OpenCode;
- replace OmniRoute;
- silently publish packages;
- infer human approval from a persona, prompt, or imported file;
- treat CI success as proof of physical-device behavior.

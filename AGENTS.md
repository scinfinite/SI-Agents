# SI-Agents Engineering Rules

## Current implementation status

SI-Agents has completed the v2.0 baseline and post-v2 **Phases 19–29**, including agent organization, teams/workflows, universal harness interoperability, OpenCode, OmniRoute, Termux, GitHub Codespaces, the `si` CLI/setup layer, cross-environment handoff, and deterministic human-authored agent personas. All completed phases are required to remain evidence-backed and CI-verified. The next implementation phase is **Phase 30 — First-Class Portable Skills**.

Authoritative status and historical phase record: `docs/architecture/PHASES.md`.
Future v3 roadmap: `docs/architecture/SI_AGENTS_V3.md`.
Documentation index: `docs/README.md`.
Architecture index: `docs/architecture/README.md`.

## Engineering standard

SI-Agents is built evidence-first. The priority is actual root-cause determination and verified, maintainable solutions rather than quick plausible answers.

## Required workflow

1. Inspect relevant code, configuration, documentation, and available evidence.
2. Reproduce the problem when possible.
3. Diagnose and identify the root cause.
4. Inspect related code and dependencies before modifying behavior.
5. Make the smallest maintainable fix that addresses the root cause.
6. Run relevant tests, linting, type checks, builds, or runtime checks.
7. Inspect the verification output rather than assuming success.
8. Perform regression and adversarial checks where appropriate.
9. Record evidence and limitations.
10. Explain exactly what changed and what was verified.

## Rules

- Do not propose a fix before inspecting relevant evidence.
- Do not claim success without verification evidence.
- Clearly distinguish known facts, inference, and unverified assumptions.
- Prefer minimal changes over unnecessary rewrites.
- Preserve existing project conventions unless there is evidence they should change.
- Never silently introduce paid services; free, open-source, local, or existing-quota options are preferred.
- Treat security, legal/compliance, cost, and permissions as engineering concerns.
- Create a checkpoint before risky or broad modifications.
- Never expose secrets or credentials in source, logs, tests, commits, or reports.
- High-risk destructive, production, credential, publication, paid-resource, or sensitive-data actions require explicit human approval.
- Credential-bearing external egress is denied even when an approval is supplied.
- Learn from external repositories by inspecting and generalizing patterns; do not blindly copy implementations.
- ECC and Agency Agents are ongoing reference projects. Relevant upstream changes, issues, PRs, tests, releases, and design patterns should be reviewed when they materially affect a SI-Agents feature.
- Keep project-specific knowledge isolated from global reusable knowledge.
- Self-improvement must be controlled, evidence-backed, benchmarked, and regression-tested.
- Architecture/phase Markdown must be updated when implementation status, verification evidence, boundaries, or roadmap state materially changes.
- Phase completion claims must identify the verification evidence; documentation status must not outrun CI or implementation reality.
- Markdown personas, skills, hooks, rules, memory, deployment manifests, and UI-authored artifacts are data/configuration until explicitly authorized; importing them must never silently grant privileges or execute code.
- Handoff artifacts are data, not authority; importing one must never grant permissions, enable harnesses, execute commands, migrate credentials, or bypass governance.
- OmniRoute remains the model/provider routing authority; SI-Agents must not recreate provider routing, pricing, quota, fallback, or circuit-breaker authority.
- Historical phase documents preserve the phase-time contract; current implementation/status belongs in `PHASES.md` and future work belongs in `SI_AGENTS_V3.md`.

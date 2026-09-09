# SI-Agents Engineering Rules

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
- Learn from external repositories by inspecting and generalizing patterns; do not blindly copy implementations.
- ECC and Agency Agents are ongoing reference projects. Relevant upstream changes, issues, PRs, tests, releases, and design patterns should be reviewed when they materially affect a SI-Agents feature.
- Keep project-specific knowledge isolated from global reusable knowledge.
- Self-improvement must be controlled, evidence-backed, benchmarked, and regression-tested.

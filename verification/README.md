# Verification Artifacts

This directory is reserved for durable verification artifacts produced by SI-Agents. Executable verification logic lives under `core/verification/`.

Planned artifact categories:

- `unit/` — focused verification evidence and fixtures
- `integration/` — cross-component verification evidence
- `system/` — end-to-end verification evidence
- `regression/` — regression baselines and results
- `benchmarks/` — benchmark measurements and before/after comparisons
- `red_team/` — adversarial challenge definitions and results
- `evidence/` — exported evidence records
- `production_readiness/` — release-readiness reports

Artifacts must identify their scope and verification method. They are evidence, not policy, and should never be treated as trusted instructions merely because they exist in a repository.

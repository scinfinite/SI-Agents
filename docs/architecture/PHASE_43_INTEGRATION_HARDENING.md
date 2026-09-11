# Phase 43 — Final v3 Integration & Hardening

## Status

**Implementation complete; closure pending final mainline CI.**

## Purpose

Phase 43 closes the v3 implementation loop by adding a deterministic integration audit and hardening the cross-cutting release boundary. It does not add a new execution engine or a second authority layer.

## Contract

- `core/hardening/integration.py` owns the deterministic v3 integration audit.
- `IntegrationReport` and `IntegrationCheck` are immutable and serializable.
- `si verify` and `si-verify` run the same audit locally or in CI.
- The audit checks required core/operator surfaces, canonical catalog shape, governance/organization configuration readability, deployment planning-only boundaries, packaging entry points, and current phase documentation.
- Missing or malformed inputs fail closed.
- Phase 42 deployment planning remains planning-only; an applied/deploy state or method is treated as an integration failure.
- The audit performs no agent, Skill, workflow, tool, shell, harness, credential, network, or external execution.
- Existing Control API, Web, TUI, evidence, governance, organization, and harness boundaries remain the single source of authority.

## Release hardening

The final release gate continues to require independent evidence for tests, lint, build, security review, migration review, and rollback testing. A missing gate cannot be inferred from another successful gate.

The integration audit is deliberately complementary to CI: it checks architectural consistency while CI verifies installation, packaging, lint, repository audit, and the complete automated test suite.

## Verification plan

1. Run the integration audit against the repository.
2. Build distributions and verify wheel installation.
3. Run the repository audit.
4. Run pinned Ruff.
5. Run the complete pytest suite, including adversarial integration tests.
6. Merge only after the feature branch gates are green.
7. Synchronize documentation and require a final mainline CI run on the documentation-closed commit.

## Security/adversarial coverage

- Missing required surfaces fail closed.
- Invalid canonical catalog shape fails closed.
- Deployment `APPLIED` state or apply/deploy method is rejected.
- Required operator entry points are checked in packaging metadata.
- The verification CLI returns non-zero when any integration check fails.
- No check has authority to execute downstream work.

## Completion gate

This phase is not considered complete until the implementation merge, documentation synchronization, and final mainline CI verification are all green.

## Next state

Phase 43 is the final v3 implementation phase. After closure, subsequent work should be treated as maintenance, defect fixes, security updates, or explicitly versioned post-v3 features rather than an unfinished v3 phase.

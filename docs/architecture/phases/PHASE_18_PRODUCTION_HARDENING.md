# Phase 18 — Production Hardening

## Objective

Make the completed SI-Agents platform release-ready without pretending that an application-level control is a host or infrastructure security boundary.

## Delivered

- Deterministic health/readiness checks with fail-closed exception handling.
- Explicit input/output/event/metadata/timeout resource limits.
- Conservative recursive redaction for secret-like keys and bearer credentials in telemetry representations.
- Evidence-based release gate covering tests, lint, build, security review, migration review, and rollback testing.
- Production policy declaring limits, telemetry rules, compatibility, recovery, and release requirements.
- Regression tests for readiness, resource boundaries, redaction, and release gating.
- CI hardening with least-privilege permissions, cancellation of superseded runs, and bounded job execution.

## Safety boundaries

Production hardening does not grant authorization. Phase 13 governance remains authoritative for credentials, sensitive egress, destructive/production actions, paid resources, and publication.

The local executor is not a security boundary. Docker isolation remains dependent on the Docker daemon and host configuration. Resource limits in this package are application-level validation and must not be described as kernel-level isolation.

Redaction is defense in depth, not proof that arbitrary secret material can never enter a process. Callers must classify and control sensitive data before external egress.

Readiness evidence is an acceptance gate, not a guarantee of future availability. Production operators still need monitoring, backups, incident response, dependency management, and infrastructure controls.

## Compatibility and migration

The package remains dependency-free and supports the project's declared Python baseline (`>=3.11`). Existing serialized formats are not silently migrated by this phase. Any future schema migration must be explicit, backward-compatible where required, tested against representative prior data, and paired with a rollback plan.

## Release acceptance

A production release should not be declared ready unless the release gate has evidence for:

1. tests passing;
2. lint passing;
3. distribution build passing;
4. security review complete;
5. migration review complete;
6. rollback behavior tested.

CI is required to pass on the final commit after all documentation and configuration changes.

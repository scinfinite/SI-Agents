# Automation

This directory contains Phase 15 automation artifacts and run-oriented documentation.

The executable automation engine lives under `core/automation/`. Jobs are declarative data; execution is limited to explicitly registered actions and passes through governance before an action runs.

Recommended automation categories include research refreshes, repository/security monitoring, maintenance, verification/test runs, and reporting/digests. External schedulers may trigger the engine later, but they are not required by the core design.

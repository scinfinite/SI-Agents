# Automation

This directory contains Phase 15 automation artifacts and run-oriented documentation.

The executable automation engine lives under `core/automation/`. Jobs are declarative data; execution is limited to explicitly registered actions and passes through governance before an action runs.

Recommended automation categories include research refreshes, repository/security monitoring, maintenance, verification/test runs, and reporting/digests. External schedulers may trigger the engine later, but they are not required by the core design.

## Current architecture boundary

Automation remains one subsystem of the completed v2.0/post-v2 foundation. Later organization, workflow, runtime, CLI, handoff, and persona layers compose with automation but do not make automation a policy authority. Phase 30 Skills will remain separately governed from automation jobs and actions.

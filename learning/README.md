# Controlled Learning

Phase 16 contains evidence-gated self-improvement artifacts. Learning is advisory until every required evaluation gate passes and a human-controlled approval step permits application.

The implementation lives under `core/learning/`. Capability intelligence ranks readiness but never grants execution permission. Improvement proposals require evidence, benchmark/regression/safety evaluation, explicit approval, and support rollback after application.

No component in this phase may silently rewrite code, promote capabilities to executable status, store secrets, or bypass governance.

## Current architecture boundary

Learning remains advisory and governed beneath the current organization/runtime layers. Agent personas, Skills, Rules, Memory, and future Control API/UI surfaces must not turn learning artifacts into automatic authority. Phase 30 Skills remain a separate, explicitly governed artifact layer.

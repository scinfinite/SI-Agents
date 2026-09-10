# Engineering Patterns

This directory is the durable artifact boundary for reusable engineering patterns produced by SI-Agents.

Patterns must retain provenance and verification state. A source observation is not automatically a validated pattern. Runtime extraction and promotion are implemented in `core/patterns/`.

Pattern artifacts should be organized by domain when they become durable enough to warrant storage, for example architecture, debugging, testing, security, databases, networking, distributed systems, DevOps, AI, and agent systems.

## Current architecture boundary

Patterns remain evidence-derived data, not policy or execution authority. Current agent personas, Skills, Rules, workflows, memory, and governance may consume validated patterns, but a pattern cannot grant permissions or authorize execution. Future Control API/Web/TUI surfaces must expose provenance and verification state rather than treating pattern matches as proof.

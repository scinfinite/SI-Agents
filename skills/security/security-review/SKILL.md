---
schema: si-agents.skill.v1
version: "1.0"
id: security-review
name: Security Review
category: security
status: validated
---

# Security Review

## Purpose
Inspect a proposed change for unsafe authority, data handling, execution, and trust-boundary behavior.

## Inputs
- change-scope
- configuration
- evidence

## Outputs
- security-findings
- remediation-guidance

## Prerequisites
- review scope is bounded
- artifacts are available for inspection

## Workflow
- inspect trust boundaries and requested authority
- identify secret-like content and unsafe execution paths
- evaluate fail-closed behavior
- record severity, evidence, and remediation

## Tools
- filesystem
- code-search

## Capabilities
- filesystem_read
- repository_read

## Permissions
- repository_read

## Verification
- findings include evidence
- dangerous paths are denied or explicitly governed

## Failure Behavior
- stop on incomplete evidence for high-risk claims
- escalate unresolved critical findings

## Evidence Requirements
- each finding references the inspected artifact
- secrets are never copied into findings

## Examples
- review a Skill artifact
- review a deployment manifest

## Compatibility
- si-core | governance | 1.x

## Provenance
SI-native security procedure authored for the SI-Agents Skill contract; independently designed around least authority and fail-closed review.

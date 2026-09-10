---
schema: si-agents.skill.v1
version: "1.0"
id: verify-change
name: Verify Change
category: testing
status: validated
---

# Verify Change

## Purpose
Determine whether a change is correct using targeted, regression, and adversarial evidence.

## Inputs
- workspace
- change-scope
- test-plan

## Outputs
- verification-result
- evidence-set

## Prerequisites
- change scope is known
- expected behavior is testable

## Workflow
- run targeted checks
- run relevant regression checks
- run adversarial or fail-closed checks where applicable
- inspect all outputs before declaring success

## Tools
- test-runner
- linter

## Capabilities
- local_command
- filesystem_read

## Permissions
- local_command

## Verification
- required checks pass
- failures are surfaced rather than suppressed

## Failure Behavior
- return failed verification with diagnostics
- never convert an inconclusive result into success

## Evidence Requirements
- record commands, outcomes, and relevant artifacts
- identify remaining uncertainty

## Examples
- verify a parser change
- verify a governance boundary

## Compatibility
- si-core | runtime | 1.x

## Provenance
SI-native verification procedure authored for the SI-Agents Skill contract; independently designed around evidence-first engineering.

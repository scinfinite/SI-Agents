---
schema: si-agents.skill.v1
version: "1.0"
id: reproduce-failure
name: Reproduce Failure
category: debugging
status: validated
---

# Reproduce Failure

## Purpose
Turn a reported defect into the smallest safe and repeatable reproduction.

## Inputs
- workspace
- reproduction-command

## Outputs
- reproduction-result
- diagnostic-evidence

## Prerequisites
- expected behavior is stated
- execution scope is bounded

## Workflow
- identify the expected failure
- execute the smallest reproducible case
- capture output, environment, and relevant diagnostics
- distinguish reproduced, disproved, and inconclusive outcomes

## Tools
- terminal
- test-runner

## Capabilities
- local_command
- filesystem_read

## Permissions
- local_command

## Verification
- expected failure is reproduced or explicitly disproved
- reproduction can be repeated from recorded inputs

## Failure Behavior
- stop when execution would exceed the approved scope
- record inability to reproduce as evidence

## Evidence Requirements
- preserve the reproduction command and result
- redact secrets and sensitive values from diagnostics

## Examples
- reproduce a failing unit test
- isolate a runtime regression

## Compatibility
- si-core | runtime | 1.x

## Provenance
SI-native debugging procedure authored for the SI-Agents Skill contract; independently designed around bounded reproduction and evidence capture.

---
schema: si-agents.skill.v1
version: "1.0"
id: inspect-repository
name: Inspect Repository
category: engineering
status: validated
---

# Inspect Repository

## Purpose
Establish a bounded, evidence-backed view of a repository before changing it.

## Inputs
- workspace
- target

## Outputs
- inspection
- evidence-summary

## Prerequisites
- readable workspace
- target scope identified

## Workflow
- identify repository root and project metadata
- inspect relevant source, configuration, tests, and documentation
- record observed facts, unknowns, and evidence locations

## Tools
- filesystem
- code-search

## Capabilities
- filesystem_read
- repository_read

## Permissions
- repository_read

## Verification
- inspection contains target evidence
- unknowns are explicitly recorded

## Failure Behavior
- stop when the workspace cannot be safely inspected
- report incomplete access instead of guessing

## Evidence Requirements
- source paths and observed facts are recorded
- no claim is promoted without supporting evidence

## Examples
- inspect a new repository before implementation
- inspect a regression area before reproducing a failure

## Compatibility
- si-core | runtime | 1.x

## Provenance
SI-native engineering procedure authored for the SI-Agents Skill contract; independently designed from general evidence-first repository inspection practices.

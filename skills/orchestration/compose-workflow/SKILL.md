---
schema: si-agents.skill.v1
version: "1.0"
id: compose-workflow
name: Compose Workflow
category: orchestration
status: validated
dependencies: [inspect-repository, verify-change]
---

# Compose Workflow

## Purpose
Combine validated Skills into an explicit dependency-aware procedure without changing their authority.

## Inputs
- skill-set
- objective

## Outputs
- composed-plan
- dependency-graph

## Prerequisites
- referenced Skills are validated
- dependency identifiers resolve

## Workflow
- load selected Skills from the registry
- validate every dependency
- construct a deterministic dependency graph
- preserve each Skill's verification and governance boundaries

## Tools
- skill-registry
- workflow-planner

## Capabilities
- filesystem_read
- repository_read

## Permissions
- repository_read

## Verification
- all dependencies resolve
- composition order is deterministic
- no Skill grants authority to another Skill

## Failure Behavior
- reject missing or cyclic dependencies
- preserve the original Skills when composition fails

## Evidence Requirements
- record selected Skill IDs and versions
- record dependency relationships and verification state

## Examples
- inspect then verify a repository change
- compose a diagnostic and validation workflow

## Compatibility
- si-core | runtime | 1.x

## Provenance
SI-native composition procedure authored for the SI-Agents Skill contract; independently designed as explicit dataflow over governed reusable procedures.

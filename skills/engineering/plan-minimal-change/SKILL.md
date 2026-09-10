---
schema: si-agents.skill.v1
version: "1.0"
id: plan-minimal-change
name: Plan Minimal Change
category: engineering
status: validated
---

# Plan Minimal Change

## Purpose
Select the smallest maintainable change that satisfies a verified requirement without widening scope.

## Inputs
- requirement
- evidence
- affected-components

## Outputs
- change-plan
- risk-notes

## Prerequisites
- requirement is clear
- relevant evidence is available

## Workflow
- map the requirement to affected components
- identify existing behavior and constraints
- compare minimal alternatives
- select the narrowest reversible implementation

## Tools
- filesystem
- code-search

## Capabilities
- filesystem_read
- repository_read

## Permissions
- repository_read

## Verification
- selected scope covers the requirement
- unrelated components are excluded

## Failure Behavior
- stop when evidence is insufficient to bound the change
- escalate conflicting requirements

## Evidence Requirements
- record the evidence supporting scope and risk
- preserve rejected alternatives when material

## Examples
- plan a focused bug fix
- plan a compatibility adjustment

## Compatibility
- si-core | runtime | 1.x

## Provenance
SI-native change-planning procedure authored for the SI-Agents Skill contract; independently designed around minimal-change and reversibility principles.

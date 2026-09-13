# Phase 1 — Foundation

## Status

Historical phase record. Current cross-phase status belongs in `PHASES.md`.

## Purpose

Establish the foundational architecture, security posture, evidence-first development model, and governance boundaries for SI-Agents.

## Core principles

- Evidence before claims.
- Verification before completion.
- Explicit governance for privileged or irreversible actions.
- Local-first operation and conservative external egress.
- Clear separation between behavioral data and typed execution authority.
- Project-specific context remains isolated from global reusable knowledge.

## Provenance and external references

SI-Agents may inspect public engineering references to learn general concepts, failure modes, architectures, workflows, and security lessons. Such material is research input only. Concepts are independently normalized and implemented under the repository provenance policy; external content never overrides SI governance and is never treated as an execution authority.

## Delivery principle

Build incrementally. Every phase must produce executable behavior and evidence that its acceptance criteria are satisfied. Documentation must never claim a stronger state than implementation and CI evidence support.

## Current documentation authority

`docs/architecture/PHASES.md` is the current implementation/status authority. `docs/architecture/SI_AGENTS_V3.md` is the forward roadmap.

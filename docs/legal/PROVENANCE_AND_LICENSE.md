# SI-Agents — Provenance and License Controls

## Purpose

This document records the repository's engineering controls for copyright, licensing, trademark, provenance, and external-reference risk. It is not legal advice and cannot guarantee that no third party will ever assert a claim.

## Current controls

1. SI-Agents-owned implementation is independently maintained in `scinfinite/SI-Agents`.
2. External repositories are treated as research input for general engineering patterns, not as source code or prompt authorities.
3. Distinctive third-party code, persona prose, prompts, documentation passages, logos, and artwork are not intended to be copied into SI-Agents.
4. External project branding is excluded from shipped implementation and operational documentation unless it identifies an actual integration.
5. OpenCode and OmniRoute remain named because they are supported integration boundaries.
6. Persona text is repository-owned configuration and is checked for hidden Unicode control characters and structural validity.
7. Dependency and distribution work must preserve each dependency's license rather than assuming the project license applies to dependencies.
8. The project license for SI-Agents-owned work is Apache-2.0.

## External-reference cleanup

The implementation should contain no unnecessary names or branding from projects that served only as inspiration. Current repository hygiene checks reject known external-reference branding in operational surfaces. Historical provenance records must remain repository-neutral.

## What the legal audit can establish

The repository audit can establish engineering controls such as:

- whether known external names remain in code/docs;
- whether license files and notices exist;
- whether dependencies have recorded licenses;
- whether persona files contain copied-looking external branding or hidden controls;
- whether package artifacts include required project notices;
- whether external integrations are clearly bounded.

The audit cannot establish:

- that no person could ever bring a lawsuit;
- that no patent, trademark, contract, publicity, or other claim exists;
- that every jurisdiction treats the same facts identically;
- that every third-party dependency is safe merely because it is open source.

## Distribution rule

Before publishing an artifact:

- run repository hygiene;
- run license/provenance audit;
- inspect the distribution manifest;
- verify bundled third-party notices;
- verify that credentials and private files are absent;
- review npm/Python package metadata;
- obtain human release approval.

## Legal research basis

The U.S. Copyright Office explains that copyright protects original expression but does not protect ideas, systems, methods, or procedures as such. India’s Copyright Office likewise explains that copyright protects expression rather than ideas and that copyright is automatic. GitHub's DMCA policy explains the platform's notice-and-takedown process and recommends professional legal advice for legal matters.

Those principles support an engineering distinction between learning general engineering ideas and copying protected expression. They do not eliminate all legal risk.

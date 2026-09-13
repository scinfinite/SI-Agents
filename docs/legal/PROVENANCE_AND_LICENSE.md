# Provenance, Licensing, and Legal-Risk Controls

## Scope

This document defines repository controls intended to reduce intellectual-property and provenance risk. It is an engineering control document, not legal advice or a guarantee against claims.

## Authorship policy

SI-Agents code, prompts, persona text, documentation, UI copy, schemas, examples, and tests should be independently authored. Public repositories may be inspected to understand general engineering patterns, but SI-Agents must not intentionally copy their implementation, prompts, distinctive documentation, branding, or other expressive material.

Ideas, methods, interfaces, and functional concepts may have different legal treatment from expressive implementation and documentation. The project therefore uses independent implementation and provenance records rather than assuming that a similar feature is itself unlawful or automatically safe.

The U.S. Copyright Office states that copyright in computer programs covers copyrightable expression, while functional aspects such as algorithms, formatting, functions, logic, and system design are not protected by copyright in the same way. This does not resolve every jurisdiction, license, trademark, patent, or contractual issue. See the official Copyright Office material before making legal conclusions. urlCopyright Office — Circular 61https://www.copyright.gov/circs/circ61.pdf?loclr=blogcop

## Repository controls

1. **Branding hygiene:** unnecessary third-party project names are not permitted in operational code, prompts, persona content, package metadata, or product copy.
2. **Integration exceptions:** OpenCode and OmniRoute may be named where they are real SI-Agents integration boundaries.
3. **License review:** new dependencies require license review before adoption.
4. **Attribution:** required third-party notices must be retained where a dependency or permitted source requires them.
5. **Originality attestation:** contributors must have the right to submit their contribution.
6. **No secret/proprietary imports:** credentials, private source, paid-only material, or confidential documents must not be imported into the repository.
7. **No prompt copying:** external prompts and persona text are research references, not templates for verbatim reuse.
8. **No deceptive affiliation:** SI-Agents must not imply endorsement, sponsorship, ownership, or affiliation with unrelated projects.
9. **Automated scanning:** repository hygiene tests reject forbidden external branding outside explicitly allowed integration references.
10. **Review before release:** release artifacts must pass provenance, license, dependency, and packaging checks.

## License

SI-Agents-owned material is distributed under the Apache License 2.0. The project must retain the full `LICENSE` text and a `NOTICE` file where required. Apache's own release guidance requires the full license text and appropriate notice handling for Apache-licensed distributions. urlApache License 2.0 release guidancehttps://apache.org/legal/release-policy.html

The Apache License includes copyright and patent grants subject to its terms, but it does not guarantee that a recipient can never face a third-party claim. urlApache License 2.0https://www.apache.org/licenses/LICENSE-2.0

## Contribution provenance

Contributors should sign off commits using the repository's contribution process and confirm that they have the right to submit the work. Large or externally sourced contributions require explicit provenance review before merging.

## Third-party integration boundaries

OpenCode and OmniRoute are integration targets, not sources of copied implementation. SI-Agents should depend only on their documented public interfaces and should not bundle their proprietary source or redistribute their assets unless their license explicitly permits it.

## Legal escalation

If a real copyright, trademark, patent, license, DMCA, ownership, employment, contractor, or confidentiality concern is raised, freeze distribution of the affected material and obtain qualified legal review. Do not attempt to solve a legal dispute by silently deleting evidence or rewriting history.

## Risk statement

These controls can substantially reduce avoidable IP/provenance risk, but no software project can truthfully promise that no person or company can file a claim. The project's goal is independent authorship, clean provenance, license compliance, truthful attribution, and prompt legal escalation when a real issue appears.

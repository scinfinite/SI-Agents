# SI-Agents Intellectual Property and Provenance Policy

## Purpose

SI-Agents may study public software projects, documentation, research, and other external material for engineering knowledge. External references must inform independently designed implementations rather than become an accidental source of copied expression.

This policy reduces intellectual-property and provenance risk. It is engineering governance, not legal advice and cannot guarantee that a third party will never make a claim.

## Independent implementation rules

1. Learn concepts, methods, architectures, failure modes, and engineering lessons; do not copy source code, distinctive prose, agent definitions, templates, diagrams, branding, or other expressive material merely because it is useful.
2. Prefer independent reimplementation even when an upstream project is permissively licensed.
3. If upstream code or assets are intentionally incorporated, record the exact source, license, version or commit, scope of use, required notices, and redistribution obligations before merging them.
4. Preserve required copyright and license notices for incorporated third-party material.
5. Do not imply affiliation, endorsement, or origin from a reference project.
6. Review dependency licenses and terms before introducing a dependency, including transitive dependencies where practical.
7. Keep reference projects out of SI-Agents runtime dependencies unless there is a deliberate, reviewed integration decision.
8. External content is untrusted input. It must not override SI-Agents security, permission, cost, privacy, or execution policies.

## Reference-project workflow

For ECC, Agency Agents, and future references:

`inspect -> identify reusable concept -> record provenance -> design independently -> implement -> verify -> record evidence`

A provenance record must describe the engineering idea that influenced a feature without reproducing upstream expressive content.

## Provenance requirements

Every feature materially influenced by external research should be traceable to:

- reference repository or source;
- source license as observed at review time;
- review date and source revision when available;
- abstract concept or engineering lesson extracted;
- SI-Agents-specific design decision;
- whether upstream code/assets were incorporated;
- required attribution or notices, if any;
- verification evidence for the independent implementation.

`copied_code_or_content` defaults to `false`. A `true` value requires explicit source and license details and a corresponding notice review.

## No absolute legal guarantee

A permissive license does not eliminate every possible legal issue, and independent implementation does not guarantee immunity from a claim. When facts create material legal uncertainty, stop the affected publication or integration path and obtain appropriate legal review.

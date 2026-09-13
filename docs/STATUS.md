# SI-Agents Current Status

**Repository:** `scinfinite/SI-Agents`  
**Current V4 baseline:** Phases 44–68 closed  
**Current hardening work:** 300 personas, capacity safety, Termux guidance, provenance/legal hygiene, documentation organization  
**Next planned phase:** Phase 69 — npm Distribution + Setup

## Current work completed in this hardening cycle

- Added repository-owned capacity policy with Low / Medium / High levels.
- Termux Low and bounded Medium work are permitted; High work and local compilation are blocked.
- Desktop and Codespace are the preferred targets for High work.
- Added capacity tests for classification and target admission.
- Expanded the runtime persona catalog to **300 personas across 18 divisions** using repository-owned catalog extensions.
- Updated persona parity to verify the 300-persona invariant.
- Added 21 newly authored persona files.
- Added a systematic `docs/phases/` navigation/archive surface for Phases 1–68 while retaining historical architecture paths for compatibility.
- Expanded `AGENTS.md` as the primary agent operating contract.
- Added `SIA_SPECS.md` as the complete current system specification.
- Added Termux runtime and capacity documentation.
- Added provenance/license controls and repository-neutral external-branding hygiene.
- Added Apache-2.0 licensing for SI-Agents-owned work.
- Preserved OpenCode and OmniRoute as explicit supported integrations.

## Verification boundary

Static repository and CI checks can verify contracts, code paths, package contents, and environment detection. They cannot prove every Android device's thermal behavior. Real-device Termux validation remains hardware-specific.

Likewise, repository hygiene can materially reduce copyright/provenance risk but cannot guarantee that no third party could ever assert a legal claim. Ambiguous ownership, patent, trademark, or jurisdictional questions must be escalated to professional legal counsel.

## Distribution target

The intended npm command is:

```bash
npx si-agents
```

Persistent global installation:

```bash
npm install -g si-agents
```

The repository can prepare and verify the npm artifact; registry publication requires the project owner's npm authentication/trusted-publishing configuration.

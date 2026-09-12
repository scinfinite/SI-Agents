# SI-Agents Web Control Center — Production Design

**Status:** Approved and implemented on `main`.

## Visual direction

The Web Control Center is the visual reference for SI-Agents product surfaces: dark navy surfaces, restrained blue/teal/purple status accents, compact operator typography, dense but readable cards/tables, rounded controls, clear status badges, and a responsive sidebar/header shell.

The interface has two supported themes:

- **Dark:** default high-contrast operator console for continuous use.
- **Light:** full light-surface equivalent with the same information hierarchy and semantic status colors.

The selected theme is stored locally as `si-agents-theme`; first visit follows the operating-system `prefers-color-scheme` preference.

## Screen contract

The production navigation preserves the complete Control Center read surface:

- Overview
- Runs
- Agents
- Teams
- Workflows
- Topology / Visualization
- Skills
- Memory
- Knowledge
- Evidence
- Organization
- Governance
- Environments
- Harnesses
- Settings

Every screen remains a client of the existing versioned Control API. No screen executes agents, workflows, tools, shell commands, or providers directly.

## Interaction contract

- Responsive sidebar collapses into an accessible mobile navigation drawer.
- Global search searches already-loaded data first and then queries the supported resource surfaces when necessary.
- Collection screens provide bounded client-side filtering without changing server authority.
- Overview hydrates live snapshot, health, runs, and events data in parallel.
- Refresh invalidates the client cache and rehydrates the current screen.
- Notifications route to the evidence surface.
- Profile routes to settings; help explains the authority boundary.
- Topology supports organization/workflow/capability views, node filtering, keyboard node selection, metadata inspection, pan, zoom, and reset.
- Reduced-motion users receive the same functional surface without unnecessary transitions.
- All controls expose visible keyboard focus and semantic labels.

## Safety and authority

The browser remains a presentation/control adapter. SI Core and the Control API remain authoritative for execution, lifecycle, governance, evidence, and state. The browser stores only presentation preference and ephemeral cached read data; authentication and authorization remain server-side concerns.

## Implementation

- `core/web/assets/index.html` — application shell and accessible controls.
- `core/web/assets/app.css` — responsive design system and light/dark themes.
- `core/web/assets/app.js` — navigation, data hydration, filtering, search, theme persistence, and topology interaction.
- `tests/unit/test_phase69_web_ui.py` — asset contract, JavaScript syntax, and server reachability regression coverage.

No external frontend framework or CDN dependency was introduced.

## Verification

The implementation was reviewed as a production UI change and merged through PR #82. The repository CI and post-merge mainline CI remain the release gates for the synchronized tree.

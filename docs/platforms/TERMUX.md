# SI-Agents on Termux

Termux is a supported lightweight execution environment for SI-Agents. It is intended for inspection, editing, lightweight agent workflows, and bounded local execution.

## Capacity profiles

| Profile | Termux workers | Typical use | Mobile policy |
|---|---:|---|---|
| Low | 1–2 | inspection, editing, small analysis | allowed |
| Medium | 3–5 | bounded multi-agent work | allowed with warning |
| High | blocked | compilation, native builds, large benchmarks, release work | use Desktop/Codespace |

The user selects workers within the profile. SI-Agents rejects values outside the profile's range.

Examples:

```bash
SI_CAPACITY=low SI_WORKERS=1 si-capacity
SI_CAPACITY=low SI_WORKERS=2 si-capacity
SI_CAPACITY=medium SI_WORKERS=3 si-capacity
SI_CAPACITY=medium SI_WORKERS=5 si-capacity
```

For JSON:

```bash
SI_CAPACITY=medium SI_WORKERS=4 si-capacity --json
```

## Heavy work

Compilation, native builds, container builds, large benchmarks, and full-release builds are classified as heavy workloads. On Termux/mobile they are denied by policy and the user is directed to Desktop or Codespace.

## OpenCode + OmniRoute

OpenCode can be used as a harness/integration layer and OmniRoute can remain the model/provider routing layer. SI-Agents keeps its own governance and execution boundaries. Capacity policy limits SI-controlled concurrency; it does not attempt to control every process launched by an external harness or provider.

## Heating and battery safety

SI-Agents intentionally avoids promising that a phone will never heat. Device temperature depends on hardware, Android/Termux scheduling, background processes, OpenCode, OmniRoute, model/provider activity, network use, and thermal management outside SI-Agents' authority.

The practical safety controls are therefore:

- bounded workers;
- no High capacity on Termux;
- heavy-workload blocking;
- explicit warnings;
- remote/Desktop/Codespace escalation for expensive work.

If the device becomes hot, stop the workload and move the task to Desktop/Codespace.

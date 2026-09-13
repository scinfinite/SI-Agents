# SI-Agents on Termux

## Supported role

Termux is a supported constrained runtime for SI-Agents. It is suitable for Low and bounded Medium work. High-capacity work is intentionally redirected to a desktop or Codespace.

## Recommended stack

- Termux with Python 3.11+.
- Git, curl, and SSH when required by the selected workflow.
- OpenCode when an OpenCode workflow is selected.
- OmniRoute when model/provider routing is selected.
- SI-Agents installed from the supported Python distribution or local checkout.

## Capacity policy

| Level | Termux | Typical examples |
|---|---|---|
| Low | Allowed; one worker | status, inspection, documentation, small edits |
| Medium | Allowed; bounded to two workers | lint, short tests, code review, small analysis |
| High | **Blocked locally** | compilation, large builds, full benchmarks, large indexing, code generation, migrations |

If a task is high capacity, use a desktop or Codespace target rather than overriding the policy.

## OpenCode + OmniRoute + SI-Agents

The three components can coexist because they have separate responsibilities:

- SI-Agents controls governance, capacity, workflows, evidence, and operator state.
- OpenCode remains the coding-agent/harness surface.
- OmniRoute remains model/provider routing.

Avoid running multiple heavy local model processes concurrently on a phone. A Low or Medium SI-Agents selection does not make an external process thermally free.

## Thermal-safety limitation

SI-Agents deliberately bounds its own local work, but software cannot guarantee a phone will never heat. Thermal behavior depends on the device, kernel, battery state, ambient temperature, OpenCode, OmniRoute, model/provider behavior, and other applications.

The safe engineering rule is therefore **load reduction + high-work offload**, not a false temperature guarantee.

## Verification

Static CI can verify Termux compatibility contracts, environment detection, command assumptions, and capacity admission. It cannot prove behavior on every physical Android device. Real-device verification should be performed separately when hardware-specific confidence is required.

## Suggested commands

```bash
python -m tools.persona_parity_audit
python -m pytest -q
si --help
```

For heavy work, move the repository/workflow to Codespaces or a desktop host before compiling or running sustained benchmarks.

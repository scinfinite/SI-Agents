# Capacity Policy

SI-Agents uses an explicit device-aware capacity policy to prevent accidental over-parallel execution on constrained hosts.

## Profiles

- **Low:** Termux/mobile 1–2 workers.
- **Medium:** Termux/mobile 3–5 workers.
- **High:** Desktop/Codespace only; Termux/mobile is blocked.

Workers are user-selectable inside the allowed range.

## Runtime enforcement

`core/capacity/policy.py` resolves the profile. The runtime scheduler and team executor clamp their effective concurrency to the resolved worker count. Heavy workload keywords such as compilation, native builds, container builds, large benchmarks, and release builds are denied on Termux/mobile.

## Configuration

```text
SI_CAPACITY=low|medium|high
SI_WORKERS=<integer>
```

`si-capacity` provides a read-only operator view of the resulting decision.

## Safety boundary

The policy limits SI-controlled work; it does not provide hardware thermal control and therefore does not guarantee a particular phone or desktop temperature. High-cost work should be moved to Desktop/Codespace when the local host is unsuitable.

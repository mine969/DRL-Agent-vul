# Tuned Action Space

This project keeps two related action representations in `env/web_sec_env.py`.

## Full vs Mock Action Spaces

| Space | Size | Purpose |
| --- | --- | --- |
| Full action book | 150 actions | Broad taxonomy and extensibility |
| Mock-target action space | 50 actions | Practical subset used by current scanner/training flow |

The 50-action mode maps each action ID through `mock_action_map` into selected full-book actions.

## Why the 50-Action Mapping Exists

- Faster convergence on the five local mock targets.
- Better signal-to-noise during training.
- More predictable behavior in current scan runs.

## High-Level Mapping Shape

- `0-24`: navigation, endpoint probing, and authentication checks.
- `25-29`: core IDOR-oriented actions.
- `30-32`: SQL injection-focused actions.
- `33-36`: XSS-focused actions.
- `37-43`: command injection, SSRF, traversal, deserialization, SSTI, CSRF, logic checks.
- `44-49`: selected advanced behavior mappings (for example auth-flow and header/token variants).

## Important Runtime Truth

Current scanner audit execution uses environment `mode="mock_targets"` in `autonomous_scan.py`, so this 50-action mapping is the active policy surface in default scans.

## Full 150-Action Book Status

- Exists in the environment implementation.
- Useful for research and future extension.
- Not directly exposed as a user-selectable scanner mode flag today.

## Practical Implication

When documenting scanner behavior, describe current runs as 50-action mapped execution with selected advanced actions, not as full unrestricted 150-action runtime.

# Enhanced Action Space Notes

This file clarifies the action-space design in `env/web_sec_env.py`.

## Action-Space Reality

- Full environment action book: 150 actions.
- Mock-target runtime action space: 50 actions.
- Scanner audit path currently uses mock-target mode.

## Full Action Taxonomy (Implementation)

The 150-action book includes ranges for:

- reconnaissance/navigation
- endpoint and auth probing
- IDOR and access-control patterns
- SQLi/XSS/file/path/CSRF/SSTI/command families
- logic and race-condition checks
- additional advanced auth and bypass-oriented actions

## Runtime Behavior in Current Scans

- `autonomous_scan.py` initializes `WebSecEnv(..., mode="mock_targets")`.
- Action IDs selected by the agent are translated through `mock_action_map`.
- This keeps scanner behavior aligned with tuned local-target training.

## Why This Matters for Documentation

- It is accurate to say the codebase contains a 150-action book.
- It is also necessary to state that default scanner execution currently uses the 50-action mapped subset.

## Extension Path

If you want full-book runtime experimentation, you need custom integration changes to scanner flow (environment mode selection, evaluation harness, and validation updates).

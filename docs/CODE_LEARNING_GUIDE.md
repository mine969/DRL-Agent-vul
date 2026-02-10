# Code Learning Guide

Use this path to understand the codebase quickly and in the right order.

## Suggested Reading Order

1. `easy_scanner.py`
2. `scanner_gui.py`
3. `autonomous_scan.py`
4. `env/web_sec_env.py`
5. `agent/improved_dqn_agent.py`
6. `utils/report_generator.py`
7. `train_mock_targets.py` and `quick_train_5000.py`

## What to Look For in Each File

## `easy_scanner.py`

- Interactive flow and `--auto` argument parsing.
- Command construction for launching `autonomous_scan.py`.

## `scanner_gui.py`

- UI controls and scan profile handling.
- `run_automated_mode(...)` for headless `--auto` behavior.

## `autonomous_scan.py`

- `WebsiteExplorer` crawl/probe behavior.
- `SecurityAuditor.start_audit(...)` phase orchestration.
- CLI flag handling in `main()`.

## `env/web_sec_env.py`

- Observation vector definition (15 dimensions).
- Full action book and mock-target mapping.
- Reward shaping and environment step loop.

## `agent/improved_dqn_agent.py`

- Prioritized replay implementation.
- Noisy linear layers and dueling network heads.
- Replay update logic and checkpoint save/load format.

## Fast Learning Exercises

1. Run `python easy_scanner.py --help` and map each flag to code.
2. Trace how `scanner_gui.py --auto` turns into an `autonomous_scan.py` subprocess call.
3. Follow one finding from environment step output to Markdown report generation.

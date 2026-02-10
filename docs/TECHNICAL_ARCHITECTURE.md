# Technical Architecture

This document describes the implementation-level architecture currently used by the scanner.

## Runtime Flow

```text
User entrypoint
  -> easy_scanner.py / scanner_gui.py / autonomous_scan.py
  -> SecurityAuditor (autonomous_scan.py)
  -> WebsiteExplorer + WebSecurityGym + ImprovedDQNAgent
  -> Finding validation and filtering
  -> Markdown report in reports/
```

## Core Components

## 1) Scanner Engine (`autonomous_scan.py`)

- `WebsiteExplorer` crawls target pages and probes common endpoints.
- `SecurityAuditor.start_audit(...)` orchestrates recon, attack loop, filtering, persistence retry, and report output.
- CLI arguments:
  - positional `url`
  - `--depth`
  - `--intensity`
  - `--model`
  - `--persist`
  - `--ai-mode`
  - `--pentester`

## 2) Environment (`env/web_sec_env.py`)

- Gym-style environment class: `WebSecurityGym` (aliased as `WebSecEnv`).
- Observation/state vector size: 15.
- Full action book size: 150.
- Mock-target mode action space: 50 actions via `mock_action_map` into selected full-book actions.

Important: the current audit path initializes environments with `mode="mock_targets"`.

## 3) Agent (`agent/improved_dqn_agent.py`)

- `ImprovedDQNAgent` uses:
  - Prioritized replay buffer
  - Noisy linear layers for exploration
  - Dueling network heads
  - Double DQN target computation
  - Optional n-step returns (default configured as `n_step=1` in training script)
- Networks and optimizer states are checkpointable via `save()` / `load()`.

## 4) Validation and Reporting (`utils/`)

- `utils/validator.py`: vulnerability-specific second-pass checks.
- `utils/false_positive_filter.py`: applied in non-AI mode in scanner pipeline.
- `utils/report_generator.py`: default path generates Markdown report (`generate_md_report`).

## Frontend Wrappers

## Easy CLI (`easy_scanner.py`)

- Interactive mode by default.
- Optional non-interactive mode with `--auto` and argument overrides.
- Builds and executes `autonomous_scan.py` commands.

## GUI (`scanner_gui.py`)

- Interactive Tk interface for selecting target, profile, depth, intensity, model, persistence.
- Headless mode (`--auto`) builds a subprocess call to `autonomous_scan.py`.

## Architecture Truth Matrix

| Topic | Current state |
| --- | --- |
| Targetless mode as scanner CLI flag | Not implemented |
| Zero-day mode as scanner CLI flag | Not implemented |
| Proxy/stealth scanner flags | Not implemented in entrypoints |
| `target_hunter` / `zero_day_hunter` modules | Present as module-level capabilities |
| Default scan report format | Markdown |

## Operational Implications

- Best-supported workflow remains local mock-target scanning and training.
- External target scans are possible but still run through the mock-target action subset and require manual validation.

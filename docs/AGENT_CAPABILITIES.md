# Agent Capabilities

This document describes capabilities that are implemented in the current codebase.

## Implemented Capabilities

## 1) Recon and Endpoint Discovery

- Crawls target pages from a start URL.
- Follows discovered links and probes common endpoints.
- Tracks discovered URL set for later attack passes.

## 2) AI-Driven Action Selection

- Uses `ImprovedDQNAgent` for action selection.
- Supports non-AI and AI-driven modes (`--ai-mode`).
- Supports deeper chain behavior (`--pentester`).

## 3) Attack Execution and Validation

- Executes mapped vulnerability actions through `WebSecurityGym`.
- Performs validator checks (`utils/validator.py`) for stronger confidence.
- Applies false-positive filtering in non-AI mode (`utils/false_positive_filter.py`).

## 4) Persistence and Retry

- Optional persistence loop with progressive retry intensity via `--persist`.

## 5) Reporting

- Writes Markdown reports to `reports/vulnerability_report_<timestamp>.md`.
- Includes finding evidence fields when available (status, reward, snippet, flags).

## 6) User-Facing Modes

- Interactive CLI (`easy_scanner.py` / `scripts/easyscan.py`).
- Interactive GUI (`scanner_gui.py`).
- Headless wrappers (`easy_scanner.py --auto`, `scanner_gui.py --auto`).

## Present but Not Exposed as Scanner Mode Flags

- `utils/target_hunter.py`
- `utils/zero_day_hunter.py`
- `utils/proxy_fetcher.py`

These modules exist, but default scanner entrypoints do not currently provide mode flags such as `--mode targetless` or `--mode zeroday`.

## Practical Capability Boundary

- Best performance and reliability are on the built-in local mock targets.
- External targets can be scanned, but results must be manually validated in authorized contexts.

# Project Overview

This repository is an AI-assisted web vulnerability scanning project built around a reinforcement learning agent and five local mock targets.

## Primary Entry Points

- `python easy_scanner.py` (interactive CLI)
- `python easyscan.py` (compatibility alias)
- `python scanner_gui.py` (interactive GUI)
- `python scanner_gui.py --auto --target http://localhost:5002` (headless GUI automation)
- `python autonomous_scan.py <url> --depth ... --intensity ... [--persist --ai-mode --pentester]` (core scanner)

## What Is Implemented Today

- Autonomous crawl and attack workflow (`autonomous_scan.py`).
- AI agent execution using `ImprovedDQNAgent` and `WebSecurityGym`.
- Local mock target training (`train_mock_targets.py`, `quick_train_5000.py`).
- Markdown report generation in `reports/`.
- Two user-facing wrappers (`easy_scanner.py`, `scanner_gui.py`) with optional non-interactive modes.

## Current Truth Matrix

| Capability | Status | Notes |
| --- | --- | --- |
| Interactive CLI scanner | Implemented | `easy_scanner.py` and `easyscan.py` |
| GUI scanner | Implemented | `scanner_gui.py` |
| Headless GUI automation | Implemented | `scanner_gui.py --auto` |
| Core scanner CLI flags (`--depth`, `--intensity`, `--persist`, `--ai-mode`, `--pentester`) | Implemented | `autonomous_scan.py` |
| Targetless CLI mode (`--mode targetless`) | Not implemented as scanner flag | `utils/target_hunter.py` exists as a module |
| Zero-day scanner mode (`--mode zeroday`) | Not implemented as scanner flag | `utils/zero_day_hunter.py` exists as a module |
| Built-in proxy/stealth scanner flags | Not implemented in scanner entrypoints | `utils/proxy_fetcher.py` exists as helper module |

## Default Training/Scan Targets

`start_services.py` launches these local applications:

| Target | URL |
| --- | --- |
| E-Commerce Platform | `http://localhost:5002` |
| Social Media Platform | `http://localhost:5003` |
| Banking Application | `http://localhost:5004` |
| Blog Platform | `http://localhost:5005` |
| File Sharing Platform | `http://localhost:5006` |

These targets are intentionally vulnerable and are the most reliable environment for this project.

## Important Runtime Detail

The current `autonomous_scan.py` audit flow creates environments in `mode="mock_targets"`. In practice, that means scanning uses the tuned 50-action policy mapping even when you provide non-local URLs.

## Reports

- Main scan path writes Markdown reports: `reports/vulnerability_report_<timestamp>.md`.
- HTML/TXT helpers exist in `utils/report_generator.py`, but the default scan path uses Markdown generation.

## Recommended Use

- Use local mock targets for training, benchmarking, and behavior validation.
- Use authorized external targets with caution and manual verification.
- Treat findings as analyst-reviewed security signals, not automatic production verdicts.

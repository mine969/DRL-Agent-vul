# Project Structure

This map focuses on the files and folders that drive current behavior.

## Top-Level Layout

```text
.
|-- easy_scanner.py
|-- easyscan.py
|-- scanner_gui.py
|-- autonomous_scan.py
|-- start_services.py
|-- config.py
|-- training/
|   |-- train_mock_targets.py      # primary training entry point (Extended D3QN, 3k eps default)
|   |-- train_ablation.py           # per-(variant,seed) ablation trainer -- Reviewer 1 gate
|   |-- evaluate_variant.py         # deterministic eval for one (variant,seed)
|   |-- stats_ablation.py           # Friedman + Wilcoxon across ablation results
|   |-- run_ablation_suite.py       # single command: all variants x seeds, training+eval+stats
|   |-- training_logger.py         # per-episode/per-finding CSV logging
|   `-- plot_curve.py              # renders real reward/loss curve from logged CSVs
|-- agent/
|   |-- improved_dqn_agent.py      # run standalone: python agent/improved_dqn_agent.py
|   `-- random_baseline_agent.py   # lower-bound comparison point for the ablation study
|-- env/
|   `-- inprocess_client.py        # fast in-process training transport
|-- utils/
|-- checkpoints/
|   |-- d3qn_primary_3k_ep*.pth    # active primary-model checkpoints (3k-episode budget)
|   |-- backup/                    # redundant checkpoint copies (every 500 eps + on exit/crash)
|   |-- ablation/                  # ablation study checkpoints, <variant>_seed<seed>_ep*.pth
|   `-- archive_10k_run/            # archived original 10k run (historical, not resumable)
|-- reports/
|-- logs/
|   |-- train_run_<timestamp>/     # episodes.csv, findings.csv, run_config.json per hero run
|   `-- ablation/                  # <variant>_seed<seed>/ subfolders, one per ablation combo
|-- research/
|   `-- results/ablation_stats.json  # Friedman/Wilcoxon output, ready for the paper
|-- docs/
`-- tests/
```

## Key Runtime Files

- `easy_scanner.py`: interactive CLI + `--auto` wrapper around `autonomous_scan.py`.
- `easyscan.py`: compatibility launcher mirroring `easy_scanner.py` behavior.
- `scanner_gui.py`: Tk GUI and headless automation mode (`--auto`).
- `autonomous_scan.py`: core scan engine (`SecurityAuditor`, crawler, attack loop, report generation).
- `start_services.py`: boots local vulnerable mock targets on ports `5002` to `5006`.

## AI and Environment

- `agent/improved_dqn_agent.py`: improved DQN implementation (PER, noisy layers, dueling + double DQN).
- `env/web_sec_env.py`: Gym-style web security environment with full 150-action book and 50-action mock mapping.
- `env/target_app_*.py`: mock applications used for training and local scans.

## Utility Modules

- `utils/report_generator.py`: Markdown/TXT/HTML report generation helpers.
- `utils/model_loader.py`: smart checkpoint/base model loading helpers.
- `utils/false_positive_filter.py`: post-processing filter (used in non-AI mode).
- `utils/validator.py`: secondary finding validation logic.
- `utils/target_hunter.py`, `utils/zero_day_hunter.py`, `utils/proxy_fetcher.py`: research/helper modules (not exposed as default scanner flags).

## Data and Outputs

- `checkpoints/`: saved model checkpoints (active: `d3qn_primary_3k_ep*.pth`; ablation: `checkpoints/ablation/`; historical: `checkpoints/archive_10k_run/`).
- `reports/`: scan reports (`vulnerability_report_<timestamp>.md`).
- `logs/`: service logs and run-time logs.

## Docs Folder

`docs/` contains user guides, architecture docs, training notes, and module-level references. This documentation has been aligned to current scanner entrypoints and currently implemented flags.

# Project Structure

This map focuses on the files and folders that drive current behavior.

## Current Status (2026-08-13)

Active training budget is **3,000 episodes** (10k archived, see below). The ablation study (6 variants x 5 seeds x 3,000 episodes) is complete; Friedman/Wilcoxon stats and the real Table I / Fig. 3 are in the paper draft.

**Cleanup debt from earlier sessions is mostly resolved.** As of 2026-08-10 the root was reorganized for a clean, professional layout (see below). `nul` is gone and `logs/ablation/*_seed91`/`*_seed92` are gone. One item remains that only a real terminal can finish, since this assistant's sandbox can create/move files but never delete them:

- `checkpoints/ablation/backup/*_seed91_ep3.pth`, `*_seed92_ep3.pth` (10 files) -- smoke-test artifacts from verifying `run_ablation_parallel.py`'s isolation, outside the real seed 1-5 range on purpose so they're never mistaken for real results, but still on disk in the `backup/` subfolder pending manual deletion. (A separate copy already lives safely in `archive/2026-08-09_cleanup/smoke_test_debris/` for provenance -- these are the loose leftovers, not the archived record.)

## Top-Level Layout

```text
.
|-- easy_scanner.py                # interactive CLI + --auto wrapper (entry point)
|-- easyscan.py                    # thin compatibility launcher for easy_scanner.py
|-- scanner_gui.py                 # Tk GUI + headless --auto mode (entry point)
|-- autonomous_scan.py             # core scan engine (entry point)
|-- start_services.py              # boots the 5 mock target apps (entry point)
|-- init_targets.py                # seeds mock target DBs
|-- proxies.txt                    # auto-regenerated cache, written by utils/proxy_fetcher.py -- not clutter
|-- training/
|   |-- train_mock_targets.py      # primary training entry point (Extended D3QN, 3k eps default)
|   |-- train_ablation.py           # per-(variant,seed) ablation trainer -- Reviewer 1 gate
|   |-- evaluate_variant.py         # deterministic eval for one (variant,seed)
|   |-- stats_ablation.py           # Friedman + Wilcoxon across ablation results
|   |-- run_ablation_suite.py       # single command: all variants x seeds, training+eval+stats
|   |-- run_ablation_parallel.py    # same suite, N worker processes in parallel (CPU-bound speedup)
|   |-- training_logger.py         # per-episode/per-finding CSV logging
|   `-- plot_curve.py              # renders real reward/loss curve from logged CSVs
|-- agent/
|   |-- improved_dqn_agent.py      # run standalone: python agent/improved_dqn_agent.py
|   `-- random_baseline_agent.py   # lower-bound comparison point for the ablation study
|-- env/
|   |-- inprocess_client.py        # fast in-process training transport
|   `-- _workers/worker<N>/         # (transient) per-parallel-worker isolated copies of the 5 target apps' .db files
|-- utils/
|-- scripts/                       # one-off analysis/tooling, not part of the live scan/train pipeline
|   |-- aggregate_results.py       # ground-truth-vs-detected rollup -> Evaluation Form.xlsx
|   |-- evaluate_fill_excel.py     # ground-truth scanning + classification helpers (imported by aggregate_results.py)
|   |-- eval_from_code.py          # standalone ground-truth extraction from target app source
|   |-- quick_train_5000.py        # legacy quick-training helper
|   `-- git-commit.ps1             # commit helper script
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
|   |-- results/ablation_stats_reward.json      # Friedman/Wilcoxon on mean_reward
|   |-- results/ablation_stats_detection.json   # Friedman/Wilcoxon on detection_rate
|   |-- results/autonomous_scan_single_run_20260810.json  # real live-scan Table I source data
|   |-- INCIT2026_submission_FINAL_10-8-2026.docx/.pdf  # current final paper draft (submission-ready)
|   |-- INCIT2026_presentation.pptx/.pdf   # conference talk deck
|   |-- INCIT2026_talk_script.md   # slide-by-slide script + interview Q&A prep
|   `-- figures/                   # figure PNGs actually embedded in the paper, + generators/ subfolder
|-- docs/
|   `-- references/                # non-code reference material (e.g. juice-shop.pdf)
|-- tests/
|-- legacy_archive/                 # old docs, verify_*/debug_* scripts, dead experiments -- lives at repo ROOT, not under archive/ (docs/ARCHITECTURE.md references it directly at this path)
`-- archive/                        # everything else historical, consolidated in one place
    |-- 2026-08-09_cleanup/        # earlier session's dated cleanup batch, incl. smoke_test_debris/ (seed91/92 leftovers)
    |-- legacy/                    # old standalone scripts/models predating the current pipeline
    `-- checkpoints_backup_v21_success/  # historical checkpoint backup, kept for provenance
```

## config.py

Root-level `config.py` was missing for part of this session (never committed to git history — likely a local file from an earlier clone that never made it in) and has been restored from a working copy, with two stale defaults corrected to match current reality: `TrainingConfig.max_episodes` (was 10000, now 3000) and `ScanConfig.crawl_depth`/`intensity` (were 30/3, now 100/50, matching `autonomous_scan.py`'s CLI defaults below). `env/web_sec_env.py` treats this file as fully optional (`try/except ImportError`, falls back to `self.config = None` with defaults handled inline) — its absence never broke training or scanning, it only silenced a startup warning.

`autonomous_scan.py`'s `--depth`/`--intensity` CLI flags do **not** read from `config.py`'s `ScanConfig` — they have their own separate argparse defaults, now aligned to the same values (100/50) so a bare invocation without flags still gets reasonable coverage.

**What was deliberately left alone:** `agent/`, `env/`, `training/`, `utils/` were not nested under a `src/` (or similar) directory. Every training, evaluation, and scanning script imports from these by their current top-level names (`from agent.improved_dqn_agent import ...`, `from env.web_sec_env import ...`, etc.) — moving them five days before the InCIT 2026 submission deadline would mean touching import paths across dozens of files for a cosmetic win, with real risk of breaking a working pipeline. If there's time after submission, that's a clean follow-up.

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

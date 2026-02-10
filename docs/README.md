# Documentation Index

This documentation set reflects the current code behavior in this repository.

## Canonical Scanner Entry Points

- Interactive CLI: `python easy_scanner.py` or `python easyscan.py`
- Easy CLI headless mode: `python easy_scanner.py --auto ...`
- GUI: `python scanner_gui.py`
- GUI headless automation: `python scanner_gui.py --auto --target http://localhost:5002`
- Core scanner CLI: `python autonomous_scan.py <url> --depth ... --intensity ... [--persist --ai-mode --pentester]`

## Truth Matrix (Implemented vs Claims)

| Area | Implemented in code | Documentation stance |
| --- | --- | --- |
| `easy_scanner.py` | Interactive menu + `--auto` flags (`--mode`, `--target`, `--all-targets`, `--model`, `--depth`, `--intensity`, `--persist`, `--no-persist`, `--open-report`) | Treated as primary beginner CLI |
| `scanner_gui.py` (interactive) | Single-target GUI scan, profiles (`Hybrid`, `Full AI`), depth/intensity sliders, model chooser, persistence toggle, findings/exploit panel | Documented as visual workflow |
| `scanner_gui.py` (`--auto`) | Headless mode forwarding settings to `autonomous_scan.py` | Documented for automation and CI usage |
| `autonomous_scan.py` | Positional URL + `--depth`, `--intensity`, `--model`, `--persist`, `--ai-mode`, `--pentester` | Treated as core scan engine |
| Report output from scan flow | Markdown report in `reports/vulnerability_report_<timestamp>.md` | Documented as default output |
| `utils/target_hunter.py` | Module exists, not wired to scanner CLI/GUI flags | Marked as module-level/aspirational |
| `utils/zero_day_hunter.py` | Module exists, not wired to scanner CLI/GUI flags | Marked as module-level/aspirational |
| `utils/proxy_fetcher.py` | Module exists, not exposed as scanner runtime flag set | Marked as module-level helper |

## Suggested Reading Order

1. `docs/QUICK_START.md`
2. `docs/BEGINNER_GUIDE.md`
3. `docs/GUI_GUIDE.md`
4. `docs/GUI_AUTOMATION.md`
5. `docs/AUTONOMOUS_SCAN_GUIDE.md`
6. `docs/PROJECT_OVERVIEW.md`
7. `docs/TECHNICAL_ARCHITECTURE.md`

## Document Categories

- Getting started: `docs/QUICK_START.md`, `docs/BEGINNER_GUIDE.md`
- User interfaces: `docs/GUI_GUIDE.md`, `docs/GUI_AUTOMATION.md`
- Scanner behavior: `docs/AUTONOMOUS_SCAN_GUIDE.md`, `docs/REAL_WORLD_USAGE.md`
- Architecture and internals: `docs/PROJECT_STRUCTURE.md`, `docs/ARCHITECTURE.md`, `docs/TECHNICAL_ARCHITECTURE.md`
- Training and models: `docs/TRAINING_RECOMMENDATIONS.md`, `docs/CHECKPOINT_SYSTEM.md`, `docs/IMPROVED_ALGORITHMS.md`
- Research modules (not default scanner modes): `docs/TARGET_HUNTER.md`, `docs/ZERO_DAY_HUNTER.md`, `docs/MAC_SPOOFING.md`

## Safety Note

Use this project only for systems you own or are explicitly authorized to test.

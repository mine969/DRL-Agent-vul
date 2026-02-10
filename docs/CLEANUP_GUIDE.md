# Cleanup Guide

Use this guide to safely reduce workspace clutter without removing core project files.

## Usually Safe to Remove

- Old reports in `reports/`
- Old logs in `logs/`
- Python cache folders (`__pycache__/`)
- Redundant intermediate checkpoints you no longer need

## Keep These

- Source code (`agent/`, `env/`, `utils/`, main scripts)
- At least one known-good model/checkpoint
- Current docs in `docs/`

## Suggested Cleanup Commands

### Windows PowerShell

```powershell
Remove-Item -Recurse -Force reports\* -ErrorAction SilentlyContinue
Remove-Item -Recurse -Force logs\* -ErrorAction SilentlyContinue
Get-ChildItem -Recurse -Directory -Filter __pycache__ | Remove-Item -Recurse -Force
```

### Optional checkpoint pruning example

Keep milestone checkpoints and latest; remove dense intermediates manually after review.

## Pre-Cleanup Checklist

1. Confirm latest model path you want to keep.
2. Confirm reports needed for audit history are archived.
3. Run `git status` before deleting tracked files.

## Post-Cleanup Validation

Run a quick smoke test:

```bash
python easy_scanner.py --help
python scanner_gui.py --help
python autonomous_scan.py --help
```

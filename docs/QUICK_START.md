# Quick Start

This is the fastest path to a working local scan.

## 1) Install Dependencies

```bash
pip install -r requirements.txt
```

## 2) Start the Mock Targets

```bash
python start_services.py
```

Keep that terminal open while scanning or training.

## 3) Ensure You Have a Model

If you already have `.pth` files in `checkpoints/`, skip this.

```bash
python train_mock_targets.py --episodes 1000
```

## 4) Run a Scan (Recommended Paths)

### Interactive CLI

```bash
python easy_scanner.py
```

Alias:

```bash
python easyscan.py
```

### GUI

```bash
python scanner_gui.py
```

### Core CLI Engine

```bash
python autonomous_scan.py http://localhost:5002 --depth 30 --intensity 3 --persist
```

## Headless Automation Examples

### Easy CLI (`easy_scanner.py`)

```bash
python easy_scanner.py --auto --all-targets --mode hybrid
python easy_scanner.py --auto --target http://localhost:5002 --mode ai --depth 40 --intensity 6 --persist
```

### GUI Headless (`scanner_gui.py --auto`)

```bash
python scanner_gui.py --auto --target http://localhost:5002
python scanner_gui.py --auto --target http://localhost:5002 --profile full-ai --depth 50 --episodes 8 --persist
```

## Where Results Go

- Default report path: `reports/vulnerability_report_<timestamp>.md`
- `easy_scanner.py` and GUI report-open actions point to that Markdown report.

## Common Issues

- No models found: run `python train_mock_targets.py --episodes 1000`.
- Target unreachable: confirm `python start_services.py` is still running.
- Slow or empty results: increase `--depth` and `--intensity`, then validate findings manually.

## Legal Reminder

Only scan systems you own or are explicitly authorized to test.

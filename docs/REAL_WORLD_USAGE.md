# Real-World Usage Guide

This guide covers practical, authorized usage outside the default local training loop.

## First Principle

Only scan systems you own or are explicitly authorized to test.

## Recommended Workflow

## 1) Validate Locally First

```bash
python start_services.py
python easy_scanner.py
```

Confirm your model, scanner, and report flow work on local targets before external runs.

## 2) Run Authorized External Scan

### Direct engine

```bash
python autonomous_scan.py https://authorized-target.example --depth 30 --intensity 3 --persist
```

### Easy CLI auto wrapper

```bash
python easy_scanner.py --auto --target https://authorized-target.example --mode hybrid --depth 30 --intensity 3 --persist
```

### GUI headless wrapper

```bash
python scanner_gui.py --auto --target https://authorized-target.example --profile hybrid --depth 30 --episodes 3 --persist
```

## 3) Review Report and Validate

- Report path: `reports/vulnerability_report_<timestamp>.md`
- Confirm high-impact findings manually before reporting or remediation tickets.

## Batch Usage Example

```bash
python autonomous_scan.py https://target-a.example --depth 20 --intensity 3
python autonomous_scan.py https://target-b.example --depth 20 --intensity 3
python autonomous_scan.py https://target-c.example --depth 20 --intensity 3
```

## Practical Limitations

- Current scan runtime uses mock-target action mapping (`mode="mock_targets"`) even on external URLs.
- Expect more manual verification effort on apps that differ from local training targets.
- Treat scanner findings as triage input, not final security conclusions.

## Options That Actually Exist

Use:

- `--depth`
- `--intensity`
- `--model`
- `--persist`
- `--ai-mode`
- `--pentester`

Avoid outdated examples using unsupported scanner flags such as `--mode targetless` or `--mode zeroday`.

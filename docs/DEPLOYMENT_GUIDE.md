# Deployment Guide

This project is usually run as scripts, not as a long-lived web service. "Deployment" here means setting up reliable execution in local labs or CI jobs.

## Local Lab Deployment

## 1) Environment Setup

```bash
pip install -r requirements.txt
```

## 2) Start Local Targets

```bash
python start_services.py
```

## 3) Run Scanner

```bash
python easy_scanner.py
```

or

```bash
python scanner_gui.py
```

## Headless Deployment Pattern

For scheduled or pipeline use:

```bash
python scanner_gui.py --auto --target http://localhost:5002 --profile hybrid --depth 30 --episodes 3 --persist
```

Equivalent direct engine path:

```bash
python autonomous_scan.py http://localhost:5002 --depth 30 --intensity 3 --persist
```

## CI Example (Minimal)

```yaml
steps:
  - name: Install deps
    run: pip install -r requirements.txt
  - name: Run scan
    run: python scanner_gui.py --auto --target http://localhost:5002 --profile hybrid --depth 20 --episodes 3 --persist
```

## Artifacts

- Reports: `reports/vulnerability_report_<timestamp>.md`
- Logs: `logs/`
- Checkpoints: `checkpoints/`

## Security and Governance

- Only deploy scans against authorized environments.
- Prefer staging/pre-production targets before production-like systems.
- Require manual analyst validation for high-severity findings.

## Non-Goals in Current Deployment

- No built-in scanner mode flags for targetless hunting or zero-day mode.
- No first-class scanner CLI stealth/proxy profile flags.

Those areas remain module-level capabilities in `utils/` and require custom integration if needed.

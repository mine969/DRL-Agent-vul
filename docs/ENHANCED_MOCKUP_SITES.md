# Mockup Site Coverage

The project ships with five local mock applications used for both training and baseline scan validation.

## How to Start Them

```bash
python start_services.py
```

Default local targets:

- `http://localhost:5002` (E-Commerce Platform)
- `http://localhost:5003` (Social Media Platform)
- `http://localhost:5004` (Banking Application)
- `http://localhost:5005` (Blog Platform)
- `http://localhost:5006` (File Sharing Platform)

## Why These Targets Matter

- Training scripts rotate across these targets.
- Scanner wrappers provide presets for these targets.
- The tuned 50-action runtime mapping is designed around these patterns.

## Vulnerability Families (Expected Baseline)

| Target | Typical vulnerability families |
| --- | --- |
| E-Commerce (`5002`) | SQLi, mass assignment, logic flaws, race conditions, IDOR, payment/bac issues |
| Social (`5003`) | stored/reflected XSS patterns, upload/path issues, IDOR, CSRF/session weaknesses |
| Banking (`5004`) | CSRF, IDOR, session issues, logic flaws |
| Blog (`5005`) | stored XSS, SSTI, CSRF, weak auth |
| File Share (`5006`) | upload controls, traversal patterns, IDOR |

## Operational Notes

- These are intentionally vulnerable apps for authorized lab usage.
- For consistent experiments, keep all services running during training/scanning.
- Reports generated from these targets are the best baseline for regression checks.

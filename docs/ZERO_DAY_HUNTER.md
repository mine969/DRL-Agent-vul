# Zero-Day Hunter Module

`utils/zero_day_hunter.py` contains helper logic for payload mutation, CVE retrieval, and configuration checks.

## Current Status

- Module exists and can be imported.
- It is not currently exposed as a scanner mode flag in `autonomous_scan.py`, `easy_scanner.py`, or `scanner_gui.py`.
- Use it from Python for research/custom extensions.

## What the Module Provides

- CVE fetching from NVD (`fetch_latest_cves`)
- Fuzz payload generation (`generate_fuzzing_payloads`)
- Payload mutation helpers (`mutate_payload`)
- CVE-derived payload suggestion (`generate_cve_based_payloads`)
- Weak config checks (`check_weak_configuration`)

## Example: Module-Level Usage

```python
from utils.zero_day_hunter import ZeroDayHunter

hunter = ZeroDayHunter()

cves = hunter.fetch_latest_cves(limit=10)
print(f"Fetched {len(cves)} CVEs")

payloads = hunter.generate_fuzzing_payloads("buffer_overflow")
print(f"Generated {len(payloads)} fuzz payloads")

mutated = hunter.mutate_payload("' OR 1=1--", "url_encode")
print(mutated)
```

## Integrating With Scanner Manually

Use module output to guide targeted, authorized scans:

```bash
python autonomous_scan.py https://authorized-target.example --depth 30 --intensity 5 --ai-mode
```

## Important Clarification

Outdated examples that imply scanner flags such as `--mode zeroday` are not valid in the current scanner CLI.

## Safety

Only run testing against systems you are explicitly authorized to assess.

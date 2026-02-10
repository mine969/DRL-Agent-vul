# Target Hunter Module

`utils/target_hunter.py` provides helper routines for discovering potential targets from public sources.

## Current Status

- Module exists and is importable.
- It is not currently exposed as first-class scanner CLI/GUI mode flags.
- Use it as a Python module in custom workflows.

## Supported Source Methods in Module

- Google-style search scraping (`dork_google`)
- Shodan API search (`search_shodan`)
- Certificate transparency lookup (`search_crtsh`)
- DuckDuckGo HTML search (`search_duckduckgo`)
- Censys search helper (`search_censys`)
- Auto-generation helper (`auto_generate_targets`)

## Example: Module-Level Usage

```python
from utils.target_hunter import TargetHunter

hunter = TargetHunter(shodan_api_key=None)

targets = hunter.search_duckduckgo("site:example.com login", num_results=5)
for t in targets:
    print(t)

auto_targets = hunter.auto_generate_targets(source="duckduckgo", max_per_source=2)
print(f"Generated {len(auto_targets)} targets")
```

## Integrating With Scanner Manually

After collecting authorized targets, run scanner entrypoints explicitly, for example:

```bash
python autonomous_scan.py https://authorized-target.example --depth 20 --intensity 3
```

## Important Legal and Operational Notes

- Respect terms of service and rate limits for discovery sources.
- Verify authorization scope before scanning any discovered host.
- Treat discovery output as candidate targets, not automatic in-scope assets.

# Architecture Overview

This project combines a reinforcement learning agent, a web environment, and scanner wrappers.

## Layered View

```text
User Interfaces
  - easy_scanner.py / easyscan.py
  - scanner_gui.py
  - autonomous_scan.py (direct)

Core Orchestration
  - SecurityAuditor
  - WebsiteExplorer

Learning and Environment
  - ImprovedDQNAgent
  - WebSecurityGym (WebSecEnv)

Support Modules
  - model loading
  - validation/filtering
  - report generation
```

## Key Design Points

- Scanner wrappers (`easy_scanner.py`, `scanner_gui.py`) delegate to `autonomous_scan.py` logic.
- Environment supports a full 150-action book and a 50-action mock-target subset.
- Current scanner audit flow runs in `mock_targets` mode.
- Reports are generated as Markdown in `reports/`.

## Current Scope

- Strongest support: local mock targets on ports `5002` to `5006`.
- External target scans are possible but still use mock-target action mapping.
- `target_hunter` and `zero_day_hunter` are module-level components, not scanner CLI modes.

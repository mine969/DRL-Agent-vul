# GUI Guide

`scanner_gui.py` is the visual interface for running scans and reviewing findings.

## Launch

```bash
python scanner_gui.py
```

## Main Controls (Left Panel)

- Target preset dropdown (`Custom / Manual`, plus local mock targets).
- Target URL input (auto-fills when a preset is selected).
- Scan mode profile:
  - `Hybrid`: depth 30, intensity 3, persistence on, AI mode off.
  - `Full AI`: depth 50, intensity 8, persistence on, AI mode on, pentester chain mode on.
- Crawl depth slider (`0` to `100`).
- Attack intensity slider (`1` to `50`).
- Model selector (checkpoint/base model chooser + file browser).
- Persistence checkbox (`ENABLE PERSISTENCE MODE`).
- `START SCAN` and `ABORT MISSION` buttons.

## Monitoring Panels

- Logs and terminal tab: live scan output.
- Live view tab: page-source snapshots when available.
- Findings list: vulnerability entries as they are confirmed.

## Weaponization Panel (Right)

When you select a finding, the panel generates:

- Summary details (`type`, `url`, `payload`, `status`, `evidence`, `reward`).
- Example attack steps.
- Ready-to-copy curl and Python snippets.

Buttons:

- `COPY PAYLOAD`
- `OPEN REPORT` (opens latest `reports/vulnerability_report_*.md`)

## How Scans Are Executed

- Interactive GUI scanning calls `SecurityAuditor.start_audit(...)` directly.
- GUI scans one configured target per run.
- Run behavior is driven by depth, intensity, persistence, and selected profile.

## What This GUI Does Not Currently Expose

- No built-in targetless/OSINT discovery mode toggle.
- No built-in proxy/stealth profile controls.
- No dedicated zero-day mode selector.

Related helper modules exist in `utils/`, but they are not wired as GUI toggles in the current code.

## Headless Automation

For non-interactive use:

```bash
python scanner_gui.py --auto --target http://localhost:5002
```

See `docs/GUI_AUTOMATION.md` for full flag reference.

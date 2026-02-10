# GUI Automation Guide

`scanner_gui.py` supports a headless mode for scripts and CI workflows.

## Command Syntax

```bash
python scanner_gui.py --auto --target <url> [options]
```

`--target` is required when `--auto` is used.

## Supported Options

- `--profile {hybrid,full-ai}`
- `--model <path>`
- `--depth <int>`
- `--episodes <int>` (alias: `--intensity`)
- `--persist` or `--no-persist`
- `--ai-mode`
- `--pentester`

## Examples

### Minimal

```bash
python scanner_gui.py --auto --target http://localhost:5002
```

### Full AI profile

```bash
python scanner_gui.py --auto --target http://localhost:5002 --profile full-ai
```

### Explicit tuning

```bash
python scanner_gui.py --auto --target http://localhost:5002 --depth 40 --episodes 6 --persist
```

### Force AI chain behavior

```bash
python scanner_gui.py --auto --target http://localhost:5002 --ai-mode --pentester
```

## Runtime Behavior

- Headless mode does not create a Tk window.
- It builds a subprocess command for `autonomous_scan.py` with matching scan arguments.
- It sets `PYTHONIOENCODING=utf-8` in subprocess environment when unset.
- Exit code is propagated from the child process.

## Comparison With Other Entry Points

- `python easy_scanner.py --auto ...`: simple headless wrapper with multi-target support.
- `python scanner_gui.py --auto ...`: GUI-flavored automation profile layer.
- `python autonomous_scan.py ...`: direct control of the core scanner engine.

## Not Supported Here

The following are not valid `scanner_gui.py --auto` flags in current code:

- `--mode zeroday`
- `--mode targetless`
- `--auto-generate`
- `--proxy-file`

Those ideas are documented as research modules, not active GUI CLI flags.

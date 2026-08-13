# Code Style Guide

These conventions keep the repository maintainable and consistent.

## Core Principles

- Prefer clear, explicit code over clever shortcuts.
- Keep functions focused on one responsibility.
- Use descriptive names for variables, functions, and classes.
- Minimize silent failure paths; log context when catching exceptions.

## Python Conventions

- Follow PEP 8 formatting.
- Use 4-space indentation.
- Keep imports grouped: stdlib, third-party, local modules.
- Add type hints where they improve readability and refactoring safety.

## Comments and Docstrings

- Write comments only when behavior is non-obvious.
- Keep module/class/function docstrings concise and factual.
- Avoid stale claims in docstrings; update docs with code changes.

## Error Handling

- Catch specific exceptions when possible.
- If broad exceptions are needed, emit actionable logging.
- Do not suppress critical failures silently in core scan paths.

## Configuration and Constants

- Keep tunable values in `config.py` or clear top-level constants.
- Avoid scattering hardcoded magic numbers across modules.

## Validation Commands

Use quick checks before sharing changes:

```bash
python -m py_compile easy_scanner.py scanner_gui.py scripts/easyscan.py autonomous_scan.py
python easy_scanner.py --help
python scanner_gui.py --help
python autonomous_scan.py --help
```

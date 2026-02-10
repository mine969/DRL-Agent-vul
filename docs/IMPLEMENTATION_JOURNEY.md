# Implementation Journey

This timeline summarizes major project evolution based on the current repository state.

## Phase 1: Core RL Scanner Foundation

- Introduced environment-driven web testing loop.
- Built initial DQN-based attack policy architecture.
- Added vulnerable mock applications for reproducible training.

## Phase 2: Training and Model Workflow

- Added `train_mock_targets.py` for rotating local target training.
- Added checkpoint saving/resume workflow (`improved_mock_ep*.pth`).
- Added long-run script path (`quick_train_5000.py`).

## Phase 3: Improved Agent Stack

- Introduced `ImprovedDQNAgent` with prioritized replay and noisy exploration.
- Adopted dueling + double DQN style updates.
- Standardized 15-dim state and tuned mock-target action mapping.

## Phase 4: Scanner UX and Wrappers

- Built interactive wrapper `easy_scanner.py`.
- Added GUI workflow in `scanner_gui.py`.
- Added non-interactive automation modes (`easy_scanner.py --auto`, `scanner_gui.py --auto`).
- Added `easyscan.py` compatibility launcher.

## Phase 5: Reporting and Validation

- Consolidated finding structure and evidence fields.
- Integrated validator and false-positive filtering path.
- Standardized report output under `reports/`.

## Phase 6: Documentation Realignment

- Removed outdated scanner command claims.
- Aligned docs to actual entrypoints and supported flags.
- Marked module-level research helpers as aspirational where not wired into scanner flags.

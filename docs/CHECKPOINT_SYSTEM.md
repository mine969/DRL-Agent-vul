# Checkpoint System

This project uses `.pth` files for model persistence across training and scanning workflows.

## Checkpoint Types in Current Code

| Pattern | Produced by | Purpose |
| --- | --- | --- |
| `checkpoints/d3qn_primary_3k_ep*.pth` | `training/train_mock_targets.py` | Main mock-target training checkpoints (active, 3,000-episode default budget since 2026-08-09) |
| `checkpoints/ablation/<variant>_seed<seed>_ep*.pth` | `training/train_ablation.py` | Reviewer-1 ablation study checkpoints (random/dqn/d3qn_full/d3qn_no_per/d3qn_no_noisy/d3qn_no_multistep x 5 seeds) |
| `checkpoints/archive_10k_run/improved_mock_ep*.pth` | (archived, not actively produced) | Original 10k-episode run (Feb 2026, real HTTP, pre-optimization). Kept for historical reference, not resumable -- see `checkpoints/archive_10k_run/README.md` |
| `checkpoints/online_session_<timestamp>.pth` | `autonomous_scan.py` with `--ai-mode` | Snapshot of online-learning scan session |
| `dqn_web_sec_model.pth` | base model artifact | Default fallback model path |
| `dqn_juiceshop_model.pth` | optional base model artifact | Additional fallback candidate |

## Loader Behavior

- `training/train_mock_targets.py`'s `find_latest_checkpoint()` defaults to pattern `d3qn_primary_3k_ep*.pth` -- this will never match anything in `checkpoints/archive_10k_run/`, by design (see that function's docstring for why the rename mattered).
- `utils/model_loader.load_model_smart(...)` attempts latest checkpoint first, then falls back to supplied base model path.
- `easy_scanner.py` discovers and ranks available checkpoint/base models for interactive and auto mode.

## Typical Workflow

## Train / Resume

```bash
python training/train_mock_targets.py                    # 3,000 episodes (default), fast in-process mode
python training/train_mock_targets.py --episodes 1000    # shorter run
python training/train_mock_targets.py --fresh             # ignore existing checkpoints, start clean
```

The script auto-resumes from the latest `d3qn_primary_3k_ep*.pth` checkpoint when found.

## Evaluate a specific checkpoint

```bash
python autonomous_scan.py http://localhost:5002 --model checkpoints/d3qn_primary_3k_ep1000.pth --depth 30 --intensity 3
```

## Ablation study checkpoints (Reviewer 1 statistical-rigor gate)

```bash
python training/run_ablation_suite.py                     # all 6 variants x 5 seeds x 3000 episodes, one command
python training/train_ablation.py --variant d3qn_full --seed 1   # a single (variant, seed) combo
```

See `research/REVISION_PLAN_incit2026.md` (Phase 4) for what this is for.

`training/quick_train_5000.py` is deprecated -- it was merged into `training/train_mock_targets.py` and now just raises `SystemExit` pointing here.

## Retention Guidance

- Keep milestone checkpoints (for example every 500 or 1000 episodes).
- Keep best-performing checkpoints from your validation runs.
- Keep latest checkpoint and at least one known-good fallback.
- Prune dense intermediate checkpoints to reduce disk usage.

## Compatibility Notes

- Most current workflows assume 15-dim state and 50-action mock-target training setup.
- Loading arbitrary legacy checkpoints with mismatched shapes can fail.
- If loading fails, retrain from a compatible checkpoint family.
- Ablation variants have different internal architectures (PER on/off, Noisy on/off) -- always load a checkpoint using the same `--variant` flag it was trained with (`training/evaluate_variant.py` handles this automatically).

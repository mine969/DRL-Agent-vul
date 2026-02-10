# Checkpoint System

This project uses `.pth` files for model persistence across training and scanning workflows.

## Checkpoint Types in Current Code

| Pattern | Produced by | Purpose |
| --- | --- | --- |
| `checkpoints/improved_mock_ep*.pth` | `train_mock_targets.py`, `quick_train_5000.py` | Main mock-target training checkpoints |
| `checkpoints/online_session_<timestamp>.pth` | `autonomous_scan.py` with `--ai-mode` | Snapshot of online-learning scan session |
| `dqn_web_sec_model.pth` | base model artifact | Default fallback model path |
| `dqn_juiceshop_model.pth` | optional base model artifact | Additional fallback candidate |

## Loader Behavior

- `utils/model_loader.find_latest_checkpoint()` defaults to pattern `improved_mock_*.pth`.
- `utils/model_loader.load_model_smart(...)` attempts latest checkpoint first, then falls back to supplied base model path.
- `easy_scanner.py` discovers and ranks available checkpoint/base models for interactive and auto mode.

## Typical Workflow

## Train / Resume

```bash
python train_mock_targets.py --episodes 1000
python train_mock_targets.py --episodes 3000
```

The script resumes from latest compatible checkpoint when found.

## Evaluate a specific checkpoint

```bash
python autonomous_scan.py http://localhost:5002 --model checkpoints/improved_mock_ep1000.pth --depth 30 --intensity 3
```

## Long-run training path

```bash
python quick_train_5000.py
python quick_train_5000.py --fresh
```

## Retention Guidance

- Keep milestone checkpoints (for example every 500 or 1000 episodes).
- Keep best-performing checkpoints from your validation runs.
- Keep latest checkpoint and at least one known-good fallback.
- Prune dense intermediate checkpoints to reduce disk usage.

## Compatibility Notes

- Most current workflows assume 15-dim state and 50-action mock-target training setup.
- Loading arbitrary legacy checkpoints with mismatched shapes can fail.
- If loading fails, retrain from a compatible checkpoint family.

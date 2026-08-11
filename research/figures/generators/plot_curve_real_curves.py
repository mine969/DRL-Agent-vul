"""
Plot a Real Training Curve from Logged Episode Data
=====================================================

Reads the episodes.csv produced by training/training_logger.py (wired into
training/train_mock_targets.py) and renders the same dual-axis reward/loss
plot style as research/generate_training_curve.py -- except from real
per-episode data logged during an actual training run, not a synthetic
np.random.seed(42) curve.

This is the direct replacement path for the paper's Fig. 3 once a real
training run has been logged: run training, then point this script at the
resulting episodes.csv.

Usage:
    python training/plot_curve.py logs/train_run_20260810_140000/episodes.csv
    python training/plot_curve.py logs/train_run_20260810_140000/episodes.csv \\
        --window 100 --out research/training_curve_real.png
"""

import argparse
import csv


def moving_average(data, window_size):
    if len(data) < window_size:
        return [], []
    cumsum = [0.0]
    for v in data:
        cumsum.append(cumsum[-1] + v)
    out = []
    for i in range(window_size, len(cumsum)):
        out.append((cumsum[i] - cumsum[i - window_size]) / window_size)
    return out


def load_episodes(csv_path):
    episodes, rewards, losses = [], [], []
    with open(csv_path, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            episodes.append(int(row["episode"]))
            rewards.append(float(row["total_reward"]))
            # avg_loss is blank on episodes where replay() returned None
            # (buffer not full yet) -- carry the last known value forward
            # so the moving average isn't skewed by treating gaps as zero.
            if row["avg_loss"]:
                losses.append(float(row["avg_loss"]))
            elif losses:
                losses.append(losses[-1])
            else:
                losses.append(0.0)
    return episodes, rewards, losses


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("episodes_csv", help="Path to a training run's episodes.csv")
    parser.add_argument("--window", type=int, default=100, help="Moving-average window (episodes)")
    parser.add_argument("--out", default=None, help="Output PNG path")
    args = parser.parse_args()

    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    episodes, rewards, losses = load_episodes(args.episodes_csv)
    n = len(episodes)
    if n == 0:
        raise SystemExit(f"No rows found in {args.episodes_csv}")

    window = min(args.window, max(1, n // 2))
    if window != args.window:
        print(f"⚠️  Only {n} episodes logged; reducing smoothing window to {window}.")

    smoothed_reward = moving_average(rewards, window)
    smoothed_loss = moving_average(losses, window)
    smoothed_x = episodes[window - 1 : window - 1 + len(smoothed_reward)]

    print(f"Loaded {n} episodes from {args.episodes_csv}")
    print(f"Reward: min={min(rewards):.2f} max={max(rewards):.2f} final={rewards[-1]:.2f}")
    print(f"Loss:   min={min(losses):.4f} max={max(losses):.4f} final={losses[-1]:.4f}")

    fig, ax1 = plt.subplots(figsize=(10, 5))

    color = "tab:blue"
    ax1.set_xlabel("Training Episodes")
    ax1.set_ylabel("Cumulative Reward per Episode", color=color)
    ax1.plot(
        smoothed_x, smoothed_reward, color=color, linewidth=2,
        label=f"Smoothed Reward ({window}-ep window)",
    )
    ax1.tick_params(axis="y", labelcolor=color)
    ax1.grid(True, linestyle="--", alpha=0.6)

    ax2 = ax1.twinx()
    color = "tab:red"
    ax2.set_ylabel("Avg. Training Loss", color=color)
    ax2.plot(
        smoothed_x, smoothed_loss, color=color, linewidth=2, linestyle="--",
        label=f"Smoothed Loss ({window}-ep window)",
    )
    ax2.tick_params(axis="y", labelcolor=color)

    plt.title(f"Extended D3QN Agent Training Progression ({n} Episodes, Real Data)")
    fig.tight_layout()

    lines_1, labels_1 = ax1.get_legend_handles_labels()
    lines_2, labels_2 = ax2.get_legend_handles_labels()
    ax1.legend(lines_1 + lines_2, labels_1 + labels_2, loc="center right")

    out_path = args.out or args.episodes_csv.replace("episodes.csv", "training_curve_real.png")
    plt.savefig(out_path, dpi=300, bbox_inches="tight")
    print(f"✅ Saved real training curve to {out_path}")


if __name__ == "__main__":
    main()

"""
Training Logger
================

Per-episode and per-finding CSV logging for training runs, plus a run
config snapshot and a live "best finds" tracker.

This exists specifically to close a real gap: the paper's Fig. 3 (reward/
loss over training episodes) is currently generated synthetically
(research/generate_training_curve.py, np.random.seed(42)) because no real
training run has ever logged its actual reward/loss per episode. Every run
through TrainingLogger writes that data for real, in a format
training/plot_curve.py can turn directly into a replacement figure.

Output layout (one directory per run):
    logs/train_run_<YYYYmmdd_HHMMSS>/
        run_config.json   -- hyperparameters and mode for this run
        episodes.csv       -- one row per episode (reward, loss, steps, ...)
        findings.csv        -- one row per confirmed vulnerability found
"""

import csv
import json
import os
import time
from datetime import datetime


class TrainingLogger:
    def __init__(self, log_root="logs", run_name=None):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.run_name = run_name or f"train_run_{timestamp}"
        self.run_dir = os.path.join(log_root, self.run_name)
        os.makedirs(self.run_dir, exist_ok=True)

        self.episodes_path = os.path.join(self.run_dir, "episodes.csv")
        self.findings_path = os.path.join(self.run_dir, "findings.csv")
        self.config_path = os.path.join(self.run_dir, "run_config.json")

        self._init_csv(
            self.episodes_path,
            [
                "episode",
                "timestamp",
                "target",
                "steps",
                "total_reward",
                "avg_loss",
                "vulns_found",
                "replay_buffer_size",
                "elapsed_sec",
            ],
        )
        self._init_csv(
            self.findings_path,
            ["episode", "timestamp", "target", "vuln_type", "reward", "step", "is_new_best"],
        )

        # vuln_type -> (best_reward, episode, target) for this run, used
        # both to decide "is this a new best" and to print a leaderboard.
        self.best_finds = {}
        self.start_time = time.time()

    @staticmethod
    def _init_csv(path, header):
        if not os.path.exists(path):
            with open(path, "w", newline="", encoding="utf-8") as f:
                csv.writer(f).writerow(header)

    def write_config(self, config: dict):
        with open(self.config_path, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=2, default=str)

    def log_episode(
        self,
        episode,
        target,
        steps,
        total_reward,
        avg_loss,
        vulns_found,
        replay_buffer_size,
    ):
        with open(self.episodes_path, "a", newline="", encoding="utf-8") as f:
            csv.writer(f).writerow(
                [
                    episode,
                    datetime.now().isoformat(timespec="seconds"),
                    target,
                    steps,
                    f"{total_reward:.4f}",
                    f"{avg_loss:.4f}" if avg_loss is not None else "",
                    vulns_found,
                    replay_buffer_size,
                    f"{time.time() - self.start_time:.1f}",
                ]
            )

    def log_finding(self, episode, target, vuln_type, reward, step):
        """Records a confirmed vulnerability finding and updates the
        best-finds leaderboard. Returns True if this is a new best for
        vuln_type (either never seen before, or a higher reward than any
        prior instance this run) -- callers use this to decide whether to
        print an immediate highlighted line."""
        prev = self.best_finds.get(vuln_type)
        is_new_best = prev is None or reward > prev[0]
        if is_new_best:
            self.best_finds[vuln_type] = (reward, episode, target)

        with open(self.findings_path, "a", newline="", encoding="utf-8") as f:
            csv.writer(f).writerow(
                [
                    episode,
                    datetime.now().isoformat(timespec="seconds"),
                    target,
                    vuln_type,
                    f"{reward:.2f}",
                    step,
                    is_new_best,
                ]
            )
        return is_new_best

    def leaderboard_lines(self):
        """Returns printable lines summarizing the best find per vuln_type,
        sorted by reward descending."""
        if not self.best_finds:
            return ["  (no confirmed findings yet)"]
        rows = sorted(self.best_finds.items(), key=lambda kv: kv[1][0], reverse=True)
        lines = []
        for vuln_type, (reward, episode, target) in rows:
            lines.append(
                f"  {vuln_type:<28s} best={reward:6.2f}  ep={episode:<6d} target={target}"
            )
        return lines

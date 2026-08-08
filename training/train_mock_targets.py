"""
Mock Targets Training -- Extended D3QN
=======================================

The single training entry point for the DRL agent (agent/improved_dqn_agent.py,
Extended D3QN: Double DQN + Dueling + PER + Noisy Networks) against the 5 mock
web applications (env/target_app_*.py). This replaces what used to be two
separate scripts (train_mock_targets.py + quick_train_5000.py) -- they had
overlapping logic that had started to drift apart, so they're merged into
this one file rather than maintained in parallel.

Usage:
    python training/train_mock_targets.py                  # 3,000 episodes, fast mode (default)
    python training/train_mock_targets.py --episodes 1000  # shorter run
    python training/train_mock_targets.py --episodes 10000 # old budget, explicit opt-in
    python training/train_mock_targets.py --real            # real HTTP instead of in-process
    python training/train_mock_targets.py --fresh            # ignore existing checkpoints
    (run from the project root, not from inside training/)

Note: default episode budget changed 2026-08-09 from 10,000 to 3,000 to
match the project-wide budget adopted for the Reviewer 1 ablation study
(see training/train_ablation.py). The original 10k checkpoint series is
archived at checkpoints/archive_10k_run/ -- kept because the paper's
Table I results were generated from it, not meant to be extended further.

Transport modes:
    Default (fast=True): in-process Flask test-client transport (see
    env/inprocess_client.py) -- same view functions / same reward signal as
    real HTTP, just without the OS socket layer, purely for training
    throughput. No separate services needed.

    --real: real HTTP against env/start_services.py-run apps. This script
    produces training checkpoints, not evaluation numbers -- the paper's
    actual results should come from the real-HTTP evaluation scripts
    (autonomous_scan.py / eval_from_code.py / evaluate_fill_excel.py), which
    don't import this module and are unaffected by this flag either way.
    Use --real here only if you specifically want a training run that also
    exercises the real HTTP path.

Logging:
    Every run writes logs/train_run_<timestamp>/episodes.csv (one row per
    episode: reward, loss, steps, vulns) and findings.csv (one row per
    confirmed vulnerability, with a running best-per-type leaderboard).
    See training/training_logger.py and training/plot_curve.py -- the
    latter turns episodes.csv into a real reward/loss figure, replacing
    the synthetic one in research/generate_training_curve.py.

Checkpoints:
    Saved atomically (temp file + rename, so a crash mid-write can't leave
    a corrupted checkpoint) every 100 episodes to checkpoints/, with a
    redundant copy to checkpoints/backup/ every 500 episodes. Any uncaught
    exception during training also triggers an emergency save before the
    error propagates, in addition to the existing Ctrl-C handling.
"""

import sys
import os

# This script lives one level below the project root (training/), so the
# root must be added to sys.path explicitly for `agent.`/`env.` package
# imports to resolve, regardless of the current working directory.
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import glob
import io
import re
import shutil
import time

import torch
from agent.improved_dqn_agent import (
    ImprovedDQNAgent,
)  # Extended D3QN: PER + Noisy Networks + Dueling + Double DQN
from env.web_sec_env import WebSecurityGym
from training.training_logger import TrainingLogger

# NOTE: UTF-8 stdout wrapping happens in __main__ below, not here at import
# time -- this module is imported as a library by training/train_ablation.py
# and training/evaluate_variant.py (for the TARGETS list), and reassigning
# sys.stdout on import closes/clobbers any wrapper the importing script
# already set up (observed: "ValueError: I/O operation on closed file").

TARGETS = [
    {"name": "E-Commerce", "port": 5002, "url": "http://localhost:5002"},
    {"name": "Social Media", "port": 5003, "url": "http://localhost:5003"},
    {"name": "Banking App", "port": 5004, "url": "http://localhost:5004"},
    {"name": "Blog Platform", "port": 5005, "url": "http://localhost:5005"},
    {"name": "File Share", "port": 5006, "url": "http://localhost:5006"},
]

CHECKPOINT_DIR = "checkpoints"
BACKUP_DIR = os.path.join(CHECKPOINT_DIR, "backup")
BACKUP_EVERY = 500  # episodes between redundant backup copies


def find_latest_checkpoint(pattern="checkpoints/d3qn_primary_3k_ep*.pth"):
    """Finds the highest-episode checkpoint matching `pattern`. Returns
    (episode_number, path) or (0, None) if none found.

    Naming note (2026-08-09): the active prefix is "d3qn_primary_3k", not
    the old "improved_mock" used by the archived 10k run. This is
    deliberate, not cosmetic -- the old 10k lineage already contains an
    improved_mock_ep3000.pth (checkpoints/archive_10k_run/), and since the
    project moved to a 3,000-episode default, a fresh run under the old
    prefix would either collide with that filename or silently auto-resume
    a brand-new 3k experiment from a checkpoint that was actually trained
    for 3000 of a *planned* 10k run under the old real-HTTP setup. The
    rename makes that impossible: this pattern will never match anything
    in checkpoints/archive_10k_run/."""
    matches = glob.glob(pattern)
    if not matches:
        return 0, None

    best_ep, best_path = 0, None
    for path in matches:
        m = re.search(r"ep(\d+)", os.path.basename(path))
        if m:
            ep = int(m.group(1))
            if ep > best_ep:
                best_ep, best_path = ep, path
    return best_ep, best_path


class MockTargetsTrainer:
    """Trainer for the Extended D3QN agent against the 5 mock targets."""

    def __init__(
        self,
        model_path="dqn_web_sec_model.pth",
        verbose=True,
        fast=True,
        fresh=False,
        max_steps=75,
        replay_every=1,
        seed=42,
    ):
        self.model_path = model_path
        self.verbose = verbose
        self.checkpoint_prefix = "d3qn_primary_3k"
        self.fresh = fresh
        self.max_steps = max_steps
        self.replay_every = replay_every
        self.seed = seed

        # fast=True (the default): in-process Flask test-client transport
        # instead of real sockets. Training-speed optimization only -- see
        # module docstring above and env/inprocess_client.py for why this
        # doesn't change what's being tested.
        self.fast = fast
        self.target_sessions = None
        if self.fast:
            from env.inprocess_client import build_target_sessions

            print(
                "⚡ Fast mode (default): in-process transport, no separate "
                "services needed. Pass --real for real HTTP."
            )
            self.target_sessions = build_target_sessions()
        else:
            print("🌐 Real HTTP mode: make sure start_services.py is running.")

        # Extended D3QN: PER + Noisy Networks + Dueling + Double DQN
        self.agent = ImprovedDQNAgent(
            state_dim=15,  # 15-dim enriched state (see env/web_sec_env.py)
            action_dim=50,  # Restricted mock_targets action space
            use_prioritized_replay=True,
            use_noisy_networks=True,
            n_step=1,  # 1-step TD; matches all published training runs
            seed=self.seed,
        )
        print("🚀 Using Extended D3QN (PER + Noisy + Dueling + Double DQN)")

        self.start_episode = 1
        if not self.fresh:
            self._load_checkpoint()
        else:
            print("🆕 --fresh requested: ignoring existing checkpoints.")

        # Logging: real per-episode reward/loss + per-finding records, so
        # a real training curve can replace the synthetic Fig. 3 (see
        # research/generate_training_curve.py) and the paper's convergence
        # claims can eventually be backed by measured data.
        self.logger = TrainingLogger()
        self.logger.write_config(
            {
                "start_episode": self.start_episode,
                "max_steps": self.max_steps,
                "replay_every": self.replay_every,
                "seed": self.seed,
                "fast_mode": self.fast,
                "state_dim": 15,
                "action_dim": 50,
                "use_prioritized_replay": True,
                "use_noisy_networks": True,
                "n_step": 1,
            }
        )
        print(f"📝 Logging to {self.logger.run_dir}/ (episodes.csv, findings.csv)")

    def _load_checkpoint(self):
        latest_ep, latest_path = find_latest_checkpoint(
            pattern=f"{CHECKPOINT_DIR}/{self.checkpoint_prefix}_ep*.pth"
        )
        if latest_path:
            try:
                self.agent.load(latest_path)
                self.start_episode = latest_ep + 1
                print(f"✅ Resuming from checkpoint: {latest_path} (episode {latest_ep})")
                return
            except Exception as e:
                print(f"⚠️  Failed to load {latest_path}: {e}. Trying base model...")

        try:
            self.agent.load(self.model_path)
            print(f"✅ Loaded base model: {self.model_path}")
        except Exception:
            print("🆕 No checkpoint or base model found -- starting fresh (random weights).")
        self.start_episode = 1

    def train(self, total_episodes=10000):
        print("=" * 70)
        print("🎯 MOCK TARGETS TRAINING")
        print("=" * 70)
        print(f"Episodes: {self.start_episode} -> {total_episodes} "
              f"(max {self.max_steps} steps/episode, replay every {self.replay_every} step(s))")
        print("=" * 70)

        start_time = time.time()
        current_episode = self.start_episode
        try:
            for episode in range(self.start_episode, total_episodes + 1):
                current_episode = episode
                target = TARGETS[episode % len(TARGETS)]

                reward, vulns, steps, avg_loss = self._train_episode(target, episode)

                self.logger.log_episode(
                    episode=episode,
                    target=target["name"],
                    steps=steps,
                    total_reward=reward,
                    avg_loss=avg_loss,
                    vulns_found=vulns,
                    replay_buffer_size=len(self.agent.memory),
                )

                if episode % 10 == 0:
                    elapsed = time.time() - start_time
                    done_count = episode - self.start_episode + 1
                    eps_per_sec = done_count / elapsed if elapsed > 0 else 0
                    eta_min = (
                        (total_episodes - episode) / eps_per_sec / 60
                        if eps_per_sec > 0
                        else 0
                    )
                    loss_str = f"{avg_loss:.3f}" if avg_loss is not None else "n/a"
                    print(
                        f"Ep {episode:5d} | Target={target['name']:<13s} | "
                        f"Reward={reward:7.1f} | Loss={loss_str:>6s} | Steps={steps:2d} | "
                        f"Vulns={vulns} | {eps_per_sec:.2f} ep/s | ETA {eta_min:.0f}m"
                    )

                # Every 200 episodes, show what the agent's best confirmed
                # finds have been so far -- lets you see training condition
                # at a glance instead of scrolling back through the log.
                if episode % 200 == 0:
                    self._print_leaderboard(episode)

                if episode % 100 == 0:
                    self._save_checkpoint(episode)

        except KeyboardInterrupt:
            print("\n\n⚠️  Training interrupted by user!")
            print(f"💾 Saving checkpoint at episode {current_episode}...")
            self._save_checkpoint(current_episode, force_backup=True)
            self._print_leaderboard(current_episode)
            return
        except Exception:
            # Emergency save on any uncaught error so a crash mid-run
            # doesn't lose training progress -- then re-raise so the
            # failure is still visible (not swallowed).
            print(f"\n❌ Uncaught error at episode {current_episode} -- attempting emergency save...")
            try:
                self._save_checkpoint(current_episode, force_backup=True)
            except Exception as save_err:
                print(f"⚠️  Emergency save also failed: {save_err}")
            raise

        print("\n" + "=" * 70)
        print("✅ TRAINING COMPLETE")
        print("=" * 70)
        self._save_checkpoint(current_episode, force_backup=True)
        self._print_leaderboard(current_episode)
        print(f"\n📈 To plot the real training curve from this run:")
        print(f"   python training/plot_curve.py {self.logger.episodes_path}")

    def _train_episode(self, target, episode):
        session = self.target_sessions[target["port"]] if self.fast else None
        env = WebSecurityGym(
            target_url=target["url"], mode="mock_targets", session=session
        )
        # Seeded reset for reproducibility across runs/seeds.
        state, _ = env.reset(seed=self.seed + episode)
        total_reward = 0.0
        vulns = 0
        losses = []
        done = False
        steps = 0

        # Online DQN loop: act -> step env -> store transition -> learn.
        # replay_every controls how often a gradient step runs relative to
        # environment steps (1 = every step, matching PER's intended usage;
        # higher values trade update frequency for raw throughput).
        while not done and steps < self.max_steps:
            action = self.agent.act(state)
            next_state, reward, terminated, truncated, info = env.step(action)
            done = terminated or truncated

            self.agent.remember(state, action, reward, next_state, done)
            if steps % self.replay_every == 0:
                loss = self.agent.replay()
                if loss is not None:
                    losses.append(loss)

            total_reward += reward
            if reward >= 1.0:  # heuristic: reward >= 1.0 implies a confirmed vuln
                vulns += 1
                vuln_type = getattr(env, "last_vuln_type", "") or "unknown"
                is_new_best = self.logger.log_finding(
                    episode=episode,
                    target=target["name"],
                    vuln_type=vuln_type,
                    reward=reward,
                    step=steps,
                )
                if is_new_best:
                    print(
                        f"  🏆 NEW BEST: {vuln_type} | reward={reward:.2f} | "
                        f"target={target['name']} | ep={episode} step={steps}"
                    )

            state = next_state
            steps += 1

        env.close()
        avg_loss = sum(losses) / len(losses) if losses else None
        return total_reward, vulns, steps, avg_loss

    def _print_leaderboard(self, episode):
        print(f"\n📊 Best finds so far (through episode {episode}):")
        for line in self.logger.leaderboard_lines():
            print(line)
        print()

    def _save_checkpoint(self, episode, force_backup=False):
        os.makedirs(CHECKPOINT_DIR, exist_ok=True)
        final_path = f"{CHECKPOINT_DIR}/{self.checkpoint_prefix}_ep{episode}.pth"

        # Atomic write: save to a temp path in the same directory, then
        # rename over the final path. A crash mid-`torch.save` leaves the
        # temp file corrupted, not the checkpoint a resume would load --
        # os.replace() is atomic on both POSIX and Windows.
        tmp_path = final_path + ".tmp"
        self.agent.save(tmp_path)
        os.replace(tmp_path, final_path)
        print(f"💾 Checkpoint saved: {final_path}")

        if force_backup or episode % BACKUP_EVERY == 0:
            os.makedirs(BACKUP_DIR, exist_ok=True)
            backup_path = os.path.join(BACKUP_DIR, os.path.basename(final_path))
            shutil.copy2(final_path, backup_path)
            print(f"🗄️  Backup copy: {backup_path}")


if __name__ == "__main__":
    import argparse

    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", line_buffering=True)

    parser = argparse.ArgumentParser(description="Train the Extended D3QN agent on the 5 mock targets.")
    parser.add_argument(
        "--episodes", type=int, default=3000,
        help=(
            "Default changed 2026-08-09 from 10000 to 3000 to match the "
            "project-wide training budget adopted for the Reviewer 1 "
            "ablation study (5 variants x 5 seeds within the Aug 14 "
            "deadline). The original 10k run is archived at "
            "checkpoints/archive_10k_run/ (kept for Table I provenance, "
            "not meant to be extended). Pass --episodes 10000 explicitly "
            "if you specifically want the old budget."
        ),
    )
    parser.add_argument("--max-steps", type=int, default=75, help="Max steps per episode.")
    parser.add_argument("--replay-every", type=int, default=1, help="Run a gradient step every N env steps.")
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument(
        "--fresh",
        action="store_true",
        help="Start fresh, ignoring existing checkpoints.",
    )
    parser.add_argument(
        "--real",
        action="store_true",
        help=(
            "Use real HTTP (real sockets against start_services.py-run apps) "
            "instead of the default in-process transport. This script "
            "produces training checkpoints, not evaluation numbers -- the "
            "paper's actual results should come from autonomous_scan.py / "
            "eval_from_code.py / evaluate_fill_excel.py, which always use "
            "real HTTP and are unaffected by this flag either way. Only "
            "pass --real if you specifically want this training run to go "
            "over real HTTP too."
        ),
    )
    args = parser.parse_args()

    trainer = MockTargetsTrainer(
        fast=not args.real,
        fresh=args.fresh,
        max_steps=args.max_steps,
        replay_every=args.replay_every,
        seed=args.seed,
    )
    try:
        trainer.train(total_episodes=args.episodes)
    except Exception:
        import traceback

        traceback.print_exc()
        print("\n❌ CRITICAL ERROR DURING TRAINING")

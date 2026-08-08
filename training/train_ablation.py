"""
Ablation Study Trainer
=======================

Trains a single (variant, seed) combination for the Reviewer-1 statistical
rigor gate (research/REVISION_PLAN_incit2026.md, Phase 4). Six comparison
points, five of which need training:

    random           -- uniform random actions, no learning (lower bound)
    dqn              -- legacy_archive/dqn_agent.py, vanilla Double DQN
    d3qn_full        -- Extended D3QN: PER + Noisy Nets + multi-step (n=3)
    d3qn_no_per      -- Extended D3QN minus Prioritized Experience Replay
    d3qn_no_noisy    -- Extended D3QN minus Noisy Networks
    d3qn_no_multistep -- Extended D3QN minus multi-step returns (n=1)

Note on n_step: training/train_mock_targets.py (the hero-run script) uses
n_step=1 by default. For this ablation, d3qn_full uses n_step=3 so that
"drop multi-step" is a real, measurable ablation rather than dropping a
component that was never on. This makes the ablation's "full" config a
slightly different hyperparameter set than the currently-deployed hero
checkpoint -- worth knowing when writing up the results, not a bug.

Usage (one run = one variant + one seed):
    python training/train_ablation.py --variant d3qn_full --seed 1 --episodes 3000
    python training/train_ablation.py --variant random --seed 1 --episodes 3000

Typically invoked by training/run_ablation_suite.py, which loops over all
(variant, seed) pairs -- see that file for the single command that runs the
whole study.

Output layout (parallel to the hero-run trainer, kept in separate folders
so the two never collide or get mixed up in the stats):
    checkpoints/ablation/<variant>_seed<seed>_ep<N>.pth
    checkpoints/ablation/backup/<variant>_seed<seed>_ep<N>.pth
    logs/ablation/<variant>_seed<seed>/{episodes.csv, findings.csv, run_config.json}
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import io
import random
import shutil
import time

import numpy as np
import torch

from agent.improved_dqn_agent import ImprovedDQNAgent
from agent.random_baseline_agent import RandomBaselineAgent
from env.web_sec_env import WebSecurityGym
from training.training_logger import TrainingLogger
from training.train_mock_targets import TARGETS

# NOTE: UTF-8 stdout wrapping is done in __main__ below, not at import time --
# reassigning sys.stdout on import breaks callers (like run_ablation_suite.py)
# that already wrapped stdout themselves, closing the underlying buffer.

CHECKPOINT_DIR = "checkpoints/ablation"
BACKUP_DIR = os.path.join(CHECKPOINT_DIR, "backup")
LOG_ROOT = "logs/ablation"
STATE_DIM = 15
ACTION_DIM = 50


def build_agent(variant: str, seed: int):
    """Constructs the agent for a given ablation variant. Global RNG seeds
    are set by the caller before this runs, for reproducibility of anything
    the agent's own __init__ does that isn't seed-parametrized."""
    if variant == "random":
        return RandomBaselineAgent(state_dim=STATE_DIM, action_dim=ACTION_DIM, seed=seed)

    if variant == "dqn":
        # Legacy vanilla Double DQN baseline -- no seed param on this class,
        # relies on the global torch/numpy/random seeding done by the caller.
        from legacy_archive.dqn_agent import DQNAgent

        return DQNAgent(state_dim=STATE_DIM, action_dim=ACTION_DIM)

    if variant == "d3qn_full":
        return ImprovedDQNAgent(
            state_dim=STATE_DIM, action_dim=ACTION_DIM,
            use_prioritized_replay=True, use_noisy_networks=True, n_step=3, seed=seed,
        )
    if variant == "d3qn_no_per":
        return ImprovedDQNAgent(
            state_dim=STATE_DIM, action_dim=ACTION_DIM,
            use_prioritized_replay=False, use_noisy_networks=True, n_step=3, seed=seed,
        )
    if variant == "d3qn_no_noisy":
        return ImprovedDQNAgent(
            state_dim=STATE_DIM, action_dim=ACTION_DIM,
            use_prioritized_replay=True, use_noisy_networks=False, n_step=3, seed=seed,
        )
    if variant == "d3qn_no_multistep":
        return ImprovedDQNAgent(
            state_dim=STATE_DIM, action_dim=ACTION_DIM,
            use_prioritized_replay=True, use_noisy_networks=True, n_step=1, seed=seed,
        )

    raise ValueError(
        f"Unknown variant '{variant}'. Expected one of: random, dqn, d3qn_full, "
        f"d3qn_no_per, d3qn_no_noisy, d3qn_no_multistep"
    )


def find_variant_checkpoint(run_name: str):
    """Highest-episode checkpoint for one (variant, seed) combo, or
    (0, None) if none exists yet. Mirrors train_mock_targets.py's
    find_latest_checkpoint but scoped to checkpoints/ablation/."""
    import glob
    import re as _re

    matches = glob.glob(f"{CHECKPOINT_DIR}/{run_name}_ep*.pth")
    best_ep, best_path = 0, None
    for path in matches:
        m = _re.search(r"_ep(\d+)\.pth$", path)
        if m and int(m.group(1)) > best_ep:
            best_ep, best_path = int(m.group(1)), path
    return best_ep, best_path


class AblationTrainer:
    def __init__(self, variant: str, seed: int, max_steps=75, replay_every=1, fresh=False):
        self.variant = variant
        self.seed = seed
        self.max_steps = max_steps
        self.replay_every = replay_every
        self.run_name = f"{variant}_seed{seed}"
        self.fresh = fresh
        self.start_episode = 1

        # Global seeding -- covers legacy DQNAgent (no seed param) and
        # anything in torch/numpy init paths not already seed-parametrized.
        random.seed(seed)
        np.random.seed(seed)
        torch.manual_seed(seed)

        from env.inprocess_client import build_target_sessions

        print(f"⚡ [{self.run_name}] fast in-process mode")
        self.target_sessions = build_target_sessions()

        self.agent = build_agent(variant, seed)
        self.is_learning = variant != "random"
        print(f"🧪 [{self.run_name}] agent ready ({'trainable' if self.is_learning else 'static/no learning'})")

        # Resume support: if this exact (variant, seed) already has a
        # checkpoint (e.g. the suite got interrupted at ep1500 of 3000),
        # pick up from there instead of restarting -- an overnight run that
        # gets killed at combo 14 of 30 shouldn't lose the 13 before it, and
        # shouldn't re-waste the partial progress on combo 14 either.
        # Random has nothing to resume (stateless, no real training).
        if self.is_learning and not fresh:
            latest_ep, latest_path = find_variant_checkpoint(self.run_name)
            if latest_path:
                try:
                    self.agent.load(latest_path)
                    self.start_episode = latest_ep + 1
                    print(f"[{self.run_name}] ✅ resuming from {latest_path} (episode {latest_ep})")
                except Exception as e:
                    print(f"[{self.run_name}] ⚠️  failed to load {latest_path}: {e} -- starting fresh")
        elif fresh:
            print(f"[{self.run_name}] --fresh requested: ignoring any existing checkpoint")

        self.logger = TrainingLogger(log_root=LOG_ROOT, run_name=self.run_name)
        self.logger.write_config(
            {
                "variant": variant,
                "seed": seed,
                "max_steps": max_steps,
                "replay_every": replay_every,
                "state_dim": STATE_DIM,
                "action_dim": ACTION_DIM,
            }
        )

    def train(self, total_episodes: int):
        if self.start_episode > total_episodes:
            print(f"[{self.run_name}] already at episode {self.start_episode - 1} >= "
                  f"target {total_episodes} -- nothing to do")
            return
        print(f"[{self.run_name}] training episodes {self.start_episode}->{total_episodes} "
              f"(max {self.max_steps} steps each)")
        start_time = time.time()
        current_episode = self.start_episode - 1
        try:
            for episode in range(self.start_episode, total_episodes + 1):
                current_episode = episode
                target = TARGETS[episode % len(TARGETS)]
                reward, vulns, steps, avg_loss = self._run_episode(target, episode)

                self.logger.log_episode(
                    episode=episode, target=target["name"], steps=steps,
                    total_reward=reward, avg_loss=avg_loss, vulns_found=vulns,
                    replay_buffer_size=self._buffer_size(),
                )

                if episode % 100 == 0:
                    elapsed = time.time() - start_time
                    episodes_done_this_run = episode - self.start_episode + 1
                    eps_per_sec = episodes_done_this_run / elapsed if elapsed > 0 else 0
                    eta_min = (total_episodes - episode) / eps_per_sec / 60 if eps_per_sec > 0 else 0
                    loss_str = f"{avg_loss:.3f}" if avg_loss is not None else "n/a"
                    print(
                        f"[{self.run_name}] Ep {episode:5d}/{total_episodes} | Reward={reward:7.1f} | "
                        f"Loss={loss_str:>6s} | Vulns={vulns} | {eps_per_sec:.2f} ep/s | ETA {eta_min:.0f}m"
                    )

                if self.is_learning and episode % 500 == 0:
                    self._save_checkpoint(episode)

        except KeyboardInterrupt:
            print(f"\n[{self.run_name}] interrupted -- saving checkpoint at episode {current_episode}")
            if self.is_learning:
                self._save_checkpoint(current_episode, force_backup=True)
            return
        except Exception:
            print(f"\n[{self.run_name}] uncaught error at episode {current_episode} -- emergency save")
            if self.is_learning:
                try:
                    self._save_checkpoint(current_episode, force_backup=True)
                except Exception as save_err:
                    print(f"[{self.run_name}] emergency save also failed: {save_err}")
            raise

        if self.is_learning:
            self._save_checkpoint(current_episode, force_backup=True)
        else:
            self.agent.save(f"{CHECKPOINT_DIR}/{self.run_name}_ep{current_episode}.pth")
        print(f"[{self.run_name}] ✅ done. Logs: {self.logger.run_dir}/")

    def _run_episode(self, target, episode):
        session = self.target_sessions[target["port"]]
        env = WebSecurityGym(target_url=target["url"], mode="mock_targets", session=session)
        state, _ = env.reset(seed=self.seed * 100000 + episode)
        total_reward, vulns, steps, done = 0.0, 0, 0, False
        losses = []

        while not done and steps < self.max_steps:
            action = self.agent.act(state, training=self.is_learning)
            next_state, reward, terminated, truncated, info = env.step(action)
            done = terminated or truncated

            if self.is_learning:
                self.agent.remember(state, action, reward, next_state, done)
                if steps % self.replay_every == 0:
                    loss = self.agent.replay()
                    if loss is not None:
                        losses.append(loss)

            total_reward += reward
            if reward >= 1.0:
                vulns += 1
                vuln_type = getattr(env, "last_vuln_type", "") or "unknown"
                is_new_best = self.logger.log_finding(
                    episode=episode, target=target["name"], vuln_type=vuln_type, reward=reward, step=steps,
                )
                if is_new_best:
                    print(f"  [{self.run_name}] 🏆 NEW BEST: {vuln_type} | reward={reward:.2f} | ep={episode}")

            state = next_state
            steps += 1

        env.close()
        avg_loss = sum(losses) / len(losses) if losses else None
        return total_reward, vulns, steps, avg_loss

    def _buffer_size(self):
        mem = getattr(self.agent, "memory", None)
        return len(mem) if mem is not None else 0

    def _save_checkpoint(self, episode, force_backup=False):
        os.makedirs(CHECKPOINT_DIR, exist_ok=True)
        final_path = f"{CHECKPOINT_DIR}/{self.run_name}_ep{episode}.pth"
        tmp_path = final_path + ".tmp"
        self.agent.save(tmp_path)
        os.replace(tmp_path, final_path)
        if force_backup or episode % 1500 == 0:
            os.makedirs(BACKUP_DIR, exist_ok=True)
            shutil.copy2(final_path, os.path.join(BACKUP_DIR, os.path.basename(final_path)))


if __name__ == "__main__":
    import argparse

    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", line_buffering=True)

    parser = argparse.ArgumentParser(description="Train one (variant, seed) combination for the ablation study.")
    parser.add_argument(
        "--variant", required=True,
        choices=["random", "dqn", "d3qn_full", "d3qn_no_per", "d3qn_no_noisy", "d3qn_no_multistep"],
    )
    parser.add_argument("--seed", type=int, required=True)
    parser.add_argument("--episodes", type=int, default=3000)
    parser.add_argument("--max-steps", type=int, default=75)
    parser.add_argument("--replay-every", type=int, default=1)
    parser.add_argument(
        "--fresh", action="store_true",
        help="Ignore any existing checkpoint for this (variant, seed) and start over from episode 1.",
    )
    args = parser.parse_args()

    trainer = AblationTrainer(
        variant=args.variant, seed=args.seed, max_steps=args.max_steps,
        replay_every=args.replay_every, fresh=args.fresh,
    )
    trainer.train(total_episodes=args.episodes)

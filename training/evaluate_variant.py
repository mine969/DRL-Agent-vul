"""
Ablation Eval: Deterministic Evaluation of One (variant, seed)
=================================================================

Loads a trained checkpoint from training/train_ablation.py and runs
greedy (no-exploration) evaluation episodes across all 5 mock targets.
This is what feeds training/stats_ablation.py -- the Friedman/Wilcoxon
tests need a consistent, comparable performance number per (variant, seed),
and that number has to come from evaluation, not training reward (training
reward is contaminated by exploration noise and, for PER/Noisy variants,
by the learning process itself still being active).

Usage:
    python training/evaluate_variant.py --variant d3qn_full --seed 1
    python training/evaluate_variant.py --variant random --seed 1 --eval-episodes 20

Output:
    logs/ablation/<variant>_seed<seed>/eval_results.csv   -- one row per eval episode
    logs/ablation/<variant>_seed<seed>/eval_summary.json  -- aggregated stats
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import csv
import glob
import json
import re

from env.web_sec_env import WebSecurityGym
from training.train_mock_targets import TARGETS
from training.train_ablation import build_agent, CHECKPOINT_DIR, LOG_ROOT, STATE_DIM, ACTION_DIM


def find_checkpoint(variant, seed):
    pattern = f"{CHECKPOINT_DIR}/{variant}_seed{seed}_ep*.pth"
    matches = glob.glob(pattern)
    if not matches:
        return None
    best_ep, best_path = -1, None
    for path in matches:
        m = re.search(r"_ep(\d+)\.pth$", path)
        if m and int(m.group(1)) > best_ep:
            best_ep, best_path = int(m.group(1)), path
    return best_path


def evaluate(variant, seed, eval_episodes=20, max_steps=75):
    agent = build_agent(variant, seed)
    is_learning = variant != "random"

    ckpt_path = None
    if is_learning:
        ckpt_path = find_checkpoint(variant, seed)
        if ckpt_path is None:
            raise FileNotFoundError(
                f"No checkpoint found for {variant}_seed{seed} in {CHECKPOINT_DIR}/. "
                f"Run training/train_ablation.py --variant {variant} --seed {seed} first."
            )
        agent.load(ckpt_path)
        print(f"[{variant}_seed{seed}] loaded {ckpt_path}")
    else:
        print(f"[{variant}_seed{seed}] random baseline -- no checkpoint to load")

    from env.inprocess_client import build_target_sessions

    target_sessions = build_target_sessions()

    run_dir = os.path.join(LOG_ROOT, f"{variant}_seed{seed}")
    os.makedirs(run_dir, exist_ok=True)
    csv_path = os.path.join(run_dir, "eval_results.csv")
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        csv.writer(f).writerow(
            ["variant", "seed", "target", "eval_episode", "total_reward", "vulns_found", "vuln_types", "steps"]
        )

    rows = []
    for target in TARGETS:
        session = target_sessions[target["port"]]
        for ep in range(eval_episodes):
            env = WebSecurityGym(target_url=target["url"], mode="mock_targets", session=session)
            # Distinct seed space from training (offset) so eval episodes
            # never replay exactly the same env RNG sequence seen in training.
            state, _ = env.reset(seed=seed * 900000 + hash(target["name"]) % 10000 + ep)
            total_reward, vulns, steps, done = 0.0, 0, 0, False
            vuln_types = []

            while not done and steps < max_steps:
                action = agent.act(state, training=False)  # greedy -- no exploration
                state, reward, terminated, truncated, info = env.step(action)
                done = terminated or truncated
                total_reward += reward
                if reward >= 1.0:
                    vulns += 1
                    vuln_types.append(getattr(env, "last_vuln_type", "") or "unknown")
                steps += 1

            env.close()
            rows.append(
                {
                    "variant": variant, "seed": seed, "target": target["name"], "eval_episode": ep,
                    "total_reward": total_reward, "vulns_found": vulns,
                    "vuln_types": "|".join(vuln_types), "steps": steps,
                }
            )

    with open(csv_path, "a", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        for r in rows:
            w.writerow([r["variant"], r["seed"], r["target"], r["eval_episode"],
                        f"{r['total_reward']:.4f}", r["vulns_found"], r["vuln_types"], r["steps"]])

    n = len(rows)
    mean_reward = sum(r["total_reward"] for r in rows) / n
    mean_vulns = sum(r["vulns_found"] for r in rows) / n
    per_target = {}
    for target in TARGETS:
        t_rows = [r for r in rows if r["target"] == target["name"]]
        per_target[target["name"]] = {
            "mean_reward": sum(r["total_reward"] for r in t_rows) / len(t_rows),
            "mean_vulns": sum(r["vulns_found"] for r in t_rows) / len(t_rows),
            "detection_rate": sum(1 for r in t_rows if r["vulns_found"] > 0) / len(t_rows),
        }

    summary = {
        "variant": variant, "seed": seed, "checkpoint": ckpt_path,
        "eval_episodes_per_target": eval_episodes, "n_total_episodes": n,
        "mean_reward": mean_reward, "mean_vulns": mean_vulns,
        "overall_detection_rate": sum(1 for r in rows if r["vulns_found"] > 0) / n,
        "per_target": per_target,
    }
    summary_path = os.path.join(run_dir, "eval_summary.json")
    with open(summary_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)

    print(f"[{variant}_seed{seed}] eval done: mean_reward={mean_reward:.2f} "
          f"mean_vulns={mean_vulns:.2f} detection_rate={summary['overall_detection_rate']:.1%}")
    print(f"[{variant}_seed{seed}] -> {csv_path}\n[{variant}_seed{seed}] -> {summary_path}")
    return summary


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--variant", required=True,
        choices=["random", "dqn", "d3qn_full", "d3qn_no_per", "d3qn_no_noisy", "d3qn_no_multistep"],
    )
    parser.add_argument("--seed", type=int, required=True)
    parser.add_argument("--eval-episodes", type=int, default=20, help="Eval episodes PER target (5 targets total).")
    parser.add_argument("--max-steps", type=int, default=75)
    args = parser.parse_args()

    evaluate(args.variant, args.seed, eval_episodes=args.eval_episodes, max_steps=args.max_steps)

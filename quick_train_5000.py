"""
Quick Training Script - 10000 Episodes
Simplified version with immediate feedback and checkpoint resume
"""

import sys
import torch
import numpy as np
from agent.improved_dqn_agent import ImprovedDQNAgent
from env.web_sec_env import WebSecurityGym
import time
import os
import glob
import argparse

# Unbuffered output
sys.stdout.reconfigure(line_buffering=True)

print("=" * 70, flush=True)
print("🚀 STARTING TRAINING - 10000 EPISODES", flush=True)
print("=" * 70, flush=True)

# Target URLs (rotating)
TARGETS = [
    "http://localhost:5002",  # E-Commerce
    "http://localhost:5003",  # Social
    "http://localhost:5004",  # Banking
    "http://localhost:5005",  # Blog
    "http://localhost:5006",  # FileShare
]


# Find latest checkpoint (compatible with old naming)
def find_available_checkpoints():
    """Find all checkpoints and return them sorted by episode (descending)."""
    patterns = [
        "checkpoints/improved_mock_ep*.pth",  # Old format
        "checkpoints/quick_train_ep*.pth",  # New format
    ]

    all_checkpoints = []
    for pattern in patterns:
        all_checkpoints.extend(glob.glob(pattern))

    if not all_checkpoints:
        return []

    # Extract episode numbers
    checkpoint_episodes = []
    for path in all_checkpoints:
        try:
            # Normalize path for multi-platform support
            path = path.replace("\\", "/")
            # Extract number from filename
            filename = os.path.basename(path)
            import re

            match = re.search(r"ep(\d+)", filename)
            if match:
                ep_num = int(match.group(1))
                checkpoint_episodes.append((ep_num, path))
        except:
            continue

    # Return sorted by episode descending
    checkpoint_episodes.sort(key=lambda x: x[0], reverse=True)
    return checkpoint_episodes


# Parse arguments
parser = argparse.ArgumentParser(description="Quick Training Script for DRL Agent")
parser.add_argument(
    "--fresh",
    action="store_true",
    help="Start fresh training without resuming from checkpoint",
)
args = parser.parse_args()

print("\n📊 Initializing Agent...", flush=True)
agent = ImprovedDQNAgent(
    state_dim=15,
    action_dim=50,
    use_prioritized_replay=True,
    use_noisy_networks=True,
    seed=42,
)

# Try to resume from checkpoint with smart fallback
start_episode = 1
if not args.fresh:
    available_checkpoints = find_available_checkpoints()
    if available_checkpoints:
        print(
            f"🔍 Found {len(available_checkpoints)} existing checkpoints.", flush=True
        )
        success = False
        for latest_ep, checkpoint_path in available_checkpoints:
            print(
                f"⚙️  Attempting to load: {checkpoint_path} (Episode {latest_ep})...",
                flush=True,
            )
            try:
                agent.load(checkpoint_path)
                start_episode = latest_ep + 1
                print(f"✅ Successfully resumed from Episode {latest_ep}!", flush=True)
                success = True
                break
            except Exception as e:
                print(f"⚠️  LOAD FAILED for {checkpoint_path}: {e}", flush=True)
                print(f"   Searching for next best checkpoint...", flush=True)

        if not success:
            print("❌ ALL checkpoints failed to load. Starting fresh.", flush=True)
            start_episode = 1
    else:
        print("🆕 No existing checkpoints found. Starting fresh training.", flush=True)
else:
    print("🚀 FRESH START requested. Ignoring existing checkpoints.", flush=True)

print("✅ Agent initialized!", flush=True)

# Training loop
print(f"\n🎯 Starting training from episode {start_episode} to 10000...", flush=True)
print("=" * 70, flush=True)

start_time = time.time()

try:
    for episode in range(start_episode, 10001):
        # Rotate targets
        target_url = TARGETS[episode % len(TARGETS)]

        try:
            # Initialize environment (verbose off for speed)
            env = WebSecurityGym(
                target_url=target_url, mode="mock_targets", verbose=False
            )
            state, _ = env.reset(seed=42 + episode)

            total_reward = 0
            steps = 0
            done = False

            # Episode loop
            while not done and steps < 75:
                action = agent.act(state)
                next_state, reward, terminated, truncated, _ = env.step(action)
                done = terminated or truncated

                agent.remember(state, action, reward, next_state, done)

                # Log if vulnerability found
                if reward >= 1.0:
                    print(
                        f"  ✨ VULN FOUND! ep={episode}, step={steps}, reward={reward:.1f}",
                        flush=True,
                    )

                # Train every 4 steps
                if steps % 4 == 0:
                    agent.replay()

                total_reward += reward
                state = next_state
                steps += 1

            print(
                f"  ✅ Ep {episode:4d} Complete | Reward: {total_reward:6.1f} | Steps: {steps:2d}",
                flush=True,
            )

            # Progress reporting
            if episode % 10 == 0:
                elapsed = time.time() - start_time
                eps_per_sec = (episode - start_episode + 1) / elapsed
                eta_seconds = (10000 - episode) / eps_per_sec if eps_per_sec > 0 else 0
                eta_minutes = int(eta_seconds / 60)

                print(
                    f"\n📊 PROGRESS: Ep {episode:4d} | Avg Speed: {eps_per_sec:.2f} ep/s | ETA: {eta_minutes}m",
                    flush=True,
                )

            # Save checkpoint (More frequent for visibility)
            if episode % 100 == 0:
                os.makedirs("checkpoints", exist_ok=True)
                checkpoint_path = f"checkpoints/improved_mock_ep{episode}.pth"
                agent.save(checkpoint_path)
                print(f"\n💾 Checkpoint saved: {checkpoint_path}\n", flush=True)

        except Exception as e:
            print(f"\n❌ ERROR in episode {episode}: {e}", flush=True)
            print("   Continuing to next episode...\n", flush=True)
            continue

except KeyboardInterrupt:
    print("\n\n⚠️  Training interrupted by user!", flush=True)
    current_ep = episode if "episode" in locals() else start_episode
    print(f"💾 Saving checkpoint at episode {current_ep}...", flush=True)
    os.makedirs("checkpoints", exist_ok=True)
    agent.save(f"checkpoints/improved_mock_ep{current_ep}.pth")
    print("✅ Saved!", flush=True)

print("\n" + "=" * 70, flush=True)
print("✅ TRAINING COMPLETE!", flush=True)
print("=" * 70, flush=True)

"""
Verification Script: Verify Reward Signaling during training
Runs a short 5-episode training burst with verbose output.
"""

import sys
import torch
import numpy as np
from agent.improved_dqn_agent import ImprovedDQNAgent
from env.web_sec_env import WebSecurityGym
import time
import os
import glob

# Unbuffered output
sys.stdout.reconfigure(line_buffering=True)

TARGETS = [
    "http://localhost:5002",  # E-Commerce
    "http://localhost:5003",  # Social
    "http://localhost:5004",  # Banking
    "http://localhost:5005",  # Blog
    "http://localhost:5006",  # FileShare
]

print("📊 Initializing Agent for Verification...", flush=True)
agent = ImprovedDQNAgent(state_dim=15, action_dim=50, seed=42)


# Load latest checkpoint
def find_latest_checkpoint():
    patterns = ["checkpoints/improved_mock_ep*.pth", "checkpoints/quick_train_ep*.pth"]
    all_checkpoints = []
    for pattern in patterns:
        all_checkpoints.extend(glob.glob(pattern))
    if not all_checkpoints:
        return None, 0
    checkpoint_episodes = []
    for path in all_checkpoints:
        try:
            ep_num = int(path.split("ep")[-1].replace(".pth", ""))
            checkpoint_episodes.append((ep_num, path))
        except:
            continue
    if not checkpoint_episodes:
        return None, 0
    checkpoint_episodes.sort(reverse=True)
    return checkpoint_episodes[0][1], checkpoint_episodes[0][0]


checkpoint_path, start_episode = find_latest_checkpoint()
if checkpoint_path:
    print(f"✅ Loading: {checkpoint_path}", flush=True)
    agent.load(checkpoint_path)
    start_episode += 1

print(f"\n🎯 Running 5-episode verification starting from {start_episode}...")
print("=" * 70)

for episode in range(start_episode, start_episode + 5):
    target_url = TARGETS[episode % len(TARGETS)]
    print(f"\n📡 EPISODE {episode} | Target: {target_url}", flush=True)

    # Verbose mode to see the actions!
    env = WebSecurityGym(target_url=target_url, mode="mock_targets", verbose=True)
    state, _ = env.reset(seed=42 + episode)

    total_reward = 0
    steps = 0
    done = False

    while not done and steps < 50:  # Limit steps for speed
        action = agent.act(state)
        # The env print the action if verbose=True
        next_state, reward, terminated, truncated, _ = env.step(action)

        if reward > 0:
            print(f"  💰 REWARD DETECTED: {reward}", flush=True)

        done = terminated or truncated
        agent.remember(state, action, reward, next_state, done)

        if steps % 4 == 0:
            agent.replay()

        total_reward += reward
        state = next_state
        steps += 1

    print(
        f"\n🏁 Finished Episode {episode} | Total Reward: {total_reward:6.1f} | Steps: {steps}",
        flush=True,
    )

print("\n" + "=" * 70)
print("✅ REWARD VERIFICATION COMPLETE!")
print("=" * 70)

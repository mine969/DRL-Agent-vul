"""
Quick Training Script - 5000 Episodes
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

# Unbuffered output
sys.stdout.reconfigure(line_buffering=True)

print("=" * 70, flush=True)
print("🚀 STARTING TRAINING - 5000 EPISODES", flush=True)
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
def find_latest_checkpoint():
    """Find the latest checkpoint to resume from."""
    patterns = [
        "checkpoints/improved_mock_ep*.pth",  # Old format
        "checkpoints/quick_train_ep*.pth"     # New format
    ]
    
    all_checkpoints = []
    for pattern in patterns:
        all_checkpoints.extend(glob.glob(pattern))
    
    if not all_checkpoints:
        return None, 0
    
    # Extract episode numbers
    checkpoint_episodes = []
    for path in all_checkpoints:
        try:
            # Extract number from filename
            ep_num = int(path.split('ep')[-1].replace('.pth', ''))
            checkpoint_episodes.append((ep_num, path))
        except:
            continue
    
    if not checkpoint_episodes:
        return None, 0
    
    # Return the latest
    checkpoint_episodes.sort(reverse=True)
    return checkpoint_episodes[0][1], checkpoint_episodes[0][0]

print("\n📊 Initializing Agent...", flush=True)
agent = ImprovedDQNAgent(
    state_dim=15,
    action_dim=50,
    use_prioritized_replay=True,
    use_noisy_networks=True,
    seed=42
)

# Try to resume from checkpoint
checkpoint_path, start_episode = find_latest_checkpoint()
if checkpoint_path:
    print(f"✅ Resuming from: {checkpoint_path} (Episode {start_episode})", flush=True)
    try:
        agent.load(checkpoint_path)
        start_episode += 1  # Start from next episode
    except Exception as e:
        print(f"⚠️  Failed to load checkpoint: {e}", flush=True)
        print("   Starting fresh...", flush=True)
        start_episode = 1
else:
    print("🆕 No checkpoint found, starting fresh", flush=True)
    start_episode = 1

print("✅ Agent initialized!", flush=True)

# Training loop
print(f"\n🎯 Starting training from episode {start_episode} to 5000...", flush=True)
print("=" * 70, flush=True)

start_time = time.time()

try:
    for episode in range(start_episode, 5001):
        # Rotate targets
        target_url = TARGETS[episode % len(TARGETS)]
        
        try:
            # Initialize environment (verbose off for speed)
            env = WebSecurityGym(target_url=target_url, mode="mock_targets", verbose=False)
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
                
                # Train every 4 steps
                if steps % 4 == 0:
                    agent.replay()
                
                total_reward += reward
                state = next_state
                steps += 1
            
            # Progress reporting
            if episode % 10 == 0:
                elapsed = time.time() - start_time
                eps_per_sec = (episode - start_episode + 1) / elapsed
                eta_seconds = (5000 - episode) / eps_per_sec if eps_per_sec > 0 else 0
                eta_minutes = int(eta_seconds / 60)
                
                print(f"Ep {episode:4d} | Reward: {total_reward:6.1f} | Steps: {steps:2d} | "
                      f"Speed: {eps_per_sec:.1f} ep/s | ETA: {eta_minutes}m", flush=True)
            
            # Save checkpoint (use old naming for compatibility)
            if episode % 500 == 0:
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
    current_ep = episode if 'episode' in locals() else start_episode
    print(f"💾 Saving checkpoint at episode {current_ep}...", flush=True)
    os.makedirs("checkpoints", exist_ok=True)
    agent.save(f"checkpoints/improved_mock_ep{current_ep}.pth")
    print("✅ Saved!", flush=True)

print("\n" + "=" * 70, flush=True)
print("✅ TRAINING COMPLETE!", flush=True)
print("=" * 70, flush=True)

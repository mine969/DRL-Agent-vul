"""
Manual Evaluation Script
Runs a one-off evaluation of the latest model checkpoint and logs to TRAINING_PROGRESS.md.
"""

import gymnasium as gym
from env.web_sec_env import WebSecurityGym
from agent.dqn_agent import DQNAgent
import torch
import numpy as np
import glob
import os
import threading
import time
import datetime
from env.target_app import app

def start_server():
    """Start the target web application"""
    try:
        app.run(debug=False, use_reloader=False, port=5000)
    except Exception as e:
        print(f"Server error (might be already running): {e}")

def find_latest_checkpoint():
    """Find the latest checkpoint file"""
    checkpoints = glob.glob("checkpoints/dqn_checkpoint_ep*.pth")
    if not checkpoints:
        return None, 0
    
    episodes = []
    for cp in checkpoints:
        try:
            ep_num = int(cp.split("ep")[1].split(".pth")[0])
            episodes.append((ep_num, cp))
        except:
            continue
    
    if episodes:
        episodes.sort(reverse=True)
        return episodes[0][1], episodes[0][0]
    return None, 0

def evaluate():
    print("🚀 Starting Manual Evaluation...")
    
    # Start server in background
    server_thread = threading.Thread(target=start_server, daemon=True)
    server_thread.start()
    time.sleep(2) # Wait for server
    
    # Setup
    env = WebSecurityGym()
    state_dim = env.observation_space.shape[0]
    action_dim = env.action_space.n
    agent = DQNAgent(state_dim, action_dim)
    
    # Load model
    checkpoint_path, episode = find_latest_checkpoint()
    if checkpoint_path:
        print(f"📂 Loading checkpoint: {checkpoint_path}")
        agent.brain.load_state_dict(torch.load(checkpoint_path))
        agent.epsilon = 0.0 # Pure exploitation
    else:
        print("❌ No checkpoint found!")
        return

    # Evaluation Loop
    eval_episodes = 5
    total_reward = 0
    vulns_found = 0
    successful_attacks = 0
    
    print(f"🧪 Running {eval_episodes} evaluation episodes...")
    
    for i in range(eval_episodes):
        state, _ = env.reset()
        done = False
        ep_reward = 0
        
        while not done:
            action = agent.act(state)
            next_state, reward, terminated, truncated, _ = env.step(action)
            done = terminated or truncated
            
            ep_reward += reward
            state = next_state
            
            if reward > 50:
                vulns_found += 1
        
        total_reward += ep_reward
        if ep_reward > 0:
            successful_attacks += 1
        print(f"   Episode {i+1}: Reward = {ep_reward:.1f}")

    # Metrics
    avg_reward = total_reward / eval_episodes
    success_rate = (successful_attacks / eval_episodes) * 100
    
    # Log
    log_file = "evaluation/TRAINING_PROGRESS.md"
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    log_entry = f"| {timestamp} | {episode} | {avg_reward:.1f} | {vulns_found} | {success_rate:.1f}% | 0.0000 | Manual Eval |\n"
    
    with open(log_file, "a") as f:
        f.write(log_entry)
        
    print("\n📊 Evaluation Results:")
    print(f"   - Avg Reward: {avg_reward:.1f}")
    print(f"   - Vulns Found: {vulns_found}")
    print(f"   - Success Rate: {success_rate:.1f}%")
    print(f"📝 Logged to {log_file}")

if __name__ == "__main__":
    evaluate()

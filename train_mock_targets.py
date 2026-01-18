"""
Mock Targets Specialized Training
=================================

This script trains the DRL agent on the 5 mock websites to improve
vulnerability detection capabilities on these specific targets.

Usage:
    python train_mock_targets.py --episodes 1000
"""

import torch
import numpy as np
from agent.dqn_agent import DQNAgent
from env.web_sec_env import WebSecurityGym
import sys
import io
import os
import subprocess
import time
import requests

# Force UTF-8 encoding
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

TARGETS = [
    {"name": "Banking App", "script": "env/target_app_banking.py", "port": 5004, "url": "http://localhost:5004"},
    {"name": "Blog Platform", "script": "env/target_app_blog.py", "port": 5005, "url": "http://localhost:5005"},
    {"name": "E-Commerce", "script": "env/target_app_ecommerce.py", "port": 5002, "url": "http://localhost:5002"},
    {"name": "File Share", "script": "env/target_app_fileshare.py", "port": 5006, "url": "http://localhost:5006"},
    {"name": "Social Media", "script": "env/target_app_social.py", "port": 5003, "url": "http://localhost:5003"}
]

class MockTargetsTrainer:
    """Trainer for Mock Targets."""
    
    def __init__(self, model_path="dqn_web_sec_model.pth", verbose=True):
        self.model_path = model_path
        self.verbose = verbose
        self.checkpoint_prefix = "agent_v2.0"
        
        # Initialize agent
        self.agent = DQNAgent(state_dim=11, action_dim=100)
        
        # Load existing model if possible
        self._load_model()
        
        # Set high epsilon for exploration
        self.agent.epsilon = 1.0
        self.agent.epsilon_min = 0.1
        self.agent.epsilon_decay = 0.995

    def _load_model(self):
        try:
            device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
            # Try to find latest checkpoint
            from utils.model_loader import find_latest_checkpoint
            # Look for 2.0 checkpoints first
            latest_ep, latest_path = find_latest_checkpoint(pattern="agent_v2.0_ep*.pth")
            
            if latest_path:
                print(f"✅ Resuming from checkpoint: {latest_path}")
                self.agent.brain.load_state_dict(torch.load(latest_path, map_location=device))
                self.agent.target_brain.load_state_dict(self.agent.brain.state_dict())
                self.start_episode = latest_ep + 1
            else:
                # Fallback to base model
                print(f"🆕 Starting fresh (or from base model)")
                try:
                    self.agent.brain.load_state_dict(torch.load(self.model_path, map_location=device))
                    self.agent.target_brain.load_state_dict(self.agent.brain.state_dict())
                    print(f"✅ Loaded base model: {self.model_path}")
                except:
                    print("⚠️ No base model found, initializing random weights")
                self.start_episode = 1
                
        except Exception as e:
            print(f"⚠️ Error loading model: {e}")
            self.start_episode = 1

    def train(self, total_episodes=1000):
        print("=" * 70)
        print("🎯 MOCK TARGETS TRAINING")
        print("=" * 70)
        print("⚠️  Make sure start_services.py is running!")
        print("=" * 70)
        
        current_episode = self.start_episode
        try:
            for episode in range(self.start_episode, total_episodes + 1):
                current_episode = episode
                # Rotate targets
                target = TARGETS[episode % len(TARGETS)]
                
                # Train one episode (services must be running)
                reward, vulns = self._train_episode(target['url'], episode)
                
                if episode % 10 == 0:
                    print(f"Episode {episode}: Target={target['name']} | Reward={reward:.1f} | Vulns={vulns} | Epsilon={self.agent.epsilon:.3f}")
                
                # Save checkpoint
                if episode % 100 == 0:
                    self._save_checkpoint(episode)
                    
        except KeyboardInterrupt:
            print("\n\n⚠️  Training interrupted by user!")
            print(f"💾 Saving checkpoint at episode {current_episode}...")
            self._save_checkpoint(current_episode)
            print(f"✅ Checkpoint saved: checkpoints/{self.checkpoint_prefix}_ep{current_episode}.pth")

    def _train_episode(self, target_url, episode):
        env = WebSecurityGym(target_url=target_url)
        state, _ = env.reset()
        total_reward = 0
        vulns = 0
        done = False
        steps = 0
        
        while not done and steps < 50:
            action = self.agent.act(state)
            next_state, reward, terminated, truncated, _ = env.step(action)
            done = terminated or truncated
            
            self.agent.remember(state, action, reward, next_state, done)
            self.agent.replay()
            
            total_reward += reward
            if reward > 50:
                vulns += 1
            
            state = next_state
            steps += 1
            
        return total_reward, vulns

    def _save_checkpoint(self, episode):
        os.makedirs("checkpoints", exist_ok=True)
        path = f"checkpoints/{self.checkpoint_prefix}_ep{episode}.pth"
        torch.save(self.agent.brain.state_dict(), path)
        print(f"💾 Saved checkpoint: {path}")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--episodes', type=int, default=1000)
    args = parser.parse_args()
    
    trainer = MockTargetsTrainer()
    trainer.train(total_episodes=args.episodes)

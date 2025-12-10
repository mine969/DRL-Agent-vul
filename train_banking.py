"""
Banking App Training
====================
Simplified training script for a single target.
"""

import torch
import numpy as np
from agent.dqn_agent import DQNAgent
from env.web_sec_env import WebSecurityGym
import sys
import io
import os

# Force UTF-8 encoding
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

TARGET_URL = "http://localhost:5004"
TARGET_NAME = "Banking App"

class BankingTrainer:
    """Trainer for Banking App."""
    
    def __init__(self):
        self.checkpoint_prefix = "multi_target_10k"
        
        # Initialize agent
        self.agent = DQNAgent(state_dim=11, action_dim=100)
        
        # Load existing model
        self._load_model()
        
        # Set high epsilon for exploration
        self.agent.epsilon = 1.0
        self.agent.epsilon_min = 0.1
        self.agent.epsilon_decay = 0.995

    def _load_model(self):
        try:
            device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
            from utils.model_loader import find_latest_checkpoint
            latest_ep, latest_path = find_latest_checkpoint(pattern="multi_target_10k_ep*.pth")
            
            if latest_path:
                print(f"✅ Resuming from checkpoint: {latest_path}")
                self.agent.brain.load_state_dict(torch.load(latest_path, map_location=device))
                self.agent.target_brain.load_state_dict(self.agent.brain.state_dict())
                self.start_episode = latest_ep + 1
            else:
                print(f"🆕 Starting fresh")
                self.start_episode = 1
                
        except Exception as e:
            print(f"⚠️ Error loading model: {e}")
            self.start_episode = 1

    def train(self, total_episodes=1000):
        print("=" * 70)
        print(f"🎯 TRAINING: {TARGET_NAME}")
        print("=" * 70)
        print(f"Target URL: {TARGET_URL}")
        print(f"Episodes: {self.start_episode} → {total_episodes}")
        print("=" * 70)
        
        current_episode = self.start_episode
        try:
            for episode in range(self.start_episode, total_episodes + 1):
                current_episode = episode
                
                # Train one episode
                reward, vulns = self._train_episode(episode)
                
                if episode % 10 == 0:
                    print(f"Episode {episode}/{total_episodes}: Reward={reward:.1f} | Vulns={vulns} | Epsilon={self.agent.epsilon:.3f}")
                
                # Save checkpoint
                if episode % 100 == 0:
                    self._save_checkpoint(episode)
                    
        except KeyboardInterrupt:
            print("\n\n⚠️  Training interrupted by user!")
            print(f"💾 Saving checkpoint at episode {current_episode}...")
            self._save_checkpoint(current_episode)
            print(f"✅ Checkpoint saved!")

    def _train_episode(self, episode):
        env = WebSecurityGym(target_url=TARGET_URL)
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
            
        env.close()
        return total_reward, vulns

    def _save_checkpoint(self, episode):
        os.makedirs("checkpoints", exist_ok=True)
        path = f"checkpoints/{self.checkpoint_prefix}_ep{episode}.pth"
        torch.save(self.agent.brain.state_dict(), path)
        print(f"💾 Saved: {path}")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--episodes', type=int, default=11000)
    args = parser.parse_args()
    
    print("\n⚠️  IMPORTANT: Make sure Banking App is running!")
    print("   Run in another terminal: python env/target_app_banking.py\n")
    
    trainer = BankingTrainer()
    trainer.train(total_episodes=args.episodes)

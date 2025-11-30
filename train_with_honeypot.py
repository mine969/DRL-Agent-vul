"""
Web Agent Training with HoneyPot Data
======================================
Trains the Web Security Agent using real-world attack patterns from HoneyPot logs.
Implements reward shaping to prioritize HoneyPot-derived payloads.
"""

import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from RL.agent.dqn_agent import DQNAgent
from RL.agent.payload_manager import PayloadManager
from RL.env.web_sec_env import WebSecurityEnv
import torch

def train_with_honeypot(episodes=1000, honeypot_path="training_data.json"):
    """
    Train the Web Agent with HoneyPot data integration.
    
    Args:
        episodes: Number of training episodes
        honeypot_path: Path to training_data.json
    """
    print("=" * 60)
    print("🍯 WEB AGENT TRAINING WITH HONEYPOT DATA")
    print("=" * 60)
    
    # Initialize PayloadManager with HoneyPot data
    payload_manager = PayloadManager(honeypot_data_path=honeypot_path)
    
    # Initialize environment and agent
    env = WebSecurityEnv()
    state_dim = env.observation_space.shape[0]
    action_dim = env.action_space.n
    
    agent = DQNAgent(state_dim, action_dim)
    
    # Try to load existing model
    model_path = "RL/dqn_web_sec_model.pth"
    if os.path.exists(model_path):
        agent.load(model_path)
        print(f"✅ Loaded existing model from {model_path}")
    
    # Training loop
    total_rewards = []
    honeypot_usage_count = 0
    
    for episode in range(episodes):
        state = env.reset()
        episode_reward = 0
        done = False
        steps = 0
        
        while not done and steps < 100:
            # Agent selects action
            action = agent.act(state)
            
            # Execute action
            next_state, reward, done, info = env.step(action)
            
            # REWARD SHAPING: Bonus for using HoneyPot payloads
            if info.get('used_honeypot_payload', False):
                reward += 5.0  # Bonus reward
                honeypot_usage_count += 1
            
            # Store experience and learn
            agent.remember(state, action, reward, next_state, done)
            agent.replay()
            
            state = next_state
            episode_reward += reward
            steps += 1
        
        total_rewards.append(episode_reward)
        
        # Progress logging
        if (episode + 1) % 50 == 0:
            avg_reward = sum(total_rewards[-50:]) / 50
            print(f"Episode {episode + 1}/{episodes} | "
                  f"Avg Reward: {avg_reward:.2f} | "
                  f"Epsilon: {agent.epsilon:.3f} | "
                  f"HoneyPot Usage: {honeypot_usage_count}")
        
        # Save checkpoint
        if (episode + 1) % 200 == 0:
            agent.save(model_path)
            print(f"💾 Checkpoint saved at episode {episode + 1}")
    
    # Final save
    agent.save(model_path)
    print("\n" + "=" * 60)
    print("✅ TRAINING COMPLETE")
    print(f"   Total HoneyPot Payload Uses: {honeypot_usage_count}")
    print(f"   Final Average Reward: {sum(total_rewards[-100:]) / 100:.2f}")
    print("=" * 60)

if __name__ == "__main__":
    # Check if HoneyPot data exists
    honeypot_path = "training_data.json"
    if not os.path.exists(honeypot_path):
        print(f"❌ Error: {honeypot_path} not found!")
        print("   Please run analyze_honeypot_logs.py first.")
        sys.exit(1)
    
    # Start training
    train_with_honeypot(episodes=1000, honeypot_path=honeypot_path)

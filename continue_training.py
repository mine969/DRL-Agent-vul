"""
Continue Training from Merged Model
====================================

Trains from merged_5000_614.pth with proper episode counting.
Saves as multi_target_10k_ep{X}.pth to reflect total training.
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


class ContinuedTrainer:
    """Continue training from merged model with proper episode counting."""
    
    def __init__(self, base_model="checkpoints/merged_5000_614.pth", base_episodes=5614, verbose=True):
        """
        Args:
            base_model: Path to merged model
            base_episodes: Total episodes in base model (5000 + 614 = 5614)
            verbose: Enable detailed logging
        """
        self.target_name = "OWASP Juice Shop"
        self.target_url = "http://localhost:3000"
        self.base_episodes = base_episodes
        self.verbose = verbose
        
        # Training metrics
        self.episode_rewards = []
        self.episode_vulns_found = []
        
        # Initialize agent
        self.agent = DQNAgent(state_dim=11, action_dim=100)
        
        # Load base model
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.agent.brain.load_state_dict(torch.load(base_model, map_location=device))
        self.agent.target_brain.load_state_dict(self.agent.brain.state_dict())
        
        print(f"✅ Loaded merged model: {base_model}")
        print(f"📊 Base training: {base_episodes} episodes")
        print(f"   - Multi-target: 5000 episodes (70%)")
        print(f"   - Juice Shop: 614 episodes (30%)")
    
    def train(self, additional_episodes=1000):
        """
        Train additional episodes on Juice Shop.
        
        Args:
            additional_episodes: Number of new episodes to train
        """
        start_ep = self.base_episodes + 1
        end_ep = self.base_episodes + additional_episodes
        
        print("\n" + "=" * 70)
        print("🧃 CONTINUED JUICE SHOP TRAINING")
        print("=" * 70)
        print(f"Target: {self.target_name}")
        print(f"URL: {self.target_url}")
        print(f"Starting from: Episode {start_ep}")
        print(f"Training to: Episode {end_ep}")
        print(f"New episodes: {additional_episodes}")
        print("=" * 70)
        print()
        
        current_episode = start_ep
        try:
            for episode in range(start_ep, end_ep + 1):
                current_episode = episode
                
                # Print progress
                if episode % 10 == 0:
                    progress = ((episode - start_ep) / additional_episodes) * 100
                    print(f"\n{'='*70}", flush=True)
                    print(f"🎯 Episode {episode} (Total: {episode}, Progress: {progress:.1f}%)", flush=True)
                    print(f"{'='*70}", flush=True)
                
                # Train one episode
                reward, vulns_found = self._train_episode(episode)
                
                # Track metrics
                self.episode_rewards.append(reward)
                self.episode_vulns_found.append(vulns_found)
                
                # Print stats every 10 episodes
                if episode % 10 == 0:
                    avg_reward = np.mean(self.episode_rewards[-100:]) if len(self.episode_rewards) >= 100 else np.mean(self.episode_rewards)
                    avg_vulns = np.mean(self.episode_vulns_found[-100:]) if len(self.episode_vulns_found) >= 100 else np.mean(self.episode_vulns_found)
                    print(f"\n📊 Statistics:")
                    print(f"  Avg Reward (last 100): {avg_reward:.2f}")
                    print(f"  Avg Vulns (last 100): {avg_vulns:.2f}")
                    print(f"  Epsilon: {self.agent.epsilon:.3f}")
                
                # Save checkpoint every 100 episodes
                if (episode - self.base_episodes) % 100 == 0:
                    self._save_checkpoint(episode)
        
        except KeyboardInterrupt:
            print("\n\n⚠️  Training interrupted by user!")
            print(f"💾 Saving checkpoint at episode {current_episode}...")
            self._save_checkpoint(current_episode)
            print(f"\n💡 To resume, run:")
            print(f"   python continue_training.py --base-episodes {current_episode} --episodes {end_ep - current_episode}")
            return
        
        # Final save
        self._save_checkpoint(end_ep)
        torch.save(self.agent.brain.state_dict(), "dqn_juiceshop_10k_model.pth")
        
        print(f"\n✅ Training complete!")
        print(f"📁 Final model: multi_target_10k_ep{end_ep}.pth")
        print(f"📁 Production model: dqn_juiceshop_10k_model.pth")
        
        self._print_final_stats()
    
    def _train_episode(self, episode):
        """Train one episode on Juice Shop."""
        env = WebSecurityGym(target_url=self.target_url)
        state, _ = env.reset()
        
        total_reward = 0
        vulns_found = 0
        done = False
        steps = 0
        max_steps = 100
        
        while not done and steps < max_steps:
            action = self.agent.act(state)
            next_state, reward, terminated, truncated, info = env.step(action)
            done = terminated or truncated
            
            self.agent.remember(state, action, reward, next_state, done)
            self.agent.replay()
            
            total_reward += reward
            if reward > 50:
                vulns_found += 1
            
            state = next_state
            steps += 1
            
            if self.verbose and steps % 20 == 0:
                try:
                    action_name = env.action_book.get(action).__name__
                except:
                    action_name = f"INVALID_ACTION_{action}"
                print(f"    Step {steps}: {action_name} | Reward={reward:.1f}", flush=True)
        
        env.close()
        return total_reward, vulns_found
    
    def _save_checkpoint(self, episode):
        """Save checkpoint with proper episode numbering."""
        os.makedirs("checkpoints", exist_ok=True)
        
        # Determine naming based on total episodes
        if episode < 10000:
            checkpoint_path = f"checkpoints/multi_target_10k_ep{episode}.pth"
        else:
            checkpoint_path = f"checkpoints/multi_target_ep{episode}.pth"
        
        torch.save(self.agent.brain.state_dict(), checkpoint_path)
        print(f"💾 Checkpoint saved: {checkpoint_path}")
    
    def _print_final_stats(self):
        """Print final statistics."""
        print("\n" + "=" * 70)
        print("📈 FINAL TRAINING STATISTICS")
        print("=" * 70)
        
        if self.episode_rewards:
            print(f"Target: {self.target_name}")
            print(f"New Episodes Trained: {len(self.episode_rewards)}")
            print(f"Total Episodes: {self.base_episodes + len(self.episode_rewards)}")
            print(f"Average Reward: {np.mean(self.episode_rewards):.2f}")
            print(f"Average Vulnerabilities: {np.mean(self.episode_vulns_found):.2f}")
            print(f"Best Episode Reward: {np.max(self.episode_rewards):.2f}")
            print(f"Total Vulnerabilities Found: {np.sum(self.episode_vulns_found)}")
        
        print("=" * 70)


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Continue training from merged model')
    parser.add_argument('--episodes', type=int, default=1000, help='Additional episodes to train')
    parser.add_argument('--base-model', default='checkpoints/merged_5000_614.pth', help='Base model')
    parser.add_argument('--base-episodes', type=int, default=5614, help='Episodes in base model')
    parser.add_argument('--verbose', action='store_true', help='Verbose output')
    
    args = parser.parse_args()
    
    # Verify Juice Shop is running
    import requests
    try:
        response = requests.get('http://localhost:3000', timeout=5)
        print("✅ OWASP Juice Shop is accessible\n")
    except:
        print("❌ ERROR: OWASP Juice Shop is not running on http://localhost:3000")
        print("   Please start Juice Shop with: docker run -d -p 3000:3000 bkimminich/juice-shop")
        exit(1)
    
    # Start training
    trainer = ContinuedTrainer(
        base_model=args.base_model,
        base_episodes=args.base_episodes,
        verbose=args.verbose
    )
    trainer.train(additional_episodes=args.episodes)

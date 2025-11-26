"""
Multi-Target Training Script
=============================

Trains the DRL agent on multiple vulnerable web applications simultaneously
using curriculum learning for better generalization.

This creates a "generalist" security scanner that can work across different
architectures rather than being overfitted to a single target.

Usage:
    python train_multi_target.py --episodes 1000
"""

import torch
import numpy as np
from agent.dqn_agent import DQNAgent
from env.web_sec_env import WebSecurityGym
import datetime
import random

class MultiTargetTrainer:
    """Trains the agent across multiple target applications."""
    
    def __init__(self, targets, model_path="dqn_web_sec_model.pth"):
        """
        Args:
            targets: List of (name, url) tuples for each target
            model_path: Path to save/load the model
        """
        self.targets = targets
        self.model_path = model_path
        
        # Initialize agent (state_dim=11, action_dim=52)
        self.agent = DQNAgent(state_dim=11, action_dim=52)
        
        # Try to load existing model
        try:
            device = torch.device("cuda" if torch.cuda.is_available() else "mps" if torch.backends.mps.is_available() else "cpu")
            self.agent.brain.load_state_dict(torch.load(model_path, map_location=device))
            print(f"✅ Loaded existing model from {model_path}")
        except:
            print(f"🆕 Starting fresh training (no existing model)")
        
        # Training metrics
        self.episode_rewards = {name: [] for name, _ in targets}
        self.episode_vulns_found = {name: [] for name, _ in targets}
        
    def train_curriculum(self, total_episodes=1000, start_episode=1):
        """
        Curriculum Learning Strategy (6 Targets):
        
        Phase 1 (0-200): Local targets only (Original, E-Commerce, Social)
        Phase 2 (201-400): Add LMS (real-world but controlled)
        Phase 3 (401-700): Add RSU Portal and DIT RSU
        Phase 4 (701-1000): All 6 targets + focus on weakest
        """
        print("=" * 70)
        print("🎓 MULTI-TARGET CURRICULUM TRAINING (6 TARGETS)")
        print("=" * 70)
        print(f"Total Episodes: {total_episodes}")
        if start_episode > 1:
            print(f"Resuming from Episode: {start_episode}")
        print(f"Targets: {len(self.targets)}")
        for name, url in self.targets:
            print(f"  - {name}: {url}")
        print("=" * 70)
        print()
        
        current_episode = start_episode
        try:
            for episode in range(start_episode, total_episodes + 1):
                current_episode = episode
                # Determine which target to use based on curriculum phase
                target_name, target_url = self._select_target(episode, total_episodes)
                
                # Train one episode on selected target
                reward, vulns_found = self._train_episode(target_name, target_url, episode)
                
                # Track metrics
                self.episode_rewards[target_name].append(reward)
                self.episode_vulns_found[target_name].append(vulns_found)
                
                # Print progress
                if episode % 10 == 0:
                    self._print_progress(episode, total_episodes)
                
                # Save checkpoint every 100 episodes
                if episode % 100 == 0:
                    self._save_checkpoint(episode)
        
        except KeyboardInterrupt:
            print("\n\n⚠️  Training interrupted by user!")
            print(f"💾 Saving checkpoint at episode {current_episode}...")
            self._save_checkpoint(current_episode)
            print(f"✅ Checkpoint saved: checkpoints/multi_target_ep{current_episode}.pth")
            print(f"\n💡 To resume training, run:")
            print(f"   python train_multi_target.py --episodes {total_episodes} --resume {current_episode}")
            return
        
        # Final save
        torch.save(self.agent.brain.state_dict(), self.model_path)
        print(f"\n✅ Training complete! Model saved to {self.model_path}")
        self._print_final_stats()
    
    def _select_target(self, episode, total_episodes):
        """Curriculum learning: gradually introduce more targets (6 total)."""
        phase_1_end = int(total_episodes * 0.2)  # 20% - Local only
        phase_2_end = int(total_episodes * 0.4)  # 40% - Add LMS
        phase_3_end = int(total_episodes * 0.7)  # 70% - Add RSU sites
        
        if episode <= phase_1_end:
            # Phase 1: Local targets only (0-2)
            return random.choice(self.targets[:3])
        
        elif episode <= phase_2_end:
            # Phase 2: Local + LMS (0-3)
            return random.choice(self.targets[:4])
        
        elif episode <= phase_3_end:
            # Phase 3: All 6 targets
            return random.choice(self.targets)
        
        else:
            # Phase 4: Focus on weakest target
            weakest = min(self.targets, 
                         key=lambda t: np.mean(self.episode_rewards[t[0]][-50:]) if self.episode_rewards[t[0]] else 0)
            return weakest
    
    def _train_episode(self, target_name, target_url, episode_num):
        """Train one episode on a specific target."""
        env = WebSecurityGym(target_url=target_url)
        state, _ = env.reset()
        
        total_reward = 0
        vulns_found = 0
        done = False
        steps = 0
        max_steps = 100
        
        while not done and steps < max_steps:
            # Agent selects action
            action = self.agent.act(state)
            
            # Execute action
            next_state, reward, terminated, truncated, info = env.step(action)
            done = terminated or truncated
            
            # Store experience and learn
            self.agent.remember(state, action, reward, next_state, done)
            self.agent.replay()
            
            # Track metrics
            total_reward += reward
            if reward > 50:  # Found a vulnerability
                vulns_found += 1
            
            state = next_state
            steps += 1
        
        env.close()
        return total_reward, vulns_found
    
    def _print_progress(self, episode, total_episodes):
        """Print training progress."""
        progress = (episode / total_episodes) * 100
        
        print(f"\n📊 Episode {episode}/{total_episodes} ({progress:.1f}%)")
        print("-" * 70)
        
        for name, _ in self.targets:
            if self.episode_rewards[name]:
                recent_rewards = self.episode_rewards[name][-10:]
                recent_vulns = self.episode_vulns_found[name][-10:]
                
                avg_reward = np.mean(recent_rewards)
                avg_vulns = np.mean(recent_vulns)
                
                print(f"  {name:20} | Avg Reward: {avg_reward:6.1f} | Avg Vulns: {avg_vulns:.1f}")
        
        print(f"  Epsilon: {self.agent.epsilon:.3f}")
    
    def _save_checkpoint(self, episode):
        """Save training checkpoint."""
        checkpoint_path = f"checkpoints/multi_target_ep{episode}.pth"
        torch.save(self.agent.brain.state_dict(), checkpoint_path)
        print(f"💾 Checkpoint saved: {checkpoint_path}")
    
    def _print_final_stats(self):
        """Print final training statistics."""
        print("\n" + "=" * 70)
        print("📈 FINAL TRAINING STATISTICS")
        print("=" * 70)
        
        for name, _ in self.targets:
            if self.episode_rewards[name]:
                total_episodes = len(self.episode_rewards[name])
                avg_reward = np.mean(self.episode_rewards[name])
                avg_vulns = np.mean(self.episode_vulns_found[name])
                
                print(f"\n{name}:")
                print(f"  Episodes Trained: {total_episodes}")
                print(f"  Avg Reward: {avg_reward:.1f}")
                print(f"  Avg Vulnerabilities Found: {avg_vulns:.1f}")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Multi-Target DRL Security Scanner Training')
    parser.add_argument('--episodes', type=int, default=1000, help='Total training episodes')
    parser.add_argument('--model', default='dqn_web_sec_model.pth', help='Model save path')
    parser.add_argument('--resume', type=int, default=0, help='Resume from episode number (loads checkpoint)')
    
    args = parser.parse_args()
    
    # Define training targets (3 local + 3 real-world)
    targets = [
        # Local test targets
        ("Original", "http://localhost:5001"),
        ("E-Commerce", "http://localhost:5002"),
        ("Social Media", "http://localhost:5003"),
        
        # Real-world targets
        ("LMS", "https://levelup.melivecode.com"),
        ("RSU Portal", "https://rsuip.org"),
        ("DIT RSU", "https://dit.rsu.ac.th"),
    ]
    
    print("=" * 70)
    print("🎯 MULTI-TARGET TRAINING CONFIGURATION")
    print("=" * 70)
    print(f"Total Targets: {len(targets)}")
    print("\nLocal Test Targets:")
    for name, url in targets[:3]:
        print(f"  ✓ {name}: {url}")
    print("\nReal-World Targets:")
    for name, url in targets[3:]:
        print(f"  🌐 {name}: {url}")
    print("=" * 70)
    print()
    
    # Create trainer and start
    trainer = MultiTargetTrainer(targets, model_path=args.model)
    
    # Load checkpoint if resuming
    if args.resume > 0:
        checkpoint_path = f"checkpoints/multi_target_ep{args.resume}.pth"
        try:
            device = torch.device("cuda" if torch.cuda.is_available() else "mps" if torch.backends.mps.is_available() else "cpu")
            trainer.agent.brain.load_state_dict(torch.load(checkpoint_path, map_location=device))
            trainer.agent.target_brain.load_state_dict(trainer.agent.brain.state_dict())
            print(f"✅ Loaded checkpoint from episode {args.resume}")
        except Exception as e:
            print(f"❌ Failed to load checkpoint: {e}")
            print(f"   Starting from scratch instead")
            args.resume = 0
    
    trainer.train_curriculum(total_episodes=args.episodes, start_episode=args.resume + 1 if args.resume > 0 else 1)


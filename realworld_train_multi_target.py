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
import sys
import io

# Force UTF-8 encoding for Windows consoles
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')


import os
import re
import glob

class MultiTargetTrainer:
    """Trains the agent across multiple target applications."""
    
    def __init__(self, targets, model_path="dqn_web_sec_model.pth", verbose=False):
        """
        Args:
            targets: List of (name, url) tuples for each target
            model_path: Path to save/load the model
            verbose: Enable detailed logging
        """
        self.targets = targets
        self.model_path = model_path
        self.verbose = verbose
        
        # Initialize agent (state_dim=11, action_dim=100)
        self.agent = DQNAgent(state_dim=11, action_dim=100)
        
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
                
                # Verbose: Print episode header
                if self.verbose:
                    print(f"\n{'='*70}", flush=True)
                    print(f"🎯 Episode {episode}/{total_episodes} | Target: {target_name}", flush=True)
                    print(f"🌐 URL: {target_url}", flush=True)
                    print(f"{'='*70}", flush=True)
                
                # Train one episode on selected target
                reward, vulns_found = self._train_episode(target_name, target_url, episode)
                
                # Track metrics
                self.episode_rewards[target_name].append(reward)
                self.episode_vulns_found[target_name].append(vulns_found)
                
                # Print progress
                if self.verbose:
                    print(f"    Episode {episode} Complete | Reward: {reward:.1f} | Vulns: {vulns_found}")
                
                if episode % 1 == 0:  # Log every episode for better visibility
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
            print(f"   (Checkpoint: multi_target_8k_ep{current_episode}.pth)")
            return
        
        # Final save
        torch.save(self.agent.brain.state_dict(), self.model_path)
        print(f"\n✅ Training complete! Model saved to {self.model_path}")
        self._print_final_stats()
    
    def _select_target(self, episode, total_episodes):
        """Curriculum learning: gradually introduce more targets (6 total)."""
        # ACCELERATED CURRICULUM: Introduce real targets much sooner
        phase_1_end = 50   # Ep 1-50: Local only (Warmup)
        phase_2_end = 100  # Ep 51-100: Add LMS
        # Ep 101+: All targets (Real-World)
        
        if episode <= phase_1_end:
            # Phase 1: Local targets only (0-2)
            return random.choice(self.targets[:3])
        
        elif episode <= phase_2_end:
            # Phase 2: Local + LMS (0-3)
            return random.choice(self.targets[:4])
        
        else:
            # Phase 3: All 6 targets (Local + Real World)
            # 70% chance to pick a Real-World target to prioritize them
            if random.random() < 0.7:
                return random.choice(self.targets[3:]) # Real-world only
            else:
                return random.choice(self.targets[:3]) # Local fallback
    
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
            
            # Environment step
            next_state, reward, done, truncated, info = env.step(action)
            
            # Store experience
            self.agent.remember(state, action, reward, next_state, done)
            
            # Train agent
            self.agent.replay()  # MAX GPU batch size configured in agent init
            
            state = next_state
            total_reward += reward
            steps += 1
            
            if reward > 50:  # Vulnerability found threshold
                vulns_found += 1
            
            # Verbose logging
            if self.verbose:
                try:
                    action_name = env.action_book.get(action).__name__
                except:
                    action_name = f"Action_{action}"
                print(f"    Step {steps}: Action={action_name} | Reward={reward:.1f} | Vuln={reward>50}", flush=True)
        
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
        # Add architecture identifier to filename
        arch_size = "8k"  # 8192 neurons = MAX mode
        checkpoint_path = f"checkpoints/multi_target_8k_ep{episode}.pth"
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



def find_latest_checkpoint():
    """Find the checkpoint with the highest episode number."""
    checkpoints = glob.glob("checkpoints/multi_target_8k_ep*.pth")
    if not checkpoints:
        return 0
    
    latest_ep = 0
    for cp in checkpoints:
        try:
            # Extract number from filename like 'multi_target_8k_ep700.pth'
            match = re.search(r'ep(\d+)\.pth', cp)
            if match:
                ep = int(match.group(1))
                if ep > latest_ep:
                    latest_ep = ep
        except:
            continue
            
    return latest_ep


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Multi-Target DRL Security Scanner Training')
    parser.add_argument('--episodes', type=int, default=1000, help='Total training episodes')
    parser.add_argument('--model', default='dqn_web_sec_model.pth', help='Model save path')
    parser.add_argument('--resume', type=int, default=0, help='Resume from episode number')
    parser.add_argument('--latest', action='store_true', help='Automatically resume from latest checkpoint')
    parser.add_argument('--no-verbose', dest='verbose', action='store_false', help='Disable detailed step-by-step logging')
    parser.set_defaults(verbose=True)
    
    args = parser.parse_args()
    
    # Define real-world training targets
    # ⚠️ IMPORTANT: Only scan websites you own or have explicit permission to test!
    targets = [
        # Example real-world targets (replace with your authorized targets)
        ("LMS Platform", "https://levelup.melivecode.com"),
        ("RSU Portal", "https://rsuip.org"),
        ("DIT RSU", "https://dit.rsu.ac.th"),
        
        # Add more targets here as needed:
        # ("Target Name", "https://example.com"),
        # ("Another Target", "https://another-example.com"),
    ]
    
    print("=" * 70)
    print("� REAL-WORLD MULTI-TARGET TRAINING")
    print("=" * 70)
    print("⚠️  WARNING: Only scan authorized targets!")
    print(f"\nTotal Real-World Targets: {len(targets)}")
    print("\nTraining Targets:")
    for name, url in targets:
        print(f"  🌐 {name}: {url}")
    print("=" * 70)
    print()
    
    # Create trainer and start
    trainer = MultiTargetTrainer(targets, model_path=args.model, verbose=args.verbose)
    
    # Handle auto-resume
    if args.latest:
        latest_ep = find_latest_checkpoint()
        if latest_ep > 0:
            print(f"🔎 Found latest checkpoint: Episode {latest_ep}")
            args.resume = latest_ep
        else:
            print("⚠️ No checkpoints found to resume from. Starting fresh.")

    # Load checkpoint if resuming
    if args.resume > 0:
        checkpoint_path = f"checkpoints/multi_target_8k_ep{args.resume}.pth"
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


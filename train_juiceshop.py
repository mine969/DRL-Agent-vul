"""
OWASP Juice Shop Specialized Training
======================================

This script trains the DRL agent exclusively on OWASP Juice Shop
to improve accuracy and reduce false positives.

Usage:
    python train_juiceshop.py --episodes 2000 --latest
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


class JuiceShopTrainer:
    """Specialized trainer for OWASP Juice Shop only."""
    
    def __init__(self, model_path="dqn_web_sec_model.pth", verbose=True, auto_resume=True, resume_path=None):
        """
        Args:
            model_path: Path to save/load the model
            verbose: Enable detailed logging
            auto_resume: Automatically load latest checkpoint if available
            resume_path: Explicit path to resume from (overrides auto_resume)
        """
        self.target_name = "OWASP Juice Shop"
        self.target_url = "http://localhost:3000"
        self.model_path = model_path
        self.verbose = verbose
        
        # Default checkpoint prefix
        self.checkpoint_prefix = "juiceshop_10k"
        
        # Training metrics
        self.episode_rewards = []
        self.episode_vulns_found = []
        
        # Initialize agent (state_dim=11, action_dim=100)
        self.agent = DQNAgent(state_dim=11, action_dim=100)
        
        # Explicit resume path
        if resume_path:
            try:
                device = torch.device("cuda" if torch.cuda.is_available() else "mps" if torch.backends.mps.is_available() else "cpu")
                self.agent.brain.load_state_dict(torch.load(resume_path, map_location=device))
                self.agent.target_brain.load_state_dict(self.agent.brain.state_dict())
                print(f"✅ Resumed from explicit checkpoint: {resume_path}")
                
                # Infer prefix and episode
                import re
                basename = os.path.basename(resume_path)
                # Match prefix before _ep
                prefix_match = re.search(r'^(.*)_ep\d+\.pth$', basename)
                if prefix_match:
                    self.checkpoint_prefix = prefix_match.group(1)
                    print(f"   Inferred checkpoint prefix: {self.checkpoint_prefix}")
                
                match = re.search(r'ep(\d+)\.pth', basename)
                if match:
                    self.start_episode = int(match.group(1)) + 1
                    print(f"   Inferred start episode: {self.start_episode}")
                else:
                    self.start_episode = 1
                    print(f"   Could not infer episode number, starting from 1")
                return
            except Exception as e:
                print(f"❌ Failed to load checkpoint {resume_path}: {e}")
                exit(1)

        # Auto-resume from latest checkpoint if enabled
        if auto_resume:
            latest_ep, checkpoint_path = self._find_latest_checkpoint()
            if latest_ep > 0:
                try:
                    device = torch.device("cuda" if torch.cuda.is_available() else "mps" if torch.backends.mps.is_available() else "cpu")
                    self.agent.brain.load_state_dict(torch.load(checkpoint_path, map_location=device))
                    self.agent.target_brain.load_state_dict(self.agent.brain.state_dict())
                    print(f"✅ Auto-resumed from checkpoint: Episode {latest_ep}")
                    print(f"📁 Loaded: {checkpoint_path}")
                    
                    # Infer prefix
                    import re
                    basename = os.path.basename(checkpoint_path)
                    prefix_match = re.search(r'^(.*)_ep\d+\.pth$', basename)
                    if prefix_match:
                        self.checkpoint_prefix = prefix_match.group(1)
                        print(f"   Inferred checkpoint prefix: {self.checkpoint_prefix}")
                        
                    self.start_episode = latest_ep + 1
                    return
                except Exception as e:
                    print(f"⚠️  Failed to load checkpoint {checkpoint_path}: {e}")
                    print(f"   Falling back to base model...")
        
        # Fallback: Try to load base model
        try:
            device = torch.device("cuda" if torch.cuda.is_available() else "mps" if torch.backends.mps.is_available() else "cpu")
            self.agent.brain.load_state_dict(torch.load(model_path, map_location=device))
            print(f"✅ Loaded existing model from {model_path}")
            self.start_episode = 1
        except:
            print(f"🆕 Starting fresh training (no existing model)")
            self.start_episode = 1
    
    def _find_latest_checkpoint(self):
        """Find the checkpoint with the highest episode number."""
        import glob
        import re
        
        # Patterns to look for
        patterns = [
            "checkpoints/juiceshop_8k_ep*.pth",
            "checkpoints/juiceshop_10k_ep*.pth",
            "checkpoints/multi_target_10k_ep*.pth"
        ]
        
        latest_ep = 0
        latest_path = None
        
        for pattern in patterns:
            checkpoints = glob.glob(pattern)
            for cp in checkpoints:
                try:
                    match = re.search(r'ep(\d+)\.pth', cp)
                    if match:
                        ep = int(match.group(1))
                        if ep > latest_ep:
                            latest_ep = ep
                            latest_path = cp
                except:
                    continue
                    
        return latest_ep, latest_path
    
    def train(self, total_episodes=2000, start_episode=None):
        """
        Train exclusively on OWASP Juice Shop.
        
        Args:
            total_episodes: Total number of episodes to train
            start_episode: Episode to start from (auto-detected if None)
        """
        # Use auto-detected start episode if not specified
        if start_episode is None:
            start_episode = self.start_episode
        
        print("=" * 70)
        print("🧃 OWASP JUICE SHOP SPECIALIZED TRAINING")
        print("=" * 70)
        print(f"Target: {self.target_name}")
        print(f"URL: {self.target_url}")
        print(f"Total Episodes: {total_episodes}")
        print(f"Checkpoint Prefix: {self.checkpoint_prefix}")
        if start_episode > 1:
            print(f"Resuming from Episode: {start_episode}")
        print("=" * 70)
        print()
        
        current_episode = start_episode
        try:
            for episode in range(start_episode, total_episodes + 1):
                current_episode = episode
                
                # Verbose: Print episode header
                if self.verbose or episode % 10 == 0:
                    print(f"\n{'='*70}", flush=True)
                    print(f"🎯 Episode {episode}/{total_episodes} ({episode/total_episodes*100:.1f}%)", flush=True)
                    print(f"{'='*70}", flush=True)
                
                # Train one episode
                reward, vulns_found = self._train_episode(episode)
                
                # Track metrics
                self.episode_rewards.append(reward)
                self.episode_vulns_found.append(vulns_found)
                
                # Print progress every 10 episodes
                if episode % 10 == 0:
                    avg_reward = np.mean(self.episode_rewards[-100:]) if len(self.episode_rewards) >= 100 else np.mean(self.episode_rewards)
                    avg_vulns = np.mean(self.episode_vulns_found[-100:]) if len(self.episode_vulns_found) >= 100 else np.mean(self.episode_vulns_found)
                    print(f"\n📊 Episode {episode}/{total_episodes}")
                    print(f"  Avg Reward (last 100): {avg_reward:.2f}")
                    print(f"  Avg Vulns (last 100): {avg_vulns:.2f}")
                    print(f"  Epsilon: {self.agent.epsilon:.3f}")
                
                # Save checkpoint every 100 episodes
                if episode % 100 == 0:
                    self._save_checkpoint(episode)
        
        except KeyboardInterrupt:
            print("\n\n⚠️  Training interrupted by user!")
            print(f"💾 Saving checkpoint at episode {current_episode}...")
            self._save_checkpoint(current_episode)
            print(f"✅ Checkpoint saved: checkpoints/{self.checkpoint_prefix}_ep{current_episode}.pth")
            print(f"\n💡 To resume training, run:")
            print(f"   python train_juiceshop.py --episodes {total_episodes}")
            return
        
        # Final save
        final_checkpoint = f"checkpoints/{self.checkpoint_prefix}_ep{total_episodes}.pth"
        torch.save(self.agent.brain.state_dict(), final_checkpoint)
        torch.save(self.agent.brain.state_dict(), "dqn_juiceshop_model.pth")
        
        print(f"\n✅ Training complete!")
        print(f"📁 Final checkpoint: {final_checkpoint}")
        print(f"📁 Production model: dqn_juiceshop_model.pth")
        
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
            # Agent selects action
            action = self.agent.act(state)
            next_state, reward, terminated, truncated, info = env.step(action)
            done = terminated or truncated
            
            # Learn from this experience
            self.agent.remember(state, action, reward, next_state, done)
            self.agent.replay()
            
            total_reward += reward
            if reward > 50:  # Vulnerability found
                vulns_found += 1
            
            state = next_state
            steps += 1
            
            # Verbose logging
            if self.verbose:
                try:
                    action_name = env.action_book.get(action).__name__
                except:
                    action_name = f"INVALID_ACTION_{action}"
                print(f"    Step {steps}: Action={action_name} | Reward={reward:.1f} | Vuln={reward>50}", flush=True)
        
        env.close()
        return total_reward, vulns_found
    
    def _save_checkpoint(self, episode):
        """Save training checkpoint."""
        os.makedirs("checkpoints", exist_ok=True)
        checkpoint_path = f"checkpoints/{self.checkpoint_prefix}_ep{episode}.pth"
        torch.save(self.agent.brain.state_dict(), checkpoint_path)
        print(f"💾 Checkpoint saved: {checkpoint_path}")
    
    def _print_final_stats(self):
        """Print final training statistics."""
        print("\n" + "=" * 70)
        print("📈 FINAL TRAINING STATISTICS")
        print("=" * 70)
        
        if self.episode_rewards:
            print(f"Target: {self.target_name}")
            print(f"Total Episodes: {len(self.episode_rewards)}")
            print(f"Average Reward: {np.mean(self.episode_rewards):.2f}")
            print(f"Average Vulnerabilities: {np.mean(self.episode_vulns_found):.2f}")
            print(f"Best Episode Reward: {np.max(self.episode_rewards):.2f}")
            print(f"Total Vulnerabilities Found: {np.sum(self.episode_vulns_found)}")
        
        print("=" * 70)


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Train DRL Agent on OWASP Juice Shop')
    parser.add_argument('--episodes', type=int, default=2000, help='Total episodes to train')
    parser.add_argument('--model', default='dqn_web_sec_model.pth', help='Base model to load')
    parser.add_argument('--verbose', action='store_true', help='Verbose output')
    parser.add_argument('--resume', help='Specific checkpoint to resume from (overrides auto-detection)')
    parser.add_argument('--prefix', help='Explicit checkpoint prefix (e.g., multi_target_10k)')
    
    args = parser.parse_args()
    
    # Verify Juice Shop is running
    import requests
    try:
        response = requests.get('http://localhost:3000', timeout=5)
        print("✅ OWASP Juice Shop is accessible")
    except:
        print("❌ ERROR: OWASP Juice Shop is not running on http://localhost:3000")
        print("   Please start Juice Shop with: docker run -d -p 3000:3000 bkimminich/juice-shop")
        exit(1)
    
    # Start training
    trainer = JuiceShopTrainer(model_path=args.model, verbose=args.verbose, resume_path=args.resume)
    
    # Override prefix if specified
    if args.prefix:
        trainer.checkpoint_prefix = args.prefix
        print(f"🔧 Checkpoint prefix set to: {trainer.checkpoint_prefix}")
        
    trainer.train(total_episodes=args.episodes)

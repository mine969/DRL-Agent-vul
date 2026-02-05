"""
Multi-Target Evaluation Script
===============================

Evaluates the trained DRL agent on all 6 targets and generates
a comprehensive performance report for research documentation.

Usage:
    python evaluate_multi_target.py --model dqn_web_sec_model.pth --episodes 10
"""

import torch
import numpy as np
from agent.dqn_agent import DQNAgent
from env.web_sec_env import WebSecurityGym
import json
import datetime
from typing import Dict, List, Tuple
import sys
import io

# Force UTF-8 encoding
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')


class MultiTargetEvaluator:
    """Evaluates trained agent across multiple targets."""
    
    def __init__(self, model_path: str = "dqn_web_sec_model.pth"):
        from utils.model_loader import load_model_smart
        
        self.model_path = model_path
        self.agent = DQNAgent(state_dim=11, action_dim=100)
        
        # Load trained model (auto-loads latest checkpoint)
        episode = load_model_smart(self.agent, model_path=model_path, auto_checkpoint=True, verbose=True)
        self.agent.brain.eval()  # Set to evaluation mode
        self.agent.epsilon = 0.0  # No exploration during evaluation
        
        if episode > 0:
            print(f"📍 Evaluating model from Episode: {episode}")
        print(f"🧠 Evaluation mode: epsilon = {self.agent.epsilon}")
    
    def evaluate_target(self, target_name: str, target_url: str, num_episodes: int = 10) -> Dict:
        """Evaluate agent on a single target."""
        print(f"\n{'='*70}")
        print(f"🎯 Evaluating: {target_name}")
        print(f"🌐 URL: {target_url}")
        print(f"{'='*70}")
        
        episode_rewards = []
        episode_vulns = []
        episode_steps = []
        successful_attacks = []
        
        for episode in range(1, num_episodes + 1):
            env = WebSecurityGym(target_url=target_url)
            state, _ = env.reset()
            
            total_reward = 0
            vulns_found = 0
            steps = 0
            max_steps = 100
            done = False
            
            attacks_this_episode = []
            
            while not done and steps < max_steps:
                # Agent selects best action (no exploration)
                action = self.agent.act(state)
                next_state, reward, done, truncated, info = env.step(action)
                
                state = next_state
                total_reward += reward
                steps += 1
                
                # Track successful attacks (reward > 50 = vulnerability found)
                if reward > 50:
                    vulns_found += 1
                    action_name = env.action_book.get(action).__name__ if action in env.action_book else f"Action_{action}"
                    attacks_this_episode.append({
                        'action': action_name,
                        'reward': reward,
                        'url': info.get('url', 'N/A')
                    })
            
            env.close()
            
            episode_rewards.append(total_reward)
            episode_vulns.append(vulns_found)
            episode_steps.append(steps)
            if attacks_this_episode:
                successful_attacks.extend(attacks_this_episode)
            
            print(f"  Episode {episode}/{num_episodes}: Reward={total_reward:.1f}, Vulns={vulns_found}, Steps={steps}")
        
        # Calculate statistics
        results = {
            'target_name': target_name,
            'target_url': target_url,
            'num_episodes': num_episodes,
            'avg_reward': float(np.mean(episode_rewards)),
            'std_reward': float(np.std(episode_rewards)),
            'avg_vulns': float(np.mean(episode_vulns)),
            'total_vulns': int(np.sum(episode_vulns)),
            'avg_steps': float(np.mean(episode_steps)),
            'successful_attacks': successful_attacks,
            'episode_rewards': episode_rewards
        }
        
        print(f"\n📊 Results for {target_name}:")
        print(f"  Avg Reward: {results['avg_reward']:.2f} ± {results['std_reward']:.2f}")
        print(f"  Avg Vulnerabilities: {results['avg_vulns']:.2f}")
        print(f"  Total Vulnerabilities: {results['total_vulns']}")
        print(f"  Avg Steps: {results['avg_steps']:.1f}")
        
        return results
    
    def evaluate_all_targets(self, targets: List[Tuple[str, str]], num_episodes: int = 10) -> Dict:
        """Evaluate agent on all targets."""
        print("\n" + "="*70)
        print("🔬 MULTI-TARGET EVALUATION")
        print("="*70)
        print(f"Model: {self.model_path}")
        print(f"Episodes per target: {num_episodes}")
        print(f"Total targets: {len(targets)}")
        print("="*70)
        
        all_results = {}
        
        for target_name, target_url in targets:
            try:
                results = self.evaluate_target(target_name, target_url, num_episodes)
                all_results[target_name] = results
            except Exception as e:
                print(f"❌ Error evaluating {target_name}: {e}")
                all_results[target_name] = {'error': str(e)}
        
        return all_results
    
    def generate_report(self, results: Dict, output_file: str = "evaluation_report.json"):
        """Generate evaluation report."""
        report = {
            'timestamp': datetime.datetime.now().isoformat(),
            'model_path': self.model_path,
            'results': results,
            'summary': self._generate_summary(results)
        }
        
        # Save JSON report
        with open(output_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"\n💾 Report saved to: {output_file}")
        
        # Print summary
        self._print_summary(report['summary'])
        
        return report
    
    def _generate_summary(self, results: Dict) -> Dict:
        """Generate summary statistics."""
        valid_results = {k: v for k, v in results.items() if 'error' not in v}
        
        if not valid_results:
            return {'error': 'No valid results'}
        
        avg_rewards = [r['avg_reward'] for r in valid_results.values()]
        total_vulns = sum(r['total_vulns'] for r in valid_results.values())
        
        # Find best and worst performing targets
        best_target = max(valid_results.items(), key=lambda x: x[1]['avg_reward'])
        worst_target = min(valid_results.items(), key=lambda x: x[1]['avg_reward'])
        
        return {
            'overall_avg_reward': float(np.mean(avg_rewards)),
            'overall_std_reward': float(np.std(avg_rewards)),
            'total_vulnerabilities_found': total_vulns,
            'best_performing_target': {
                'name': best_target[0],
                'avg_reward': best_target[1]['avg_reward']
            },
            'worst_performing_target': {
                'name': worst_target[0],
                'avg_reward': worst_target[1]['avg_reward']
            },
            'targets_evaluated': len(valid_results)
        }
    
    def _print_summary(self, summary: Dict):
        """Print summary statistics."""
        print("\n" + "="*70)
        print("📈 EVALUATION SUMMARY")
        print("="*70)
        
        if 'error' in summary:
            print(f"❌ {summary['error']}")
            return
        
        print(f"Targets Evaluated: {summary['targets_evaluated']}")
        print(f"Overall Avg Reward: {summary['overall_avg_reward']:.2f} ± {summary['overall_std_reward']:.2f}")
        print(f"Total Vulnerabilities Found: {summary['total_vulnerabilities_found']}")
        print(f"\nBest Performing: {summary['best_performing_target']['name']} ({summary['best_performing_target']['avg_reward']:.2f})")
        print(f"Worst Performing: {summary['worst_performing_target']['name']} ({summary['worst_performing_target']['avg_reward']:.2f})")
        print("="*70)


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Evaluate Multi-Target DRL Agent')
    parser.add_argument('--model', default='dqn_web_sec_model.pth', help='Path to trained model')
    parser.add_argument('--episodes', type=int, default=10, help='Episodes per target')
    parser.add_argument('--output', default='evaluation_report.json', help='Output report file')
    
    args = parser.parse_args()
    
    # Define targets (same as training)
    targets = [
        ("E-Commerce Platform", "http://localhost:5002"),
        ("Social Media", "http://localhost:5003"),
        ("SecureBank", "http://localhost:5004"),
        ("VulnBlog", "http://localhost:5005"),
        ("FileShare Pro", "http://localhost:5006"),
        ("OWASP Juice Shop", "http://localhost:3000"),
    ]
    
    # Run evaluation
    evaluator = MultiTargetEvaluator(model_path=args.model)
    results = evaluator.evaluate_all_targets(targets, num_episodes=args.episodes)
    report = evaluator.generate_report(results, output_file=args.output)
    
    print(f"\n✅ Evaluation complete!")
    print(f"📄 Full report: {args.output}")

"""
Deploy Trained Agent Against External Targets (e.g., DVWA)

This script loads your trained DQN model and runs it against any target website.
"""

import torch
import numpy as np
from agent.dqn_agent import DQNAgent
from env.web_sec_env import WebSecurityGym
import argparse

def load_trained_agent(model_path, state_dim=7, action_dim=15):
    """Load a trained DQN agent from checkpoint"""
    agent = DQNAgent(state_dim, action_dim)
    agent.q_network.load_state_dict(torch.load(model_path))
    agent.q_network.eval()  # Set to evaluation mode
    agent.epsilon = 0.0  # No exploration, only exploitation
    print(f"✅ Loaded trained model from: {model_path}")
    return agent

def test_agent(target_url, model_path="dqn_web_sec_model.pth", episodes=10, verbose=True):
    """
    Test the trained agent against a target website
    
    Args:
        target_url: URL of the target (e.g., "http://localhost/dvwa")
        model_path: Path to the trained model weights
        episodes: Number of test episodes to run
        verbose: Print detailed output
    """
    
    # Create environment pointing to target
    env = WebSecurityGym(target_url=target_url)
    
    # Load trained agent
    agent = load_trained_agent(model_path)
    
    print(f"\n🎯 Target: {target_url}")
    print(f"🤖 Running {episodes} test episodes...\n")
    print("=" * 60)
    
    vulnerabilities_found = []
    
    for episode in range(episodes):
        state, _ = env.reset()
        total_reward = 0
        done = False
        step_count = 0
        
        episode_log = []
        
        while not done and step_count < 50:
            # Agent selects best action (no exploration)
            action = agent.act(state)
            next_state, reward, terminated, truncated, info = env.step(action)
            done = terminated or truncated
            
            total_reward += reward
            step_count += 1
            
            # Log significant events
            if reward > 50:  # Vulnerability found!
                action_name = get_action_name(action)
                vuln_info = {
                    'episode': episode + 1,
                    'action': action_name,
                    'reward': reward,
                    'step': step_count
                }
                vulnerabilities_found.append(vuln_info)
                episode_log.append(f"  🚨 VULNERABILITY FOUND: {action_name} (Reward: {reward})")
            
            state = next_state
        
        if verbose:
            print(f"\nEpisode {episode + 1}/{episodes}")
            print(f"  Total Reward: {total_reward}")
            print(f"  Steps: {step_count}")
            if episode_log:
                for log in episode_log:
                    print(log)
            print("-" * 60)
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 SUMMARY")
    print("=" * 60)
    print(f"Total Vulnerabilities Found: {len(vulnerabilities_found)}")
    
    if vulnerabilities_found:
        print("\n🔴 Vulnerabilities Detected:")
        for vuln in vulnerabilities_found:
            print(f"  - Episode {vuln['episode']}: {vuln['action']} (Step {vuln['step']}, Reward: {vuln['reward']})")
    else:
        print("\n✅ No vulnerabilities detected (or agent needs more training)")
    
    return vulnerabilities_found

def get_action_name(action):
    """Map action ID to human-readable name"""
    action_map = {
        0: "Navigate Home",
        1: "Navigate Login",
        2: "Navigate Search",
        3: "SQLi (Basic)",
        4: "XSS (Basic)",
        5: "Navigate Ping",
        6: "Navigate Profile",
        7: "Navigate Fetch",
        8: "Command Injection",
        9: "IDOR Attack",
        10: "SSRF Attack",
        11: "Wait (Rate Limit Bypass)",
        12: "Extract CSRF Token",
        13: "SQLi (Obfuscated)",
        14: "XSS (Obfuscated)"
    }
    return action_map.get(action, f"Unknown Action {action}")

def interactive_mode(target_url, model_path="dqn_web_sec_model.pth"):
    """
    Interactive mode: Watch the agent in real-time
    """
    env = WebSecurityGym(target_url=target_url)
    agent = load_trained_agent(model_path)
    
    print(f"\n🎮 INTERACTIVE MODE")
    print(f"Target: {target_url}")
    print("Press Ctrl+C to stop\n")
    
    try:
        episode = 1
        while True:
            print(f"\n{'='*60}")
            print(f"Episode {episode}")
            print('='*60)
            
            state, _ = env.reset()
            done = False
            step = 0
            
            while not done and step < 50:
                action = agent.act(state)
                action_name = get_action_name(action)
                
                print(f"\nStep {step + 1}: {action_name}")
                
                next_state, reward, terminated, truncated, info = env.step(action)
                done = terminated or truncated
                
                if reward > 0:
                    print(f"  ✅ Reward: +{reward}")
                elif reward < -5:
                    print(f"  ⚠️  Penalty: {reward}")
                
                if reward > 50:
                    print(f"  🚨 VULNERABILITY EXPLOITED!")
                
                state = next_state
                step += 1
                
                import time
                time.sleep(0.5)  # Slow down for visibility
            
            episode += 1
            
    except KeyboardInterrupt:
        print("\n\n👋 Stopped by user")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Deploy trained RL agent against target websites")
    parser.add_argument("--target", type=str, required=True, help="Target URL (e.g., http://localhost/dvwa)")
    parser.add_argument("--model", type=str, default="dqn_web_sec_model.pth", help="Path to trained model")
    parser.add_argument("--episodes", type=int, default=10, help="Number of test episodes")
    parser.add_argument("--interactive", action="store_true", help="Run in interactive mode")
    
    args = parser.parse_args()
    
    if args.interactive:
        interactive_mode(args.target, args.model)
    else:
        test_agent(args.target, args.model, args.episodes)

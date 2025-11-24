"""
AI Training Loop
================

This script is the "Gym" where the AI Agent trains.
It runs the agent through thousands of practice scenarios (episodes) to learn how to hack.

Key Steps:
1. Start the target website (the "sparring partner").
2. Create the AI Agent (the "student").
3. Loop through episodes:
    - Agent tries actions.
    - Environment gives feedback (rewards).
    - Agent learns from mistakes.
4. Save progress regularly (checkpoints).
"""

import gymnasium as gym
from env.web_sec_env import WebSecEnv
from agent.dqn_agent import DQNAgent
import time
import threading
import os
import torch
import glob
import datetime

def launch_target_website():
    """Starts the vulnerable website in a background thread."""
    from env.target_app import app
    # Run without reloader to avoid duplicate processes
    app.run(debug=False, use_reloader=False)

def find_latest_checkpoint():
    """
    Looks for the most recent 'save file' to resume training.
    Returns: (path_to_checkpoint, episode_number)
    """
    checkpoints = glob.glob("checkpoints/dqn_checkpoint_ep*.pth")
    if not checkpoints:
        return None, 0
    
    # Extract episode numbers to find the highest one
    episodes = []
    for cp in checkpoints:
        try:
            # Filename format: dqn_checkpoint_ep100.pth
            ep_num = int(cp.split("ep")[1].split(".pth")[0])
            episodes.append((ep_num, cp))
        except:
            continue
    
    if episodes:
        # Sort by episode number (highest first)
        episodes.sort(reverse=True)
        return episodes[0][1], episodes[0][0]
    return None, 0

def evaluate_performance(agent, env, current_episode, log_file="evaluation/TRAINING_PROGRESS.md"):
    """
    Periodically tests the agent without 'random exploration' to see how smart it has become.
    Logs the results to a file.
    """
    print(f"\n🧪 Starting evaluation for Episode {current_episode}...")
    
    test_runs = 5
    total_score = 0
    vulnerabilities_found = 0
    successful_hacks = 0
    
    # Save the current "curiosity" level (epsilon)
    # We want the agent to use its BEST skills now, not try random things.
    saved_epsilon = agent.epsilon
    agent.epsilon = 0.0 
    
    for _ in range(test_runs):
        state, _ = env.reset()
        done = False
        run_score = 0
        
        while not done:
            # Ask the agent for the best move
            action = agent.act(state)
            next_state, reward, terminated, truncated, _ = env.step(action)
            done = terminated or truncated
            
            run_score += reward
            state = next_state
            
            # A high reward (>50) means it found a vulnerability
            if reward > 50:
                vulnerabilities_found += 1
        
        total_score += run_score
        if run_score > 0:
            successful_hacks += 1
            
    # Restore "curiosity" for further training
    agent.epsilon = saved_epsilon
    
    # Calculate stats
    avg_score = total_score / test_runs
    success_rate = (successful_hacks / test_runs) * 100
    
    # Log results
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    log_entry = f"| {timestamp} | {current_episode} | {avg_score:.1f} | {vulnerabilities_found} | {success_rate:.1f}% | {saved_epsilon:.4f} | Automatic Eval |\n"
    
    with open(log_file, "a") as f:
        f.write(log_entry)
        
    print(f"📊 Evaluation Report:")
    print(f"   - Average Score: {avg_score:.1f}")
    print(f"   - Vulnerabilities Found: {vulnerabilities_found}")
    print(f"   - Success Rate: {success_rate:.1f}%")
    print(f"📝 Results logged to {log_file}\n")

def start_training_session():
    """Main function to run the training loop."""
    
    # 1. Start the target website
    server_thread = threading.Thread(target=launch_target_website, daemon=True)
    server_thread.start()
    
    print("Waiting for target website to launch...")
    time.sleep(2)
    
    # 2. Initialize Environment and Agent
    env = WebSecEnv()
    state_size = 11 # The agent sees 11 features (Updated for Business Context)
    action_size = env.action_space.n # The agent has 48 possible moves
    
    agent = DQNAgent(state_size, action_size)
    
    # 3. Check for previous progress
    checkpoint_path, start_episode = find_latest_checkpoint()
    
    model_loaded = False

    # Priority 1: Resume from Checkpoint
    if checkpoint_path:
        print(f"\n📂 Found checkpoint history: {checkpoint_path}")
        print(f"🔄 Resuming episode count from {start_episode}")
        try:
            agent.brain.load_state_dict(torch.load(checkpoint_path))
            agent.target_brain.load_state_dict(agent.brain.state_dict())
            print("✅ Checkpoint loaded successfully!")
            model_loaded = True
            
            # Adjust curiosity
            agent.epsilon = max(agent.epsilon_min, agent.epsilon * (agent.epsilon_decay ** start_episode))
            print(f"   Curiosity level (Epsilon) adjusted to: {agent.epsilon:.4f}\n")
        except Exception as e:
            print(f"⚠️  Could not load checkpoint: {e}")
            print("   Attempting to fall back to main model...\n")

    # Priority 2: Load Main Model (if no checkpoint or checkpoint failed)
    if not model_loaded and os.path.exists("dqn_web_sec_model.pth"):
        print("🧠 Loading upgraded Deep Brain model...")
        try:
            agent.brain.load_state_dict(torch.load("dqn_web_sec_model.pth"))
            agent.target_brain.load_state_dict(agent.brain.state_dict())
            print("✅ Model loaded successfully!")
            model_loaded = True
        except Exception as e:
            print(f"⚠️  Could not load model: {e}")
            
    if not model_loaded:
        print("\n🆕 No valid save file found. Starting fresh!\n")
        start_episode = 0
    
    # Training Configuration
    total_episodes = 1000      # Extended training for Pentester Mode

    save_frequency = 20       # Save every 20 episodes
    eval_frequency = 20       # Test performance every 20 episodes
    
    print(f"Training for {total_episodes} episodes...")
    print(f"Autosaving every {save_frequency} episodes.")
    print("Press Ctrl+C to stop safely.\n")
    print("=" * 60)
    
    try:
        for episode in range(start_episode, total_episodes):
            state, _ = env.reset()
            episode_score = 0
            done = False
            
            # Play one full "game" (episode)
            while not done:
                # Decide action
                action = agent.act(state)
                
                # Take action
                next_state, reward, terminated, truncated, _ = env.step(action)
                done = terminated or truncated
                
                # Learn from the result
                agent.remember(state, action, reward, next_state, done)
                agent.replay() # This is where the actual learning happens (updating the brain)
                
                state = next_state
                episode_score += reward
            
            print(f"Episode: {episode+1}/{total_episodes}, Score: {episode_score}, Curiosity: {agent.epsilon:.2f}")
            
            # Save Checkpoint
            if (episode + 1) % save_frequency == 0:
                checkpoint_path = f"checkpoints/dqn_checkpoint_ep{episode+1}.pth"
                os.makedirs("checkpoints", exist_ok=True)
                torch.save(agent.brain.state_dict(), checkpoint_path)
                print(f"💾 Progress saved: {checkpoint_path}")
            
            # Run Evaluation
            if (episode + 1) % eval_frequency == 0:
                evaluate_performance(agent, env, episode+1)
        
        # Save Final Model
        torch.save(agent.brain.state_dict(), "dqn_web_sec_model.pth")
        print("\n✅ Training complete! Final model saved.")
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Training paused by user.")
        # Save with episode number so we can resume exactly here
        checkpoint_path = f"checkpoints/dqn_checkpoint_ep{episode}_INTERRUPTED.pth"
        os.makedirs("checkpoints", exist_ok=True)
        torch.save(agent.brain.state_dict(), checkpoint_path)
        print(f"💾 Progress saved to: {checkpoint_path}")
        print("   (You can resume from here next time!)")

if __name__ == "__main__":
    start_training_session()

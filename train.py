import gymnasium as gym
from env.web_sec_env import WebSecEnv
from agent.dqn_agent import DQNAgent
import time
import threading
import os
import torch
import glob

def start_server():
    from env.target_app import app
    app.run(debug=False, use_reloader=False)

def find_latest_checkpoint():
    """Find the latest checkpoint file"""
    checkpoints = glob.glob("checkpoints/dqn_checkpoint_ep*.pth")
    if not checkpoints:
        return None, 0
    
    # Extract episode numbers and find the latest
    episodes = []
    for cp in checkpoints:
        try:
            ep_num = int(cp.split("ep")[1].split(".pth")[0])
            episodes.append((ep_num, cp))
        except:
            continue
    
    if episodes:
        episodes.sort(reverse=True)
        return episodes[0][1], episodes[0][0]
    return None, 0

def train():
    # Start Flask server in background
    server_thread = threading.Thread(target=start_server, daemon=True)
    server_thread.start()
    
    print("Waiting for server to start...")
    time.sleep(2)
    
    # Create environment and agent
    env = WebSecEnv()
    state_dim = env.observation_space.shape[0]
    action_dim = env.action_space.n
    
    agent = DQNAgent(state_dim, action_dim)
    
    # Check for existing checkpoint to resume from
    checkpoint_path, start_episode = find_latest_checkpoint()
    if checkpoint_path:
        print(f"\n📂 Found checkpoint: {checkpoint_path}")
        print(f"🔄 Resuming from episode {start_episode}")
        agent.q_network.load_state_dict(torch.load(checkpoint_path))
        # Adjust epsilon based on episodes completed
        agent.epsilon = max(agent.epsilon_min, agent.epsilon * (agent.epsilon_decay ** start_episode))
        print(f"   Epsilon adjusted to: {agent.epsilon:.4f}\n")
    else:
        print("\n🆕 No checkpoint found, starting from scratch\n")
        start_episode = 0
    
    episodes = 500  # Best quality - can run overnight
    checkpoint_interval = 20  # Save every 20 episodes
    
    print("Starting training for {} episodes...".format(episodes))
    print("Checkpoints will be saved every {} episodes".format(checkpoint_interval))
    print("Press Ctrl+C to stop training and save progress\n")
    print(f"Environment: {action_dim} actions, {state_dim} state features")
    print("=" * 60)
    
    try:
        for e in range(start_episode, episodes):
            state, _ = env.reset()
            total_reward = 0
            done = False
            
            while not done:
                action = agent.act(state)
                next_state, reward, terminated, truncated, _ = env.step(action)
                done = terminated or truncated
                
                agent.remember(state, action, reward, next_state, done)
                agent.replay()
                
                state = next_state
                total_reward += reward
            
            print(f"Episode: {e+1}/{episodes}, Score: {total_reward}, Epsilon: {agent.epsilon:.2f}")
            
            # Save checkpoint every N episodes
            if (e + 1) % checkpoint_interval == 0:
                checkpoint_path = f"checkpoints/dqn_checkpoint_ep{e+1}.pth"
                os.makedirs("checkpoints", exist_ok=True)
                torch.save(agent.q_network.state_dict(), checkpoint_path)
                print(f"💾 Checkpoint saved: {checkpoint_path} (static - will not be overwritten)")
        
        # Save final model
        torch.save(agent.q_network.state_dict(), "dqn_web_sec_model.pth")
        print("\n✅ Training complete! Model saved to dqn_web_sec_model.pth")
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Training interrupted by user")
        torch.save(agent.q_network.state_dict(), "dqn_web_sec_model.pth")
        print("💾 Model saved to dqn_web_sec_model.pth")

if __name__ == "__main__":
    train()

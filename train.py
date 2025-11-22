import threading
import time
import numpy as np
import os
import torch
from env.target_app import app
from env.web_sec_env import WebSecEnv
from agent.dqn_agent import DQNAgent

def run_server():
    app.run(port=5000, use_reloader=False)

def train():
    # Start the vulnerable app in a separate thread
    server_thread = threading.Thread(target=run_server, daemon=True)
    server_thread.start()
    print("Waiting for server to start...")
    time.sleep(2) # Give it a moment

    env = WebSecEnv()
    state_dim = env.observation_space.shape[0]
    action_dim = env.action_space.n
    
    agent = DQNAgent(state_dim, action_dim)
    
    episodes = 500  # Increased from 200 to 500 for comprehensive learning
    checkpoint_interval = 20  # Save every 20 episodes (more frequent)
    
    print("Starting training for {} episodes...".format(episodes))
    print("Checkpoints will be saved every {} episodes".format(checkpoint_interval))
    print("Press Ctrl+C to stop training and save progress\n")
    print(f"Environment: {action_dim} actions, {state_dim} state features")
    print("=" * 60)
    
    try:
        for e in range(episodes):
            state, _ = env.reset()
            total_reward = 0
            done = False
            
            while not done:
                action = agent.act(state)
                next_state, reward, terminated, truncated, _ = env.step(action)
                done = terminated or truncated
                
                agent.remember(state, action, reward, next_state, done)
                state = next_state
                total_reward += reward
                
                agent.replay()
                
            print(f"Episode: {e+1}/{episodes}, Score: {total_reward}, Epsilon: {agent.epsilon:.2f}")
            
            # Save checkpoint every N episodes
            if (e + 1) % checkpoint_interval == 0:
                checkpoint_path = f"checkpoints/dqn_checkpoint_ep{e+1}.pth"
                os.makedirs("checkpoints", exist_ok=True)
                torch.save(agent.q_network.state_dict(), checkpoint_path)
                print(f"  → Checkpoint saved: {checkpoint_path}")

        print("\nTraining finished successfully!")
        
    except KeyboardInterrupt:
        print("\n\n[!] Training interrupted by user")
        print(f"Completed {e+1}/{episodes} episodes")
    
    # Save the final/current model
    torch.save(agent.q_network.state_dict(), "dqn_web_sec_model.pth")
    print(f"Model saved to dqn_web_sec_model.pth")

if __name__ == "__main__":
    train()

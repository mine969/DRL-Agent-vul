import threading
import time
import numpy as np
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

    episodes = 200
    
    print(f"Starting training for {episodes} episodes...")

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

    print("Training finished.")
    
    # Save the trained model
    torch.save(agent.q_network.state_dict(), "dqn_web_sec_model.pth")
    print("Model saved to dqn_web_sec_model.pth")

if __name__ == "__main__":
    train()

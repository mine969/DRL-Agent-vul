import gymnasium as gym
import numpy as np
from gymnasium import spaces
from agent.dqn_agent import DQNAgent
import sys

# NOTE: This is a template. You must install the specific environment libraries yourself.
# Example: pip install gym-network-intrusion
# For CyberBattleSim, you typically need to clone the repo and install from source.

def make_cyber_env(env_name):
    """
    Factory function to create and wrap external environments.
    """
    try:
        # Try importing common libraries (uncomment as needed)
        # import cyberbattlesim
        # import secgym 
        
        # For demonstration, we will use a standard Gym env if the specific one isn't found
        # In reality, you would do: env = gym.make("CyberBattleSim-v0")
        print(f"Attempting to load {env_name}...")
        env = gym.make(env_name)
        
        # ADAPTER: Most cyber envs have complex Dict or Graph observations.
        # Our simple DQN expects a flat vector. We use a wrapper to flatten it.
        env = gym.wrappers.FlattenObservation(env)
        
        return env
    except ImportError as e:
        print(f"Error: Could not import module for {env_name}. {e}")
        print("Please ensure the environment package is installed.")
        return None
    except Exception as e:
        print(f"Error creating environment: {e}")
        return None

def train_external(env_name="CartPole-v1"): # Defaulting to CartPole as a placeholder for "Any Gym Env"
    env = make_cyber_env(env_name)
    if env is None:
        return

    # Dynamic Dimension Handling
    # The wrapper ensures observation_space is a Box (flat vector)
    if isinstance(env.observation_space, spaces.Box):
        state_dim = int(np.prod(env.observation_space.shape))
    else:
        print(f"Unsupported observation space: {env.observation_space}")
        return

    if isinstance(env.action_space, spaces.Discrete):
        action_dim = env.action_space.n
    else:
        print("Only Discrete action spaces are supported by this DQN.")
        return

    print(f"Initialized Environment: {env_name}")
    print(f"State Dim: {state_dim}, Action Dim: {action_dim}")

    agent = DQNAgent(state_dim, action_dim)
    episodes = 10 # Short run for demo

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
            
        print(f"Episode: {e+1}/{episodes}, Score: {total_reward:.2f}")

    print("External training demo finished.")

if __name__ == "__main__":
    # To use with CyberBattleSim (if installed):
    # train_external("CyberBattleTiny-v0")
    
    # To use with a generic Gym env (proof of concept):
    train_external("CartPole-v1")

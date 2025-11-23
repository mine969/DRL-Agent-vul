"""
The AI Brain (DQN Agent)
========================

This file defines the "Brain" of our AI Hacker.
It uses a technique called Deep Q-Learning (DQN) to learn from experience.

Concepts:
- Brain (Neural Network): Estimates how good an action is.
- Memory (Replay Buffer): Remembers past actions and rewards.
- Learning (Replay): Reviews past memories to improve the Brain.
"""

import torch
import torch.nn as nn
import torch.optim as optim
import numpy as np
import random
from typing import Tuple, Dict, List
import os

class ExperienceMemory:
    """
    The Agent's Memory.
    It stores past experiences so the agent can learn from them later.
    
    Optimization:
    Uses pre-allocated Numpy arrays for super-fast (O(1)) speed.
    """
    def __init__(self, state_size: int, action_size: int, capacity: int = 10000):
        self.capacity = capacity
        self.pointer = 0
        self.current_size = 0
        
        # Pre-allocate memory blocks (like empty slots in a bookshelf)
        self.states = np.zeros((capacity, state_size), dtype=np.float32)
        self.actions = np.zeros((capacity, 1), dtype=np.int64)
        self.rewards = np.zeros((capacity, 1), dtype=np.float32)
        self.next_states = np.zeros((capacity, state_size), dtype=np.float32)
        self.dones = np.zeros((capacity, 1), dtype=np.float32)
        
        # Use GPU if available
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    def save(self, state: np.ndarray, action: int, reward: float, next_state: np.ndarray, done: bool):
        """Saves a single experience to memory."""
        self.states[self.pointer] = state
        self.actions[self.pointer] = action
        self.rewards[self.pointer] = reward
        self.next_states[self.pointer] = next_state
        self.dones[self.pointer] = done
        
        # Move pointer to next slot (loop back to start if full)
        self.pointer = (self.pointer + 1) % self.capacity
        self.current_size = min(self.current_size + 1, self.capacity)

    def recall_batch(self, batch_size: int) -> Tuple[torch.Tensor, ...]:
        """Randomly recalls a batch of past experiences for training."""
        indices = np.random.randint(0, self.current_size, size=batch_size)
        
        return (
            torch.FloatTensor(self.states[indices]).to(self.device),
            torch.LongTensor(self.actions[indices]).to(self.device),
            torch.FloatTensor(self.rewards[indices]).to(self.device),
            torch.FloatTensor(self.next_states[indices]).to(self.device),
            torch.FloatTensor(self.dones[indices]).to(self.device)
        )

    def __len__(self) -> int:
        return self.current_size


class NeuralNetworkBrain(nn.Module):
    """
    The actual 'Brain' structure.
    It takes the current situation (State) and predicts the best move (Action).
    """
    def __init__(self, input_size: int, output_size: int):
        super(NeuralNetworkBrain, self).__init__()
        # Layers of neurons
        self.layer1 = nn.Linear(input_size, 512)
        self.layer2 = nn.Linear(512, 512)
        self.layer3 = nn.Linear(512, 256)
        self.output_layer = nn.Linear(256, output_size)
        
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """Passes information through the brain to get a decision."""
        x = torch.relu(self.layer1(x))
        x = torch.relu(self.layer2(x))
        x = torch.relu(self.layer3(x))
        return self.output_layer(x)


class DQNAgent:
    """
    The AI Agent Controller.
    Manages the Brain, Memory, and Learning process.
    """
    def __init__(self, state_dim: int, action_dim: int):
        self.state_dim = state_dim
        self.action_dim = action_dim
        
        # Learning Settings
        self.gamma = 0.99           # How much we care about future rewards
        self.epsilon = 1.0          # Curiosity level (1.0 = 100% random)
        self.epsilon_min = 0.01     # Minimum curiosity
        self.epsilon_decay = 0.995  # How fast curiosity fades
        self.batch_size = 32        # How many memories to learn from at once
        self.learning_rate = 0.001
        
        # Hardware Setup
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        print(f"🚀 AI Brain initialized on: {self.device}")
        if self.device.type == 'cuda':
            print(f"   GPU Model: {torch.cuda.get_device_name(0)}")
        
        # Initialize Components
        self.memory = ExperienceMemory(state_dim, action_dim, capacity=10000)
        self.q_network = NeuralNetworkBrain(state_dim, action_dim).to(self.device)
        
        # Optimizer (The "Teacher" that corrects the brain)
        self.optimizer = optim.Adam(self.q_network.parameters(), lr=self.learning_rate)
        self.loss_function = nn.MSELoss()

    def act(self, state: np.ndarray) -> int:
        """
        Decides what to do next.
        Either explores randomly (Curiosity) or uses the Brain (Experience).
        """
        # 1. Explore: Try something random?
        if np.random.rand() <= self.epsilon:
            return random.randrange(self.action_dim)
        
        # 2. Exploit: Use the Brain
        state_tensor = torch.FloatTensor(state).unsqueeze(0).to(self.device)
        with torch.no_grad():
            predicted_rewards = self.q_network(state_tensor)
        
        # Pick the action with the highest predicted reward
        return int(np.argmax(predicted_rewards.cpu().data.numpy()))

    def remember(self, state: np.ndarray, action: int, reward: float, next_state: np.ndarray, done: bool):
        """Stores a new experience in memory."""
        self.memory.save(state, action, reward, next_state, done)

    def replay(self):
        """
        The Learning Step.
        Reviews a batch of past memories and updates the brain to be smarter.
        """
        if len(self.memory) < self.batch_size:
            return
        
        # 1. Recall a batch of memories
        states, actions, rewards, next_states, dones = self.memory.recall_batch(self.batch_size)
        
        # 2. Predict what we THOUGHT would happen (Current Q)
        current_q_values = self.q_network(states).gather(1, actions).squeeze(1)
        
        # 3. Calculate what ACTUALLY happened (Target Q)
        # Formula: Reward + (Future Value * Discount)
        next_q_values = self.q_network(next_states).max(1)[0]
        target_q_values = rewards.squeeze(1) + (1 - dones.squeeze(1)) * self.gamma * next_q_values
        
        # 4. Calculate the mistake (Loss)
        loss = self.loss_function(current_q_values, target_q_values.detach())
        
        # 5. Correct the Brain (Backpropagation)
        self.optimizer.zero_grad()
        loss.backward()
        self.optimizer.step()
        
        # 6. Reduce curiosity slightly (become more confident)
        if self.epsilon > self.epsilon_min:
            self.epsilon *= self.epsilon_decay


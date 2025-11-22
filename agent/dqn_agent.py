"""
Optimized Deep Q-Network (DQN) Agent

Performance improvements:
- O(1) Replay Buffer using numpy arrays (vs O(n) deque)
- Type hints for code quality
- Efficient batch sampling
- GPU acceleration support
"""

import torch
import torch.nn as nn
import torch.optim as optim
import numpy as np
import random
from typing import Tuple, Dict, List
import os

class ReplayBuffer:
    """
    Optimized Replay Buffer using numpy arrays for O(1) access
    """
    def __init__(self, state_dim: int, action_dim: int, max_size: int = 10000):
        self.max_size = max_size
        self.ptr = 0
        self.size = 0
        
        # Pre-allocate memory for O(1) insertion
        self.states = np.zeros((max_size, state_dim), dtype=np.float32)
        self.actions = np.zeros((max_size, 1), dtype=np.int64)
        self.rewards = np.zeros((max_size, 1), dtype=np.float32)
        self.next_states = np.zeros((max_size, state_dim), dtype=np.float32)
        self.dones = np.zeros((max_size, 1), dtype=np.float32)
        
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    def add(self, state: np.ndarray, action: int, reward: float, next_state: np.ndarray, done: bool):
        """Add experience to buffer in O(1)"""
        self.states[self.ptr] = state
        self.actions[self.ptr] = action
        self.rewards[self.ptr] = reward
        self.next_states[self.ptr] = next_state
        self.dones[self.ptr] = done
        
        self.ptr = (self.ptr + 1) % self.max_size
        self.size = min(self.size + 1, self.max_size)

    def sample(self, batch_size: int) -> Tuple[torch.Tensor, torch.Tensor, torch.Tensor, torch.Tensor, torch.Tensor]:
        """Sample batch in O(1)"""
        ind = np.random.randint(0, self.size, size=batch_size)
        
        return (
            torch.FloatTensor(self.states[ind]).to(self.device),
            torch.LongTensor(self.actions[ind]).to(self.device),
            torch.FloatTensor(self.rewards[ind]).to(self.device),
            torch.FloatTensor(self.next_states[ind]).to(self.device),
            torch.FloatTensor(self.dones[ind]).to(self.device)
        )

    def __len__(self) -> int:
        return self.size


class QNetwork(nn.Module):
    """Deep Q-Network Architecture"""
    def __init__(self, state_dim: int, action_dim: int):
        super(QNetwork, self).__init__()
        self.fc1 = nn.Linear(state_dim, 512)
        self.fc2 = nn.Linear(512, 512)
        self.fc3 = nn.Linear(512, 256)
        self.fc4 = nn.Linear(256, action_dim)
        
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        x = torch.relu(self.fc1(x))
        x = torch.relu(self.fc2(x))
        x = torch.relu(self.fc3(x))
        return self.fc4(x)


class DQNAgent:
    """Optimized DQN Agent"""
    def __init__(self, state_dim: int, action_dim: int):
        self.state_dim = state_dim
        self.action_dim = action_dim
        
        # Hyperparameters
        self.gamma = 0.99
        self.epsilon = 1.0
        self.epsilon_min = 0.01
        self.epsilon_decay = 0.995
        self.batch_size = 32
        self.lr = 0.001
        
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        print(f"🚀 Agent using device: {self.device}")
        if self.device.type == 'cuda':
            print(f"   GPU: {torch.cuda.get_device_name(0)}")
        
        # Optimized Replay Buffer
        self.memory = ReplayBuffer(state_dim, action_dim, max_size=10000)
        
        self.q_network = QNetwork(state_dim, action_dim).to(self.device)
        self.optimizer = optim.Adam(self.q_network.parameters(), lr=self.lr)
        self.criterion = nn.MSELoss()

    def act(self, state: np.ndarray) -> int:
        """Select action using Epsilon-Greedy policy"""
        if np.random.rand() <= self.epsilon:
            return random.randrange(self.action_dim)
        
        state_tensor = torch.FloatTensor(state).unsqueeze(0).to(self.device)
        with torch.no_grad():
            q_values = self.q_network(state_tensor)
        return int(np.argmax(q_values.cpu().data.numpy()))

    def remember(self, state: np.ndarray, action: int, reward: float, next_state: np.ndarray, done: bool):
        """Store experience in replay buffer"""
        self.memory.add(state, action, reward, next_state, done)

    def replay(self):
        """Train the network on a batch of experiences"""
        if len(self.memory) < self.batch_size:
            return
        
        # Sample batch (Optimized)
        states, actions, rewards, next_states, dones = self.memory.sample(self.batch_size)
        
        # Q(s, a)
        current_q = self.q_network(states).gather(1, actions).squeeze(1)
        
        # Q(s', a')
        next_q = self.q_network(next_states).max(1)[0]
        target_q = rewards.squeeze(1) + (1 - dones.squeeze(1)) * self.gamma * next_q
        
        loss = self.criterion(current_q, target_q.detach())
        
        self.optimizer.zero_grad()
        loss.backward()
        self.optimizer.step()
        
        # Decay epsilon
        if self.epsilon > self.epsilon_min:
            self.epsilon *= self.epsilon_decay


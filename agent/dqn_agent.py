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
        
        # Common Feature Layer
        # Common Feature Layer (Deep Brain Architecture)
        # Common Feature Layer (MAX GPU MODE - RTX 2070 Optimized)
        self.feature_layer = nn.Sequential(
            nn.Linear(input_size, 8192), # MAXIMUM input layer
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(8192, 4096),       # Deep abstraction
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(4096, 2048),       # Intermediate
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(2048, 1024),       # Bottleneck
            nn.ReLU()
        )
        
        # Stream 1: Value (V) - How good is the current state?
        # Stream 1: Value (V) - How good is the current state?
        self.value_stream = nn.Sequential(
            nn.Linear(1024, 1024),
            nn.ReLU(),
            nn.Linear(1024, 1) 
        )
        
        # Stream 2: Advantage (A) - How much better is this action than others?
        self.advantage_stream = nn.Sequential(
            nn.Linear(1024, 1024),
            nn.ReLU(),
            nn.Linear(1024, output_size) 
        )
        
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """Passes information through the Dueling Network."""
        features = self.feature_layer(x)
        
        values = self.value_stream(features)
        advantages = self.advantage_stream(features)
        
        # Combine V and A to get Q
        # Q(s,a) = V(s) + (A(s,a) - mean(A(s,a)))
        q_values = values + (advantages - advantages.mean(dim=1, keepdim=True))
        return q_values


class DQNAgent:
    """
    The AI Agent Controller.
    Manages the Brain, Memory, and Learning process.
    """
    def __init__(self, state_dim: int, action_dim: int):
        self.state_dim = state_dim
        self.action_dim = action_dim
        
        # Learning Settings (Optimized for Multi-Target Training)
        self.gamma = 0.99           # Discount factor for future rewards
        self.epsilon = 1.0          # Initial exploration rate
        self.epsilon_min = 0.05     # Higher min for continued exploration on diverse targets
        self.epsilon_decay = 0.9997 # Slower decay for better generalization
        self.batch_size = 4096      # MAX BATCH for RTX 2070
        self.learning_rate = 0.0002 # Lower LR for larger batch
        self.tau = 0.01             # Faster soft update for adapting to new targets
        
        # Hardware Setup
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        print(f"AI Brain initialized on: {self.device}")
        if self.device.type == 'cuda':
            print(f"   GPU Model: {torch.cuda.get_device_name(0)}")
            torch.backends.cudnn.benchmark = True # Auto-tune for max speed
            torch.backends.cuda.matmul.allow_tf32 = True # Enable TF32 for speed
            print(f"   CuDNN Benchmark: ENABLED")
            print(f"   TF32 Math: ENABLED (MAX Speed Mode)")
            print(f"   Batch Size: 4096 (MAX)")
            print(f"   Network Size: 8192 neurons (MAX)")
        
        # Initialize Components
        self.memory = ExperienceMemory(state_dim, action_dim, capacity=10000)
        
        # 1. Main Brain (The one that learns)
        self.brain = NeuralNetworkBrain(state_dim, action_dim).to(self.device)
        
        # 2. Target Brain (The stable reference)
        self.target_brain = NeuralNetworkBrain(state_dim, action_dim).to(self.device)
        self.target_brain.load_state_dict(self.brain.state_dict()) # Start as a clone
        self.target_brain.eval() # Never train this directly!
        
        # Optimizer (The "Teacher" that corrects the brain)
        self.optimizer = optim.Adam(self.brain.parameters(), lr=self.learning_rate)
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
            predicted_rewards = self.brain(state_tensor)
        
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
        current_q_values = self.brain(states).gather(1, actions).squeeze(1)
        
        # 3. Calculate what ACTUALLY happened (Target Q) using Double DQN
        # Step A: Main Brain picks the best action for the next state
        best_actions = self.brain(next_states).argmax(1).unsqueeze(1)
        
        # Step B: Target Brain calculates the value of that action
        # This prevents the agent from being "overconfident"
        next_q_values = self.target_brain(next_states).gather(1, best_actions).squeeze(1)
        
        # Step C: Bellman Equation
        target_q_values = rewards.squeeze(1) + (1 - dones.squeeze(1)) * self.gamma * next_q_values
        
        # 4. Calculate the mistake (Loss)
        loss = self.loss_function(current_q_values, target_q_values.detach())
        
        # 5. Correct the Brain (Backpropagation)
        self.optimizer.zero_grad()
        loss.backward()
        self.optimizer.step()
        
        # 6. Soft Update: Slowly blend Main Brain into Target Brain
        self.soft_update()
        
        # 6. Reduce curiosity slightly (become more confident)
        if self.epsilon > self.epsilon_min:
            self.epsilon *= self.epsilon_decay

    def soft_update(self):
        """
        Slowly updates the Target Brain to match the Main Brain.
        This creates a "Moving Target" that is stable but eventually catches up.
        Formula: Target = (tau * Main) + ((1-tau) * Target)
        """
        for target_param, local_param in zip(self.target_brain.parameters(), self.brain.parameters()):
            target_param.data.copy_(self.tau * local_param.data + (1.0 - self.tau) * target_param.data)


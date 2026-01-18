"""
DQN Agent Implementation
========================

Deep Q-Network agent for web security testing.
Implements a Double DQN with experience replay and target networks.

Concepts:
- Neural Network: Estimates Q-values for state-action pairs
- Experience Replay: Stores and samples past experiences for learning
- Target Network: Stable reference network for Q-value estimation
- Epsilon-Greedy: Balances exploration vs exploitation

Author: DRL Web Security Team
Date: 2025
"""

import torch
import torch.nn as nn
import torch.optim as optim
import numpy as np
import random
from typing import Tuple, Dict, List, Optional
import os
from pathlib import Path

try:
    from config import AgentConfig, get_config
    _CONFIG_AVAILABLE = True
except ImportError:
    _CONFIG_AVAILABLE = False
    # Fallback defaults if config module not available
    from dataclasses import dataclass
    
    @dataclass
    class AgentConfig:
        state_dim: int = 11
        action_dim: int = 100
        learning_rate: float = 0.0001
        gamma: float = 0.99
        epsilon_start: float = 1.0
        epsilon_end: float = 0.05
        epsilon_decay: float = 0.9995
        memory_size: int = 10000
        batch_size: int = 64
        target_update_frequency: int = 100
        device: str = "auto"
        hidden_sizes: List[int] = None
        
        def __post_init__(self):
            if self.hidden_sizes is None:
                self.hidden_sizes = [256, 128]

class ExperienceMemory:
    """
    Experience Replay Buffer.
    
    Stores past experiences (state, action, reward, next_state, done) 
    for learning through experience replay. Uses pre-allocated NumPy arrays
    for efficient O(1) insertion and random sampling.
    
    Attributes:
        capacity: Maximum number of experiences to store
        pointer: Current write position (circular buffer)
        current_size: Current number of stored experiences
        states: Pre-allocated array for states
        actions: Pre-allocated array for actions
        rewards: Pre-allocated array for rewards
        next_states: Pre-allocated array for next states
        dones: Pre-allocated array for done flags
        
    Example:
        >>> memory = ExperienceMemory(state_size=11, action_size=100, capacity=10000)
        >>> memory.save(state, action, reward, next_state, done)
        >>> states, actions, rewards, next_states, dones = memory.recall_batch(32)
    """
    
    def __init__(
        self,
        state_size: int,
        action_size: int,
        capacity: int = 10000
    ):
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

    def save(
        self,
        state: np.ndarray,
        action: int,
        reward: float,
        next_state: np.ndarray,
        done: bool
    ) -> None:
        """
        Save a single experience to memory.
        
        Args:
            state: Current state observation
            action: Action taken
            reward: Reward received
            next_state: Next state after action
            done: Whether episode terminated
        """
        self.states[self.pointer] = state
        self.actions[self.pointer] = action
        self.rewards[self.pointer] = reward
        self.next_states[self.pointer] = next_state
        self.dones[self.pointer] = done
        
        # Move pointer to next slot (loop back to start if full)
        self.pointer = (self.pointer + 1) % self.capacity
        self.current_size = min(self.current_size + 1, self.capacity)

    def recall_batch(
        self,
        batch_size: int
    ) -> Tuple[torch.Tensor, torch.Tensor, torch.Tensor, torch.Tensor, torch.Tensor]:
        """
        Sample a random batch of experiences for training.
        
        Args:
            batch_size: Number of experiences to sample
            
        Returns:
            Tuple of (states, actions, rewards, next_states, dones) as tensors
            
        Raises:
            ValueError: If batch_size > current_size
        """
        if batch_size > self.current_size:
            raise ValueError(f"Batch size {batch_size} exceeds available experiences {self.current_size}")
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
    Dueling DQN Architecture.
    
    Implements a dueling network that separates value estimation (V) 
    and advantage estimation (A) before combining them into Q-values.
    This allows the network to learn state values independently from
    action advantages.
    
    Architecture:
        Input → Feature Layer (256 → 128) → [Value Stream, Advantage Stream]
        Q(s,a) = V(s) + (A(s,a) - mean(A(s)))
        
    Attributes:
        feature_layer: Shared feature extraction layers
        value_stream: State value estimation (V)
        advantage_stream: Action advantage estimation (A)
    """
    
    def __init__(
        self,
        input_size: int,
        output_size: int,
        hidden_sizes: Optional[List[int]] = None
    ):
        """
        Initialize the neural network.
        
        Args:
            input_size: Dimension of input state
            output_size: Dimension of action space
            hidden_sizes: List of hidden layer sizes (default: [256, 128])
        """
        super(NeuralNetworkBrain, self).__init__()
        
        if hidden_sizes is None:
            hidden_sizes = [256, 128]
        
        # Build feature extraction layers
        layers = []
        prev_size = input_size
        for hidden_size in hidden_sizes:
            layers.append(nn.Linear(prev_size, hidden_size))
            layers.append(nn.ReLU())
            prev_size = hidden_size
        
        self.feature_layer = nn.Sequential(*layers)
        feature_output_size = hidden_sizes[-1]
        
        # Value stream: Estimates how good the current state is
        self.value_stream = nn.Sequential(
            nn.Linear(feature_output_size, 128),
            nn.ReLU(),
            nn.Linear(128, 1)
        )
        
        # Advantage stream: Estimates advantage of each action
        self.advantage_stream = nn.Sequential(
            nn.Linear(feature_output_size, 128),
            nn.ReLU(),
            nn.Linear(128, output_size)
        )
        
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """
        Forward pass through the dueling network.
        
        Args:
            x: Input state tensor (batch_size, state_dim)
            
        Returns:
            Q-values for all actions (batch_size, action_dim)
        """
        # Extract features
        features = self.feature_layer(x)
        
        # Compute value and advantage
        values = self.value_stream(features)  # (batch_size, 1)
        advantages = self.advantage_stream(features)  # (batch_size, action_dim)
        
        # Combine using dueling architecture formula
        # Q(s,a) = V(s) + (A(s,a) - mean(A(s)))
        # This centers advantages to reduce variance
        q_values = values + (advantages - advantages.mean(dim=1, keepdim=True))
        return q_values


class DQNAgent:
    """
    Deep Q-Network Agent for web security testing.
    
    Implements a Double DQN with experience replay, target networks,
    and epsilon-greedy exploration. Manages the learning process and
    action selection.
    
    Attributes:
        state_dim: Dimension of state space
        action_dim: Dimension of action space
        epsilon: Current exploration rate (0-1)
        device: Computing device (CPU or GPU)
        memory: Experience replay buffer
        brain: Main Q-network
        target_brain: Target Q-network (stable reference)
        
    Example:
        >>> agent = DQNAgent(state_dim=11, action_dim=100)
        >>> action = agent.act(state, training=True)
        >>> agent.remember(state, action, reward, next_state, done)
        >>> agent.replay()
    """
    
    def __init__(
        self,
        state_dim: int,
        action_dim: int,
        config: Optional[AgentConfig] = None
    ):
        """
        Initialize the DQN agent.
        
        Args:
            state_dim: Dimension of state space
            action_dim: Dimension of action space
            config: Agent configuration (uses default if None)
        """
        # Load configuration
        if config is None and _CONFIG_AVAILABLE:
            config = get_config().agent
        elif config is None:
            config = AgentConfig()
        
        self.config = config
        self.state_dim = state_dim
        self.action_dim = action_dim
        
        # Learning hyperparameters
        self.gamma = config.gamma
        self.epsilon = config.epsilon_start
        self.epsilon_min = config.epsilon_end
        self.epsilon_decay = config.epsilon_decay
        self.batch_size = config.batch_size
        self.learning_rate = config.learning_rate
        self.tau = 0.01  # Soft update coefficient
        
        # Hardware setup
        if config.device == "auto":
            self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        else:
            self.device = torch.device(config.device)
        
        self._log_initialization()
        
        # Initialize components
        self.memory = ExperienceMemory(
            state_dim,
            action_dim,
            capacity=config.memory_size
        )
        
        # Main Q-network (learns)
        self.brain = NeuralNetworkBrain(
            state_dim,
            action_dim,
            hidden_sizes=config.hidden_sizes
        ).to(self.device)
        
        # Target Q-network (stable reference for learning)
        self.target_brain = NeuralNetworkBrain(
            state_dim,
            action_dim,
            hidden_sizes=config.hidden_sizes
        ).to(self.device)
        self.target_brain.load_state_dict(self.brain.state_dict())
        self.target_brain.eval()  # Never train directly
        
        # Optimizer
        self.optimizer = optim.Adam(
            self.brain.parameters(),
            lr=self.learning_rate
        )
        self.loss_function = nn.MSELoss()
        
        # Training step counter for target network updates
        self.training_steps = 0
    
    def _log_initialization(self):
        """Log initialization information."""
        print(f"DQN Agent initialized on: {self.device}")
        if self.device.type == 'cuda':
            print(f"  GPU Model: {torch.cuda.get_device_name(0)}")
            torch.backends.cudnn.benchmark = True
            torch.backends.cuda.matmul.allow_tf32 = True
            print(f"  CuDNN Benchmark: ENABLED")
            print(f"  TF32 Math: ENABLED")
        print(f"  Batch Size: {self.batch_size}")
        print(f"  Network Architecture: {self.config.hidden_sizes}")
        print(f"  Memory Capacity: {self.config.memory_size}")

    def act(
        self,
        state: np.ndarray,
        training: bool = True
    ) -> int:
        """
        Select an action using epsilon-greedy policy.
        
        Args:
            state: Current state observation (state_dim,)
            training: Whether in training mode (affects epsilon usage)
            
        Returns:
            Selected action index (0 to action_dim-1)
        """
        # Exploration: Random action with probability epsilon
        if training and np.random.rand() <= self.epsilon:
            return random.randrange(self.action_dim)
        
        # Exploitation: Select best action according to Q-network
        state_tensor = torch.FloatTensor(state).unsqueeze(0).to(self.device)
        with torch.no_grad():
            q_values = self.brain(state_tensor)
        
        # Return action with highest Q-value
        return int(q_values.argmax().item())

    def remember(
        self,
        state: np.ndarray,
        action: int,
        reward: float,
        next_state: np.ndarray,
        done: bool
    ) -> None:
        """
        Store an experience in the replay buffer.
        
        Args:
            state: Current state
            action: Action taken
            reward: Reward received
            next_state: Next state after action
            done: Whether episode terminated
        """
        self.memory.save(state, action, reward, next_state, done)

    def replay(self) -> Optional[float]:
        """
        Perform one learning step using experience replay.
        
        Samples a batch of experiences and updates the Q-network using
        Double DQN algorithm to prevent overestimation.
        
        Returns:
            Training loss value, or None if insufficient experiences
        """
        # Check if we have enough experiences
        if len(self.memory) < self.batch_size:
            return None
        
        # Sample batch of experiences
        states, actions, rewards, next_states, dones = self.memory.recall_batch(
            self.batch_size
        )
        
        # Current Q-values for taken actions
        current_q_values = self.brain(states).gather(1, actions).squeeze(1)
        
        # Double DQN: Use main network to select actions, target network to evaluate
        # This reduces overestimation bias
        with torch.no_grad():
            # Select best actions using main network
            best_actions = self.brain(next_states).argmax(1).unsqueeze(1)
            # Evaluate using target network
            next_q_values = self.target_brain(next_states).gather(
                1, best_actions
            ).squeeze(1)
            # Bellman equation: Q* = r + gamma * max Q(s', a')
            target_q_values = (
                rewards.squeeze(1) +
                (1 - dones.squeeze(1)) * self.gamma * next_q_values
            )
        
        # Compute loss and update network
        loss = self.loss_function(current_q_values, target_q_values.detach())
        
        self.optimizer.zero_grad()
        loss.backward()
        # Gradient clipping for stability
        torch.nn.utils.clip_grad_norm_(self.brain.parameters(), max_norm=1.0)
        self.optimizer.step()
        
        # Soft update target network
        self.soft_update()
        
        # Decay epsilon (reduce exploration over time)
        if self.epsilon > self.epsilon_min:
            self.epsilon = max(
                self.epsilon_min,
                self.epsilon * self.epsilon_decay
            )
        
        self.training_steps += 1
        return loss.item()

    def soft_update(self) -> None:
        """
        Soft update target network using polyak averaging.
        
        Gradually blends main network weights into target network.
        Formula: θ_target = τ * θ_main + (1 - τ) * θ_target
        
        This creates a stable but slowly-moving target for learning,
        improving training stability compared to hard updates.
        """
        for target_param, main_param in zip(
            self.target_brain.parameters(),
            self.brain.parameters()
        ):
            target_param.data.copy_(
                self.tau * main_param.data + (1.0 - self.tau) * target_param.data
            )
    
    def save(self, filepath: str) -> None:
        """
        Save the agent's state to a file.
        
        Saves the main network, target network, optimizer state,
        and training hyperparameters.
        
        Args:
            filepath: Path to save the model (should end with .pth)
            
        Example:
            >>> agent.save("checkpoints/agent_ep100.pth")
        """
        filepath = Path(filepath)
        filepath.parent.mkdir(parents=True, exist_ok=True)
        
        checkpoint = {
            'brain_state_dict': self.brain.state_dict(),
            'target_brain_state_dict': self.target_brain.state_dict(),
            'optimizer_state_dict': self.optimizer.state_dict(),
            'epsilon': self.epsilon,
            'training_steps': self.training_steps,
            'state_dim': self.state_dim,
            'action_dim': self.action_dim,
            'gamma': self.gamma,
            'epsilon_decay': self.epsilon_decay,
            'epsilon_min': self.epsilon_min,
            'batch_size': self.batch_size,
            'learning_rate': self.learning_rate,
            'tau': self.tau
        }
        
        torch.save(checkpoint, filepath)
        print(f"✓ Agent saved to {filepath}")
    
    def load(self, filepath: str, strict: bool = True) -> None:
        """
        Load the agent's state from a file.
        
        Args:
            filepath: Path to the checkpoint file
            strict: Whether to strictly enforce that the keys match
            
        Raises:
            FileNotFoundError: If checkpoint file doesn't exist
            RuntimeError: If checkpoint format is invalid
            
        Example:
            >>> agent.load("checkpoints/agent_ep100.pth")
        """
        filepath = Path(filepath)
        
        if not filepath.exists():
            raise FileNotFoundError(f"Checkpoint not found: {filepath}")
        
        try:
            checkpoint = torch.load(filepath, map_location=self.device)
            
            # Load network states
            self.brain.load_state_dict(
                checkpoint['brain_state_dict'],
                strict=strict
            )
            self.target_brain.load_state_dict(
                checkpoint['target_brain_state_dict'],
                strict=strict
            )
            
            # Load optimizer state (if available)
            if 'optimizer_state_dict' in checkpoint:
                self.optimizer.load_state_dict(checkpoint['optimizer_state_dict'])
            
            # Load training state
            if 'epsilon' in checkpoint:
                self.epsilon = checkpoint['epsilon']
            if 'training_steps' in checkpoint:
                self.training_steps = checkpoint['training_steps']
            
            print(f"✓ Agent loaded from {filepath}")
            if 'training_steps' in checkpoint:
                print(f"  Training steps: {self.training_steps}")
                print(f"  Epsilon: {self.epsilon:.4f}")
                
        except Exception as e:
            raise RuntimeError(f"Failed to load checkpoint: {e}") from e
    
    def get_state_dict(self) -> Dict:
        """
        Get the current agent state as a dictionary.
        
        Returns:
            Dictionary containing all agent state information
        """
        return {
            'brain_state_dict': self.brain.state_dict(),
            'target_brain_state_dict': self.target_brain.state_dict(),
            'optimizer_state_dict': self.optimizer.state_dict(),
            'epsilon': self.epsilon,
            'training_steps': self.training_steps,
            'state_dim': self.state_dim,
            'action_dim': self.action_dim,
            'gamma': self.gamma,
            'epsilon_decay': self.epsilon_decay,
            'epsilon_min': self.epsilon_min,
            'batch_size': self.batch_size,
            'learning_rate': self.learning_rate,
            'tau': self.tau
        }


# Code Style Guide

This document defines the coding standards and best practices for the DRL Web Vulnerability Scanner project.

## Table of Contents

1. [General Principles](#general-principles)
2. [Python Style](#python-style)
3. [Documentation](#documentation)
4. [Type Hints](#type-hints)
5. [Error Handling](#error-handling)
6. [Code Organization](#code-organization)
7. [Naming Conventions](#naming-conventions)
8. [Examples](#examples)

## General Principles

### 1. Readability First
- Code should be self-documenting through clear naming
- Prefer explicit over implicit
- Break complex logic into smaller, named functions
- Use meaningful variable names

### 2. Maintainability
- DRY (Don't Repeat Yourself) - avoid code duplication
- Single Responsibility Principle - each function/class has one purpose
- Keep functions small and focused (< 50 lines when possible)

### 3. Flexibility
- Use configuration files instead of hardcoded values
- Support multiple modes/options via parameters
- Design for extension, not just current needs

## Python Style

### PEP 8 Compliance
- Follow PEP 8 style guide
- Use 4 spaces for indentation (no tabs)
- Maximum line length: 100 characters (soft limit)
- Use blank lines to separate logical sections

### Imports
```python
# Standard library imports
import os
import sys
from typing import List, Dict, Optional
from pathlib import Path

# Third-party imports
import torch
import numpy as np
import requests

# Local application imports
from agent.dqn_agent import DQNAgent
from config import get_config
```

### Code Formatting
```python
# Good: Clear, readable function
def calculate_reward(
    vulnerability_found: bool,
    phase: int,
    current_phase: int,
    base_reward: float = -1.0
) -> float:
    """
    Calculate reward based on action outcome.
    
    Args:
        vulnerability_found: Whether a vulnerability was detected
        phase: Phase of the action taken
        current_phase: Current kill chain phase
        base_reward: Base reward per step
        
    Returns:
        Calculated reward value
    """
    reward = base_reward
    
    if vulnerability_found:
        reward += 100.0
    
    if phase == current_phase:
        reward += 10.0
    
    return reward
```

## Documentation

### Docstrings
All public functions, classes, and modules should have docstrings.

**Module-level docstrings:**
```python
"""
Module Name
===========

Brief description of what this module does.

Detailed description if needed.

Author: Your Name
Date: 2025-01-XX
"""
```

**Class docstrings:**
```python
class DQNAgent:
    """
    Deep Q-Network Agent for web security testing.
    
    This agent uses a DQN to learn optimal actions for discovering
    web vulnerabilities through reinforcement learning.
    
    Attributes:
        state_dim: Dimension of the state space
        action_dim: Dimension of the action space
        epsilon: Exploration rate (0-1)
    """
```

**Function docstrings:**
```python
def train(
    episodes: int,
    target_url: str,
    checkpoint_dir: Optional[str] = None
) -> Dict[str, List[float]]:
    """
    Train the DQN agent on a target application.
    
    Args:
        episodes: Number of training episodes
        target_url: URL of the target application
        checkpoint_dir: Directory to save checkpoints (default: checkpoints/)
        
    Returns:
        Dictionary containing training metrics:
        - 'rewards': List of episode rewards
        - 'losses': List of training losses
        - 'vulnerabilities_found': List of vulnerabilities per episode
        
    Raises:
        ConnectionError: If target URL is unreachable
        ValueError: If episodes < 1
        
    Example:
        >>> metrics = train(episodes=100, target_url="http://localhost:5002")
        >>> print(f"Average reward: {np.mean(metrics['rewards'])}")
    """
```

### Comments
- Use comments to explain "why", not "what"
- Avoid obvious comments
- Explain complex algorithms or non-obvious logic
- Use TODO/FIXME only for temporary notes (remove before merge)

```python
# Good: Explains why
# Use epsilon-greedy to balance exploration vs exploitation
# We decay epsilon to gradually shift from exploration to exploitation
if random.random() < self.epsilon:
    action = random.randint(0, self.action_dim - 1)

# Bad: States the obvious
# Increment i by 1
i += 1
```

## Type Hints

Always use type hints for function parameters and return values.

```python
from typing import List, Dict, Optional, Tuple, Union

def process_vulnerabilities(
    findings: List[Dict[str, str]],
    severity_filter: Optional[str] = None,
    max_results: int = 100
) -> Tuple[List[Dict[str, str]], int]:
    """
    Process and filter vulnerability findings.
    
    Returns:
        Tuple of (filtered_findings, total_count)
    """
    # Implementation
    pass
```

### Common Types
```python
# Collections
from typing import List, Dict, Set, Tuple

# Optional values
from typing import Optional

# Union types
from typing import Union

# Callable
from typing import Callable

# Path objects
from pathlib import Path
```

## Error Handling

### Use Exceptions Appropriately
```python
def load_model(model_path: Path) -> torch.nn.Module:
    """
    Load a trained model from file.
    
    Raises:
        FileNotFoundError: If model file doesn't exist
        ValueError: If model file is corrupted
    """
    if not model_path.exists():
        raise FileNotFoundError(f"Model file not found: {model_path}")
    
    try:
        model = torch.load(model_path, map_location='cpu')
        return model
    except Exception as e:
        raise ValueError(f"Failed to load model: {e}") from e
```

### Specific Exception Types
- Use specific exceptions, not bare `except:`
- Create custom exceptions for domain-specific errors
- Always chain exceptions with `from e`

```python
# Custom exceptions
class ConfigurationError(Exception):
    """Raised when configuration is invalid."""
    pass

class ScanError(Exception):
    """Raised when scan operation fails."""
    pass

# Usage
try:
    config = load_config()
except FileNotFoundError as e:
    raise ConfigurationError(f"Config file not found: {e}") from e
```

## Code Organization

### File Structure
```
module_name.py
├── Imports (standard, third-party, local)
├── Constants
├── Custom Exceptions
├── Classes
│   └── Methods (public first, then private)
├── Functions
└── Main execution (if script)
```

### Class Organization
```python
class WebSecurityGym:
    """Class docstring."""
    
    # Class constants
    DEFAULT_TIMEOUT = 10
    MAX_RETRIES = 3
    
    # Class variables (if any)
    
    def __init__(self, ...):
        """Initialize instance."""
        # Instance variables
        pass
    
    # Public methods first
    def reset(self, ...) -> np.ndarray:
        """Public method."""
        pass
    
    def step(self, ...) -> Tuple:
        """Public method."""
        pass
    
    # Private methods (prefixed with _)
    def _setup_session(self, ...):
        """Private helper method."""
        pass
```

## Naming Conventions

### Variables and Functions
- Use `snake_case` for functions and variables
- Use descriptive names
- Boolean variables should be questions or start with `is_`, `has_`, `should_`

```python
# Good
vulnerability_found = True
is_authenticated = False
has_waf_protection = True
should_save_checkpoint = True

# Bad
found = True
auth = False
waf = True
save = True
```

### Classes
- Use `PascalCase` for classes
- Use nouns or noun phrases

```python
class VulnerabilityScanner:
    pass

class PayloadManager:
    pass
```

### Constants
- Use `UPPER_SNAKE_CASE` for module-level constants

```python
MAX_EPISODES = 10000
DEFAULT_TIMEOUT = 10
CHECKPOINT_FREQUENCY = 10
```

### Private Methods/Variables
- Prefix with single underscore `_` for internal use

```python
class DQNAgent:
    def _calculate_q_values(self, state):
        """Private method."""
        pass
    
    def _update_target_network(self):
        """Private method."""
        pass
```

## Examples

### Good Code Example
```python
"""
DQN Agent Implementation
========================

Deep Q-Network agent for web security testing.
"""

from typing import Tuple, List, Optional
import torch
import numpy as np

from config import AgentConfig


class DQNAgent:
    """
    Deep Q-Network Agent.
    
    Implements a DQN with experience replay and target networks
    for learning optimal security testing actions.
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
        self.config = config or AgentConfig()
        self.state_dim = state_dim
        self.action_dim = action_dim
        self.epsilon = self.config.epsilon_start
        
        # Initialize neural network
        self.q_network = self._build_network()
        self.target_network = self._build_network()
        self._update_target_network()
        
    def act(
        self,
        state: np.ndarray,
        training: bool = True
    ) -> int:
        """
        Select an action using epsilon-greedy policy.
        
        Args:
            state: Current state observation
            training: Whether in training mode (affects epsilon)
            
        Returns:
            Selected action index
        """
        if training and np.random.random() < self.epsilon:
            return np.random.randint(self.action_dim)
        
        with torch.no_grad():
            state_tensor = torch.FloatTensor(state).unsqueeze(0)
            q_values = self.q_network(state_tensor)
            return q_values.argmax().item()
    
    def _build_network(self) -> torch.nn.Module:
        """Build the Q-network architecture."""
        # Implementation
        pass
    
    def _update_target_network(self):
        """Copy weights from main network to target network."""
        self.target_network.load_state_dict(self.q_network.state_dict())
```

### Configuration Usage
```python
from config import get_config, TrainingConfig

# Use global config
config = get_config()
episodes = config.training.max_episodes

# Or create custom config
custom_training = TrainingConfig(
    max_episodes=5000,
    checkpoint_frequency=5
)
```

## Tools

### Linting
- Use `flake8` for style checking
- Use `mypy` for type checking
- Use `black` for code formatting (optional, but consistent)

### Pre-commit Checks
```bash
# Check style
flake8 --max-line-length=100 .

# Check types
mypy .

# Format code (if using black)
black .
```

## Additional Resources

- [PEP 8 Style Guide](https://pep8.org/)
- [Google Python Style Guide](https://google.github.io/styleguide/pyguide.html)
- [Type Hints Documentation](https://docs.python.org/3/library/typing.html)
- [Python Docstring Conventions](https://www.python.org/dev/peps/pep-0257/)

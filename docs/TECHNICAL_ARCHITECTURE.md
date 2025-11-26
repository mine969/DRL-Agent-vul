# Technical Architecture

## System Overview

The DRL Web Security Agent uses a **Deep Q-Network (DQN)** with **Phase-Based Reward Shaping** to learn autonomous web vulnerability discovery through a Kill Chain approach.

## Core Components

### 1. Environment (`env/web_sec_env.py`)

**Gymnasium-based environment** simulating a web browser interacting with vulnerable applications.

**State Space (11 dimensions):**

- Current page ID
- HTTP status code
- Vulnerability detected flag
- Sensitive data flag
- WAF triggered flag
- Rate limit flag
- Authentication status
- Response time
- Content variance
- Input count
- Business context

**Action Space (100 discrete actions):**

- Phase 1: Reconnaissance (0-29)
- Phase 2: Discovery (30-59)
- Phase 3: Exploitation (60-89)
- Phase 4: Post-Exploitation (90-99)

**Reward Function:**

- Base penalty: -1 per step
- Vulnerability found: +100
- Phase bonus: +10 (correct phase)
- Phase completion: +20
- Phase skip penalty: -5
- WAF trigger: -10
- Rate limit: -20

### 2. Agent (`agent/dqn_agent.py`)

**Neural Network Architecture:**

```
Input (11) → FC1 (8192) → ReLU → FC2 (8192) → ReLU → FC3 (100)
```

**Hyperparameters:**

- Learning rate: 0.0001
- Gamma (discount): 0.99
- Epsilon (exploration): 1.0 → 0.01
- Epsilon decay: 0.995
- Batch size: 4096
- Memory size: 100,000

**Optimization:**

- Optimizer: Adam
- Loss: MSE (Mean Squared Error)
- TF32 Math: Enabled
- GPU: CUDA with cuDNN benchmark

### 3. Phase-Based Reward Shaping

**Algorithm:**

```python
def _validate_phase_action(action_id):
    # Determine action phase
    phase = action_id // 30 if action_id < 90 else 3

    # Check if unlocked
    if not phase_unlocked[phase]:
        return -5.0  # Penalty

    # Reward correct sequencing
    if phase == current_phase:
        bonus = 10.0
        progress[phase] += 1

        # Unlock next phase after 5 actions
        if progress[phase] >= 5:
            phase_unlocked[phase + 1] = True
            bonus += 20.0

        return bonus

    return 0.0
```

**Benefits:**

- Guides exploration through logical attack sequence
- Prevents random action selection
- Accelerates convergence
- Mimics real-world pentesting workflow

### 4. Training Loop (`train_multi_target.py`)

**Curriculum Learning:**

- Rotates through 6 target applications
- Each episode: 100 steps
- Checkpoint every 10 episodes

**Experience Replay:**

- Store transitions: (state, action, reward, next_state, done)
- Sample random batches for training
- Break correlation between consecutive samples

**Target Network:**

- Separate network for stable Q-value estimation
- Updated periodically to reduce oscillation

### 5. Transfer Learning (`ensemble_transfer_learning.py`)

**Smart Weight Transfer:**

- Old architecture: 52 actions
- New architecture: 100 actions
- Hidden layers: Fully transferred
- Output layer: Partially transferred (first 52 actions)
- New actions: Randomly initialized

## Performance Optimizations

### GPU Acceleration

**MAX Settings:**

- 8192 neurons per layer
- 4096 batch size
- TF32 tensor cores
- cuDNN benchmark mode

**Expected Speedup:** 35-40% vs standard settings

### Memory Management

- Replay buffer: Circular queue (100K transitions)
- Checkpoint compression: PyTorch state_dict
- Gradient clipping: Prevents exploding gradients

## Deployment Architecture

### Autonomous Scanning

```
User Input → Agent → Environment → Target Website
     ↑                                    ↓
     └──────── Vulnerability Report ──────┘
```

### GUI Mode

```
User → GUI → Agent → Environment → Target
  ↑                                    ↓
  └────── Real-time Visualization ─────┘
```

## Scalability

- **Horizontal:** Multiple agents on different targets
- **Vertical:** Larger neural networks (16K+ neurons)
- **Distributed:** Multi-GPU training (future)

## Security Considerations

- **Sandboxed environment:** Isolated from production
- **Rate limiting:** Respects target server limits
- **Ethical use:** Educational purposes only
- **Logging:** All actions recorded for audit

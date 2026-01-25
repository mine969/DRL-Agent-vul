# Checkpoint System

## Overview

The checkpoint system saves the agent's neural network weights every 10 episodes, enabling training resumption and model evaluation.

## Checkpoint Format

**Naming Convention:**

```
multi_target_8k_ep{episode}.pth
```

**Examples:**

- `multi_target_8k_ep10.pth` - Episode 10
- `multi_target_8k_ep1000.pth` - Episode 1000
- `multi_target_8k_ep2000.pth` - Episode 2000 (final)

**Architecture Identifier:**

- `8k` = 8192 neurons (MAX GPU mode)
- `4k` = 4096 neurons (Ultra mode)
- `2k` = 2048 neurons (Standard mode)

## File Structure

```python
checkpoint = {
    'fc1.weight': Tensor(8192, 11),
    'fc1.bias': Tensor(8192),
    'fc2.weight': Tensor(8192, 8192),
    'fc2.bias': Tensor(8192),
    'fc3.weight': Tensor(100, 8192),
    'fc3.bias': Tensor(100)
}
```

**Size:** ~8.5 MB per checkpoint

## Saving Checkpoints

### Automatic Saving

Checkpoints are saved automatically:

- Every 10 episodes during training
- On Ctrl+C (keyboard interrupt)
- On training completion

### Manual Saving

```python
from agent.dqn_agent import DQNAgent

agent = DQNAgent(state_dim=11, action_dim=100)
torch.save(agent.brain.state_dict(), 'checkpoints/manual_save.pth')
```

## Loading Checkpoints

### Resume Training

```bash
python train_multi_target.py --episodes 2000 --resume 1000
```

This loads `checkpoints/multi_target_8k_ep1000.pth` and continues from episode 1001.

### Load for Deployment

```python
from agent.dqn_agent import DQNAgent
import torch

agent = DQNAgent(state_dim=11, action_dim=100)
agent.brain.load_state_dict(
    torch.load('checkpoints/multi_target_8k_ep2000.pth')
)
agent.brain.eval()  # Set to evaluation mode
```

## Checkpoint Management

### Storage Requirements

**For 2000 episodes:**

- Checkpoints: 200 files
- Size per file: ~8.5 MB
- **Total:** ~1.7 GB

### Cleanup Strategy

**Keep:**

- Every 100th checkpoint (ep100, ep200, ...)
- Best performing checkpoint
- Final checkpoint

**Delete:**

- Intermediate checkpoints (ep10, ep20, ..., ep90)

**Script:**

```bash
# Keep only every 100th checkpoint
for i in {10..90..10}; do
    rm checkpoints/multi_target_8k_ep${i}.pth
done
```

## Transfer Learning

### From Old Architecture (52 actions)

```python
# Load old checkpoint
old_state = torch.load('dqn_checkpoint_ep1000.pth')

# Create new agent (100 actions)
new_agent = DQNAgent(state_dim=11, action_dim=100)
new_state = new_agent.brain.state_dict()

# Transfer compatible layers
for key in old_state.keys():
    if 'fc3' not in key:  # Hidden layers
        new_state[key] = old_state[key]
    else:  # Output layer (partial transfer)
        if 'weight' in key:
            new_state[key][:52, :] = old_state[key]
        elif 'bias' in key:
            new_state[key][:52] = old_state[key]

# Load transferred weights
new_agent.brain.load_state_dict(new_state)
```

### Ensemble Learning

Combine multiple checkpoints:

```python
# Load checkpoints
state1 = torch.load('checkpoint1.pth')
state2 = torch.load('checkpoint2.pth')

# Average weights
ensemble_state = {}
for key in state1.keys():
    ensemble_state[key] = (state1[key] + state2[key]) / 2

# Save ensemble
torch.save(ensemble_state, 'ensemble_checkpoint.pth')
```

## Checkpoint Evaluation

### Performance Metrics

```python
from env.web_sec_env import WebSecurityGym

env = WebSecurityGym(target_url="http://localhost:5001")
agent.brain.eval()

total_reward = 0
for episode in range(100):
    state, _ = env.reset()
    done = False

    while not done:
        action = agent.act(state, training=False)  # Greedy
        state, reward, done, truncated, _ = env.step(action)
        total_reward += reward
        done = done or truncated

avg_reward = total_reward / 100
print(f"Average Reward: {avg_reward:.2f}")
```

### Vulnerability Discovery Rate

```python
vulns_found = 0
episodes = 100

for ep in range(episodes):
    state, _ = env.reset()
    done = False

    while not done:
        action = agent.act(state, training=False)
        state, reward, done, truncated, info = env.step(action)

        if reward > 50:  # Vulnerability found
            vulns_found += 1
            break

        done = done or truncated

discovery_rate = vulns_found / episodes
print(f"Discovery Rate: {discovery_rate:.1%}")
```

## Best Practices

### 1. Version Control

- Tag important checkpoints in git
- Document performance metrics
- Keep training logs

### 2. Backup Strategy

- Copy checkpoints to cloud storage
- Keep local and remote backups
- Test restoration periodically

### 3. Naming Convention

- Use descriptive names
- Include architecture info
- Add date/time for experiments

### 4. Monitoring

- Track checkpoint sizes
- Monitor disk space
- Alert on save failures

## Troubleshooting

### Checkpoint Not Found

```python
import os

checkpoint_path = 'checkpoints/multi_target_8k_ep1000.pth'
if not os.path.exists(checkpoint_path):
    print(f"Checkpoint not found: {checkpoint_path}")
    # List available checkpoints
    checkpoints = sorted([f for f in os.listdir('checkpoints/') if f.endswith('.pth')])
    print(f"Available: {checkpoints}")
```

### Dimension Mismatch

```python
try:
    agent.brain.load_state_dict(torch.load(checkpoint_path))
except RuntimeError as e:
    print(f"Dimension mismatch: {e}")
    print("Use transfer learning script for architecture changes")
```

### Corrupted Checkpoint

```python
try:
    state_dict = torch.load(checkpoint_path)
    # Verify all keys exist
    required_keys = ['fc1.weight', 'fc1.bias', 'fc2.weight', 'fc2.bias', 'fc3.weight', 'fc3.bias']
    missing = [k for k in required_keys if k not in state_dict]

    if missing:
        print(f"Corrupted checkpoint - missing keys: {missing}")
except Exception as e:
    print(f"Failed to load checkpoint: {e}")
```

## Future Enhancements

- [ ] Automatic checkpoint compression
- [ ] Cloud backup integration
- [ ] Checkpoint diff visualization
- [ ] Performance-based auto-selection
- [ ] Distributed checkpoint storage

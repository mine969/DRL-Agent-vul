# Extended D3QN — Improved Algorithms

This file documents the algorithms currently implemented in `agent/improved_dqn_agent.py`. The agent implements five of the six core Rainbow DQN extensions (Distributional RL is **not** implemented), giving it an **Extended Double Dueling Deep Q-Network (Extended D3QN)** architecture.

## Implemented Techniques

## 1) Prioritized Experience Replay (PER)

- Stores transitions with priorities based on TD error.
- Samples high-value transitions more often.
- Uses importance weights to reduce sampling bias.

## 2) Noisy Linear Exploration

- Uses learnable noise in network layers.
- Replaces plain epsilon-greedy action randomness in core path.
- Supports noise reset during training steps.

## 3) Dueling Network Heads

- Splits value and advantage streams.
- Combines them into Q-values via dueling formulation.

## 4) Double DQN Targeting

- Main network selects next action.
- Target network evaluates selected action.
- Reduces overestimation bias.

## 5) Optional N-Step Return Buffer

- Agent supports n-step return accumulation.
- Current training script defaults to `n_step=1` for stability.

## Current Training Configuration (from scripts)

`train_mock_targets.py` initializes:

```python
ImprovedDQNAgent(
    state_dim=15,
    action_dim=50,
    use_prioritized_replay=True,
    use_noisy_networks=True,
    n_step=1,
)
```

## What This Is (And What It Isn't)

- The active implementation combines: **PER + Noisy Networks + Dueling Network + Double DQN + (optional) n-step returns**.
- This corresponds to **5 out of 6** core Rainbow DQN techniques. The missing piece is **Distributional RL (C51/Categorical DQN)**.
- For paper and documentation purposes, this architecture is correctly called an **Extended D3QN** or a **Partial Rainbow DQN implementation**.

## Why This Matters for the Scanner

- Better sample efficiency during training on mock targets.
- More stable policy behavior than a basic DQN baseline.
- Cleaner checkpointing and resume flow for long-running training.

# Agent — Extended D3QN Web Security Agent

The active agent is `improved_dqn_agent.py`. It implements **Extended D3QN**
(Double DQN + Dueling network + Prioritized Experience Replay + Noisy Networks).

---

## Files

| File | Status | Purpose |
|---|---|---|
| `improved_dqn_agent.py` | **Active** | Extended D3QN — used by all training & scanning scripts |
| `payload_manager.py` | Active | 200+ attack payloads for the action space |
| `dqn_agent.py` | Archived → `legacy_archive/` | Old plain DQN with epsilon-greedy; no longer used |

---

## Classes inside `improved_dqn_agent.py`

```
PrioritizedReplayBuffer
    Circular buffer of (state, action, reward, next_state, done) tuples.
    Each experience has a priority = |TD error| + ε.
    Sampling probability ∝ priority^α — high-error experiences are
    replayed more often so the network focuses on what it got wrong.

NoisyLinear
    A drop-in replacement for nn.Linear that adds learned noise to both
    weights and biases. The noise parameters are trained by gradient
    descent alongside the Q-values, so the network learns how much to
    explore in each state rather than following a fixed epsilon schedule.

DuelingNoisyDQN
    The neural network backbone.
    Input: 15-dim state vector
    Shared layers → split into two heads:
        Value head  V(s)      — how good is this state overall?
        Advantage head A(s,a) — how much better is action a vs average?
    Combined: Q(s,a) = V(s) + (A(s,a) − mean_a A(s,a))
    Output: Q-value for each of the 50 (or 150) actions

ImprovedDQNAgent
    Top-level controller. Owns the two networks (q_network, target_network),
    the replay buffer, and the optimizer.
    Key methods: act(), remember(), replay(), soft_update(), save(), load()
```

---

## How one training step works

```
env.reset()  →  15-dim state vector s
                        │
              agent.act(s, training=True)
                        │  NoisyLinear layers add noise automatically
                        │  DuelingNoisyDQN → Q(s, a) for all actions
                        │  pick a = argmax Q(s, a)
                        ▼
              env.step(a)  →  (s', reward, done)
                        │
              agent.remember(s, a, reward, s', done)
                        │  stored in PrioritizedReplayBuffer
                        │  assigned max_priority so it gets sampled soon
                        ▼
              agent.replay()
                        │
                        │  1. Sample batch weighted by priority
                        │  2. Double-DQN target:
                        │       a* = argmax_a  Q_main(s', a)   ← main picks action
                        │       y  = r + γ·Q_target(s', a*)   ← target scores it
                        │     (two networks → removes overestimation bias)
                        │  3. Loss = Σ w_i · (Q_main(s,a) − y)²
                        │     w_i = importance-sampling weight from PER
                        │  4. Backprop, clip gradients
                        │  5. Update PER priorities: p_i = |TD error| + ε
                        │  6. soft_update():
                        │       θ_target ← 0.01·θ_main + 0.99·θ_target
                        ▼
              next step ...
```

---

## Quick usage

```python
from agent.improved_dqn_agent import ImprovedDQNAgent

# Create agent (PER is required)
agent = ImprovedDQNAgent(
    state_dim=15,       # matches WebSecurityGym output
    action_dim=50,      # 50 in mock-target mode, 150 in full mode
    use_prioritized_replay=True,
    use_noisy_networks=True,
    n_step=1,           # 1 = standard single-step TD (used in all published runs)
)

# Training loop (simplified)
state, _ = env.reset()
for _ in range(max_steps):
    action = agent.act(state, training=True)
    next_state, reward, done, _, _ = env.step(action)
    agent.remember(state, action, reward, next_state, done)
    agent.replay()
    state = next_state
    if done:
        break

# Save / load
agent.save("checkpoints/my_run_ep1000.pth")
agent.load("checkpoints/my_run_ep1000.pth")

# Inference (no noise)
action = agent.act(state, training=False)
```

---

## Parameter reference

| Parameter | Default | What it controls |
|---|---|---|
| `state_dim` | `15` | Observation vector size from `WebSecurityGym` |
| `action_dim` | `50` | 50 actions (mock mode) or 150 (full mode) |
| `use_prioritized_replay` | `True` | Must stay `True` — PER is required |
| `use_noisy_networks` | `True` | Enables NoisyLinear exploration layers |
| `n_step` | `1` | Multi-step return horizon; 1 = standard TD |
| `seed` | `None` | Seeds replay buffer RNG for reproducibility |

---

## Related files

- [`../train_mock_targets.py`](../train_mock_targets.py) — standard training script
- [`../env/web_sec_env.py`](../env/web_sec_env.py) — Gymnasium environment (state + reward)
- [`../docs/IMPROVED_ALGORITHMS.md`](../docs/IMPROVED_ALGORITHMS.md) — deep dive into each algorithm
- [`../docs/AI_CONCEPTS.md`](../docs/AI_CONCEPTS.md) — RL concepts mapped to this repo
- [`../docs/TRAINING_PROCESS.md`](../docs/TRAINING_PROCESS.md) — step-by-step training guide

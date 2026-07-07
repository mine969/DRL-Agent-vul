# Extended D3QN — Algorithm Deep Dive

The agent in `agent/improved_dqn_agent.py` is an **Extended D3QN**:
Double DQN + Dueling network + Prioritized Experience Replay + Noisy Networks.

This document explains what each technique does, why it was added, and
how it maps to the actual code.

---

## 1. Prioritized Experience Replay (PER)

**The problem it solves:**
Plain experience replay samples transitions uniformly at random.
Most transitions are routine (agent wanders, gets a small negative reward).
The rare transitions where the agent discovers a vulnerability are the
most informative — but they get sampled at the same rate as everything else.

**What PER does:**
Assigns a priority `p = |TD error| + e` to each stored transition.
Sampling probability is proportional to `p^alpha`.
Transitions the network is most surprised by (large TD error) are
replayed more often, so the network focuses on what it got wrong.

**Bias correction:**
More frequent sampling of high-error transitions biases the gradient.
Importance-sampling weights `w = (1 / N*P(i))^beta` correct for this.
`beta` anneals from 0.4 to 1.0 over training.

**Where in code:** `PrioritizedReplayBuffer` class. Called via
`agent.memory.add(...)` and `agent.memory.sample(batch_size)`.

```python
# Priority update after each replay step (simplified)
td_errors = (current_q - target_q).abs().detach().cpu().numpy()
self.memory.update_priorities(indices, td_errors)
```

---

## 2. Noisy Networks for Exploration

**The problem it solves:**
Epsilon-greedy exploration picks a random action with probability epsilon,
regardless of the current state. It is state-blind — equally random
whether the agent is in a familiar situation or a completely new one.

**What Noisy Networks do:**
Replace standard `nn.Linear` layers with `NoisyLinear` layers that add
learnable Gaussian noise directly to the weights and biases:

```
y = (mu_w + sigma_w * eps_w) * x + (mu_b + sigma_b * eps_b)
```

`mu` (mean) and `sigma` (noise scale) are both trained by gradient descent.
The network learns how much to explore in each state and anneals
noise naturally as it becomes confident — no epsilon schedule needed.

**Where in code:** `NoisyLinear` class. Used inside `DuelingNoisyDQN`.
Noise is re-sampled each forward pass during training (`reset_noise()`),
and not reset during inference (`training=False` in `agent.act()`).

---

## 3. Dueling Network Architecture

**The problem it solves:**
In many states, the choice of action barely matters — the state itself
is simply good or bad. A plain DQN must learn a separate Q-value for
every (state, action) pair, even when the action is irrelevant.

**What Dueling does:**
Splits the network's final layers into two parallel heads:

```
Shared layers --> V(s)      (scalar: how good is this state?)
             --> A(s, a)    (vector: advantage of each action)

Q(s, a) = V(s) + (A(s, a) - mean_a A(s, a))
```

The mean subtraction keeps V and A identifiable
(otherwise the network could absorb all signal into either head).

**Benefit:** The value head `V(s)` is updated by every action taken,
not just the chosen one — faster learning of state quality.

**Where in code:** `DuelingNoisyDQN.forward()`. Look for `value` and
`advantage` streams being combined before returning Q-values.

---

## 4. Double DQN

**The problem it solves:**
Plain DQN computes the TD target using the target network for both
selecting and evaluating the best next action:

```
y = r + gamma * max_a Q_target(s', a)
```

`max_a` of noisy estimates is always an optimistic (biased high)
estimate. Over millions of updates this causes Q-values to inflate
and training to destabilise.

**What Double DQN does:**
Decouples the two roles across two different networks:

```
a* = argmax_a  Q_main(s', a)      <- main network selects the action
y  = r + gamma * Q_target(s', a*) <- target network scores that action
```

The two networks make different errors, so their combination mostly
cancels the overestimation.

**Where in code:** `ImprovedDQNAgent.replay()`.

```python
# Double DQN target
next_actions = self.q_network(next_states).argmax(1).unsqueeze(1)
next_q_values = self.target_network(next_states).gather(1, next_actions)
targets = rewards + (self.gamma ** self.n_step) * next_q_values * (1 - dones)
```

---

## 5. Soft Target Network Update (Polyak Averaging)

**The problem it solves:**
The target network provides the labels the main network trains toward.
If the target were updated every step, both networks would chase each other
in a feedback loop — unstable.

Plain DQN copies weights every N steps (hard update), which causes sudden
jumps in the target and oscillating loss curves.

**What soft update does:**
Each step, blend a small fraction `tau = 0.01` of the main network into
the target:

```
theta_target <- tau * theta_main + (1 - tau) * theta_target
```

The target moves smoothly and continuously rather than jumping.

**Where in code:** `ImprovedDQNAgent.soft_update()`, called at the end
of every `replay()` call.

---

## 6. N-Step Returns (optional, currently n=1)

**What it does:**
Instead of using a 1-step TD target `r + gamma*V(s')`, accumulate rewards
over n steps before bootstrapping:

```
y = r_t + gamma*r_{t+1} + gamma^2*r_{t+2} + ... + gamma^n * V(s_{t+n})
```

Larger n propagates reward signals faster but adds variance.

**Current setting:** `n_step=1` in all published training runs — standard
single-step TD. The infrastructure exists if you want to experiment with
`n_step=3`.

---

## Current Training Configuration

```python
ImprovedDQNAgent(
    state_dim=15,
    action_dim=50,
    use_prioritized_replay=True,   # PER — required
    use_noisy_networks=True,       # NoisyLinear exploration
    n_step=1,                      # standard TD
)
```

Run: `python train_mock_targets.py --episodes 1000`

---

## Why This Combination Works

Each technique targets a different weakness of plain DQN:

| Weakness of plain DQN | Fix applied |
|---|---|
| Wastes samples on boring transitions | PER — replay important ones more |
| Exploration is state-blind | Noisy Networks — learned per-state noise |
| Must learn Q for every (s,a) pair separately | Dueling — share value estimation across actions |
| Q-values inflate over training | Double DQN — decouple selection from scoring |
| Hard target copy causes training jumps | Soft update — smooth continuous target tracking |

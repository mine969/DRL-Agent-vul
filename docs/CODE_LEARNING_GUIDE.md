# 👨‍💻 Code Learning Guide: Under the Hood

This guide explains the actual code for beginners. We will look at the three most important files.

## 1. `agent/dqn_agent.py` (The Brain)

This file defines the **Agent**. It's where the learning happens.

### Key Class: `DQNAgent`

```python
class DQNAgent:
    def __init__(self, state_dim, action_dim):
        # ... setup ...
        self.memory = ReplayBuffer(...) # The Agent's memory
        self.q_network = QNetwork(...)  # The Neural Network
```

### Key Function: `act()`

This is how the agent decides what to do.

```python
def act(self, state):
    # Epsilon-Greedy Logic
    if random.random() <= self.epsilon:
        return random.randrange(self.action_dim) # EXPLORE: Do something random

    # EXPLOIT: Ask the Neural Network for the best move
    state_tensor = torch.FloatTensor(state)...
    q_values = self.q_network(state_tensor)
    return np.argmax(q_values) # Pick the action with highest score
```

---

## 2. `env/web_sec_env.py` (The World)

This file defines the **Environment**. It simulates the website interaction.

### Key Class: `OptimizedWebSecEnv`

It follows the standard Gym format: `reset()` and `step()`.

### Key Function: `step(action)`

This runs one "turn" of the game.

```python
def step(self, action):
    # 1. Execute the action (e.g., Click link, Inject SQL)
    response, reward = self.action_map[action]()

    # 2. Calculate new state (What do we see now?)
    self.last_response_time = ...
    self.content_variance = ...

    # 3. Return everything to the Agent
    return self._get_obs(), reward, done, ...
```

### Key Function: `_check_vulnerability()`

This calculates the score.

```python
def _check_vulnerability(self, response, ...):
    if "admin" in response.text:    # Did we hack it?
        return 100.0                # Big Reward!
    if "WAF Blocked" in response.text:
        return -10.0                # Punishment!
    return 0.0
```

---

## 3. `autonomous_scan.py` (The Body)

This script puts everything together to scan a real website.

### Key Class: `ReconAgent`

It maps out the website before attacking.

```python
def crawl(self):
    # Uses a Queue (deque) for Breadth-First Search
    queue = deque([base_url])
    while queue:
        url = queue.popleft()
        # Visit page, find links, add to queue...
```

### Key Function: `scan()`

The main loop.

1. **Recon**: Find all pages.
2. **Test**: For every page found...
   - Create a `WebSecEnv` for that page.
   - Let the `DQNAgent` play on that page for 30 steps.
   - If the Agent gets a high score (>50), report a bug!

---

## 4. `agent/payload_manager.py` (The Arsenal)

A simple helper to manage attack strings.

```python
class PayloadManager:
    def get_sqli(self, complexity):
        if complexity == "time":
            return "WAITFOR DELAY '0:0:5'" # Advanced Attack
        return "' OR 1=1--"                # Simple Attack
```

**Why?** Keeping payloads here makes the code cleaner and easier to update.

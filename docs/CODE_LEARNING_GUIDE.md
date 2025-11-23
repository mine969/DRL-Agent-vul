# 👨‍💻 Code Learning Guide: Under the Hood

This guide explains the actual code for beginners. We will look at the three most important files.

## 1. `agent/dqn_agent.py` (The Brain)

This file defines the **Agent**. It's where the learning happens.

### Key Class: `DQNAgent`

```python
class DQNAgent:
    def __init__(self, state_dim, action_dim):
        # ... setup ...
        self.memory = ExperienceMemory(...) # The Agent's memory
        self.brain = NeuralNetworkBrain(...)  # The Neural Network
```

### Key Function: `act()`

This is how the agent decides what to do.

```python
def act(self, state):
    # 1. Explore: Try something random?
    if np.random.rand() <= self.epsilon:
        return random.randrange(self.action_dim)

    # 2. Exploit: Use the Brain
    state_tensor = torch.FloatTensor(state)...
    predicted_rewards = self.brain(state_tensor)
    return int(np.argmax(predicted_rewards...)) # Pick the best move
```

---

## 2. `env/web_sec_env.py` (The World)

This file defines the **Environment**. It simulates the website interaction.

### Key Class: `WebSecurityGym`

It follows the standard Gym format: `reset()` and `step()`.

### Key Function: `step(action_id)`

This runs one "turn" of the game.

```python
def step(self, action_id):
    # 1. Perform the Action (e.g., Click link, Inject SQL)
    response, reward = self.action_book[action_id]()

    # 2. Analyze the Result (What do we see now?)
    self._analyze_response_content(response)

    # 3. Return everything to the Agent
    return self._get_observation(), reward, done, ...
```

### Key Function: `_calculate_reward()`

This calculates the score.

```python
def _calculate_reward(self, response, ...):
    if "admin" in response.text:    # Did we hack it?
        return 100.0                # Big Reward!
    if "WAF Blocked" in response.text:
        return -10.0                # Punishment!
    return 0.0
```

---

## 3. `autonomous_scan.py` (The Body)

This script puts everything together to scan a real website.

### Key Class: `WebsiteExplorer`

It maps out the website before attacking.

```python
def explore(self):
    # Uses a Queue (deque) for Breadth-First Search
    queue = deque([base_url])
    while queue:
        url = queue.popleft()
        # Visit page, find links, add to queue...
```

### Key Class: `SecurityAuditor`

The main scanner logic.

```python
def start_audit(self):
    # Phase 1: Reconnaissance
    discovered_urls = self.explorer.explore()

    # Phase 2: Attack
    for url in discovered_urls:
        # Let the AI Agent play on this page
        findings = self._audit_page(url)

    # Phase 3: Report
    self._generate_final_report(...)
```

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

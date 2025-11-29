# Penetration Testing Agent

Core Deep Q-Learning agent for web security penetration testing.

## 📁 Components

### `dqn_agent.py` (241 lines)

**Double DQN Agent** for web security testing

**Classes**:

- `ExperienceMemory` - Stores 10,000 attack experiences
- `NeuralNetworkBrain` - Dueling network architecture
- `DQNAgent` - Main agent controller

**Features**:

- Epsilon-greedy exploration
- Experience replay
- Soft target network updates
- Model save/load

### `payload_manager.py` (600+ lines)

**Attack Payloads & Techniques**

**Capabilities**:

- SQL Injection payloads
- XSS attack vectors
- IDOR exploitation
- CSRF token bypass
- Command injection
- File upload attacks
- Authentication bypass
- Session hijacking

## 🎯 Usage

### Training

```python
from agent.dqn_agent import DQNAgent
from env.web_sec_env import WebSecurityGym

env = WebSecurityGym("http://localhost:5002")
agent = DQNAgent(state_dim=20, action_dim=15)

# Train
for episode in range(1000):
    state = env.reset()
    # ... training loop
```

### Deployment

```python
# Load trained model
agent.load("dqn_web_sec_model.pth")

# Run security scan
state = env.reset()
action = agent.act(state, training=False)
```

## 📚 Related Files

- `../autonomous_scan.py` - Main security auditor
- `../scanner_gui.py` - GUI interface
- `../deploy_agent.py` - Deployment script
- `../train_multi_target.py` - Training script

## 🔗 See Also

- [Main README](../README.md)
- [Project Structure](../docs/PROJECT_STRUCTURE.md)
- [Technical Architecture](../docs/TECHNICAL_ARCHITECTURE.md)

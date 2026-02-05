# Architecture Overview

## System Architecture

The DRL Web Vulnerability Scanner uses a **Deep Q-Network (DQN)** architecture with a **Gymnasium-based environment** to learn optimal vulnerability discovery strategies through reinforcement learning.

## Component Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Application Layer                         │
├─────────────────────────────────────────────────────────────┤
│  scanner_gui.py  │  autonomous_scan.py  │  train_*.py       │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                      Agent Layer                             │
├─────────────────────────────────────────────────────────────┤
│  DQNAgent                                                   │
│  ├── NeuralNetworkBrain (Dueling DQN)                      │
│  ├── ExperienceMemory (Replay Buffer)                      │
│  └── Training Logic (Double DQN, Soft Updates)            │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                   Environment Layer                          │
├─────────────────────────────────────────────────────────────┤
│  WebSecurityGym (Gymnasium Environment)                    │
│  ├── State Space (15 dimensions)                           │
│  ├── Action Space (50 mock / 150 full)                     │
│  ├── Reward Function (Phase-based shaping)                 │
│  └── Action Execution (HTTP requests, payload injection)  │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                    Target Layer                              │
├─────────────────────────────────────────────────────────────┤
│  Mock Vulnerable Applications                               │
│  ├── E-Commerce (port 5002)                                │
│  ├── Social Media (port 5003)                              │
│  ├── Banking (port 5004)                                   │
│  ├── Blog (port 5005)                                      │
│  └── File Share (port 5006)                                │
└─────────────────────────────────────────────────────────────┘
```

## Configuration System

All configuration is centralized in `config.py`:

```python
from config import get_config

config = get_config()

# Agent configuration
agent_config = config.agent
learning_rate = agent_config.learning_rate
batch_size = agent_config.batch_size

# Training configuration
training_config = config.training
max_episodes = training_config.max_episodes

# Scan configuration
scan_config = config.scan
crawl_depth = scan_config.crawl_depth
```

## Data Flow

### Training Flow

1. **Initialize** → Environment resets, agent starts
2. **Observe** → Agent receives state (15-dim vector)
3. **Act** → Agent selects action (0-49 mock / 0-149 full)
4. **Execute** → Environment performs action (HTTP request)
5. **Reward** → Environment calculates reward
6. **Learn** → Agent stores experience and learns
7. **Repeat** → Until episode ends (50-100 steps)

### Scanning Flow

1. **Discovery** → Crawl and map target application
2. **Analysis** → Agent analyzes discovered endpoints
3. **Attack** → Agent selects and executes attacks
4. **Validation** → Verify vulnerabilities found
5. **Report** → Generate comprehensive report

## Neural Network Architecture

### Dueling DQN Structure

```
Input (15-dim state)
    ↓
Feature Layer
    ├── Linear(15 → 256) → ReLU
    └── Linear(256 → 128) → ReLU
    ↓
    ├── Value Stream → V(s)    [Scalar: How good is this state?]
    └── Advantage Stream → A(s,a) [Vector: How much better is each action?]
    ↓
    Combine: Q(s,a) = V(s) + (A(s,a) - mean(A(s)))
    ↓
Output (50/150-dim Q-values)
```

### Hyperparameters

```python
# Agent Configuration
learning_rate: 0.0001
gamma (discount): 0.99
epsilon_start: 1.0
epsilon_end: 0.01
epsilon_decay: 0.995
batch_size: 64 (configurable)
memory_size: 100000
tau (soft update): 0.01

# Training Configuration
max_episodes: 10000
max_steps_per_episode: 50
checkpoint_frequency: 50
```

## Action Space

Mock targets use a 50-action tuned subset; the full action book extends to 150 actions with advanced techniques.

### Phase 1: Reconnaissance (Actions 0-29)
- **Passive OSINT (0-19):** Whois, DNS, GitHub, Shodan, Wayback Machine
- **Active OSINT (20-29):** Port scanning, WAF detection, API discovery

### Phase 2: Discovery (Actions 30-59)
- **Authentication (30-39):** SQL Injection, Brute Force, JWT Attacks
- **Injection (40-49):** XSS, SSTI, Command Injection, LFI
- **Logic (50-59):** Mass Assignment, Rate Limit Bypass, IDOR

### Phase 3: Exploitation (Actions 60-89)
- **Advanced Injection (60-69):** Blind SQLi, RCE, Deserialization
- **Cloud/Infrastructure (70-79):** SSRF, Docker, Kubernetes
- **System Exploits (80-89):** Path Traversal, XXE, HTTP Smuggling

### Phase 4: Post-Exploitation (Actions 90-99)
- Database dumping, Token theft, Privilege escalation

## State Space

15-dimensional observation vector:

1. **Current Page ID** (0-1000) - Normalized
2. **HTTP Status Code** (200, 404, 500, etc.) - Normalized
3. **Vulnerability Detected** (0/1)
4. **Sensitive Data Seen** (0/1)
5. **WAF Triggered** (0/1)
6. **Rate Limited** (0/1)
7. **Authenticated** (0/1)
8. **Response Time** (seconds) - Normalized
9. **Content Variance** (0-1) - Page similarity
10. **Input Count** (number of forms/inputs) - Normalized
11. **Business Context** (0/1) - Admin/payment pages
12. **Steps Remaining** (0-1) - Episode progress
13. **Phase ID** (0-1) - Kill chain phase
14. **Vulnerability Coverage** (0-1) - Unique vulns found
15. **Endpoint Coverage** (0-1) - Visited/known ratio

## Reward Function

```python
# Base reward (per step)
reward = -0.01

# Vulnerability discovered
if vulnerability_found:
    reward += 1.0

# Phase-based bonuses
if action_phase == current_phase:
    reward += 0.1  # Correct phase
    phase_progress[phase] += 1
    
    if phase_completed:
        reward += 0.2  # Phase completion
        unlock_next_phase()

# Penalties
if wrong_phase:
    reward -= 0.05  # Phase skip penalty
    
if waf_triggered:
    reward -= 0.1  # WAF detection
    
if rate_limited:
    reward -= 0.1  # Rate limiting
```

## Configuration System

### Configuration Hierarchy

1. **Default Values** → Defined in `config.py`
2. **Environment Variables** → Override defaults
3. **Runtime Arguments** → CLI/GUI parameters
4. **Config Files** → Future: YAML/JSON support

### Usage Example

```python
from config import get_config, AgentConfig, TrainingConfig

# Use default configuration
config = get_config()
agent = DQNAgent(
    state_dim=config.agent.state_dim,
    action_dim=config.agent.action_dim,
    config=config.agent
)

# Custom configuration
custom_agent_config = AgentConfig(
    learning_rate=0.0005,
    batch_size=128,
    hidden_sizes=[512, 256, 128]
)
agent = DQNAgent(
    state_dim=11,
    action_dim=100,
    config=custom_agent_config
)
```

## Code Organization

### Module Structure

```
agent/
├── dqn_agent.py          # DQN Agent implementation
│   ├── ExperienceMemory  # Replay buffer
│   ├── NeuralNetworkBrain # Dueling DQN network
│   └── DQNAgent          # Main agent class
│
└── payload_manager.py    # Attack payloads (200+)

env/
├── web_sec_env.py        # Gymnasium environment
│   ├── WebSecurityGym    # Main environment class
│   └── Action execution  # HTTP requests, payloads
│
└── target_app_*.py       # Mock applications (5 files)

utils/
├── proxy_fetcher.py      # Proxy management
├── vulnerability_database.py  # Vuln descriptions
├── report_generator.py   # Report creation
├── target_hunter.py      # OSINT discovery
└── zero_day_hunter.py    # Fuzzing, CVE intelligence
```

## Design Patterns

### 1. Strategy Pattern
- **Payload Manager**: Different payload strategies per attack type
- **Scan Modes**: Different scanning strategies (auto, aggressive, osint)

### 2. Factory Pattern
- **Target Creation**: Factory for creating target environments
- **Report Generation**: Factory for different report formats, including captured flags and evidence

### 3. Observer Pattern
- **Training Callbacks**: Monitor training progress
- **Scan Progress**: Track scanning progress

### 4. Singleton Pattern
- **Configuration**: Global config instance
- **Payload Manager**: Shared payload instance

## Error Handling

### Exception Hierarchy

```python
class ConfigurationError(Exception):
    """Raised when configuration is invalid."""
    pass

class ScanError(Exception):
    """Raised when scan operation fails."""
    pass

class TrainingError(Exception):
    """Raised when training fails."""
    pass
```

### Error Handling Strategy

1. **Validation**: Validate inputs at boundaries
2. **Specific Exceptions**: Use specific exception types
3. **Error Messages**: Clear, actionable error messages
4. **Graceful Degradation**: Fallback to safe defaults
5. **Logging**: Log all errors for debugging

## Testing Strategy

### Unit Tests
- Test individual components in isolation
- Mock external dependencies
- Test edge cases and error conditions

### Integration Tests
- Test component interactions
- Test end-to-end workflows
- Test with real target applications

### Performance Tests
- Benchmark training speed
- Profile memory usage
- Optimize hot paths

## Extensibility

### Adding New Actions

1. Add action to `web_sec_env.py` action_book
2. Implement action execution logic
3. Update payload manager if needed
4. Update documentation

### Adding New Targets

1. Create new target app in `env/`
2. Add to configuration in `config.py`
3. Update `start_services.py`
4. Document vulnerabilities

### Adding New Features

1. Follow code style guide (`docs/CODE_STYLE.md`)
2. Add type hints
3. Write docstrings
4. Update documentation
5. Add tests

## Performance Considerations

### Training Optimization
- GPU acceleration (CUDA)
- Batch processing
- Memory-efficient replay buffer
- Gradient clipping

### Scanning Optimization
- Parallel requests (future)
- Connection pooling
- Caching discovered endpoints
- Smart payload selection

## Security Considerations

### For Training
- Mock applications only
- Isolated network (localhost)
- No real credentials

### For Scanning
- Always get authorization
- Rate limiting
- Stealth modes
- Proxy support

## Future Enhancements

### Planned Features
- [ ] Parallel environment support
- [ ] Distributed training
- [ ] Model ensemble
- [ ] Automated retraining
- [ ] Web dashboard
- [ ] API server
- [ ] Plugin system

### Code Quality
- [ ] Comprehensive test suite
- [ ] CI/CD pipeline
- [ ] Code coverage tracking
- [ ] Automated linting
- [ ] Performance benchmarking

# Contributing Guide

Thank you for your interest in contributing to the DRL Web Vulnerability Scanner!

## Table of Contents

1. [Code of Conduct](#code-of-conduct)
2. [Getting Started](#getting-started)
3. [Development Setup](#development-setup)
4. [Coding Standards](#coding-standards)
5. [Commit Guidelines](#commit-guidelines)
6. [Pull Request Process](#pull-request-process)
7. [Reporting Issues](#reporting-issues)

## Code of Conduct

- Be respectful and inclusive
- Focus on constructive feedback
- Help others learn and improve
- Follow security best practices

## Getting Started

### Prerequisites

- Python 3.8+
- pip or conda
- Git
- (Optional) CUDA-capable GPU for training

### Development Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd "DQN web vul"
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Verify installation**
   ```bash
   python -c "from agent.dqn_agent import DQNAgent; print('✓ Installation successful')"
   ```

## Development Setup

### Project Structure

```
DQN web vul/
├── agent/           # Agent implementation
├── env/             # Environment & target apps
├── utils/           # Utility modules
├── docs/            # Documentation
├── config.py        # Configuration system
└── tests/           # Test suite (coming soon)
```

### Running Tests

```bash
# Run all tests
python -m pytest tests/

# Run specific test
python -m pytest tests/test_agent.py

# Run with coverage
pytest --cov=agent --cov=env tests/
```

### Starting Development

1. **Start target applications**
   ```bash
   python start_services.py
   ```

2. **Run training**
   ```bash
   python train_multi_target.py --episodes 100
   ```

3. **Test scanning**
   ```bash
   python autonomous_scan.py --target http://localhost:5002
   ```

## Coding Standards

### Code Style

- Follow PEP 8 style guide
- Use type hints for all functions
- Write comprehensive docstrings
- Keep functions small (< 50 lines)
- Use meaningful variable names

**See [CODE_STYLE.md](docs/CODE_STYLE.md) for detailed guidelines.**

### Type Hints

Always use type hints:

```python
def calculate_reward(
    vulnerability_found: bool,
    phase: int,
    base_reward: float = -1.0
) -> float:
    """Calculate reward based on action outcome."""
    # Implementation
    pass
```

### Docstrings

Use Google-style docstrings:

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
        checkpoint_dir: Directory to save checkpoints
        
    Returns:
        Dictionary containing training metrics:
        - 'rewards': List of episode rewards
        - 'losses': List of training losses
        
    Raises:
        ConnectionError: If target URL is unreachable
        ValueError: If episodes < 1
    """
    # Implementation
    pass
```

### Configuration

Use the centralized configuration system:

```python
from config import get_config

config = get_config()
agent = DQNAgent(
    state_dim=config.agent.state_dim,
    action_dim=config.agent.action_dim,
    config=config.agent
)
```

### Error Handling

Use specific exceptions:

```python
class ConfigurationError(Exception):
    """Raised when configuration is invalid."""
    pass

def load_config(filepath: str) -> Dict:
    """Load configuration from file."""
    if not Path(filepath).exists():
        raise ConfigurationError(f"Config file not found: {filepath}")
    # Implementation
    pass
```

## Commit Guidelines

### Commit Message Format

```
<type>: <subject>

<body>

<footer>
```

### Types

- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

### Examples

```
feat: Add configuration management system

- Created centralized config.py with dataclasses
- Added support for environment variable overrides
- Updated all modules to use new config system

Closes #123
```

```
fix: Resolve template placeholder issue in social media app

Fixed all routes using old '{{ content | safe }}' placeholder
to use new '{% block content %}{% endblock %}' syntax.

Fixes #456
```

## Pull Request Process

### Before Submitting

1. **Update documentation**
   - Update README.md if needed
   - Add/update docstrings
   - Update relevant docs/ files

2. **Run tests**
   ```bash
   pytest tests/
   python -m py_compile agent/ env/ utils/
   ```

3. **Check code style**
   ```bash
   flake8 --max-line-length=100 .
   mypy .
   ```

4. **Update CHANGELOG.md**
   - Add entry describing your changes

### PR Checklist

- [ ] Code follows style guidelines
- [ ] Type hints added
- [ ] Docstrings added
- [ ] Tests pass
- [ ] Documentation updated
- [ ] CHANGELOG.md updated
- [ ] No linter errors

### Review Process

1. Create a feature branch
2. Make your changes
3. Run tests and linting
4. Submit pull request
5. Address review feedback
6. Merge when approved

## Reporting Issues

### Bug Reports

Include:
- Description of the bug
- Steps to reproduce
- Expected behavior
- Actual behavior
- Environment details
- Error messages/logs

### Feature Requests

Include:
- Use case
- Proposed solution
- Alternatives considered
- Impact/benefits

## Development Tips

### Debugging

1. Enable debug logging:
   ```python
   import logging
   logging.basicConfig(level=logging.DEBUG)
   ```

2. Use print statements for quick debugging
3. Use breakpoints in IDE
4. Check logs/ directory

### Testing

1. Test with mock targets first
2. Use small episode counts for quick tests
3. Validate with real-world targets (with permission)

### Documentation

- Keep documentation up to date
- Add examples to docstrings
- Update README for major changes
- Document configuration options

## Questions?

- Open an issue on GitHub
- Check existing documentation
- Review code comments
- Ask in discussions

Thank you for contributing! 🎉

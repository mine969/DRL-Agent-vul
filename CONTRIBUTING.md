# Contributing to DRL Security Agent

Thank you for your interest in contributing! This document provides guidelines for contributing to the project.

## 🎯 Ways to Contribute

- 🐛 Report bugs
- 💡 Suggest new features
- 📝 Improve documentation
- 🔧 Submit code improvements
- 🎓 Share research findings

## 📋 Getting Started

1. **Fork the repository**
2. **Clone your fork**
   ```bash
   git clone https://github.com/yourusername/RL.git
   cd RL
   ```
3. **Create a branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

## 🔧 Development Setup

```bash
# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run tests (if available)
python -m pytest tests/
```

## 📝 Code Guidelines

### Python Style

- Follow PEP 8
- Use type hints
- Add docstrings to functions/classes
- Keep functions focused and small

### Example

```python
def detect_vulnerability(response: dict, vuln_type: str) -> bool:
    """
    Detect if response contains a specific vulnerability.

    Args:
        response: HTTP response dictionary
        vuln_type: Type of vulnerability to check

    Returns:
        True if vulnerability detected, False otherwise
    """
    # Implementation
    pass
```

## 🧪 Testing

- Add tests for new features
- Ensure existing tests pass
- Test on multiple targets
- Document test cases

## 📚 Documentation

- Update README.md if needed
- Add docstrings to new code
- Update relevant docs/ files
- Include usage examples

## 🔒 Security

- **Never commit credentials**
- **Test only on authorized targets**
- **Report security issues privately**
- **Follow responsible disclosure**

## 📬 Submitting Changes

1. **Commit your changes**

   ```bash
   git add .
   git commit -m "feat: add new vulnerability detection"
   ```

2. **Push to your fork**

   ```bash
   git push origin feature/your-feature-name
   ```

3. **Create Pull Request**
   - Describe your changes
   - Reference related issues
   - Include test results

## 🎨 Commit Message Format

```
<type>: <description>

[optional body]

[optional footer]
```

**Types**:

- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation
- `style`: Formatting
- `refactor`: Code restructuring
- `test`: Adding tests
- `chore`: Maintenance

**Examples**:

```
feat: add SSTI detection to payload manager
fix: resolve checkpoint loading error
docs: update training guide with new examples
```

## 🐛 Reporting Bugs

Include:

- Description of the bug
- Steps to reproduce
- Expected vs actual behavior
- Environment details
- Error messages/logs

## 💡 Feature Requests

Include:

- Use case description
- Proposed solution
- Alternative approaches
- Potential impact

## ⚖️ Code of Conduct

- Be respectful and inclusive
- Provide constructive feedback
- Focus on the code, not the person
- Help others learn and grow

## 📞 Contact

- GitHub Issues: For bugs and features
- Discussions: For questions and ideas

---

**Thank you for contributing!** 🙏

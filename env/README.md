# Target Environments

5 deliberately vulnerable web applications for training and testing the DRL security agent.

## 🎯 Applications

| #   | Application      | Port | File                      | Database       | Vulnerabilities                             |
| --- | ---------------- | ---- | ------------------------- | -------------- | ------------------------------------------- |
| 1   | **E-Commerce**   | 5002 | `target_app_ecommerce.py` | `ecommerce.db` | SQLi, IDOR, Business Logic, Race Conditions |
| 2   | **Social Media** | 5003 | `target_app_social.py`    | `social.db`    | XSS, File Upload, CSRF, Session Fixation    |
| 3   | **Banking**      | 5004 | `target_app_banking.py`   | `banking.db`   | CSRF, IDOR, Logic Flaws                     |
| 4   | **Blog**         | 5005 | `target_app_blog.py`      | `blog.db`      | Stored XSS, SSTI, CSRF                      |
| 5   | **File Share**   | 5006 | `target_app_fileshare.py` | `fileshare.db` | File Upload, Path Traversal, IDOR           |

## 🚀 Quick Start

### Initialize Databases

```bash
python ../init_targets.py
```

### Run Individual Target

```bash
python target_app_ecommerce.py
# Visit http://localhost:5002
```

### Run All Targets (PowerShell)

```powershell
Start-Process python -ArgumentList "target_app_ecommerce.py"
Start-Process python -ArgumentList "target_app_social.py"
Start-Process python -ArgumentList "target_app_banking.py"
Start-Process python -ArgumentList "target_app_blog.py"
Start-Process python -ArgumentList "target_app_fileshare.py"
```

## 📊 Default Credentials

All applications:

- **Admin**: `admin` / `admin123`
- **User**: `user` / `password`

## 🧪 Training Environment

### `web_sec_env.py` (3,800+ lines)

**Gymnasium Environment** for RL training

**Features**:

- 15-dimensional state space
- 50 actions (mock targets) / 150 actions (full mode)
- Phase-based reward shaping
- Vulnerability detection
- Response analysis

**Usage**:

```python
from env.web_sec_env import WebSecurityGym

env = WebSecurityGym("http://localhost:5002")
state, info = env.reset()
action = 0  # Navigate
next_state, reward, terminated, truncated, info = env.step(action)
```

## 📁 Database Files

All databases stored in this folder:

- `ecommerce.db` - E-commerce data
- `social.db` - Social media data
- `banking.db` - Banking data (created on first run)
- `blog.db` - Blog data (created on first run)
- `fileshare.db` - File share data (created on first run)

## ⚠️ Important Notes

1. **For Research Only** - These are deliberately vulnerable
2. **Never Deploy** - Not for production use
3. **Isolated Environment** - Run in controlled network
4. **Reset Databases** - Delete `.db` files to reset

## 📚 Documentation

See [TARGETS_README.md](TARGETS_README.md) for comprehensive documentation including:

- Vulnerability details
- Research use cases
- Training workflows
- Expected results

## 🔗 Related Files

- `../train_mock_targets.py` - Train on all 5 targets
- `../init_targets.py` - Initialize databases
- `../autonomous_scan.py` - Run a trained agent against a target

---

**Ready for DRL security research! 🎯**

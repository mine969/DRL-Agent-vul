# 🎯 Target Applications for DRL Security Research

This directory contains **5 deliberately vulnerable web applications** designed for training and testing the Deep Reinforcement Learning security agent.

## 📋 Available Targets

| #   | Application             | Port | Focus Areas                              | Database           |
| --- | ----------------------- | ---- | ---------------------------------------- | ------------------ |
| 1   | **E-Commerce Platform** | 5002 | Business Logic, Payment, Race Conditions | `env/ecommerce.db` |
| 2   | **Social Media**        | 5003 | XSS, File Upload, IDOR, CSRF             | `env/social.db`    |
| 3   | **Banking App**         | 5004 | CSRF, Logic Flaws, Session Security      | `env/banking.db`   |
| 4   | **Blog Platform**       | 5005 | Stored XSS, SSTI, Comment Injection      | `env/blog.db`      |
| 5   | **File Sharing**        | 5006 | File Upload, Path Traversal, IDOR        | `env/fileshare.db` |

## 🚀 Quick Start

### Run Individual Targets

```bash
# E-Commerce Platform
python env/target_app_ecommerce.py

# Social Media
python env/target_app_social.py

# Banking App
python env/target_app_banking.py

# Blog Platform
python env/target_app_blog.py

# File Sharing
python env/target_app_fileshare.py
```

### Run All Targets (PowerShell)

```powershell
# Start all 5 targets in separate terminals
Start-Process python -ArgumentList "env/target_app_ecommerce.py"
Start-Process python -ArgumentList "env/target_app_social.py"
Start-Process python -ArgumentList "env/target_app_banking.py"
Start-Process python -ArgumentList "env/target_app_blog.py"
Start-Process python -ArgumentList "env/target_app_fileshare.py"
```

## 🧪 Training Your Agent

### Example: Train on E-Commerce

```python
from env.web_sec_env import WebSecurityGym

# Point to local target
env = WebSecurityGym(target_url="http://localhost:5002")

# Train your Double DQN agent
# ... your training code ...
```

### Multi-Target Training

```python
targets = [
    "http://localhost:5002",  # E-Commerce
    "http://localhost:5003",  # Social
    "http://localhost:5004",  # Banking
    "http://localhost:5005",  # Blog
    "http://localhost:5006",  # FileShare
]

for target in targets:
    env = WebSecurityGym(target_url=target)
    # Train and evaluate
```

## 📊 Vulnerability Coverage

### Target 1: E-Commerce (Port 5002)

- ✅ SQL Injection (Login, Search, Filters)
- ✅ Mass Assignment (Registration)
- ✅ Business Logic Flaws (Negative Quantity)
- ✅ Race Conditions (Checkout, Stock)
- ✅ IDOR (Orders, Products)
- ✅ Payment Bypass (Zero/Negative Amount)
- ✅ Broken Access Control (Admin Endpoints)

**Default Credentials:**

- `admin / admin123`
- `customer / password`

### Target 2: Social Media (Port 5003)

- ✅ Stored XSS (Posts, Comments, Messages)
- ✅ Reflected XSS (Search)
- ✅ Unrestricted File Upload
- ✅ Path Traversal
- ✅ IDOR (Profiles, Messages, Posts)
- ✅ CSRF (Friend Requests)
- ✅ Session Fixation
- ✅ Predictable Reset Tokens

**Default Credentials:**

- `admin / admin123`
- `alice / password`

### Target 3: Banking (Port 5004)

- ✅ CSRF (Money Transfer)
- ✅ IDOR (Account Access)
- ✅ Session Security Issues
- ✅ Logic Flaws (Insufficient Balance Check)

**Default Credentials:**

- `admin / admin123`
- `user / password`

### Target 4: Blog (Port 5005)

- ✅ Stored XSS (Posts, Comments)
- ✅ SSTI (Server-Side Template Injection)
- ✅ CSRF (Post Creation)
- ✅ Weak Authentication

**Default Credentials:**

- `admin / admin123`
- `blogger / password`

### Target 5: File Sharing (Port 5006)

- ✅ Unrestricted File Upload
- ✅ Path Traversal (Download)
- ✅ IDOR (Delete, Download)
- ✅ No File Type Validation

**Default Credentials:**

- `admin / admin123`
- `user / password`

## 🎓 Research Use Cases

### 1. **Curriculum Learning**

Train your agent progressively:

1. Start with Banking (simpler, fewer endpoints)
2. Move to Blog (moderate complexity)
3. Progress to E-Commerce (complex business logic)
4. Challenge with Social Media (multiple attack vectors)
5. Master File Sharing (file-based attacks)

### 2. **Transfer Learning**

- Train on E-Commerce → Test on Social Media
- Evaluate knowledge transfer across domains

### 3. **Comparative Analysis**

- Compare DQN vs Double DQN performance
- Benchmark against baseline algorithms

### 4. **Vulnerability Detection Rate**

- Measure detection accuracy per target
- Calculate precision/recall for each vulnerability type

## 📁 File Organization

```
env/
├── target_app_ecommerce.py    # E-Commerce application
├── target_app_social.py       # Social Media application
├── target_app_banking.py      # Banking application
├── target_app_blog.py         # Blog application
├── target_app_fileshare.py    # File Sharing application
├── web_sec_env.py             # RL Environment (Gym)
├── ecommerce.db               # E-Commerce database
├── social.db                  # Social Media database
├── banking.db                 # Banking database
├── blog.db                    # Blog database
└── fileshare.db               # File Sharing database
```

## ⚠️ Important Notes

1. **For Research Only**: These applications are deliberately vulnerable. Never deploy to production.
2. **Isolated Environment**: Run in a controlled, isolated environment.
3. **Database Reset**: Delete `.db` files to reset to initial state.
4. **Port Conflicts**: Ensure ports 5002-5006 are available.

## 🔬 Example Research Workflow

```bash
# 1. Start all targets
python start_services.py

# 2. Train your agent
python train_mock_targets.py --episodes 1000

# 3. Evaluate and compare
python research/evaluate_agent.py --agent improved --checkpoint checkpoints/improved_mock_ep1000.pth
```

## 📈 Expected Results

Your research should demonstrate:

- **Vulnerability Detection Rate**: % of vulnerabilities found
- **False Positive Rate**: Accuracy of detections
- **Training Efficiency**: Episodes needed to converge
- **Transfer Learning**: Performance on unseen targets
- **Comparison**: DQN vs Double DQN vs Baseline

---

**Happy Researching! 🧠🔒**

            # Using Your Trained Agent Against DVWA or Other Targets

## Quick Start

### 1. Test Against DVWA

```bash
# Make sure DVWA is running on http://localhost/dvwa
python deploy_agent.py --target http://localhost/dvwa --episodes 10
```

### 2. Test Against Any Website

```bash
python deploy_agent.py --target http://your-target-site.com --episodes 5
```

### 3. Interactive Mode (Watch Agent Live)

```bash
python deploy_agent.py --target http://localhost/dvwa --interactive
```

### 4. Use Specific Checkpoint

```bash
python deploy_agent.py --target http://localhost/dvwa --model checkpoints/dqn_checkpoint_ep100.pth
```

## Important Notes

### ⚠️ DVWA Setup Required

The agent expects certain URL patterns. For DVWA, you may need to:

1. **Set DVWA Security Level to Low**

   - Login to DVWA
   - Go to "DVWA Security"
   - Set to "Low"

2. **Update Target URLs** (if needed)

   Edit `env/web_sec_env.py` to match DVWA's structure:

   ```python
   # Example for DVWA SQLi
   if action == 13:  # SQLi Obfuscated
       # DVWA SQLi is at /vulnerabilities/sqli/
       r = requests.get(f"{self.target_url}/vulnerabilities/sqli/",
                       params={"id": "1' or '1'='1", "Submit": "Submit"})
   ```

### 🔧 Adapting to Different Targets

Since your agent was trained on a custom environment, it may need adaptation:

**Option A: Create DVWA-Specific Environment**

```python
# Create env/dvwa_env.py
class DVWAEnv(WebSecEnv):
    def __init__(self, target_url="http://localhost/dvwa"):
        super().__init__(target_url)
        self.session = requests.Session()
        self.login_to_dvwa()  # Auto-login

    def login_to_dvwa(self):
        # DVWA requires login first
        self.session.post(
            f"{self.target_url}/login.php",
            data={"username": "admin", "password": "password", "Login": "Login"}
        )
```

**Option B: Fine-tune Agent on DVWA**

```python
# Load pre-trained weights and continue training on DVWA
from deploy_agent import load_trained_agent

agent = load_trained_agent("dqn_web_sec_model.pth")
dvwa_env = DVWAEnv("http://localhost/dvwa")

# Fine-tune for 50 more episodes
for e in range(50):
    state, _ = dvwa_env.reset()
    # ... training loop
```

## Example Output

```
🎯 Target: http://localhost/dvwa
🤖 Running 10 test episodes...

============================================================

Episode 1/10
  Total Reward: 45
  Steps: 28
------------------------------------------------------------

Episode 2/10
  Total Reward: 95
  Steps: 15
  🚨 VULNERABILITY FOUND: SQLi (Obfuscated) (Reward: 100)
------------------------------------------------------------

============================================================
📊 SUMMARY
============================================================
Total Vulnerabilities Found: 1

🔴 Vulnerabilities Detected:
  - Episode 2: SQLi (Obfuscated) (Step 12, Reward: 100)
```

## Limitations

1. **Training Environment Mismatch**: Agent was trained on your custom app, not DVWA
2. **URL Structure**: DVWA has different URL patterns
3. **Authentication**: DVWA requires login before testing
4. **Response Parsing**: Agent looks for specific success indicators

## Recommended Workflow

1. **Test on Training Environment First**

   ```bash
   python deploy_agent.py --target http://localhost:5000 --episodes 5
   ```

2. **Create DVWA Adapter** (see Option A above)

3. **Fine-tune on DVWA** (see Option B above)

4. **Deploy Against DVWA**
   ```bash
   python deploy_agent.py --target http://localhost/dvwa --episodes 10
   ```

## Advanced: Real-World Deployment

For production pentesting:

```python
# Create a wrapper that logs findings
class PentestAgent:
    def __init__(self, agent, target):
        self.agent = agent
        self.target = target
        self.findings = []

    def scan(self):
        # Run agent
        vulns = test_agent(self.target, episodes=20)

        # Generate report
        self.generate_report(vulns)

    def generate_report(self, vulns):
        with open('pentest_report.md', 'w') as f:
            f.write(f"# Penetration Test Report\n")
            f.write(f"Target: {self.target}\n\n")
            for v in vulns:
                f.write(f"- {v['action']}: Found at step {v['step']}\n")
```

## Ethical Use Only! ⚖️

**ONLY use this agent on:**

- Your own applications
- Systems you have explicit permission to test
- Lab environments (DVWA, WebGoat, etc.)

**NEVER use on:**

- Production systems without authorization
- Third-party websites
- Any system you don't own or have written permission to test

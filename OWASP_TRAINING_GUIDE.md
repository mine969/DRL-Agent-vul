# 🎯 OWASP Top 10 2025 Training Guide

## Quick Start

### 1. Start the Training Environment

```bash
python env/owasp_training_app.py
```

The server will start on `http://localhost:5000`

### 2. Train the AI Agent

```bash
# In a new terminal
python train.py
```

The AI will automatically connect to `localhost:5000` and learn to exploit all OWASP Top 10 2025 vulnerabilities!

### 3. Monitor Training Progress

Watch the console output to see:

- Episodes completed
- Vulnerabilities discovered
- Rewards earned
- Success rate

### 4. Test the Trained Agent

```bash
python autonomous_scan.py http://localhost:5000 --depth 50 --intensity 5
```

---

## What the AI Will Learn

### ✅ A01: Broken Access Control

- **IDOR**: `/profile?uid=999`
- **Missing Auth**: `/admin/users`

### ✅ A02: Security Misconfiguration

- **Debug Mode**: `/debug`
- **Config Exposure**: `/config`

### ✅ A03: Supply Chain Failures

- **Typosquatting**: POST `/install_package` with `{"package": "reqeusts"}`

### ✅ A04: Cryptographic Failures

- **Weak Hash**: `/weak_crypto?data=test`
- **JWT None**: `/get_token`

### ✅ A05: Injection

- **SQL Injection**: `/search?q=' OR '1'='1`
- **XSS**: POST `/comment` with `{"comment": "<script>alert(1)</script>"}`
- **SSTI**: `/template?name={{7*7}}`
- **Command Injection**: POST `/ping` with `{"host": "localhost; whoami"}`

### ✅ A06: Insecure Design

- **Business Logic**: POST `/purchase` with `{"product_id": 1, "quantity": -999}`
- **Race Condition**: POST `/race_condition` (send multiple concurrent requests)

### ✅ A07: Auth Failures

- **SQL Auth Bypass**: POST `/login` with `{"username": "admin' OR '1'='1' --", "password": "x"}`
- **Weak Reset**: POST `/reset_password`

### ✅ A08: Data Integrity

- **Deserialization**: POST `/deserialize` with pickled data

### ✅ A09: Logging Failures

- **Log Injection**: POST `/log_action` with `{"action": "test\r\n[CRITICAL] Fake"}`

### ✅ A10: Exception Handling

- **Error Disclosure**: `/divide?a=10&b=0`

---

## Training Tips

### For Best Results:

1. **Train for 500+ episodes** to learn all vulnerabilities
2. **Use GPU** if available (automatic with CUDA)
3. **Monitor rewards** - should increase over time
4. **Check logs** in `evaluation/TRAINING_PROGRESS.md`

### Expected Performance:

- **Episodes 1-100**: Learning basics, random exploration
- **Episodes 100-300**: Discovering vulnerabilities
- **Episodes 300-500**: Mastering exploitation
- **Episodes 500+**: Expert level, 90%+ success rate

---

## Verify Training

### Check if AI Learned:

```bash
# Run evaluation
python manual_eval.py

# Scan the training app
python autonomous_scan.py http://localhost:5000 --depth 50

# Check the report
cat reports/vulnerability_report_*.md
```

### Expected Results:

The AI should find **ALL 10 OWASP categories** with multiple vulnerabilities in each!

---

## Advanced Training

### Increase Difficulty:

Edit `env/owasp_training_app.py` to add:

- WAF simulation
- Rate limiting
- CAPTCHA
- More complex logic

### Custom Payloads:

Edit `agent/payload_manager.py` to add your own exploits

---

## Safety Notes

⚠️ **NEVER deploy `owasp_training_app.py` in production!**

This app is:

- ✅ Perfect for training
- ✅ Safe on localhost
- ❌ EXTREMELY vulnerable
- ❌ NOT for production

---

## Troubleshooting

### Port Already in Use:

```bash
# Kill process on port 5000
netstat -ano | findstr :5000
taskkill /PID <PID> /F
```

### Training Not Working:

1. Ensure training app is running
2. Check `http://localhost:5000` in browser
3. Verify no firewall blocking
4. Check GPU availability with `nvidia-smi`

---

## Next Steps

After training:

1. ✅ Scan real vulnerable apps (with permission!)
2. ✅ Try DVWA, WebGoat, Juice Shop
3. ✅ Participate in bug bounties
4. ✅ Build custom training scenarios

---

_Happy Training! Your AI will become an OWASP Top 10 2025 expert!_ 🚀

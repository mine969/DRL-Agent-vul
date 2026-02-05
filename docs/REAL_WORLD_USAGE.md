# 🌐 Real-World Usage Guide

## Complete Step-by-Step Guide for Real Scanning

### 📋 Prerequisites

1. **Training Complete** (or use a checkpoint)
2. **Target Website** running and accessible
3. **Permission** to test the target (CRITICAL!)

---

## 🎯 Scenario 1: Scanning DVWA (Most Common)

### Step 1: Setup DVWA

```bash
# Make sure DVWA is running
# Usually at: http://localhost/dvwa or http://localhost:80/dvwa

# Login to DVWA first:
# Username: admin
# Password: password

# Set security level to LOW:
# DVWA Security → Low
```

### Step 2: Run the Scanner

```bash
# Navigate to project folder
cd d:\github\RL

# Run interactive scanner
python scan.py
```

### Step 3: Enter Target

```
🎯 Enter website URL or IP: http://localhost/dvwa
Is this correct? (y/n): y

Would you like to customize scan options?
(y/n) [default: n]: n

Press Enter to begin...
```

### Step 4: Wait for Results

```
🕷️  Starting reconnaissance...
📍 Crawling: http://localhost/dvwa
📍 Crawling: http://localhost/dvwa/login.php
...
🔴 PHASE 2: VULNERABILITY TESTING
🎯 Testing: http://localhost/dvwa/login.php
  🚨 Found 1 potential vulnerability(ies)
...
```

### Step 5: Review Reports

```bash
# Open in browser
start vulnerability_report_20251123_060000.html

# Or read text version
notepad vulnerability_report_20251123_060000.txt
```

---

## 🎯 Scenario 2: Scanning Your Own Website

### Step 1: Ensure Website is Running

```bash
# Example: Your website at http://192.168.1.100
# Make sure it's accessible from your machine
ping 192.168.1.100
```

### Step 2: Run Scanner

```bash
python scan.py
```

### Step 3: Enter Your Website

```
🎯 Enter website URL or IP: http://192.168.1.100
Is this correct? (y/n): y
```

### Step 4: Customize if Needed

```
Would you like to customize scan options?
(y/n) [default: n]: y

Max pages to crawl [default: 30]: 50
Test episodes per page [default: 3]: 5
Model file [default: dqn_web_sec_model.pth]: checkpoints/dqn_checkpoint_ep500.pth
```

---

## 🎯 Scenario 3: Scanning Remote Website

### Step 1: Verify Access

```bash
# Make sure you can reach the site
curl http://target-website.com
```

### Step 2: Run Scanner

```bash
python scan.py
```

### Step 3: Enter Remote URL

```
🎯 Enter website URL or IP: http://target-website.com
Is this correct? (y/n): y
```

---

## 🎯 Scenario 4: Testing Different Checkpoints

### Compare Model Performance

**Test 1: Episode 100**

```bash
python scan.py
# Enter target: http://localhost/dvwa
# Model: checkpoints/dqn_checkpoint_ep100.pth
```

**Test 2: Episode 300**

```bash
python scan.py
# Enter target: http://localhost/dvwa
# Model: checkpoints/dqn_checkpoint_ep300.pth
```

**Test 3: Final Model (500)**

```bash
python scan.py
# Enter target: http://localhost/dvwa
# Model: dqn_web_sec_model.pth
```

**Compare Results:**

- Check which model found more vulnerabilities
- Check which model had fewer false positives
- Use the best performing model for production

---

## 📊 Understanding the Reports

All report formats include captured flags (CTF{...}) and evidence fields when present.

### HTML Report (Best for Presentations)

```bash
# Open in browser
start vulnerability_report_20251123_060000.html
```

**What you'll see:**

- 📊 Statistics dashboard
- 🔴 Vulnerability details with:
  - Impact level (CRITICAL/HIGH/MEDIUM)
  - CVSS score
  - How to exploit
  - Potential damage
  - How to fix
  - Captured flags and evidence snippets when present

### TXT Report (Best for Quick Review)

```bash
# Open in Notepad
notepad vulnerability_report_20251123_060000.txt
```

**What you'll see:**

```
======================================================================
SECURITY VULNERABILITY REPORT
======================================================================
Target: http://localhost/dvwa
Scan Date: 2025-11-23 06:00:00

----------------------------------------------------------------------
SUMMARY
----------------------------------------------------------------------
Pages Discovered:        15
Total Vulnerabilities:   3
  - Critical:            2
  - High:                1
  - Medium:              0

======================================================================
VULNERABILITIES FOUND
======================================================================

[1] SQL Injection
----------------------------------------------------------------------
Impact Level:  CRITICAL
CVSS Score:    9.8
Affected URL:  http://localhost/dvwa/login.php

Description:
  Allows attackers to execute arbitrary SQL commands on the database
...
```

---

## 🔧 Advanced Usage

### Custom Scan Parameters

```bash
python autonomous_scan.py http://target.com --depth 100 --episodes 10
```

**Parameters:**

- `--depth 100`: Crawl up to 100 pages
- `--episodes 10`: Test each page 10 times (more thorough)
- `--model checkpoints/dqn_checkpoint_ep500.pth`: Use specific model

### Scan Multiple Targets

```bash
# Create a batch script
# scan_multiple.bat

python autonomous_scan.py http://site1.com --depth 30
python autonomous_scan.py http://site2.com --depth 30
python autonomous_scan.py http://site3.com --depth 30
```

---

## 🎯 Real-World Workflow

### Professional Penetration Testing

**Phase 1: Reconnaissance**

```bash
python scan.py
# Target: http://client-website.com
# Depth: 50
# Episodes: 5
```

**Phase 2: Review Findings**

```bash
# Open HTML report
start vulnerability_report_*.html

# Document findings
# Screenshot critical vulnerabilities
```

**Phase 3: Manual Verification**

```bash
# For each vulnerability found:
# 1. Verify it manually
# 2. Document proof of concept
# 3. Assess real-world impact
```

**Phase 4: Report to Client**

```bash
# Use the generated reports
# Add manual verification screenshots
# Provide remediation timeline
```

---

## ⚠️ Important Safety Rules

### ✅ DO:

- Test your own websites
- Test with written permission
- Test in lab environments (DVWA, WebGoat)
- Document all findings
- Report responsibly

### ❌ DON'T:

- Scan websites without permission
- Test production systems without approval
- Share vulnerabilities publicly before fixes
- Use for malicious purposes
- Ignore rate limits or DoS protections

---

## 🐛 Troubleshooting

### "No vulnerabilities found"

**Possible reasons:**

1. Website is actually secure ✅
2. Agent needs more training (use ep500)
3. Website structure differs from training
4. Defenses are too strong

**Solutions:**

- Try different checkpoint (ep300, ep500)
- Increase episodes: `--episodes 10`
- Check if website is accessible

### "Connection refused"

**Solutions:**

```bash
# Check if target is running
ping target-website.com

# Check if port is open
telnet target-website.com 80

# Try with http:// or https://
```

### "Too many false positives"

**Solutions:**

- Use higher episode checkpoint (ep500)
- Manually verify each finding
- Adjust confidence threshold

---

## 📈 Best Practices

### 1. Start Small

```bash
# First scan: Small depth
python scan.py
# Depth: 10
```

### 2. Increase Gradually

```bash
# Second scan: Medium depth
python scan.py
# Depth: 30
```

### 3. Full Scan

```bash
# Final scan: Full depth
python scan.py
# Depth: 100
```

### 4. Use Best Model

```bash
# Always use ep500 for production
python scan.py
# Model: dqn_web_sec_model.pth (or checkpoints/dqn_checkpoint_ep500.pth)
```

### 5. Document Everything

- Save all reports
- Screenshot vulnerabilities
- Note timestamps
- Record scan parameters

---

## 🎓 Example: Complete DVWA Scan

```bash
# 1. Start DVWA
# http://localhost/dvwa

# 2. Set security to LOW
# Login → DVWA Security → Low

# 3. Run scanner
cd d:\github\RL
python scan.py

# 4. Enter details
# URL: http://localhost/dvwa
# Customize: n
# Press Enter

# 5. Wait (~5-10 minutes)

# 6. Review results
start vulnerability_report_*.html

# 7. Expected findings:
# - SQL Injection (login.php)
# - XSS (search functionality)
# - Command Injection (ping)
# - IDOR (profile pages)
# - SSRF (fetch functionality)
```

---

## 📞 Quick Reference

| Task           | Command                                                  |
| -------------- | -------------------------------------------------------- |
| Simple scan    | `python scan.py`                                         |
| Advanced scan  | `python autonomous_scan.py http://target.com`            |
| Custom depth   | `python autonomous_scan.py http://target.com --depth 50` |
| Specific model | `python scan.py` → enter checkpoint path                 |
| View reports   | `start vulnerability_report_*.html`                      |

---

## 🎯 Summary

**For most users:**

```bash
python scan.py
# Enter your target URL
# Press Enter
# Wait for results
# Open HTML report
```

**That's it!** The scanner handles everything else automatically. 🚀

# 🛡️ Web Security Scanner - Complete Beginner's Guide

## What Is This?

This is an **AI-powered security scanner** that automatically finds vulnerabilities (security weaknesses) in websites. Think of it as a robot that tests if a website is secure.

## 📋 Prerequisites (What You Need)

### 1. Python Installed

- **Check if you have it**: Open Command Prompt and type `python --version`
- **If not installed**: Download from [python.org](https://python.org) (get version 3.10 or newer)

### 2. Install Required Libraries

Open Command Prompt in the project folder and run:

```bash
pip install -r requirements.txt
```

## 🎯 How to Use (Step-by-Step)

### Step 1: Train the AI Agent (First Time Only)

**What this does**: Teaches the AI how to find security problems

```bash
python train.py
```

**What you'll see**:

- Episode numbers counting up (1/500, 2/500, etc.)
- Scores showing how well the AI is learning
- This takes 2-4 hours - let it run!

**When to stop**:

- Wait for at least 100 episodes
- Or press `Ctrl+C` to stop early (it auto-saves progress)

**Result**: You'll get a file called `dqn_web_sec_model.pth` (the trained AI brain)

---

### Step 2: Scan a Website

**What this does**: The AI automatically finds and tests all pages on a website

```bash
python autonomous_scan.py http://your-website.com
```

**Replace `http://your-website.com` with**:

- Your own website URL
- A test website like `http://localhost/dvwa`
- Any site you have permission to test

**What happens**:

1. 🕷️ **Crawling**: AI visits the homepage and finds all linked pages
2. 🔍 **Discovery**: AI looks for hidden pages (admin, api, etc.)
3. 🔴 **Testing**: AI tries to find security problems on each page
4. 📊 **Reporting**: AI creates a detailed report

**Time**: Usually 5-15 minutes depending on website size

---

### Step 3: Read the Report

After scanning, you'll get a file called `vulnerability_report_[timestamp].html`

**Open it in your browser** (Chrome, Firefox, etc.) to see:

- ✅ All pages found on the website
- 🔴 Security vulnerabilities discovered
- ⚠️ Impact level (Critical, High, Medium, Low)
- 📝 How attackers could exploit each vulnerability
- 🛠️ How to fix each problem

---

## 🎮 Common Commands

### Quick Scan (Fast)

```bash
python autonomous_scan.py http://your-site.com --depth 10
```

Only checks 10 pages - good for quick tests

### Deep Scan (Thorough)

```bash
python autonomous_scan.py http://your-site.com --depth 100
```

Checks up to 100 pages - finds more vulnerabilities

### Use a Checkpoint (Partially Trained Model)

```bash
python autonomous_scan.py http://your-site.com --model checkpoints/dqn_checkpoint_ep100.pth
```

Uses a model saved after 100 training episodes

### Zero-Day Hunter Mode (Find Unknown Vulnerabilities)

```bash
python autonomous_scan.py http://your-site.com --mode zeroday
```

**What this does**: Uses fuzzing and CVE intelligence to find unknown vulnerabilities

**When to use**: When you want to discover new, undocumented security issues

### Targetless Mode (Auto-Find Targets)

```bash
# Find targets using Google
python autonomous_scan.py --mode targetless --google-dork "inurl:admin.php"

# Find targets using Shodan (requires API key)
python autonomous_scan.py --mode targetless --shodan-query "apache" --shodan-key YOUR_KEY
```

**What this does**: Automatically discovers vulnerable websites to test

**When to use**: Bug bounty hunting, security research

**Note**: Only use on targets you have permission to test!

---

## 📊 Understanding the Report

### Impact Levels

| Level           | Meaning                        | Example                             |
| --------------- | ------------------------------ | ----------------------------------- |
| 🔴 **CRITICAL** | Attacker can take full control | SQL Injection allowing admin access |
| 🟠 **HIGH**     | Serious data breach possible   | Stealing user passwords             |
| 🟡 **MEDIUM**   | Limited damage possible        | Viewing other users' profiles       |
| 🟢 **LOW**      | Minor information leak         | Seeing software version numbers     |

### Vulnerability Types Explained

**SQL Injection (SQLi)**

- **What it is**: Attacker can access/modify database
- **Danger**: Steal all user data, delete everything
- **Example**: Login bypass, data theft

**Cross-Site Scripting (XSS)**

- **What it is**: Attacker can run malicious code in users' browsers
- **Danger**: Steal login cookies, redirect users
- **Example**: Fake login forms, session hijacking

**Command Injection**

- **What it is**: Attacker can run commands on the server
- **Danger**: Full server takeover
- **Example**: Delete files, install malware

**IDOR (Insecure Direct Object Reference)**

- **What it is**: Access other users' data by changing IDs
- **Danger**: Privacy breach
- **Example**: Viewing someone else's profile by changing URL

**SSRF (Server-Side Request Forgery)**

- **What it is**: Make the server access internal resources
- **Danger**: Access admin panels, internal APIs
- **Example**: Reading server configuration files

---

## ⚠️ Important Safety Rules

### ✅ DO Use On:

- Your own websites
- Test environments (DVWA, WebGoat)
- Systems you have written permission to test

### ❌ DON'T Use On:

- Websites you don't own
- Production systems without permission
- Any site without authorization

**Why?** Unauthorized security testing is **illegal** in most countries!

---

## 🐛 Troubleshooting

### "Command not found: python"

**Solution**: Install Python from python.org

### "Module not found" errors

**Solution**: Run `pip install -r requirements.txt`

### "Connection refused" when scanning

**Solution**: Make sure the target website is running and accessible

### Training is very slow

**Solution**:

- This is normal! Training takes hours
- You can use checkpoints (saved every 20 episodes)
- Or reduce episodes: edit `train.py` and change `episodes = 500` to `episodes = 100`

### No vulnerabilities found

**Possible reasons**:

- Website is actually secure (good!)
- Agent needs more training (run more episodes)
- Website structure is different from training environment

---

## 📁 Important Files

| File                          | What It Does                                  |
| ----------------------------- | --------------------------------------------- |
| `train.py`                    | Trains the AI agent                           |
| `autonomous_scan.py`          | Scans websites automatically                  |
| `dqn_web_sec_model.pth`       | The trained AI brain (created after training) |
| `checkpoints/`                | Saved progress during training                |
| `vulnerability_report_*.html` | Scan results (open in browser)                |

---

## 🎓 Learning More

### Want to understand how it works?

1. The AI learns by trying different attacks
2. It gets "rewards" when it finds vulnerabilities
3. Over time, it learns which attacks work best
4. This is called "Reinforcement Learning"

### Want to improve results?

1. Train for more episodes (500+ recommended)
2. Test on similar websites to training environment
3. Use the latest checkpoint for best results

---

## 💡 Quick Reference Card

```
┌─────────────────────────────────────────────┐
│         QUICK COMMAND REFERENCE             │
├─────────────────────────────────────────────┤
│ Train AI:                                   │
│   python train.py                           │
│                                             │
│ Scan Website:                               │
│   python autonomous_scan.py http://site.com │
│                                             │
│ Quick Scan (10 pages):                      │
│   python autonomous_scan.py http://site.com │
│   --depth 10                                │
│                                             │
│ Stop Training:                              │
│   Press Ctrl+C (auto-saves)                 │
└─────────────────────────────────────────────┘
```

---

## 🆘 Need Help?

1. Check the error message carefully
2. Make sure all prerequisites are installed
3. Verify you have permission to test the target
4. Try with a smaller `--depth` value first

Remember: This tool is for **ethical security testing only**! Always get permission before testing any website.

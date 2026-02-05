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
python train_mock_targets.py --episodes 1000
```

**What you'll see**:

- Episode numbers counting up (1/1000, 2/1000, etc.)
- Scores showing how well the AI is learning
- This takes 2-4 hours - let it run!

**When to stop**:

- Wait for at least 100 episodes
- Or press `Ctrl+C` to stop early (it auto-saves progress)

**Result**: You'll get checkpoints in `checkpoints/` (e.g., `improved_mock_ep1000.pth`)

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
- 🏁 Captured flags (CTF{...}) and evidence snippets when present

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
python autonomous_scan.py http://your-site.com --model checkpoints/improved_mock_ep100.pth
```

Uses a model saved after 100 training episodes

### Full AI Mode (Deeper Exploration)

```bash
python autonomous_scan.py http://your-site.com --depth 50 --intensity 8 --ai-mode --pentester
```

**What this does**: Enables chain attacks and online learning for deeper exploration

**When to use**: When you want a thorough scan on authorized targets

### GUI-Only Modes

Targetless hunting, OSINT-only recon, and stealth profiles are available in the GUI:

```bash
python scanner_gui.py
```

---

## 🧠 Scanning Strategies (Recommended Settings)

### For Unknown / New Websites (Start Here) 🛡️

**Goal**: Map the site safely without crashing it or getting blocked.

- **Crawl Depth**: `30` (Enough to find main pages)
- **Intensity**: `2` (Gentle testing)
- **Command**:
  ```bash
  python autonomous_scan.py http://target.com --depth 30 --intensity 2
  ```

### For Standard Security Testing ⚖️

**Goal**: Thorough check of a stable website.

- **Crawl Depth**: `50`
- **Intensity**: `3` (Default balance)
- **Command**:
  ```bash
  python autonomous_scan.py http://target.com --depth 50 --intensity 3
  ```

### For Deep / Aggressive Testing 🔥

**Goal**: Find deep vulnerabilities in robust applications.

- **Crawl Depth**: `100`
- **Intensity**: `5` (Maximum attack power)
- **Command**:
  ```bash
  python autonomous_scan.py http://target.com --depth 100 --intensity 5
  ```

---

## 📊 Understanding the Report

### Captured Flags & Evidence

- **Flags Captured**: Any `CTF{...}` values found during scanning
- **Evidence**: Status codes, rewards, and response snippets that justify the finding

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
- You can use checkpoints (saved every 50 episodes by default)
- Or reduce episodes: run `python train_mock_targets.py --episodes 100`

### No vulnerabilities found

**Possible reasons**:

- Website is actually secure (good!)
- Agent needs more training (run more episodes)
- Website structure is different from training environment

---

## 📁 Important Files

| File                          | What It Does                                  |
| ----------------------------- | --------------------------------------------- |
| `train_mock_targets.py`       | Trains the AI agent on mock targets           |
| `autonomous_scan.py`          | Scans websites automatically                  |
| `checkpoints/improved_mock_ep*.pth` | Training checkpoints                     |
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
│   python train_mock_targets.py --episodes 1000 │
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

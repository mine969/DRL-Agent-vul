# 🖥️ GUI Scanner - User Guide (2025 Edition)

## Quick Start

### Launch the GUI

```bash
python scanner_gui.py
```

**That's it!** A beautiful cyberpunk-themed window will open.

---

## 🚀 Latest Features (2025)

- **200+ Proxies** - Automatically fetched and validated

### Exploit Factory

- **📋 Full Exploit URLs** - Ready-to-paste URLs with payloads
- **💻 CURL Commands** - Copy-paste ready
- **🐍 Python Scripts** - Auto-generated exploit code
- **💡 Suggested Payloads** - 200+ attack vectors

### Enhanced UX

- **💡 Tooltips** - Hover over elements for hints
- **📊 Status Bar** - Real-time feedback at bottom
- **📜 Scrollable Controls** - Responsive left panel for all screens
- **🎨 Resizable Layout** - Adjustable panels (PanedWindow)

---

## 🎨 GUI Features

### Modern Cyberpunk Theme

- Professional red team aesthetic
- Hacker green on black background
- High contrast for accessibility
- Easy on the eyes for long sessions

### Mission Parameters

- **Target URL**: Type or paste
- **Crawl Depth**: Slider (1-100 pages)
- **Test Episodes**: Slider (1-10 per page)
- **AI Model**: Dropdown with all checkpoints

### Scan Modes

- **AUTO** - Balanced AI-driven scan
- **AGGRESSIVE** - Deep penetration testing
- **OSINT** - Reconnaissance only
- **SPECIFIC** - Single attack type
- **ZERO-DAY HUNTER** - Advanced fuzzing & CVEs

### Stealth Configuration

- **Stealth Level**: Low/Medium/High/Paranoid
- **Proxy File**: Auto-fetch or manual upload
- **Request Delays**: Automatic based on stealth level

### Real-Time Feedback

- Live progress bar
- Status updates in status bar
- Scrolling log output
- Timestamp for each event
- Color-coded messages

### One-Click Actions

- ⚡ **FLASH ATTACK**: Quick one-click scan
- 🚀 **LAUNCH SCAN**: Begin scanning
- 🛑 **ABORT MISSION**: Cancel anytime
- 📄 **OPEN REPORT**: View HTML report
- 🔄 **FETCH PROXIES**: Auto-download proxies

---

## 📋 Step-by-Step Usage

### 1. Launch GUI

```bash
cd d:\github\RL
python scanner_gui.py
```

### 2. Configure Mission

- **Target URL**: Enter `http://target.com`
- **Crawl Depth**: Adjust slider (default: 30)
- **Test Episodes**: Adjust slider (default: 3)
- **Scan Mode**: Select AUTO/AGGRESSIVE/OSINT/SPECIFIC/ZERO-DAY
- **AI Model**: Select from dropdown (use latest)

### 3. Configure Stealth (Optional)

- **Stealth Level**: Choose Low/Medium/High/Paranoid
- **Proxy File**: Click 🔄 to auto-fetch or 📂 to browse

### 4. Start Scan

- Click **⚡ FLASH ATTACK** for quick scan, OR
- Click **🚀 LAUNCH SCAN** for configured scan
- Watch real-time progress!

### 5. Monitor Progress

- Progress bar shows activity
- Status bar shows current phase
- Log shows detailed output
- Findings list populates in real-time

### 6. View Results

- Click on a finding in the list
- **Exploit Factory** shows:
  - Full exploit URLs
  - CURL commands
  - Python scripts
  - Suggested payloads
- Click **📄 OPEN REPORT** for full HTML report

---

## 🎯 GUI vs Command Line

### Use GUI When:

- ✅ You prefer visual interfaces
- ✅ You want to see real-time progress
- ✅ You're new to command line
- ✅ You want easy model selection
- ✅ You need exploit code generation
- ✅ You want to test different modes quickly

### Use Command Line When:

- ✅ You're comfortable with terminals
- ✅ You want to script/automate
- ✅ You're running on a server
- ✅ You prefer keyboard-only workflow
- ✅ You want to batch process

**Both work equally well!** Choose what you prefer.

---

## 🎨 UI Elements Explained

### Header

```
💀 DRL AI RED TEAM - AUTONOMOUS ATTACKER
```

- Cyberpunk branding
- Professional red team theme

### Left Panel - Mission Control (Scrollable)

```
🎯 MISSION PARAMETERS
├── Target URL
├── Crawl Depth (slider)
├── Test Episodes (slider)
└── AI Model (dropdown)

⚙️ SCAN MODE
├── 🤖 AUTO MODE
├── 🔥 AGGRESSIVE MODE
├── 🕵️ OSINT MODE
├── 🎯 SPECIFIC ATTACK
└── 💀 ZERO-DAY HUNTER

🥷 STEALTH CONFIGURATION
├── Stealth Level (dropdown)
└── Proxy File (auto-fetch/browse)

⚡ FLASH ATTACK (button)
🚀 LAUNCH SCAN (button)
🛑 ABORT MISSION (button)
```

### Middle Panel - Intelligence

```
📊 SCAN OUTPUT
├── Real-time log (scrollable)
└── Status updates

🎯 DETECTED VULNERABILITIES
└── Findings list (scrollable)
```

### Right Panel - Exploit Factory

```
💣 EXPLOIT FACTORY
├── Vulnerability details
├── Full exploit URLs
├── CURL commands
├── Python scripts
└── Suggested payloads

📋 COPY PAYLOAD (button)
📄 OPEN REPORT (button)
```

### Footer

```
⚠️ For Authorized Security Testing Only | Status: Ready
```

- Safety reminder
- Real-time status

---

## 🔧 Advanced Features

### Aggressive Mode

When enabled:

- Crawl depth × 1.5
- Test intensity × 2
- Epsilon = 0.3 (more exploration)
- Higher noise level

### Auto-Fetch Proxies

Click 🔄 button to:

1. Fetch from 6 sources
2. Remove duplicates
3. Save to `proxies.txt`
4. Auto-load into scanner

Sources:

- free-proxy-list.net
- proxyscrape.com
- geonode.com
- proxy-list.download
- pubproxy.com
- GitHub proxy lists

### Exploit Factory

When you click a finding:

- **Full URLs**: `http://target.com?id=1' OR 1=1--`
- **CURL**: Ready-to-run commands
- **Python**: Auto-generated scripts
- **Payloads**: 200+ attack vectors

### Model Selection

Dropdown shows:

- `dqn_web_sec_model.pth (Final)`
- `checkpoints/multi_target_ep800.pth`
- `checkpoints/multi_target_ep700.pth`
- ... and more

**Tip**: Models sorted newest first!

---

## 🎮 Keyboard Shortcuts

- **Tab**: Navigate between fields
- **Enter**: Start scan (when button focused)
- **Esc**: Stop scan (when scanning)

---

## 🐛 Troubleshooting

### "No models found"

**Solution:**

```bash
# Train a model first
python train_multi_target.py --episodes 100
# Then restart GUI
python scanner_gui.py
```

### GUI doesn't open

**Solution:**

```bash
# Make sure tkinter is installed
python -m tkinter
# Should open a test window
```

### Proxy fetch fails

**Solution:**

- Check internet connection
- Some sources may be down
- Try manual proxy file upload

---

## 💡 Tips & Tricks

### Tip 1: Flash Attack

For quick scans:

1. Enter target URL
2. Click **⚡ FLASH ATTACK**
3. Done! (uses AUTO mode, depth=10, episodes=1)

### Tip 2: Aggressive Testing

For deep scans:

1. Select **🔥 AGGRESSIVE MODE**
2. Increase depth to 50+
3. Increase episodes to 5+
4. Enable proxies for stealth

### Tip 3: OSINT Only

For reconnaissance:

1. Select **🕵️ OSINT MODE**
2. No attacks will be performed
3. Only information gathering

### Tip 4: Exploit Generation

1. Run scan
2. Click on finding
3. Copy full URLs from Exploit Factory
4. Paste in browser/Burp Suite

---

## 🎯 Example Workflows

### Quick Scan (Flash Attack)

```
1. Enter: http://target.com
2. Click: ⚡ FLASH ATTACK
3. Wait: ~2 minutes
4. Review: Findings list
```

### Deep Penetration Test

```
1. Enter: http://target.com
2. Mode: 🔥 AGGRESSIVE
3. Depth: 50
4. Episodes: 5
5. Stealth: High
6. Proxies: Auto-fetch
7. Click: 🚀 LAUNCH SCAN
8. Wait: ~15 minutes
9. Review: Full report
```

### OSINT Reconnaissance

```
1. Enter: http://target.com
2. Mode: 🕵️ OSINT
3. Depth: 30
4. Click: 🚀 LAUNCH SCAN
5. Review: Discovered endpoints
```

---

## 📊 Comparison

| Feature            | GUI (2025) | Command Line |
| ------------------ | ---------- | ------------ |
| Ease of Use        | ⭐⭐⭐⭐⭐ | ⭐⭐⭐       |
| Visual Feedback    | ⭐⭐⭐⭐⭐ | ⭐⭐         |
| Real-time Progress | ⭐⭐⭐⭐⭐ | ⭐⭐⭐       |
| Exploit Generation | ⭐⭐⭐⭐⭐ | ⭐⭐⭐       |
| Proxy Management   | ⭐⭐⭐⭐⭐ | ⭐⭐⭐       |
| Automation         | ⭐⭐       | ⭐⭐⭐⭐⭐   |
| Resource Usage     | ⭐⭐⭐⭐   | ⭐⭐⭐⭐⭐   |
| Learning Curve     | ⭐⭐⭐⭐⭐ | ⭐⭐⭐       |

**Recommendation**: GUI for testing, CLI for automation!

---

## 🚀 Quick Reference

| Action        | How To                        |
| ------------- | ----------------------------- |
| Launch GUI    | `python scanner_gui.py`       |
| Quick scan    | Click "⚡ FLASH ATTACK"       |
| Full scan     | Click "🚀 LAUNCH SCAN"        |
| Stop scan     | Click "🛑 ABORT MISSION"      |
| Fetch proxies | Click "🔄" next to proxy file |
| View exploit  | Click finding in list         |
| Copy payload  | Click "📋 COPY PAYLOAD"       |
| View report   | Click "📄 OPEN REPORT"        |
| Change mode   | Select radio button           |
| Adjust depth  | Drag slider                   |

---

## 🎉 Summary

The 2025 GUI provides:

- ✅ Cyberpunk red team interface
- ✅ 4 scan modes (Auto/Aggressive/OSINT/Specific)
- ✅ Auto-fetch proxies (6 sources)
- ✅ Full exploit URLs (copy-paste ready)
- ✅ 200+ attack payloads
- ✅ Real-time feedback
- ✅ One-click Flash Attack
- ✅ Professional reports

**Perfect for:**

- Penetration testers
- Security researchers
- Bug bounty hunters
- Red team operations
- Security training

**Launch it now:**

```bash
python scanner_gui.py
```

Enjoy the ultimate hacking interface! 💀🔥

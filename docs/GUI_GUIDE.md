# 🖥️ GUI Scanner - User Guide

## Quick Start

### Launch the GUI

```bash
python scanner_gui.py
```

**That's it!** A beautiful window will open.

---

## 🎨 GUI Features

### Modern Dark Theme

- Professional cybersecurity aesthetic
- Easy on the eyes for long sessions
- High contrast for accessibility

### Easy Configuration

- **Target URL**: Just type or paste
- **Crawl Depth**: Slider (1-100 pages)
- **Test Episodes**: Slider (1-10 per page)
- **AI Model**: Dropdown with all available models

### Real-Time Feedback

- Live progress bar
- Status updates
- Scrolling log output
- Timestamp for each event

### One-Click Actions

- 🚀 **Start Scan**: Begin scanning
- ⏹️ **Stop Scan**: Cancel anytime
- 📄 **View Report**: Open HTML report in browser
- 🗑️ **Clear Log**: Clean output window

---

## 📋 Step-by-Step Usage

### 1. Launch GUI

```bash
cd d:\github\RL
python scanner_gui.py
```

### 2. Configure Scan

- **Target URL**: Enter `http://localhost/dvwa`
- **Crawl Depth**: Adjust slider (default: 30)
- **Test Episodes**: Adjust slider (default: 3)
- **AI Model**: Select from dropdown (use latest for best results)

### 3. Start Scan

- Click **🚀 Start Scan**
- Confirm the settings
- Watch real-time progress!

### 4. Monitor Progress

- Progress bar shows activity
- Status label shows current phase
- Log shows detailed output

### 5. View Results

- Click **📄 View HTML Report** when done
- Report opens in your browser
- Beautiful, professional format!

---

## 🎯 GUI vs Command Line

### Use GUI When:

- ✅ You prefer visual interfaces
- ✅ You want to see real-time progress
- ✅ You're new to command line
- ✅ You want easy model selection
- ✅ You like clicking buttons

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
🛡️ AI-Powered Web Security Scanner
```

- Shows app name and icon
- Professional branding

### Left Panel - Configuration

```
⚙️ Configuration
├── 🎯 Target URL
├── 🕷️ Crawl Depth (slider)
├── 🔄 Test Episodes (slider)
├── 🤖 AI Model (dropdown)
├── 🚀 Start Scan (button)
└── ⏹️ Stop Scan (button)
```

### Right Panel - Output

```
📊 Scan Output
├── Progress Bar
├── Status Label
├── Log Output (scrollable)
├── 📄 View HTML Report (button)
└── 🗑️ Clear Log (button)
```

### Footer

```
⚠️ For Authorized Security Testing Only
```

- Safety reminder
- Version info

---

## 🔧 Advanced Features

### Model Selection

The dropdown shows all available models:

- `dqn_web_sec_model.pth (Final - Best Quality)`
- `checkpoints/dqn_checkpoint_ep500.pth (Episode 500)`
- `checkpoints/dqn_checkpoint_ep400.pth (Episode 400)`
- ... and more

**Tip**: Models are sorted newest first!

### Real-Time Logging

Log entries show:

- `[12:34:56] ℹ️ Info message`
- `[12:34:57] ✅ Success message`
- `[12:34:58] ⚠️ Warning message`
- `[12:34:59] ❌ Error message`

Color-coded icons for quick scanning!

### Progress Tracking

- **Animated progress bar** during scan
- **Status updates** for each phase:
  - "Ready to scan"
  - "Scanning in progress..."
  - "Scan complete - X vulnerabilities found"

---

## 🎮 Keyboard Shortcuts

While the GUI is focused:

- **Tab**: Navigate between fields
- **Enter**: Start scan (when Start button focused)
- **Esc**: Stop scan (when scanning)
- **Ctrl+L**: Clear log (custom shortcut)

---

## 🐛 Troubleshooting

### "No models found"

**Solution:**

```bash
# Train a model first
python train.py
# Then restart GUI
python scanner_gui.py
```

### GUI doesn't open

**Solution:**

```bash
# Make sure tkinter is installed (usually comes with Python)
python -m tkinter
# Should open a test window
```

### "Model file not found"

**Solution:**

- Check that the model file exists
- Refresh model list (restart GUI)
- Train a new model if needed

---

## 💡 Tips & Tricks

### Tip 1: Use Sliders

- Drag sliders for quick adjustments
- Current value shown on the right
- Instant visual feedback

### Tip 2: Monitor Logs

- Scroll through logs during scan
- Auto-scrolls to latest entry
- Clear when needed for fresh view

### Tip 3: Compare Models

```
1. Scan with ep100
2. Note results
3. Scan with ep500
4. Compare reports
```

### Tip 4: Save Configuration

The GUI remembers your last settings!

- Target URL
- Depth
- Episodes
- Model selection

---

## 🎯 Example Workflow

### Scanning DVWA with GUI

**Step 1: Launch**

```bash
python scanner_gui.py
```

**Step 2: Configure**

- Target: `http://localhost/dvwa`
- Depth: `30` (slider)
- Episodes: `3` (slider)
- Model: `dqn_web_sec_model.pth (Final - Best Quality)`

**Step 3: Scan**

- Click **🚀 Start Scan**
- Confirm dialog: **Yes**
- Watch progress!

**Step 4: Results**

- Wait for "Scan complete" message
- Click **📄 View HTML Report**
- Review findings in browser

**Step 5: Next Scan**

- Change target URL
- Click **🚀 Start Scan** again
- That's it!

---

## 🎨 Accessibility Features

### Visual

- ✅ High contrast dark theme
- ✅ Large, readable fonts
- ✅ Color-coded status icons
- ✅ Clear button labels

### Interaction

- ✅ Keyboard navigation (Tab)
- ✅ Mouse-friendly buttons
- ✅ Slider controls
- ✅ Confirmation dialogs

### Feedback

- ✅ Real-time status updates
- ✅ Progress indicators
- ✅ Success/error messages
- ✅ Timestamped logs

---

## 📊 Comparison

| Feature            | GUI        | Command Line |
| ------------------ | ---------- | ------------ |
| Ease of Use        | ⭐⭐⭐⭐⭐ | ⭐⭐⭐       |
| Visual Feedback    | ⭐⭐⭐⭐⭐ | ⭐⭐         |
| Real-time Progress | ⭐⭐⭐⭐⭐ | ⭐⭐⭐       |
| Automation         | ⭐⭐       | ⭐⭐⭐⭐⭐   |
| Resource Usage     | ⭐⭐⭐⭐   | ⭐⭐⭐⭐⭐   |
| Learning Curve     | ⭐⭐⭐⭐⭐ | ⭐⭐⭐       |

**Recommendation**: Start with GUI, use CLI for automation!

---

## 🚀 Quick Reference

| Action       | How To                      |
| ------------ | --------------------------- |
| Launch GUI   | `python scanner_gui.py`     |
| Start scan   | Click "🚀 Start Scan"       |
| Stop scan    | Click "⏹️ Stop Scan"        |
| View report  | Click "📄 View HTML Report" |
| Clear log    | Click "🗑️ Clear Log"        |
| Change model | Select from dropdown        |
| Adjust depth | Drag slider                 |

---

## 🎉 Summary

The GUI provides:

- ✅ Beautiful, modern interface
- ✅ Easy configuration
- ✅ Real-time feedback
- ✅ One-click scanning
- ✅ Professional results

**Perfect for:**

- Beginners
- Visual learners
- Quick scans
- Demonstrations
- Non-technical users

**Launch it now:**

```bash
python scanner_gui.py
```

Enjoy the beautiful interface! 🎨

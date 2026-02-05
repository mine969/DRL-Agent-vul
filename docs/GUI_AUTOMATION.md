# 🤖 GUI Automation Guide

## GUI Now Has Full Automation Support! ⚡

The GUI can now be used in **two modes**:

### 1. Interactive Mode (GUI)

```bash
python scanner_gui.py
```

Beautiful graphical interface - click and scan!

### 2. Automated Mode (Headless)

```bash
python scanner_gui.py --auto --target http://site.com
```

No GUI, runs directly - perfect for automation!

---

## 🎯 Automated Mode Usage

### Basic Automated Scan

```bash
python scanner_gui.py --auto --target http://localhost/dvwa
```

### Custom Parameters

```bash
python scanner_gui.py --auto --target http://site.com --depth 50 --episodes 5
```

### Specific Model

```bash
python scanner_gui.py --auto --target http://site.com --model checkpoints/dqn_checkpoint_ep500.pth
```

---

## 📊 Performance Comparison (Updated!)

| Feature          | GUI (Interactive) | GUI (Automated) | CLI        |
| ---------------- | ----------------- | --------------- | ---------- |
| Ease of Use      | ⭐⭐⭐⭐⭐        | ⭐⭐⭐⭐        | ⭐⭐⭐     |
| Visual Feedback  | ⭐⭐⭐⭐⭐        | ⭐⭐⭐          | ⭐⭐       |
| Automation       | ⭐⭐⭐⭐⭐        | ⭐⭐⭐⭐⭐      | ⭐⭐⭐⭐⭐ |
| Scripting        | ⭐⭐⭐⭐⭐        | ⭐⭐⭐⭐⭐      | ⭐⭐⭐⭐⭐ |
| Resource Usage   | ⭐⭐⭐⭐          | ⭐⭐⭐⭐⭐      | ⭐⭐⭐⭐⭐ |
| Batch Processing | ⭐⭐⭐⭐⭐        | ⭐⭐⭐⭐⭐      | ⭐⭐⭐⭐⭐ |

**Now GUI = CLI for automation!** ✅

---

## 🚀 Automation Examples

### Example 1: Batch Scanning

```bash
# scan_multiple.bat
python scanner_gui.py --auto --target http://site1.com --depth 30
python scanner_gui.py --auto --target http://site2.com --depth 30
python scanner_gui.py --auto --target http://site3.com --depth 30
```

### Example 2: Scheduled Scan

```bash
# Windows Task Scheduler
python scanner_gui.py --auto --target http://my-site.com --depth 50
```

### Example 3: CI/CD Pipeline

```yaml
# .github/workflows/security-scan.yml
- name: Security Scan
  run: |
    python scanner_gui.py --auto --target http://staging.example.com
```

### Example 4: Different Models

```bash
# Test with multiple models
python scanner_gui.py --auto --target http://site.com --model checkpoints/dqn_checkpoint_ep100.pth
python scanner_gui.py --auto --target http://site.com --model checkpoints/dqn_checkpoint_ep300.pth
python scanner_gui.py --auto --target http://site.com --model dqn_web_sec_model.pth
```

---

## 📋 Command-Line Arguments

| Argument     | Required          | Default               | Description                    |
| ------------ | ----------------- | --------------------- | ------------------------------ |
| `--auto`     | For automation    | -                     | Enable automated mode (no GUI) |
| `--target`   | Yes (with --auto) | -                     | Target URL to scan             |
| `--depth`    | No                | 30                    | Maximum pages to crawl         |
| `--episodes` | No                | 3                     | Test episodes per page         |
| `--model`    | No                | dqn_web_sec_model.pth | Model file to use              |

---

## 🎮 When to Use Each Mode

### Use Interactive GUI When:

- ✅ Learning the tool
- ✅ One-off scans
- ✅ Want visual feedback
- ✅ Prefer clicking over typing
- ✅ Demonstrating to others

### Use Automated GUI When:

- ✅ Batch processing
- ✅ Scheduled scans
- ✅ CI/CD pipelines
- ✅ Scripting
- ✅ Running on servers
- ✅ No display available

### Use CLI (scan.py/autonomous_scan.py) When:

- ✅ You prefer traditional CLI tools
- ✅ Already have scripts using it
- ✅ Personal preference

**All three options are equally powerful now!** 🎉

---

## 💡 Pro Tips

### Tip 1: Silent Batch Processing

```bash
# Redirect output to log file
python scanner_gui.py --auto --target http://site.com > scan_log.txt 2>&1
```

### Tip 2: Error Handling in Scripts

```bash
# Check exit code
python scanner_gui.py --auto --target http://site.com
if %ERRORLEVEL% NEQ 0 (
    echo Scan failed!
    exit /b 1
)
```

### Tip 3: Parse Reports Programmatically

```python
import glob
import os

# Find latest report
reports = glob.glob("vulnerability_report_*.txt")
latest = max(reports, key=os.path.getctime)

# Parse it
with open(latest) as f:
    content = f.read()
    if "CRITICAL" in content:
        print("Critical vulnerabilities found!")
    if "Flags Captured" in content or "CTF{" in content:
        print("Captured flags detected in report!")
```

---

## 🔄 Migration from CLI

### Before (CLI)

```bash
python autonomous_scan.py http://site.com --depth 50 --episodes 5
```

### After (GUI Automated)

```bash
python scanner_gui.py --auto --target http://site.com --depth 50 --episodes 5
```

**Same functionality, same performance!** ✅

---

## 📊 Output Format

### Automated Mode Output

```
======================================================================
🛡️  AI-POWERED WEB SECURITY SCANNER - AUTOMATED MODE
======================================================================

🎯 Target:       http://localhost/dvwa
🕷️  Crawl Depth:  30 pages
🔄 Episodes:     3 per page
🤖 Model:        dqn_web_sec_model.pth

======================================================================
⚠️  Make sure you have permission to test this target!
======================================================================

[12:34:56] ℹ️  Starting scan...
[12:35:01] ✅ Scan complete!

📊 Results:
   - Vulnerabilities found: 3

📁 Reports saved:
   - vulnerability_report_20251123_123501.html (HTML)
   - vulnerability_report_20251123_123501.txt (TXT)
   - vulnerability_report_20251123_123501.md (MD)

======================================================================
✅ Automated scan completed successfully!
======================================================================
```

---

## 🎯 Summary

### GUI Automation Features ✨ NEW!

✅ **Command-line arguments** - Full automation support  
✅ **Headless mode** - No GUI required  
✅ **Same performance** - Identical to CLI  
✅ **Batch processing** - Multiple targets  
✅ **Scriptable** - Use in any script  
✅ **Exit codes** - Proper error handling  
✅ **Flexible** - Interactive OR automated

### Why This Is Better

**Before:**

- GUI = Interactive only (⭐⭐ for automation)
- CLI = Automation only

**Now:**

- GUI = Interactive AND Automated (⭐⭐⭐⭐⭐ for both!)
- CLI = Still available for those who prefer it

**You get the best of both worlds!** 🎉

---

## 🚀 Get Started

### Interactive Mode

```bash
python scanner_gui.py
```

### Automated Mode

```bash
python scanner_gui.py --auto --target http://your-site.com
```

### Help

```bash
python scanner_gui.py --help
```

**Now the GUI is just as powerful as CLI for automation!** ⚡

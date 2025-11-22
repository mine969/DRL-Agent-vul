# 🚀 Super Simple Scanner - Quick Start

## The Easiest Way to Scan!

Just run **one command** and answer the questions:

```bash
python scan.py
```

That's it! No complicated commands to remember!

## What It Does

The script will ask you:

1. **"Enter website URL or IP"**

   - Type: `http://localhost/dvwa`
   - Or: `192.168.1.100`
   - Or: `example.com` (it adds http:// automatically)

2. **"Is this correct?"**

   - Type: `y` and press Enter

3. **"Customize scan options?"**
   - Type: `n` for default settings (recommended)
   - Or `y` to customize depth and episodes

Then it automatically:

- 🕷️ Crawls the website
- 🔍 Finds all pages
- 🔴 Tests for vulnerabilities
- 📊 Creates 3 reports (HTML, TXT, MD)

## Example Session

```
🛡️  AI-POWERED WEB SECURITY SCANNER
======================================================================

🎯 Enter website URL or IP: localhost/dvwa
ℹ️  Adding 'http://' prefix...

📍 Target: http://localhost/dvwa
Is this correct? (y/n): y

Would you like to customize scan options?
(y/n) [default: n]: n

======================================================================
SCAN CONFIGURATION
======================================================================
Target URL:       http://localhost/dvwa
Max Pages:        30
Episodes/Page:    3
Model:            dqn_web_sec_model.pth
======================================================================

⚠️  Ready to start scanning!
Press Enter to begin (or Ctrl+C to cancel)...

🚀 Starting scan...
```

## Reports Generated

After scanning, you'll get **3 files**:

1. **`vulnerability_report_[timestamp].html`**

   - Beautiful report with colors
   - Open in Chrome/Firefox
   - Best for presentations

2. **`vulnerability_report_[timestamp].txt`**

   - Plain text format
   - Easy to read in Notepad
   - Good for quick review

3. **`vulnerability_report_[timestamp].md`**
   - Markdown format
   - Good for documentation

## Comparison

### Old Way ❌

```bash
python autonomous_scan.py --target http://localhost/dvwa --depth 30 --episodes 3 --model dqn_web_sec_model.pth
```

Too complicated to remember!

### New Way ✅

```bash
python scan.py
```

Just answer simple questions!

## Tips

- **First time?** Just press Enter for all questions (uses defaults)
- **Want more pages?** Say `y` to customize, then enter a higher number
- **Wrong URL?** Press Ctrl+C and start again
- **No model found?** Train first: `python train.py`

## Troubleshooting

**"Model file not found"**

- Run `python train.py` first to train the AI
- Or use a checkpoint: when asked for model, type `checkpoints/dqn_checkpoint_ep100.pth`

**"Connection refused"**

- Make sure the target website is running
- Check if you typed the URL correctly

**Want to stop?**

- Press `Ctrl+C` anytime

## All Available Scanners

| Script               | Usage                        | Best For       |
| -------------------- | ---------------------------- | -------------- |
| `scan.py`            | Interactive (asks questions) | **Beginners**  |
| `autonomous_scan.py` | Command-line with arguments  | Advanced users |
| `deploy_agent.py`    | Test specific URLs           | Quick tests    |

**Recommendation**: Start with `scan.py` - it's the easiest!

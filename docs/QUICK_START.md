# 🚀 Quick Start Guide (2025 Edition)

## Installation

### 1. Clone Repository

```bash
git clone https://github.com/yourusername/RL.git
cd RL
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Verify Installation

```bash
python -c "import torch; print(torch.cuda.is_available())"
# Should print: True (if you have GPU)
```

---

## Training Your First Agent

### Option 1: Quick Training (2000 episodes)

```bash
python train_multi_target.py --episodes 2000
```

**Time**: ~32 hours  
**Result**: Decent agent for testing

### Option 2: Production Agent (5000 episodes)

```bash
python train_multi_target.py --episodes 5000
```

**Time**: ~80 hours  
**Result**: Professional-grade agent

### Option 3: Resume Training

```bash
# Auto-resume from latest checkpoint
python train_multi_target.py --latest --episodes 5000

# Resume from specific episode
python train_multi_target.py --resume 2000 --episodes 5000
```

---

## Using the Scanner

### GUI Mode (Recommended for Beginners)

```bash
python scanner_gui.py
```

**Features**:

- 🎯 Visual interface
- 🔥 Aggressive scan mode
- 🔄 Auto-fetch proxies (6 sources)
- 📋 Full exploit URLs
- ⚡ One-click Flash Attack

**Quick Workflow**:

1. Enter target URL
2. Click "⚡ FLASH ATTACK"
3. Review findings
4. Click finding for exploit code

### Command Line Mode

```bash
# Basic scan
python autonomous_scan.py --target http://example.com

# Aggressive scan
python autonomous_scan.py --target http://example.com --mode aggressive

# OSINT only
python autonomous_scan.py --target http://example.com --mode osint

# Specific attack
python autonomous_scan.py --target http://example.com --mode specific --attack "SQL Injection"
```

---

## Scan Modes

### AUTO Mode (Default)

```bash
python autonomous_scan.py --target http://example.com --mode auto
```

- AI agent decides actions
- Balanced approach
- Low noise level

### AGGRESSIVE Mode

```bash
python autonomous_scan.py --target http://example.com --mode aggressive
```

- 1.5x crawl depth
- 2x test intensity
- More exploration (epsilon=0.3)
- Higher noise level

### OSINT Mode

```bash
python autonomous_scan.py --target http://example.com --mode osint
```

- Reconnaissance only
- No attacks performed
- Silent operation

### SPECIFIC Mode

```bash
python autonomous_scan.py --target http://example.com --mode specific --attack "XSS"
```

- Test single vulnerability
- Faster execution
- Focused testing

### ZERO-DAY Mode

```bash
python autonomous_scan.py --target http://example.com --mode zeroday
```

- Fuzzing and mutation testing
- CVE intelligence integration
- Configuration vulnerability scanning
- Discovers unknown vulnerabilities

### TARGETLESS Mode

```bash
# Using Google Dorks
python autonomous_scan.py --mode targetless --google-dork "inurl:admin.php"

# Using Shodan
python autonomous_scan.py --mode targetless --shodan-query "apache" --shodan-key YOUR_KEY

# Using CRT.sh (Certificate Transparency)
python autonomous_scan.py --mode targetless --crtsh example.com

# Using DuckDuckGo
python autonomous_scan.py --mode targetless --duckduckgo "site:example.com login"

# Using Censys
python autonomous_scan.py --mode targetless --censys-query "services.http.response.body:admin" --censys-id YOUR_ID --censys-secret YOUR_SECRET

# Combine multiple sources
python autonomous_scan.py --mode targetless --google-dork "inurl:login" --shodan-query "apache" --shodan-key YOUR_KEY
```

- Auto-discovers targets via OSINT
- 5 discovery sources available
- Autonomous target hunting
- Perfect for bug bounty hunting

---

## Using Proxies

### Auto-Fetch (GUI)

1. Open GUI
2. Click 🔄 button next to proxy file
3. Wait for fetch (200+ proxies)
4. Proxies auto-loaded

### Manual (CLI)

```bash
# Create proxy file
echo "http://proxy1.com:8080" > proxies.txt
echo "http://proxy2.com:3128" >> proxies.txt

# Use in scan
python autonomous_scan.py --target http://example.com --proxy-file proxies.txt
```

### Proxy Sources

The auto-fetch pulls from:

- free-proxy-list.net
- proxyscrape.com
- geonode.com
- proxy-list.download
- pubproxy.com
- GitHub proxy lists

---

## Stealth Levels

```bash
# Low stealth (fast)
python autonomous_scan.py --target http://example.com --stealth low

# Medium stealth (balanced)
python autonomous_scan.py --target http://example.com --stealth medium

# High stealth (slow, careful)
python autonomous_scan.py --target http://example.com --stealth high

# Paranoid (very slow, maximum stealth)
python autonomous_scan.py --target http://example.com --stealth paranoid
```

**Stealth affects**:

- Request delays
- User-Agent rotation
- Proxy usage
- Request patterns

---

## Viewing Reports

### HTML Report (Best)

```bash
# Auto-opens in browser after scan
# Or manually:
start reports/vulnerability_report_TIMESTAMP.html  # Windows
open reports/vulnerability_report_TIMESTAMP.html   # Mac
xdg-open reports/vulnerability_report_TIMESTAMP.html  # Linux
```

### Markdown Report

```bash
# View in editor
code reports/vulnerability_report_TIMESTAMP.md
```

### Text Report

```bash
# View in terminal
cat reports/vulnerability_report_TIMESTAMP.txt
```

---

## Common Workflows

### Workflow 1: Quick Bug Bounty Scan

```bash
# 1. GUI Flash Attack
python scanner_gui.py
# Enter target, click ⚡ FLASH ATTACK

# 2. Review findings
# Click on finding for exploit URLs

# 3. Test manually
# Copy full URL, paste in browser/Burp
```

### Workflow 2: Deep Penetration Test

```bash
# 1. Aggressive scan with proxies
python autonomous_scan.py \
  --target http://target.com \
  --mode aggressive \
  --crawl-depth 50 \
  --intensity 5 \
  --stealth high \
  --proxy-file proxies.txt

# 2. Review comprehensive report
start reports/vulnerability_report_*.html

# 3. Exploit findings
# Use generated CURL/Python scripts
```

### Workflow 3: OSINT Reconnaissance

```bash
# 1. Silent information gathering
python autonomous_scan.py \
  --target http://target.com \
  --mode osint \
  --crawl-depth 100

# 2. Analyze discovered endpoints
# Check report for sensitive files

# 3. Plan attack strategy
# Based on discovered attack surface
```

### Workflow 4: Zero-Day Hunting

```bash
# 1. Run Zero-Day Hunter mode
python autonomous_scan.py \
  --target http://target.com \
  --mode zeroday \
  --crawl-depth 30 \
  --intensity 5

# 2. Review fuzzing results
# Check for crashes, errors, unusual responses

# 3. Investigate CVE intelligence findings
# Verify version-specific vulnerabilities
```

### Workflow 5: Targetless Bug Bounty Hunting

```bash
# 1. Auto-discover targets using multiple sources
python autonomous_scan.py \
  --mode targetless \
  --google-dork "inurl:admin site:.edu" \
  --shodan-query "apache 2.4" \
  --shodan-key YOUR_KEY \
  --crtsh example.com

# 2. Agent scans all discovered targets
# Automatically tests each found URL

# 3. Review consolidated report
# All findings from all targets in one report
```

---

## Troubleshooting

### "No models found"

```bash
# Train a model first
python train_multi_target.py --episodes 1000
```

### "CUDA out of memory"

```bash
# Reduce batch size in train_multi_target.py
# Change: batch_size = 4096
# To: batch_size = 2048
```

### "Connection refused"

```bash
# Make sure target is running
# Check firewall settings
# Try with http:// instead of https://
```

### "No vulnerabilities found"

```bash
# Try aggressive mode
python autonomous_scan.py --target http://target.com --mode aggressive

# Or increase depth/intensity
python autonomous_scan.py --target http://target.com --crawl-depth 50 --intensity 5
```

---

## Next Steps

### After Your First Scan

1. ✅ Review the HTML report
2. ✅ Test exploit URLs manually
3. ✅ Try different scan modes
4. ✅ Experiment with stealth levels

### Improve Your Agent

1. ✅ Train longer (5000+ episodes)
2. ✅ Test on multiple targets
3. ✅ Compare checkpoint performance
4. ✅ Fine-tune hyperparameters

### Advanced Usage

1. ✅ Read `DEPLOYMENT_GUIDE.md`
2. ✅ Check `REAL_WORLD_USAGE.md`
3. ✅ Study `TRAINING_RECOMMENDATIONS.md`
4. ✅ Explore `GUI_GUIDE.md`

---

## Quick Reference

| Task             | Command                                                                                     |
| ---------------- | ------------------------------------------------------------------------------------------- |
| Train agent      | `python train_multi_target.py --episodes 5000`                                              |
| Resume training  | `python train_multi_target.py --latest --episodes 5000`                                     |
| GUI scan         | `python scanner_gui.py`                                                                     |
| CLI scan         | `python autonomous_scan.py --target URL`                                                    |
| Aggressive scan  | `python autonomous_scan.py --target URL --mode aggressive`                                  |
| OSINT only       | `python autonomous_scan.py --target URL --mode osint`                                       |
| Zero-Day hunting | `python autonomous_scan.py --target URL --mode zeroday`                                     |
| Targetless scan  | `python autonomous_scan.py --mode targetless --google-dork "query" --shodan-query "apache"` |
| With proxies     | `python autonomous_scan.py --target URL --proxy-file proxies.txt`                           |
| High stealth     | `python autonomous_scan.py --target URL --stealth high`                                     |

---

## Getting Help

- 📖 Read the docs in `docs/` folder
- 🐛 Check `TROUBLESHOOTING.md`
- 💬 Open an issue on GitHub
- 📧 Contact the maintainers

---

## ⚠️ Legal Notice

**This tool is for authorized security testing only.**

- ✅ Get written permission before scanning
- ✅ Only test systems you own or have authorization for
- ❌ Unauthorized scanning is illegal
- ❌ You are responsible for your actions

**Use responsibly!** 🛡️

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
python train_mock_targets.py --episodes 2000
```

**Time**: ~32 hours  
**Result**: Decent agent for testing

### Option 2: Production Agent (5000 episodes)

```bash
python quick_train_5000.py
```

**Time**: ~80 hours  
**Result**: Professional-grade agent

### Option 3: Resume Training

```bash
# Auto-resume from latest checkpoint
python train_mock_targets.py --episodes 5000

# Force a clean start (ignore checkpoints)
python quick_train_5000.py --fresh
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
python autonomous_scan.py http://example.com --depth 20 --intensity 5

# Deep scan with Full AI behavior
python autonomous_scan.py http://example.com --depth 50 --intensity 8 --ai-mode --pentester

# Persist until a vulnerability is found
python autonomous_scan.py http://example.com --depth 30 --intensity 5 --persist

# Use a specific model checkpoint
python autonomous_scan.py http://example.com --model checkpoints/improved_mock_ep1000.pth
```

---

## Scan Modes (Current CLI)

The CLI supports depth/intensity plus AI flags for deeper scans:

- `--ai-mode` enables Full AI reconnaissance + learning
- `--pentester` enables chain attacks (deeper exploration)
- `--persist` keeps trying until a vulnerability is found
- `--model` loads a specific checkpoint

### CLI Examples

```bash
# Balanced scan
python autonomous_scan.py http://example.com --depth 20 --intensity 5

# Deep scan with full AI behavior
python autonomous_scan.py http://example.com --depth 50 --intensity 8 --ai-mode --pentester

# Persist until a vulnerability is found
python autonomous_scan.py http://example.com --depth 30 --intensity 5 --persist
```

### GUI-Only Features

The GUI includes OSINT-only recon, specific vulnerability targeting, targetless hunting, proxy fetching, and stealth profiles.

```bash
python scanner_gui.py
```

---

## Troubleshooting

### "No models found"

```bash
# Train a model first
python train_mock_targets.py --episodes 1000
```

### "CUDA out of memory"

```bash
# Reduce batch size in config.py
# Change: batch_size = 64
# To: batch_size = 32
```

### "Connection refused"

```bash
# Make sure target is running
# Check firewall settings
# Try with http:// instead of https://
```

### "No vulnerabilities found"

```bash
# Try a deeper scan
python autonomous_scan.py http://target.com --depth 50 --intensity 8 --ai-mode --pentester

# Or increase depth/intensity
python autonomous_scan.py http://target.com --depth 50 --intensity 5
```

---

## Next Steps

### After Your First Scan

1. ✅ Review the HTML report (includes captured flags and evidence)
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

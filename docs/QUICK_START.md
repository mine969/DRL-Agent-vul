# Quick Start Guide

## Prerequisites

- Python 3.8+
- CUDA-capable GPU (recommended: RTX 2070 or better)
- 2GB+ free disk space

## Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/DRL-Agent-vul.git
cd DRL-Agent-vul

# Create virtual environment
python -m venv .venv
.venv\Scripts\activate  # Windows
# source .venv/bin/activate  # Linux/Mac

# Install dependencies
pip install -r requirements.txt
```

## Training the Agent

### Start Fresh Training

```bash
python train_multi_target.py --episodes 2000
```

### Resume Training

```bash
python train_multi_target.py --episodes 2000 --resume 1000
```

### Training Features

- **Checkpoints:** Saved every 10 episodes
- **Auto-save:** Press Ctrl+C to save and stop
- **GPU Acceleration:** Automatic CUDA detection
- **Progress Tracking:** Real-time metrics in terminal

## Using the Trained Agent

### Autonomous Scanning

```bash
python autonomous_scan.py --target http://example.com
```

### Interactive GUI

```bash
python scanner_gui.py
```

## Architecture Overview

**Kill Chain (100 Actions):**

1. **Reconnaissance (0-29):** OSINT, port scanning, subdomain enumeration
2. **Discovery (30-59):** Vulnerability probing, injection testing
3. **Exploitation (60-89):** Advanced attacks, RCE, cloud exploits
4. **Post-Exploitation (90-99):** Data exfiltration, privilege escalation

**Phase-Based Reward Shaping:**

- Progressive unlocking of attack phases
- +10 bonus for correct phase actions
- +20 bonus for phase completion
- -5 penalty for skipping phases

## Training Targets

The agent trains against 6 targets:

1. localhost:5001 - Core vulnerabilities
2. localhost:5002 - E-commerce platform
3. localhost:5003 - Social media app
4. levelup.melivecode.com - LMS platform
5. rsuip.org - University portal
6. dit.rsu.ac.th - Department site

## Expected Results

- **Training Time:** 16-20 hours (2000 episodes)
- **Checkpoints:** 200 files (~1.7 GB)
- **GPU Usage:** 90-95% utilization
- **Success Rate:** Improves progressively

## Troubleshooting

**GPU Not Detected:**

```bash
python -c "import torch; print(torch.cuda.is_available())"
```

**Training Crashes:**

- Check target apps are running
- Verify sufficient disk space
- Review last checkpoint

**Slow Training:**

- Ensure TF32 is enabled
- Check GPU temperature
- Reduce batch size if OOM

## Next Steps

1. Monitor training progress
2. Evaluate checkpoints at ep500, ep1000, ep1500
3. Deploy best checkpoint for real-world scanning
4. Review `docs/` for advanced usage

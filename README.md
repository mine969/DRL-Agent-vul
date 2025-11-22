# 🛡️ AI-Powered Web Security Scanner

**Autonomous Deep Reinforcement Learning agent for web vulnerability discovery**

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![PyTorch](https://img.shields.io/badge/PyTorch-2.7+-red.svg)](https://pytorch.org/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![GPU](https://img.shields.io/badge/GPU-Accelerated-brightgreen.svg)](docs/GPU_SUCCESS.md)

---

## 🚀 Quick Start

### For Beginners (GUI)

```bash
python scanner_gui.py
```

Beautiful graphical interface - just enter a URL and click scan!

### For Command Line Users

```bash
python scan.py
```

Interactive terminal - answer simple questions and go!

### For Advanced Users

```bash
python autonomous_scan.py http://target.com --depth 50 --episodes 5
```

---

## ✨ Features

- 🤖 **AI-Powered**: Deep Q-Network (DQN) trained on 500 episodes
- 🕷️ **Autonomous Discovery**: Automatically crawls and finds pages
- 🎯 **15 Attack Vectors**: SQLi, XSS, IDOR, SSRF, Command Injection, and more
- 📊 **Professional Reports**: HTML, TXT, and Markdown formats
- ⚡ **GPU Accelerated**: 10-15x faster training with CUDA
- 🎨 **Modern GUI**: Beautiful dark-themed interface
- 🔄 **Checkpoint System**: 25+ model versions to choose from

---

## 📁 Project Structure

```
d:/github/RL/
├── 📄 README.md                 # This file
├── 📄 requirements.txt          # Python dependencies
│
├── 🎮 Main Scripts
│   ├── scanner_gui.py           # GUI application (easiest!)
│   ├── scan.py                  # Interactive CLI scanner
│   ├── autonomous_scan.py       # Advanced scanner
│   ├── train.py                 # Training script
│   └── deploy_agent.py          # Quick testing tool
│
├── 🧠 Core Components
│   ├── agent/
│   │   └── dqn_agent.py        # DQN implementation
│   └── env/
│       ├── web_sec_env.py      # Gymnasium environment
│       ├── target_app.py       # Flask test server
│       └── templates/          # Modern UI
│
├── 💾 Models & Checkpoints
│   ├── checkpoints/            # Training checkpoints (ep20, ep40, ...)
│   └── dqn_web_sec_model.pth   # Final trained model
│
└── 📚 Documentation
    ├── BEGINNER_GUIDE.md       # Complete beginner's guide
    ├── QUICK_START.md          # Quick reference
    ├── GUI_GUIDE.md            # GUI usage guide
    ├── REAL_WORLD_USAGE.md     # Practical examples
    ├── AUTONOMOUS_SCAN_GUIDE.md # Advanced scanning
    ├── DEPLOYMENT_GUIDE.md     # DVWA deployment
    ├── CHECKPOINT_SYSTEM.md    # Model management
    ├── SPEED_UP_TRAINING.md    # Training optimization
    ├── GPU_SUCCESS.md          # GPU setup
    ├── CLEANUP_GUIDE.md        # File management
    └── TRANSFER_LEARNING.md    # Pre-trained models
```

---

## 🎯 Usage Options

### Option 1: GUI (Recommended for Beginners)

```bash
python scanner_gui.py
```

- Beautiful dark-themed interface
- Real-time progress tracking
- One-click scanning
- Visual model selection

**See**: [GUI Guide](docs/GUI_GUIDE.md)

### Option 2: Interactive CLI

```bash
python scan.py
```

- Simple question-and-answer format
- No complex commands
- Automatic page discovery
- 3 report formats (HTML/TXT/MD)

**See**: [Quick Start Guide](docs/QUICK_START.md)

### Option 3: Advanced CLI

```bash
python autonomous_scan.py http://target.com --depth 50 --episodes 5 --model checkpoints/dqn_checkpoint_ep500.pth
```

- Full control over parameters
- Scriptable and automatable
- Batch processing support

**See**: [Autonomous Scan Guide](docs/AUTONOMOUS_SCAN_GUIDE.md)

---

## 📖 Documentation

### Getting Started

- 📘 [**Beginner's Guide**](docs/BEGINNER_GUIDE.md) - Complete guide for non-technical users
- 🚀 [**Quick Start**](docs/QUICK_START.md) - Get scanning in 5 minutes
- 🖥️ [**GUI Guide**](docs/GUI_GUIDE.md) - Using the graphical interface

### Usage Guides

- 🌐 [**Real-World Usage**](docs/REAL_WORLD_USAGE.md) - Practical scanning examples
- 🕷️ [**Autonomous Scanning**](docs/AUTONOMOUS_SCAN_GUIDE.md) - Advanced features
- 🎯 [**Deployment Guide**](docs/DEPLOYMENT_GUIDE.md) - Testing against DVWA

### Technical Documentation

- 💾 [**Checkpoint System**](docs/CHECKPOINT_SYSTEM.md) - Model management
- ⚡ [**Speed Up Training**](docs/SPEED_UP_TRAINING.md) - Optimization tips
- 🎮 [**GPU Setup**](docs/GPU_SUCCESS.md) - CUDA acceleration
- 🔄 [**Transfer Learning**](docs/TRANSFER_LEARNING.md) - Pre-trained models
- 🧹 [**Cleanup Guide**](docs/CLEANUP_GUIDE.md) - File management

---

## 🎓 Training

### First Time Training

```bash
python train.py
```

- Trains for 500 episodes (~1-2 hours with GPU)
- Saves checkpoints every 20 episodes
- Auto-resumes from latest checkpoint
- GPU accelerated (10-15x faster)

### Resume Training

```bash
python train.py
```

Automatically detects and resumes from the latest checkpoint!

**See**: [Speed Up Training Guide](docs/SPEED_UP_TRAINING.md)

---

## 📊 Reports

Each scan generates **3 comprehensive reports**:

### 1. HTML Report (Best for Viewing)

- Beautiful, color-coded interface
- CVSS scores and impact levels
- Step-by-step exploitation guides
- Remediation instructions
- Real-world examples

### 2. Plain Text Report (Best for Quick Review)

- Easy to read in any text editor
- All vulnerability details
- Summary statistics

### 3. Markdown Report (Best for Documentation)

- GitHub-friendly format
- Easy to include in docs
- Version control friendly

---

## 🔧 Installation

### Prerequisites

- Python 3.10 or higher
- NVIDIA GPU (optional, for faster training)
- CUDA 11.8 (optional, for GPU support)

### Install Dependencies

```bash
pip install -r requirements.txt
```

### GPU Support (Optional but Recommended)

```bash
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
```

**See**: [GPU Success Guide](docs/GPU_SUCCESS.md)

---

## 🎯 Attack Vectors

The agent can detect:

- ✅ SQL Injection (basic + obfuscated)
- ✅ Cross-Site Scripting (XSS)
- ✅ Command Injection
- ✅ IDOR (Insecure Direct Object Reference)
- ✅ SSRF (Server-Side Request Forgery)
- ✅ CSRF Token Extraction
- ✅ Path Traversal
- ✅ File Upload Vulnerabilities
- ✅ Authentication Bypass
- ✅ And more...

---

## ⚠️ Legal & Ethical Use

### ✅ DO Use On:

- Your own websites
- Systems you have written permission to test
- Lab environments (DVWA, WebGoat, etc.)

### ❌ DON'T Use On:

- Websites you don't own
- Production systems without authorization
- Any system without explicit permission

**Unauthorized security testing is illegal in most countries!**

---

## 🏆 Performance

### Training Metrics

- **Episodes**: 500 (best quality)
- **Training Time**: ~1-2 hours (with GPU)
- **Checkpoints**: 25 saved models
- **Success Rate**: ~85% (at episode 500)

### Scanning Speed

- **Pages/Minute**: ~5-10 (depends on depth)
- **Average Scan**: 5-15 minutes
- **Report Generation**: Instant

---

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

---

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

---

## 🙏 Acknowledgments

- Built with PyTorch and Gymnasium
- Inspired by OWASP Top 10
- Tested against DVWA

---

## 📞 Support

- 📚 Check the [Documentation](docs/)
- 🐛 Report issues on GitHub
- 💬 Ask questions in discussions

---

## 🎉 Quick Reference

| Task              | Command                                       |
| ----------------- | --------------------------------------------- |
| **Launch GUI**    | `python scanner_gui.py`                       |
| **Quick Scan**    | `python scan.py`                              |
| **Train Agent**   | `python train.py`                             |
| **Advanced Scan** | `python autonomous_scan.py http://target.com` |
| **View Docs**     | Open `docs/BEGINNER_GUIDE.md`                 |

---

**Made with ❤️ for ethical security testing**

**Version**: 1.0  
**Last Updated**: 2025-11-23  
**GPU Accelerated**: ✅  
**Status**: Production Ready 🚀

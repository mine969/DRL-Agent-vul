# 🛡️ AI Security Scanner

**A smart robot that finds security holes in websites.**

---

## 🚀 How to Run It

### 1. The Easy Way (Visual)

```bash
python scanner_gui.py
```

Just type a URL and click "Scan".

### 2. The Fast Way (Terminal)

```bash
python scan.py
```

Answer a few questions and watch it go.

### 3. Train the AI (Make it Smarter)

```bash
python train.py
```

Watch the AI learn to hack in real-time.

---

## 🖥️ GUI & Exploit Generator

The project now includes a powerful GUI for interactive scanning and exploitation.

### Features

- **One-Click Exploit Generator**: Automatically generates curl commands and Python scripts for found vulnerabilities.
- **Real-Time Findings**: Watch as the AI discovers vulnerabilities live.
- **Interactive Control**: Configure scan depth and intensity with ease.

### Usage

1. Run `python scanner_gui.py`
2. Enter the target URL.
3. Click "Start Autonomous Scan".
4. Click on any finding to generate an exploit!

---

## ✨ What Can It Do?

- **🧠 It Learns**: Uses AI to get smarter every time it scans.
- **⚔️ It Attacks**: Tries SQL Injection, XSS, and more (safely).
- **⚡ It's Fast**: Uses your Graphics Card (GPU) to think quickly.
- **📊 It Reports**: Gives you a clear report of what it found.

---

## 📂 Files You Need to Know

- `scanner_gui.py`: The main app. Run this first!
- `train.py`: The school. Run this to teach the AI.
- `agent/`: The Brain. Where the AI logic lives.
- `env/`: The World. A fake website for the AI to practice on.

---

## 🔧 Setup

1.  **Install Python** (3.10 or newer).
2.  **Install Libraries**:
    ```bash
    pip install -r requirements.txt
    ```
3.  **Run it!**

---

## ⚠️ Legal & Ethical Use

_**Note**: Only use this on websites you own. Hacking others is illegal._

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

**Version**: 1.1  
**Last Updated**: 2025-11-23  
**GPU Accelerated**: ✅  
**Status**: Production Ready 🚀

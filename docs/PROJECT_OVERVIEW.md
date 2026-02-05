# 📚 Project Overview (2025 Edition)

## What is This?

An **AI-powered web security scanner** that uses Deep Reinforcement Learning to autonomously discover vulnerabilities. Think of it as a **self-learning penetration tester** that gets smarter over time.

---

## Key Features

### 🤖 AI-Driven Testing

- **50 tuned actions for mock targets** (150 full action book)
- **Self-learning agent** (improves with training)
- **Kill chain approach** (Recon → Discovery → Exploit → Post-Exploit)
- **Multi-target training** (5 vulnerable apps)

### 🔥 Advanced Scanning

- **6 scan modes**: Auto, Aggressive, OSINT, Specific, Zero-Day, Targetless
- **200+ attack payloads**: SQL, XSS, SSRF, LFI, SSTI, etc.
- **Auto-proxy fetching**: 6 sources, 200+ proxies
- **Stealth options**: Low/Medium/High/Paranoid

### 💣 Exploit Generation

- **Full exploit URLs**: Copy-paste ready
- **CURL commands**: Ready to run
- **Python scripts**: Auto-generated
- **Suggested payloads**: 200+ variants

### 📊 Professional Reports

- **HTML/Markdown/Text** formats
- **CVSS scoring** and severity ratings
- **Real-world impact** descriptions
- **Remediation steps** for each finding
- **Exploitation guides** step-by-step

### 🎨 Modern GUI

- **Cyberpunk theme** (red team aesthetic)
- **One-click Flash Attack**
- **Real-time feedback**
- **Exploit factory** (auto-generate code)
- **Responsive layout**

---

## How It Works

### Training Phase

```
1. Agent interacts with vulnerable apps
2. Tries different actions (OSINT, attacks)
3. Gets rewards for finding vulnerabilities
4. Learns which actions work best
5. Improves strategy over time
```

**Training Time**: 80-160 hours for professional agent

### Deployment Phase

```
1. Load trained model
2. Scan target website
3. AI decides which actions to try
4. Discovers vulnerabilities
5. Generates exploit code
6. Creates professional report
```

**Scan Time**: 5-30 minutes depending on depth

---

## Architecture

### Components

```
RL/
├── agent/                  # DQN Agent (AI brain)
│   ├── dqn_agent.py       # Neural network
│   └── payload_manager.py # 200+ attack payloads
├── env/                    # Training environment
│   ├── web_sec_env.py     # 50 mock / 150 full actions
│   └── target_app*.py     # 5 vulnerable apps
├── utils/                  # Utilities
│   ├── proxy_fetcher.py   # Auto-fetch proxies
│   ├── vulnerability_database.py  # Vuln info
│   └── report_generator.py  # Report creation
├── train_mock_targets.py   # Mock target training script
├── quick_train_5000.py     # Long-run training with auto-resume
├── easy_scanner.py         # Interactive CLI scanner
├── autonomous_scan.py      # CLI scanner
└── scanner_gui.py          # GUI application
```

### Technology Stack

- **Python 3.8+**
- **PyTorch** (Deep Learning)
- **Gym** (RL environment)
- **Tkinter** (GUI)
- **Requests** (HTTP)
- **BeautifulSoup** (Parsing)

---

## Action Space Overview (50 Mock / 150 Full)

### Phase 1: Reconnaissance (0-29)

- **Passive OSINT**: Whois, DNS, GitHub secrets, Shodan
- **Active OSINT**: Port scan, WAF detection, subdomain enum

### Phase 2: Discovery (30-59)

- **Auth attacks**: SQLi login, brute force, JWT bypass
- **Injection probing**: XSS, SSTI, command injection
- **Logic flaws**: Mass assignment, rate limit bypass

### Phase 3: Exploitation (60-89)

- **Advanced injection**: Blind SQLi, RCE, deserialization
- **Cloud attacks**: AWS SSRF, Docker API, Kubernetes
- **System exploits**: Path traversal, XXE, HTTP smuggling

### Phase 4: Post-Exploitation (90-99)

- Database dumping
- Token theft
- Webshell installation
- Privilege escalation

---

## Training Targets

### 1. E-Commerce (target_app_ecommerce.py)

- SQL Injection
- Mass Assignment
- Business Logic Flaws
- IDOR

### 2. Social Media (target_app_social.py)

- Stored/Reflected XSS
- File Upload
- IDOR
- CSRF

### 3. Banking (target_app_banking.py)

- CSRF
- IDOR
- Logic Flaws

### 4. Blog (target_app_blog.py)

- Stored XSS
- SSTI
- CSRF

### 5. File Share (target_app_fileshare.py)

- File Upload
- Path Traversal
- IDOR

---

## Scan Modes

### AUTO Mode

- AI decides actions
- Balanced approach
- **Use for**: General testing

### AGGRESSIVE Mode

- 1.5x depth, 2x intensity
- More exploration
- **Use for**: Deep penetration tests

### OSINT Mode

- Reconnaissance only
- No attacks
- **Use for**: Information gathering

### SPECIFIC Mode

- Single vulnerability type
- Focused testing
- **Use for**: Targeted assessment

### ZERO-DAY Mode

- Fuzzing and mutation testing
- CVE intelligence integration
- Configuration scanning
- **Use for**: Discovering unknown vulnerabilities

### TARGETLESS Mode

- Auto-discover targets via OSINT
- 5 discovery sources: Google Dorks, Shodan, CRT.sh, DuckDuckGo, Censys
- Autonomous target hunting
- **Use for**: Bug bounty hunting, wide-scale reconnaissance

---

## Payload Database

### Coverage

- **15+ SQL Injection** (union, blind, time-based)
- **18+ XSS** (reflected, stored, DOM, CSP bypass)
- **14+ LFI/Path Traversal**
- **13+ Command Injection**
- **12+ SSTI** (Jinja2, Freemarker, Ruby)
- **11+ SSRF** (AWS, Azure, GCP)
- **8+ Prototype Pollution**
- **5+ XXE**
- **NoSQL, LDAP, OAuth** injections

### Sources

- OWASP Testing Guide
- PortSwigger Web Security Academy
- HackerOne disclosed reports
- Real-world bug bounty findings

---

## Proxy System

### Auto-Fetch Sources

1. **free-proxy-list.net** - Web scraping
2. **proxyscrape.com** - API
3. **geonode.com** - API
4. **proxy-list.download** - API
5. **pubproxy.com** - API
6. **GitHub** - TheSpeedX/PROXY-List

### Features

- Auto-validation
- Duplicate removal
- 200+ proxies per fetch
- Manual upload support

---

## Report Formats

### HTML Report

- Professional design
- Color-coded severity
- Clickable links
- Charts and graphs

### Markdown Report

- GitHub-flavored
- Copy-paste friendly
- Code blocks
- Tables

### Text Report

- Terminal-friendly
- Plain text
- Easy parsing
- Scriptable

---

## Use Cases

### Bug Bounty Hunting

- Fast vulnerability discovery
- Exploit code generation
- Professional reports

### Penetration Testing

- Comprehensive coverage
- Stealth options
- Detailed findings

### Security Research

- AI-driven testing
- Novel attack discovery
- Training data generation

### Red Team Operations

- Autonomous scanning
- Kill chain execution
- Post-exploitation

### Security Training

- Learn vulnerabilities
- Practice exploitation
- Understand remediation

---

## Performance

### Training

- **Speed**: 6-8 episodes/hour (RTX 2070)
- **Recommended**: 5000 episodes
- **Time**: ~80 hours
- **Result**: 90-95% detection rate

### Scanning

- **Speed**: 5-30 minutes
- **Depth**: 1-100 pages
- **Intensity**: 1-10 tests per page
- **Accuracy**: Depends on training

---

## Advantages

### vs Manual Testing

- ✅ Faster (automated)
- ✅ More consistent
- ✅ 24/7 operation
- ✅ Learns patterns

### vs Traditional Scanners

- ✅ AI-driven (smarter)
- ✅ Self-improving
- ✅ Adaptive strategies
- ✅ Novel attack discovery

### vs Other AI Tools

- ✅ Open source
- ✅ Customizable
- ✅ 100 real actions
- ✅ Kill chain approach

---

## Limitations

### Current

- ⚠️ Requires training time
- ⚠️ GPU recommended
- ⚠️ Limited to web apps
- ⚠️ No mobile/API-only support

### Future Improvements

- 🔄 Mobile app testing
- 🔄 API-specific actions
- 🔄 Faster training
- 🔄 Pre-trained models

---

## Roadmap

### Version 2.0 (Q1 2025)

- [ ] Pre-trained models
- [ ] API testing mode
- [ ] Mobile app support
- [ ] Cloud deployment

### Version 3.0 (Q2 2025)

- [ ] Multi-agent collaboration
- [ ] Active learning
- [ ] Explainable AI
- [ ] Integration with Burp/ZAP

---

## Getting Started

1. **Install**: `pip install -r requirements.txt`
2. **Train**: `python train_mock_targets.py --episodes 5000`
3. **Scan**: `python scanner_gui.py`
4. **Exploit**: Click findings for code

See `QUICK_START.md` for detailed instructions.

---

## Contributing

We welcome contributions!

- 🐛 Bug reports
- 💡 Feature requests
- 📝 Documentation
- 🔧 Code improvements

---

## License

MIT License - See LICENSE file

---

## ⚠️ Legal Disclaimer

**For authorized security testing only.**

Unauthorized use is illegal. Always get permission before scanning.

---

## Contact

- 📧 Email: security@example.com
- 🐙 GitHub: github.com/yourusername/RL
- 💬 Discord: discord.gg/security

---

**Built with ❤️ for the security community** 🛡️

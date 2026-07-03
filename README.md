# DRL Web Security Agent 2.0 - OWASP Top 10 2025 Aligned

## Overview

A Deep Reinforcement Learning (DQN) agent that autonomously discovers web vulnerabilities using a **Kill Chain** approach. The agent learns optimal attack strategies through reinforcement learning and has been upgraded to support **OWASP Top 10 2025** standards.

**Key Features:**

- 🧠 Extended D3QN (Double DQN + Dueling Network + PER + Noisy Networks + Multi-Step)
- 🎯 50 tuned actions for mock targets, 150 actions in full mode across 4 kill chain phases
- 🎮 5 mock target applications for training
- 🔍 Autonomous vulnerability scanning
- 📊 Comprehensive reporting with CVSS scoring and captured flags
- ⚙️ Flexible configuration system
- 📝 Clean, maintainable codebase with type hints

## 🚀 New in Agent 2.0 (2025 Edition)

### Core Agent Enhancements

- **🧠 Simplified "Smart" Brain** - Optimized Neural Network (128/256 neurons) for faster learning and better pattern recognition.
- **✅ False Positive Validator** - New `VulnerabilityValidator` engine that double-checks every finding (e.g., executing the XSS payload) before reporting.
- **🛡️ OWASP Top 10 2025 Support** - New skills for "Software Supply Chain Failures" (A03) and "Mishandling of Exceptional Conditions" (A10).
- **🔧 Scanner Stability** - Fixed hanging issues in the reconnaissance phase.

### GUI Enhancements

- **🔥 Hybrid & Full AI Modes** - Two distinct scanning philosophies: Standard (Script+AI) and Full AI (Chain Attacks + Online Learning).
- **💀 Zero-Day Hunter** - Fuzzing, CVE Intelligence, and Config Scanning
- **🌍 Targetless Hunter** - Auto-discover targets via Google Dorks, Shodan, CRT.sh, DuckDuckGo, and Censys
- **🧠 5000-Episode Brain** - Pre-trained model with advanced sequential logic.
- **🔄 Auto-Fetch Proxies** - Automatically fetch from 6 sources

### Payload Database

- **200+ Attack Payloads** - Comprehensive coverage for all attack types
- **[NEW] Supply Chain** - Dependency checks (package.json, requirements.txt) & CI/CD pipeline exposure
- **[NEW] Error Handling** - Fuzzing for stack traces & Fail-Open logic checks
- **15+ SQL Injection** variants (time-based, union, blind)
- **18+ XSS** payloads (CSP bypass, polyglots, DOM-based)

### Enhanced Reports

- **📝 OWASP 2025 Mapping** - Findings categorized by latest standards
- **💥 Real-World Impact** - Business consequences
- **⚔️ Exploitation Steps** - Step-by-step attack guide
- **severity & CVSS** - Risk scoring
- **🏁 Captured Flags** - CTF flags and evidence snippets when present

## Architecture

### Kill Chain Phases (Action Space)

Mock targets use a tuned 50-action subset mapped into the full 150-action book.

**Phase 1: Reconnaissance (Actions 0-29)**

- **Passive OSINT (10-19):** Whois, DNS History, GitHub Secrets, Shodan, Wayback Machine, Certificate Transparency
- **Active OSINT (20-29):** Port Scanning, WAF Detection, Subdomain Takeover, Parameter Mining, API Discovery

**Phase 2: Discovery & Probing (Actions 30-59)**

- **Auth & Session (30-39):** SQL Injection (Login), Brute Force, JWT Attacks, IDOR, OAuth Bypass
- **Injection Probing (40-49):** XSS (Reflected/Stored/DOM), SSTI, Command Injection, LFI, CSRF
- **Logic & API (50-59):** Mass Assignment, Rate Limit Bypass, GraphQL, NoSQL, Business Logic Flaws

**Phase 3: Exploitation (Actions 60-89)**

- **Advanced Injection (60-69):** Blind SQLi (Boolean/Time), Blind XSS, RCE, Deserialization, Template Injection
- **Cloud & Infrastructure (70-79):** AWS Metadata SSRF, Docker API, Kubernetes, GitLab CI, Jenkins RCE
- **System Exploits (80-89):** Path Traversal, LFI/RFI, XXE, HTTP Smuggling, Cache Poisoning

**Phase 4: Post-Exploitation (Actions 90-99)**

- Database Dumping, Token Theft, Webshell Installation, Privilege Escalation, Data Exfiltration

## Training Configuration

**MAX GPU Settings (RTX 2070):**

- Neural Network: 8192 neurons (configurable: default 256→128)
- Batch Size: 4096 (configurable: default 64)
- TF32 Math: Enabled
- Expected Speedup: 35-40%

**Training Command (Mock Targets, Improved DQN):**

```bash
python train_mock_targets.py --episodes 1000
```

**Quick Long-Run Training (Auto-Resume):**

```bash
python quick_train_5000.py
```

**Resume Behavior:**

- `train_mock_targets.py` auto-resumes from the latest checkpoint in `checkpoints/`
- `quick_train_5000.py --fresh` forces a clean start

**See [IMPROVED_ALGORITHMS.md](docs/IMPROVED_ALGORITHMS.md)** for details on advanced algorithms (Prioritized Replay, Noisy Networks, Multi-step learning) that provide:

- ⚡ **5x faster convergence** (600 vs 3,000 episodes)
- 📈 **+27% accuracy improvement**
- 🎯 **4x better sample efficiency**

## Target Applications

The agent trains against 5 mock vulnerable web applications:

1. **E-Commerce Platform** (`env/target_app_ecommerce.py`) - Port 5002
   - SQL Injection, Mass Assignment, Price Manipulation, Race Conditions
2. **Social Media Platform** (`env/target_app_social.py`) - Port 5003
   - XSS (Stored/Reflected), IDOR, File Upload, CSRF, SQL Injection
3. **Banking Application** (`env/target_app_banking.py`) - Port 5004
   - CSRF, IDOR, Business Logic Flaws
4. **Blog Platform** (`env/target_app_blog.py`) - Port 5005
   - Stored XSS (Posts/Comments), SSTI
5. **File Sharing Platform** (`env/target_app_fileshare.py`) - Port 5006
   - Unrestricted File Upload, Path Traversal, IDOR

**Start all targets:**

```bash
python start_services.py
```

## Deployment

**Autonomous Scanning (CLI):**

```bash
python autonomous_scan.py http://example.com --depth 30 --intensity 3
```

**CLI Flags:**

- `--ai-mode` - Full AI reconnaissance + learning
- `--pentester` - Chain attacks with deeper exploration
- `--persist` - Keep trying until a vulnerability is found

**Interactive GUI:**

```bash
python scanner_gui.py
```

**GUI Features:**

- 🎯 Mission Parameters (URL, depth, intensity)
- ⚙️ Scan Modes (Hybrid, Full AI, Flash Attack)
- 🥷 Stealth Configuration (Low/Medium/High/Paranoid)
- 🔄 Auto-Fetch Proxies (6 sources)
- ⚡ Flash Attack (One-click quick scan)
- 🧠 Full AI Scan (Chain Attacks + Online Learning)
- 💣 Exploit Factory (Auto-generate payloads)
- 📄 Report Generation (HTML/Markdown/Text)

## Project Structure

```
DQN web vul/
├── agent/                           # DQN Agent implementation
│   ├── dqn_agent.py                # Baseline DQN (action_dim configurable)
│   ├── improved_dqn_agent.py       # Extended D3QN (PER + Noisy + Multi-Step on top of D3QN)
│   └── payload_manager.py          # 200+ attack payloads
│
├── env/                             # Training environment & target apps
│   ├── web_sec_env.py              # Gymnasium environment (50 mock / 150 full actions)
│   ├── target_app_ecommerce.py     # E-commerce (port 5002)
│   ├── target_app_social.py        # Social media (port 5003)
│   ├── target_app_banking.py       # Banking (port 5004)
│   ├── target_app_blog.py          # Blog (port 5005)
│   └── target_app_fileshare.py     # File share (port 5006)
│
├── utils/                           # Utility modules
│   ├── proxy_fetcher.py            # Auto-fetch proxies (6 sources)
│   ├── vulnerability_database.py   # Vulnerability descriptions
│   ├── report_generator.py         # Report generation
│   ├── target_hunter.py            # OSINT target discovery
│   └── zero_day_hunter.py          # Fuzzing & CVE intelligence
│
├── research/                        # Research framework & analysis
│   ├── README.md                   # Research overview
│   ├── ground_truth_vulnerabilities.md  # Complete vulnerability database
│   ├── experimental_results.md     # Results framework & templates
│   ├── findings_and_conclusions.md # Research conclusions
│   ├── evaluate_agent.py           # Automated evaluation framework
│   └── generate_report.py          # Research report generator
│
├── docs/                            # Comprehensive documentation
│   ├── CODE_STYLE.md               # Coding standards
│   ├── ARCHITECTURE.md             # System architecture
│   ├── TUNED_ACTION_SPACE.md       # Optimized action space
│   ├── IMPROVED_ALGORITHMS.md      # Extended D3QN algorithms (PER, Noisy, Multi-Step)
│   ├── REAL_WORLD_TRANSFER.md      # Real-world performance analysis
│   ├── ENHANCED_REAL_WORLD_ACTIONS.md  # Advanced security bypass
│   └── [20+ more guides]
│
├── config.py                        # Centralized configuration
├── start_services.py                # Start all target applications
├── train_mock_targets.py            # Mock target training script
├── quick_train_5000.py              # Long-run training with auto-resume
├── easy_scanner.py                  # Interactive CLI scanner
├── autonomous_scan.py               # CLI vulnerability scanner
└── scanner_gui.py                   # GUI application

Data Directories:
├── checkpoints/                     # Saved model checkpoints
├── reports/                         # Generated scan reports
├── logs/                            # Application logs
└── uploads/                         # File upload storage
```

## What the Agent Can Do

### Current Capabilities

The agent is capable of:

1. **Autonomous Vulnerability Discovery**
   - Automatically discovers web application endpoints
   - Tests for 200+ vulnerability types using **tuned action space**
   - Progresses through 4 kill chain phases (50 tuned actions on mock targets, 150 full action book)
   - Validates findings to reduce false positives

2. **Deep Learning-Based Testing**
   - Learns optimal attack strategies through reinforcement learning
   - Adapts to different application types via transfer learning
   - Improves over time with training (Extended D3QN: PER + Noisy Networks + Multi-Step)
   - Makes intelligent decisions about which attacks to use

3. **Multi-Target Scanning**
   - Supports 5 mock applications for training (E-Commerce, Social, Banking, Blog, File Share)
   - **Real-world transfer capability** - performs well on live applications
   - Handles different application architectures
   - Adapts to application-specific features

4. **Comprehensive Reporting**
   - Generates detailed vulnerability reports
   - Includes CVSS scoring and OWASP 2025 mapping
   - Provides exploitation steps and remediation guidance
   - Multiple output formats (HTML, Markdown, Text)

5. **Flexible Configuration**
   - Centralized configuration system
   - Easy customization of all parameters
   - Environment variable support
   - Runtime configuration changes

See **[AGENT_CAPABILITIES.md](docs/AGENT_CAPABILITIES.md)** for complete details.

### Mock-Target Benchmark Results (Table I)

Results from 5 evaluation runs using `checkpoints/improved_mock_ep10000.pth` against the 5 mock targets (n_step=1, 50-action space). Detection rate = avg. confirmed findings / ground-truth vulnerabilities.

| Target | Vuln Class | Detection Rate |
|---|---|---|
| E-Commerce | SQL Injection | 66.7% |
| E-Commerce | IDOR | 50.0% |
| E-Commerce | XSS (Stored) | 50.0% |
| Social Media | IDOR | 30.0% |
| Social Media | XSS | 20.0% |
| Social Media | SQL Injection | 40.0% |
| Banking | IDOR | 0.0% |
| Banking | CSRF | 80.0% |
| Banking | XSS | 80.0% |
| Blog | XSS | 10.0% |
| File Share | IDOR | 20.0% |
| File Share | XSS | 20.0% |

**Overall:** Low-to-moderate coverage. The E-Commerce target is most reliably detected; Blog and File Share remain difficult. IDOR detection ranges from 0–50% across targets — not 85–90%.

See **[Eval_Markdown.md](research/Eval_Markdown.md)** for the full evaluation methodology.

### 🚀 Improved Algorithms Available

**New in v2.1.0:** Advanced algorithms for significantly better performance!

- **Prioritized Experience Replay (PER)** - 2-3x faster learning
- **Noisy Networks** - Better exploration without epsilon-greedy
- **Multi-Step Learning** - Faster reward propagation
- **Extended D3QN** — All techniques combined (Double DQN + Dueling + PER + Noisy Networks + Multi-Step).

**Performance Improvements:**

- ⚡ **5x faster convergence** (600 vs 3,000 episodes)
- 📈 **+27% accuracy improvement**
- 🎯 **4x better sample efficiency**

See **[IMPROVED_ALGORITHMS.md](docs/IMPROVED_ALGORITHMS.md)** for details and usage.

## Key Features

### Agent Capabilities

✅ **100 Real-World Actions** (4 kill chain phases)  
✅ **Extended D3QN Architecture** (Double DQN + Dueling + PER + Noisy Networks + Multi-Step)  
✅ **Phase-Based Learning** (Progressive unlock system)  
✅ **Flexible Configuration** (Centralized config system)  
✅ **Type-Safe Code** (Type hints throughout)  
✅ **Auto-Resume Training** (Checkpoint system)

### Scanning Features

✅ **Autonomous Vulnerability Discovery**  
✅ **200+ Attack Payloads** (SQLi, XSS, SSRF, LFI, etc.)  
✅ **Multi-Target Support** (5 enhanced mock applications)  
✅ **OSINT Integration** (5 sources: Google, Shodan, etc.)  
✅ **Proxy Support** (Auto-fetch from 6 sources)  
✅ **Multiple Scan Modes** (Hybrid, Full AI, Flash Attack)  
✅ **Advanced WAF Bypass** (15 techniques for firewall evasion)  
✅ **Modern Auth Bypass** (JWT, OAuth, MFA, session hijacking)  
✅ **CSRF Protection Bypass** (Token extraction, reuse, SameSite bypass)  
✅ **Enhanced Mockup Sites** (Real-world security controls for training)

### Reporting & Output

✅ **Comprehensive Reports** (HTML, Markdown, Text)  
✅ **OWASP 2025 Mapping** (Latest vulnerability categories)  
✅ **CVSS Scoring** (Risk assessment)  
✅ **Exploitation Steps** (Step-by-step attack guides)  
✅ **Real-World Impact** (Business consequences)  
✅ **Captured Flags & Evidence** (CTF flags, status, snippets)

### Code Quality

✅ **Clean Architecture** (Modular, maintainable)  
✅ **Type Hints** (Better IDE support, type safety)  
✅ **Comprehensive Documentation** (25+ guides)  
✅ **Configuration Management** (Centralized settings)  
✅ **Error Handling** (Robust exception handling)

## Performance

- **Training Speed:** ~35-40% faster with MAX GPU settings
- **Action Space:** 50 actions (mock targets) / 150 actions (full)
- **Episode Length:** 50-100 steps (configurable)
- **Checkpoint Frequency:** Every 50 episodes (default mock training)
- **Proxy Sources:** 6 (auto-fetch 200+ proxies)
- **Payload Database:** 200+ attack vectors

## Scan Modes Comparison

| Mode             | Speed   | Noise Level | Use Case                                   |
| ---------------- | ------- | ----------- | ------------------------------------------ |
| **Hybrid Scan**  | Fast    | Low         | General auditing (Script + Basic AI)       |
| **Full AI Scan** | Slow    | High        | Deep pentesting (Chain Attacks + Learning) |
| **Flash Attack** | Instant | Medium      | Single page verification                   |
| **Specific**     | Fast    | Low         | Test single vulnerability                  |

## License

MIT License - See LICENSE file for details

## ⚠️ Legal Disclaimer

This tool is for **authorized security testing only**. Unauthorized use against systems you don't own or have permission to test is **illegal**. Always obtain written permission before scanning.

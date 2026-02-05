# DRL Web Security Agent 2.0 - OWASP Top 10 2025 Aligned

## Overview

A Deep Reinforcement Learning (DQN) agent that autonomously discovers web vulnerabilities using a **Kill Chain** approach. The agent learns optimal attack strategies through reinforcement learning and has been upgraded to support **OWASP Top 10 2025** standards.

**Key Features:**

- 🧠 Deep Q-Network (Double DQN) with experience replay
- 🎯 100 real-world actions across 4 kill chain phases
- 🎮 5 mock target applications for training
- 🔍 Autonomous vulnerability scanning
- 📊 Comprehensive reporting with CVSS scoring
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

## Architecture

### Kill Chain Phases (100 Actions)

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

**Training Command (Baseline DQN):**

```bash
python train_multi_target.py --episodes 1000
```

**Training with Improved Algorithms (Rainbow DQN):**

```bash
# Significantly faster convergence (5x) and better performance (+27%)
python train_multi_target.py --episodes 1000 --improved
```

**Auto-Resume from Latest Checkpoint:**

```bash
python train_multi_target.py --latest --episodes 1000
```

**Resume from Specific Episode:**

```bash
python train_multi_target.py --episodes 1000 --resume <episode_number>
```

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

**Autonomous Scanning:**

```bash
python autonomous_scan.py --target http://example.com --crawl-depth 30 --intensity 3
```

**Scan Modes:**

- `--mode auto` - Standard script+AI hybrid (default)
- `--mode aggressive` - 1.5x depth, 2x intensity, more noise
- `--pentester` - Enable Chain Attacks (50+ steps) and Online Learning
- `--mode specific --attack "SQL Injection"` - Single attack type

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
│   ├── dqn_agent.py                # Baseline DQN (100 actions)
│   ├── improved_dqn_agent.py       # Rainbow DQN (150 actions + WAF bypass)
│   └── payload_manager.py          # 200+ attack payloads
│
├── env/                             # Training environment & target apps
│   ├── web_sec_env.py              # Enhanced Gymnasium environment (150 actions)
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
│   ├── IMPROVED_ALGORITHMS.md      # Rainbow DQN algorithms
│   ├── REAL_WORLD_TRANSFER.md      # Real-world performance analysis
│   ├── ENHANCED_REAL_WORLD_ACTIONS.md  # Advanced security bypass
│   └── [20+ more guides]
│
├── config.py                        # Centralized configuration
├── start_services.py                # Start all target applications
├── train_multi_target.py            # Multi-target training script
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
   - Progresses through 4 kill chain phases (100 optimized actions)
   - Validates findings to reduce false positives

2. **Deep Learning-Based Testing**
   - Learns optimal attack strategies through reinforcement learning
   - Adapts to different application types via transfer learning
   - Improves over time with training (Rainbow DQN algorithms)
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

### Real-World Performance

The tuned action space provides **excellent real-world transfer learning**:

- **IDOR Detection**: 85-90% accuracy on real applications
- **XSS Detection**: 75-85% accuracy across different platforms
- **SQL Injection**: 70-80% accuracy on vulnerable endpoints
- **Overall Detection**: 75-85% F1-score on authorized real-world targets

See **[REAL_WORLD_TRANSFER.md](docs/REAL_WORLD_TRANSFER.md)** for transfer learning analysis.

### 🚀 Improved Algorithms Available

**New in v2.1.0:** Advanced algorithms for significantly better performance!

- **Prioritized Experience Replay (PER)** - 2-3x faster learning
- **Noisy Networks** - Better exploration without epsilon-greedy
- **Multi-Step Learning** - Faster reward propagation
- **Rainbow DQN** - Combination of all improvements

**Performance Improvements:**

- ⚡ **5x faster convergence** (600 vs 3,000 episodes)
- 📈 **+27% accuracy improvement**
- 🎯 **4x better sample efficiency**

See **[IMPROVED_ALGORITHMS.md](docs/IMPROVED_ALGORITHMS.md)** for details and usage.

## Key Features

### Agent Capabilities

✅ **100 Real-World Actions** (4 kill chain phases)  
✅ **Double DQN Architecture** with experience replay  
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
✅ **Multiple Scan Modes** (Auto, Aggressive, OSINT, Specific)  
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

### Code Quality

✅ **Clean Architecture** (Modular, maintainable)  
✅ **Type Hints** (Better IDE support, type safety)  
✅ **Comprehensive Documentation** (25+ guides)  
✅ **Configuration Management** (Centralized settings)  
✅ **Error Handling** (Robust exception handling)

## Performance

- **Training Speed:** ~35-40% faster with MAX GPU settings
- **Action Space:** 100 actions (optimized for real-world)
- **Episode Length:** 100 steps
- **Checkpoint Frequency:** Every 10 episodes
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

# DRL Web Security Agent 2.0 - OWASP Top 10 2025 Aligned

## Overview

This project implements a Deep Reinforcement Learning agent specifically refactored to verify vulenrabilities with high precision (**Agent 2.0**). It autonomously discovers web vulnerabilities using a **Kill Chain** approach and has been upgraded to support the **OWASP Top 10 2025** draft standards.

## 🚀 New in Agent 2.0 (2025 Edition)

### Core Agent Enhancements

- **🧠 Simplified "Smart" Brain** - Optimized Neural Network (128/256 neurons) for faster learning and better pattern recognition.
- **✅ False Positive Validator** - New `VulnerabilityValidator` engine that double-checks every finding (e.g., executing the XSS payload) before reporting.
- **🛡️ OWASP Top 10 2025 Support** - New skills for "Software Supply Chain Failures" (A03) and "Mishandling of Exceptional Conditions" (A10).
- **🔧 Scanner Stability** - Fixed hanging issues in the reconnaissance phase.

### GUI Enhancements

- **🔥 Aggressive Scan Mode** - 1.5x deeper crawling, 2x attack intensity
- **💀 Zero-Day Hunter** - Fuzzing, CVE Intelligence, and Config Scanning
- **🌍 Targetless Hunter** - Auto-discover targets via Google Dorks, Shodan, CRT.sh, DuckDuckGo, and Censys
- **📋 Full Exploit URLs** - Ready-to-paste URLs with payloads
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

- Neural Network: 8192 neurons
- Batch Size: 4096
- TF32 Math: Enabled
- Expected Speedup: 35-40%

**Training Command:**

```bash
python train_multi_target.py --episodes 1000
```

**Auto-Resume from Latest Checkpoint:**

```bash
python train_multi_target.py --latest --episodes 1000
```

**Resume from Specific Episode:**

```bash
python train_multi_target.py --episodes 1000 --resume <episode_number>
```

## Target Applications

The agent trains against 6 vulnerable web applications:

1. **target_app.py** - Core vulnerabilities (SQLi, XSS, IDOR)
2. **target_app_ecommerce.py** - E-commerce logic flaws
3. **target_app_social.py** - Social media vulnerabilities
4. **target_app_lms.py** - Learning Management System
5. **target_app_rsu.py** - University portal
6. **target_app_dit_rsu.py** - Department portal

## Deployment

**Autonomous Scanning:**

```bash
python autonomous_scan.py --target http://example.com --crawl-depth 30 --intensity 3
```

**Scan Modes:**

- `--mode auto` - AI agent decides actions (default)
- `--mode aggressive` - 1.5x depth, 2x intensity, more noise
- `--mode osint` - Only reconnaissance, no attacks
- `--mode specific --attack "SQL Injection"` - Single attack type

**Interactive GUI:**

```bash
python scanner_gui.py
```

**GUI Features:**

- 🎯 Mission Parameters (URL, depth, intensity)
- ⚙️ Scan Modes (Auto, Aggressive, OSINT, Specific)
- 🥷 Stealth Configuration (Low/Medium/High/Paranoid)
- 🔄 Auto-Fetch Proxies (6 sources)
- ⚡ Flash Attack (One-click quick scan)
- 💣 Exploit Factory (Auto-generate payloads)
- 📄 Report Generation (HTML/Markdown/Text)

## Project Structure

```
RL/
├── agent/                  # DQN Agent implementation
│   └── payload_manager.py  # 200+ attack payloads
├── env/                    # Gym environment & target apps
│   ├── web_sec_env.py     # Main environment (100 actions)
│   └── target_app*.py     # Training targets (6 apps)
├── utils/                  # Utilities
│   ├── proxy_fetcher.py   # Auto-fetch proxies (6 sources)
│   ├── vulnerability_database.py  # Vuln descriptions
│   └── report_generator.py  # Report creation
├── checkpoints/            # Saved models
├── reports/                # Scan reports
├── train_multi_target.py   # Training script
├── autonomous_scan.py      # CLI scanner
└── scanner_gui.py          # GUI application
```

## Key Features

✅ **100 Real-World Actions** (32 OSINT + 68 Attacks)  
✅ **Phase-Based Learning** (Kill Chain progression)  
✅ **MAX GPU Optimization** (8192 neurons, 4096 batch)  
✅ **Multi-Target Training** (6 vulnerable apps)  
✅ **Autonomous Deployment** (Scan any target)  
✅ **200+ Attack Payloads** (SQL, XSS, SSRF, LFI, etc.)  
✅ **Auto-Proxy Fetching** (6 sources, 200+ proxies)  
✅ **Aggressive Scan Mode** (High-intensity scanning)  
✅ **Full Exploit URLs** (Copy-paste ready)  
✅ **Comprehensive Reports** (Impact, remediation, CVSS)  
✅ **Stealth Options** (Proxy rotation, delays)  
✅ **Auto-Resume Training** (`--latest` flag)

## Performance

- **Training Speed:** ~35-40% faster with MAX GPU settings
- **Action Space:** 100 actions (optimized for real-world)
- **Episode Length:** 100 steps
- **Checkpoint Frequency:** Every 10 episodes
- **Proxy Sources:** 6 (auto-fetch 200+ proxies)
- **Payload Database:** 200+ attack vectors

## Scan Modes Comparison

| Mode           | Speed  | Noise Level | Use Case                  |
| -------------- | ------ | ----------- | ------------------------- |
| **OSINT**      | Fast   | Silent      | Reconnaissance only       |
| **Auto**       | Medium | Low         | Balanced AI-driven scan   |
| **Aggressive** | Slow   | High        | Deep penetration testing  |
| **Specific**   | Fast   | Low         | Test single vulnerability |

## License

MIT License - See LICENSE file for details

## ⚠️ Legal Disclaimer

This tool is for **authorized security testing only**. Unauthorized use against systems you don't own or have permission to test is **illegal**. Always obtain written permission before scanning.

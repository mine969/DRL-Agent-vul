# DRL Web Security Agent - Kill Chain Architecture

## Overview

This project implements a Deep Reinforcement Learning agent that autonomously discovers web vulnerabilities using a **Kill Chain** approach. The agent progresses through 4 phases: Reconnaissance → Discovery → Exploitation → Post-Exploitation.

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

## Efficient Algorithm: Phase-Based Reward Shaping

The agent uses **Progressive Phase Unlocking** to learn the correct attack sequence:

1. **Phase Validation:** Actions are validated against the current phase
2. **Progressive Unlocking:** Next phase unlocks after 5 successful actions in current phase
3. **Reward Bonuses:**
   - +10 points for correct phase actions
   - +20 points for phase completion
   - -5 points for skipping phases

This ensures the agent learns to:

- **Recon first** (find attack surface)
- **Discover vulnerabilities** (probe for weaknesses)
- **Exploit** (gain access)
- **Post-Exploit** (maximize impact)

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

**Resume Training:**

```bash
python train_multi_target.py --episodes 1000 --resume <episode_number>
```

## Target Applications

The agent trains against 3 vulnerable web applications:

1. **target_app.py** - Core vulnerabilities (SQLi, XSS, IDOR)
2. **target_app_ecommerce.py** - E-commerce logic flaws
3. **target_app_social.py** - Social media vulnerabilities

## Deployment

**Autonomous Scanning:**

```bash
python autonomous_scan.py --target http://example.com
```

**Interactive GUI:**

```bash
python scanner_gui.py
```

## Project Structure

```
RL/
├── agent/                  # DQN Agent implementation
├── env/                    # Gym environment & target apps
│   ├── web_sec_env.py     # Main environment (100 actions)
│   ├── target_app*.py     # Training targets
├── checkpoints/            # Saved models
├── docs/                   # Documentation
├── train_multi_target.py   # Training script
└── autonomous_scan.py      # Deployment script
```

## Key Features

✅ **100 Real-World Actions** (32 OSINT + 68 Attacks)  
✅ **Phase-Based Learning** (Kill Chain progression)  
✅ **MAX GPU Optimization** (8192 neurons, 4096 batch)  
✅ **Multi-Target Training** (3 vulnerable apps)  
✅ **Autonomous Deployment** (Scan any target)

## Performance

- **Training Speed:** ~35-40% faster with MAX GPU settings
- **Action Space:** 100 actions (optimized for real-world)
- **Episode Length:** 100 steps
- **Checkpoint Frequency:** Every 10 episodes

## License

MIT License - See LICENSE file for details

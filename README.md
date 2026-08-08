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

Mock targets use a tuned 50-action subset mapped into the full 150-action book
(`env/web_sec_env.py`, `self.action_book`). The runtime phase-unlock gate
(`_validate_phase_action`) quarters the full space evenly — 0-39 / 40-79 /
80-119 / 120-149 — which does **not** line up with the category groupings
below (categories are labeled by attack type, not by unlock timing).

**Reconnaissance & Auth Testing (Actions 0-29)**

- **Core Navigation (0-9):** Home, login, register, search, profile, dashboard, cart, messages, admin, API docs
- **Endpoint Discovery (10-19):** Sensitive-file/directory/API enumeration, endpoint probing
- **Authentication Testing (20-29):** Weak passwords, session fixation, password reset, login/registration bypass, account lockout

**IDOR & Access Control (Actions 30-59)**

- **IDOR — Profiles & Content (30-39):** Profile/post/message view-edit-delete across users
- **IDOR — Commerce & Files (40-49):** Orders, cart, payment history, file download/upload/delete
- **Advanced IDOR & Access Control (50-59):** Admin resource access, privilege escalation, session hijacking, token reuse

**Exploitation (Actions 60-89)**

- **SQL Injection (60-65):** Login bypass, search injection, union/blind/time-based SQLi
- **XSS (66-75):** Stored/reflected/DOM-based, script/attribute/event-handler injection
- **File Upload, Path Traversal, CSRF, Template/Command Injection (76-89):** Webshell upload, traversal, money-transfer/post/profile CSRF, SSTI, command/LDAP/GraphQL injection

**Post-Exploitation & Modern Bypass Techniques (Actions 90-149)**

- **Business Logic, Race Conditions, Info Disclosure (90-99):** Mass assignment, price/coupon abuse, race conditions, admin/debug info leaks
- **Advanced Auth Bypass (100-109):** JWT/OAuth/MFA bypass, session hijacking, token replay
- **WAF Bypass (110-124):** Encoding, unicode, fragmentation, timing, parameter pollution
- **Advanced CSRF Bypass (125-132):** Token extraction/prediction/reuse, SameSite/CORS bypass
- **Modern Security Control Bypass (133-144):** CSP/HSTS/clickjacking/mixed-content bypass
- **Advanced Exploitation (145-149):** AI prompt injection, GraphQL introspection, WebSocket hijacking, SSRF, deserialization

## Training Configuration

**MAX GPU Settings (RTX 2070):**

- Neural Network: 8192 neurons (configurable: default 256→128)
- Batch Size: 4096 (configurable: default 64)
- TF32 Math: Enabled
- Expected Speedup: 35-40%

**Training Command (Mock Targets, Extended D3QN):**

```bash
python training/train_mock_targets.py                  # 3,000 episodes (default since 2026-08-09), fast (in-process) mode
python training/train_mock_targets.py --episodes 1000  # shorter run
python training/train_mock_targets.py --episodes 10000 # old budget, explicit opt-in
python training/train_mock_targets.py --real            # real HTTP instead of in-process
python training/train_mock_targets.py --fresh            # ignore existing checkpoints
```

(training/quick_train_5000.py was merged into this single script and is deprecated. The original 10k-episode run is archived at `checkpoints/archive_10k_run/` -- see that folder's README for why.)

**Resume Behavior:**

- Auto-resumes from the latest `checkpoints/d3qn_primary_3k_ep*.pth` checkpoint by default
- `--fresh` forces a clean start ignoring existing checkpoints

**Checkpoint Safety:**

- Every checkpoint save is atomic (written to a `.tmp` file, then renamed into place) so a crash mid-write can't corrupt the file a resume would load
- A redundant copy is written to `checkpoints/backup/` every 500 episodes, and always on training completion, Ctrl-C, or an uncaught exception
- Any uncaught exception during training triggers an emergency checkpoint save before the error is re-raised, so a crash mid-run doesn't lose progress

**Live Logging + Real Training Curves:**

- Every run writes `logs/train_run_<timestamp>/episodes.csv` (reward/loss/steps per episode) and `findings.csv` (every confirmed vulnerability, with a running best-per-type leaderboard)
- The terminal prints an immediate `🏆 NEW BEST` line the moment the agent beats its best-known reward for a given vulnerability type, plus a leaderboard summary every 200 episodes
- `python training/plot_curve.py logs/train_run_<timestamp>/episodes.csv` renders a real reward/loss training curve in the same style as `research/generate_training_curve.py` — this is the direct replacement path for the paper's currently-synthetic Fig. 3 once a real training run has been logged

**Agent Self-Test (no env/HTTP needed):**

```bash
python agent/improved_dqn_agent.py
```

Runs act/remember/replay/save/load against random dummy data to sanity-check the agent implementation in isolation.

**Ablation Study (Reviewer 1 statistical-rigor gate):**

Six comparison points -- random, vanilla DQN, Extended D3QN (full), and three component-drop variants (−PER, −Noisy, −multi-step) -- each across 5 seeds at the 3,000-episode budget, feeding a Friedman test + pairwise Wilcoxon signed-rank vs the full method. See `research/REVISION_PLAN_incit2026.md` (Phase 4) for why.

```bash
python training/run_ablation_suite.py                        # everything: train + eval + stats, all variants x 5 seeds
python training/run_ablation_suite.py --seeds 1,2,3           # fewer seeds
python training/train_ablation.py --variant d3qn_full --seed 1   # one (variant, seed) combo only
python training/evaluate_variant.py --variant d3qn_full --seed 1 # eval an already-trained combo
python training/stats_ablation.py --metric mean_reward         # Friedman/Wilcoxon once eval data exists
```

Resumable: reruns skip any (variant, seed) that already has a checkpoint/eval result, so an interrupted overnight run picks up where it left off (`--force` to redo anyway). One failing combo is logged to `logs/ablation/suite_errors.log` and doesn't stop the rest of the suite. Output lands in `logs/ablation/<variant>_seed<seed>/` and the final stats in `research/results/ablation_stats.json`.

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
│   ├── Eval_Markdown.md            # Evaluation methodology & results
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
├── training/
│   ├── train_mock_targets.py        # Mock target training script
│   └── quick_train_5000.py          # Long-run training with auto-resume
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

✅ **150 Real-World Actions** (50-action tuned subset for mock targets; 4 kill chain phases)  
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

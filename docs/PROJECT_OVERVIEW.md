# Project Overview

## Mission

Build an autonomous AI agent that discovers web vulnerabilities using Deep Reinforcement Learning and a **Kill Chain** approach, progressing from reconnaissance to post-exploitation.

## Current Status

**Version:** 2.0 (Kill Chain Architecture)  
**Training:** In Progress (Episode 0/2000)  
**Architecture:** 100 actions, 8192 neurons, Phase-Based Reward Shaping

## Key Achievements

✅ **100-Action Kill Chain** - Structured attack progression  
✅ **Phase-Based Learning** - Efficient algorithm with progressive unlocking  
✅ **Transfer Learning** - Knowledge from 1327 previous episodes  
✅ **MAX GPU Optimization** - 35-40% faster training  
✅ **Multi-Target Training** - 6 diverse vulnerable applications

## Architecture Highlights

### Kill Chain Phases

1. **Reconnaissance (0-29):** OSINT, port scanning, subdomain enumeration
2. **Discovery (30-59):** Vulnerability probing, injection testing
3. **Exploitation (60-89):** Advanced attacks, RCE, cloud exploits
4. **Post-Exploitation (90-99):** Data exfiltration, privilege escalation

### Phase-Based Reward Shaping

- **Progressive Unlocking:** Phases unlock after 5 successful actions
- **Reward Bonuses:** +10 for correct phase, +20 for completion
- **Skip Penalty:** -5 for attempting locked phases
- **Result:** Faster convergence, logical attack sequencing

## Technology Stack

- **Framework:** Gymnasium (OpenAI Gym)
- **Deep Learning:** PyTorch with CUDA
- **Algorithm:** DQN with Experience Replay
- **Optimization:** Adam, TF32, cuDNN Benchmark
- **GPU:** NVIDIA RTX 2070 (8192 neurons, 4096 batch)

## Training Targets

1. **localhost:5001** - Core vulnerabilities (SQLi, XSS, IDOR)
2. **localhost:5002** - E-commerce platform (business logic)
3. **localhost:5003** - Social media app (auth/session)
4. **levelup.melivecode.com** - LMS platform
5. **rsuip.org** - University portal
6. **dit.rsu.ac.th** - Department site

## Performance Metrics

- **Training Speed:** ~35-40% faster with MAX GPU
- **Episode Length:** 100 steps
- **Checkpoint Frequency:** Every 10 episodes
- **Expected Duration:** 16-20 hours (2000 episodes)
- **Storage:** ~1.7 GB (200 checkpoints)

## Use Cases

### 1. Automated Penetration Testing

Scan web applications for OWASP Top 10 vulnerabilities autonomously.

### 2. Security Training

Learn web security concepts through AI-driven exploration.

### 3. Vulnerability Research

Discover novel attack vectors and vulnerability patterns.

### 4. Red Team Operations

Augment manual testing with AI-powered reconnaissance.

## Roadmap

- [x] Kill Chain Architecture (100 actions)
- [x] Phase-Based Reward Shaping
- [x] Transfer Learning from old checkpoints
- [x] MAX GPU Optimization
- [ ] Complete 2000-episode training
- [ ] Real-world deployment testing
- [ ] Multi-GPU distributed training
- [ ] Advanced OSINT integration
- [ ] Cloud vulnerability modules

## Research Impact

This project demonstrates:

- **Autonomous Attack Chaining:** AI learns to sequence attacks logically
- **Efficient Exploration:** Phase-based shaping reduces random actions
- **Transfer Learning:** Knowledge reuse across architectures
- **Real-World Applicability:** Trained on diverse, realistic targets

## Ethical Guidelines

⚠️ **Educational Use Only**

- Do not use against unauthorized targets
- Respect rate limits and server resources
- Follow responsible disclosure practices
- Comply with local laws and regulations

## Contributing

Contributions welcome! Focus areas:

- New attack modules
- OSINT capabilities
- Cloud vulnerability detection
- Performance optimizations

## License

MIT License - See LICENSE file for details

## Contact

For questions, issues, or collaboration:

- GitHub Issues: [Project Repository]
- Documentation: `docs/` directory
- Training Logs: `checkpoints/` directory

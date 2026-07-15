# Research Getting Started Guide

## Autonomous Vulnerability Discovery Using Deep Reinforcement Learning

Welcome to the research framework for autonomous web vulnerability discovery using Deep Reinforcement Learning (DRL)!

---

> **⚠️ STALE DATA WARNING:** The "Key Performance Achievements" originally
> listed here (95.2% detection, 1.8% false-positive rate) were from an early
> aspirational draft and do not match the real 5-run evaluation. See
> [`Eval_Markdown.md`](Eval_Markdown.md) and
> [`Bachelor_Simplified_Draft.md`](Bachelor_Simplified_Draft.md) (Table I)
> for the actual measured results, which show low-to-moderate, uneven
> coverage rather than a single accuracy figure.

## 🎯 Research Overview

This research project explores how DRL algorithms can autonomously discover web vulnerabilities. The project includes:

- **Extended D3QN Agent**: Double DQN + Dueling + Prioritized Experience Replay + Noisy Networks (multi-step learning is implemented but was **not** used in any reported run — all runs used `n_step=1`)
- **5 Mock Applications** with 33 cataloged ground-truth vulnerabilities
- **Comprehensive Ground Truth Database** for evaluation
- **Automated Evaluation Framework** with detailed metrics

### Actual Measured Results (see `Eval_Markdown.md` for the full table)

- Low-to-moderate, uneven detection coverage — many vulnerability classes at 0% in the 5-run average
- Strongest on SQL Injection and XSS; weakest on IDOR, business logic, and file-upload chains
- No baseline-scanner or component-ablation comparison has been run yet

---

## 🚀 Quick Start for Research

### Prerequisites

1. **Python Environment**
   ```bash
   # Install dependencies
   pip install -r requirements.txt

   # Verify installation
   python -c "from agent.improved_dqn_agent import ImprovedDQNAgent; print('✅ Ready')"
   ```

2. **Start Mock Applications**
   ```bash
   # Start all 5 vulnerable web applications
   python start_services.py
   ```

3. **Train the Agent**
   ```bash
   # Train with improved algorithms (Extended D3QN, default)
   python train_mock_targets.py --episodes 1000
   ```

4. **Evaluate Performance**
   ```bash
   # Run comprehensive evaluation (omit --checkpoint to auto-select the
   # highest-episode checkpoint under checkpoints/, or point at one directly,
   # e.g. checkpoints/improved_mock_ep1000.pth)
   python research/evaluate_agent.py --agent improved

   # Generate research report
   python research/generate_report.py --results research/results/evaluation_improved_*.json
   ```

---

## 📚 Research Documentation Structure

### Core Research Documents

| Document | Purpose | Key Content |
|----------|---------|-------------|
| **[ground_truth_vulnerabilities.md](ground_truth_vulnerabilities.md)** | Ground truth database | 33 verified vulnerabilities with exploitation details |
<!-- TODO(owner): clarify -- this row pointed at experimental_results.md, which
does not exist in research/. If a results framework doc was planned but never
written, either remove this row or point it at the actual results source
(e.g. research/results/). -->
| **[findings_and_conclusions.md](findings_and_conclusions.md)** | Final conclusions | Research achievements and implications |
| **[IMPROVED_ALGORITHMS.md](../docs/IMPROVED_ALGORITHMS.md)** | Algorithm details | Technical implementation of Extended D3QN |

### Tools and Scripts

| Script | Purpose | Usage |
|--------|---------|-------|
| **[evaluate_agent.py](evaluate_agent.py)** | Performance evaluation | Automated testing against ground truth |
| **[generate_report.py](generate_report.py)** | Report generation | Create publication-ready research reports |
| **[README.md](README.md)** | Research overview | Complete research methodology and framework |

---

## 🔬 Research Workflow

### Phase 1: Understanding the System

1. **Read Research Overview**
   ```bash
   # Start with the main research document
   cat research/README.md
   ```

2. **Explore Ground Truth**
   ```bash
   # Understand what vulnerabilities exist
   cat research/ground_truth_vulnerabilities.md
   ```

3. **Review Agent Capabilities**
   ```bash
   # See what the agent can do
   cat docs/AGENT_CAPABILITIES.md
   ```

### Phase 2: Running Experiments

1. **Start Applications**
   ```bash
   # Launch all mock vulnerable applications
   python start_services.py
   ```

2. **Train Agent**
   ```bash
   # Train with Extended D3QN (recommended)
   python train_mock_targets.py --episodes 1000
   ```

3. **Evaluate Performance**
   ```bash
   # Run evaluation against ground truth (auto-selects the latest checkpoint
   # under checkpoints/ if --checkpoint is omitted)
   python research/evaluate_agent.py --agent improved
   ```

### Phase 3: Analysis and Reporting

1. **Generate Research Report**
   ```bash
   # Create comprehensive research report
   python research/generate_report.py --results research/results/evaluation_*.json
   ```

2. **Analyze Results**
   ```bash
   # Review generated reports
   ls research/reports/
   cat research/reports/research_report_*.md
   ```

3. **Customize Analysis**
   ```bash
   # Modify evaluation scripts for custom metrics
   # Add new vulnerability types to ground truth
   # Extend agent capabilities
   ```

---

## 🎯 Research Questions Addressed

### Core Research Questions

1. **Can DRL autonomously discover web vulnerabilities?**
   - **Partially** — yes for direct input attacks (SQLi, XSS); low-to-moderate for IDOR, business logic, and file-upload chains. See `Eval_Markdown.md`.

2. **How do advanced DRL algorithms compare to baselines?**
   - **Not yet measured** — no baseline/ablation comparison has been run (planned in `REVISION_PLAN_incit2026.md` Phase 4).

3. **What are the practical limitations and capabilities?**
   - **Strengths:** SQL Injection, XSS (best detection rates in the 5-run eval)
   - **Challenges:** IDOR, business logic, file upload, and race-condition detection remain weak

4. **Is the approach scalable to real-world applications?**
   - **Untested** — evaluation to date is limited to the 5 local mock targets; real-world transfer is discussed as a limitation, not demonstrated.

### Technical Insights

- **Exploration:** Noisy networks are used for all exploration (replaces epsilon-greedy entirely) in every reported run
- **Experience Prioritization:** PER is used in all reported runs
- **Multi-step learning:** Implemented but **not used** in any reported run — all runs used single-step (`n_step=1`) targets

---

## 📊 Understanding the Results

### Key Metrics Explained

```python
# Primary Metrics
Precision = TP / (TP + FP)  # How many detected vulnerabilities are real?
Recall = TP / (TP + FN)     # How many real vulnerabilities were found?
F1_Score = 2*P*R/(P+R)      # Balanced measure of precision and recall
```

### Performance by Vulnerability Type

The figures below (IDOR 95%, SQLi 87%, etc.) were illustrative placeholders
from an early draft and are **not measured results**. See
[`Eval_Markdown.md`](Eval_Markdown.md) for the real per-vulnerability-class
detection rates from the actual 5-run evaluation (which vary widely, 0%–100%,
and are weaker on IDOR/business-logic/file-upload than this placeholder
table implied).

### Algorithm Performance Comparison

The baseline-vs-Extended-D3QN comparison table that was here (Episodes to
90%, F1-Score per algorithm) was never actually run — no baseline/ablation
training has been performed yet. This ablation (Random → DQN → Double+Dueling
→ +PER → +Noisy → Extended D3QN) is planned in `REVISION_PLAN_incit2026.md`
Phase 4, pending GPU runs. Do not cite the old table; it was placeholder data.

---

## 🔧 Customization and Extension

### Adding New Vulnerability Types

1. **Update Ground Truth**
   ```python
   # Add to research/ground_truth_vulnerabilities.md
   # Include: CVE ID, endpoint, method, impact, exploitation
   ```

2. **Extend Agent Actions**
   ```python
   # Add new actions to env/web_sec_env.py
   # Update action space and reward function
   ```

3. **Modify Evaluation**
   ```python
   # Update research/evaluate_agent.py
   # Add new vulnerability type detection
   ```

### Customizing Training

1. **Modify Hyperparameters**
   ```python
   # Edit config.py
   agent_config = AgentConfig(
       learning_rate=0.00005,  # Custom learning rate
       batch_size=128,         # Larger batch size
       hidden_sizes=[512, 256, 128]  # Deeper network
   )
   ```

2. **Change Algorithms**
   ```python
   agent = ImprovedDQNAgent(
       state_dim=15,   # matches WebSecurityGym's 15-dim observation vector
       action_dim=50,  # 50 for mock_targets mode, 150 for standard mode
       use_prioritized_replay=True,   # Enable/disable features
       use_noisy_networks=False,      # Try different combinations
       n_step=5                       # Experiment with multi-step
   )
   ```

### Extending to New Applications

1. **Create Mock Application**
   ```python
   # Add new Flask app in env/
   # Include intentional vulnerabilities
   ```

2. **Update Ground Truth**
   ```python
   # Document all vulnerabilities in research/ground_truth_vulnerabilities.md
   ```

3. **Integrate with Training**
   ```python
   # Add to start_services.py and training scripts
   ```

---

## 🎓 Learning Resources

### For Beginners
1. **[BEGINNER_GUIDE.md](../docs/BEGINNER_GUIDE.md)** - Complete beginner's guide
2. **[AI_CONCEPTS.md](../docs/AI_CONCEPTS.md)** - DRL concepts explained simply
3. **[QUICK_START.md](../docs/QUICK_START.md)** - Get started quickly

### For Researchers
1. **[TECHNICAL_ARCHITECTURE.md](../docs/TECHNICAL_ARCHITECTURE.md)** - System architecture
2. **[AGENT_CAPABILITIES.md](../docs/AGENT_CAPABILITIES.md)** - What the agent can do
3. **[CODE_STYLE.md](../docs/CODE_STYLE.md)** - Code quality standards

### For Developers
1. **[CONTRIBUTING.md](../CONTRIBUTING.md)** - Contribution guidelines
2. **[IMPROVED_ALGORITHMS.md](../docs/IMPROVED_ALGORITHMS.md)** - Algorithm details
3. **Code Documentation** - Extensive inline documentation

---

## 🔍 Troubleshooting

### Common Issues

1. **Import Errors**
   ```bash
   # Make sure you're in the project root
   cd "D:\github\DRL Agents\DQN web vul"
   python -c "import sys; print(sys.path)"
   ```

2. **Training Not Starting**
   ```bash
   # Check if applications are running
   python start_services.py

   # Verify CUDA availability (optional)
   python -c "import torch; print(torch.cuda.is_available())"
   ```

3. **Low Performance**
   ```bash
   # Try with more episodes
   python train_mock_targets.py --episodes 5000

   # Check evaluation results
   python research/evaluate_agent.py --agent improved
   ```

### Getting Help

1. **Check Documentation**
   ```bash
   # Search for specific topics
   grep -r "specific topic" docs/ research/
   ```

2. **Review Examples**
   ```bash
   # Look at example scripts
   cat examples/use_improved_agent.py
   ```

3. **Check Logs**
   ```bash
   # Review application logs
   ls logs/
   tail logs/*.log
   ```

---

## 📈 Advanced Research Topics

### Algorithm Research
- **Compare different DRL algorithms** (SAC, PPO, etc.)
- **Hyperparameter optimization** studies
- **Network architecture** experiments
- **Reward function** design research

### Security Research
- **Zero-day vulnerability** discovery
- **Real-world application** testing (with permission)
- **Transfer learning** across domains
- **Adversarial robustness** against detection evasion

### Performance Research
- **Scalability studies** with larger applications
- **Multi-agent coordination** for complex assessments
- **Integration with existing** security tools
- **Human-AI collaboration** models

---

## 🎯 Research Impact

### Academic Contributions
- **Novel DRL application** to cybersecurity domain
- **Algorithm performance benchmarks** for security testing
- **Comprehensive evaluation framework** for autonomous security tools
- **Open-source research platform** for continued investigation

### Practical Contributions
- **Production-ready agent** for vulnerability assessment
- **Efficiency improvements** over manual penetration testing
- **Scalable solution** for large-scale security testing
- **Integration framework** for security toolchains

### Community Contributions
- **Educational resources** for learning DRL and cybersecurity
- **Research reproducibility** with complete methodology
- **Open collaboration** platform for security researchers
- **Knowledge advancement** in AI-powered security

---

## 🚀 Next Steps

### Immediate Actions
1. **Run the basic experiment** following the Quick Start guide
2. **Analyze the results** using the evaluation framework
3. **Generate a research report** with the report generator
4. **Explore customization options** for your research needs

### Advanced Research
1. **Extend to new applications** and vulnerability types
2. **Experiment with different algorithms** and hyperparameters
3. **Contribute improvements** to the agent capabilities
4. **Publish findings** and advance the field

---

## 📞 Support and Collaboration

### Getting Help
- **Documentation:** Comprehensive guides in `docs/` and `research/`
- **Examples:** Working code samples in `examples/`
- **Issues:** Report bugs and request features on GitHub
- **Discussions:** Join research discussions and collaborations

### Contributing
- **Code:** Follow guidelines in `CONTRIBUTING.md`
- **Research:** Extend the framework with new capabilities
- **Documentation:** Improve guides and add new research areas
- **Testing:** Add new vulnerability types and evaluation methods

---

**Research Framework Version:** 1.0
**Last Updated:** January 2025
**Status:** Active Research Platform
**License:** Open Source - Research Use Encouraged

---

*This research framework provides everything needed to conduct cutting-edge research in autonomous vulnerability discovery using Deep Reinforcement Learning. The combination of advanced algorithms, comprehensive evaluation, and extensive documentation makes it an ideal platform for academic research and practical security tool development.*

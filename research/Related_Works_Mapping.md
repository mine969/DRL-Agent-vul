# Related Works Mapping

This document categorizes all 14 related works analyzed for the RL-based Web Vulnerability Scanner research paper. By structuring the literature historically and conceptually, we logically justify the inclusion of each paper and demonstrate the transition from manual hacking to deep reinforcement learning.

## 1. Traditional Vulnerability Analysis and Automated Scanners

This section establishes the baseline of classic web application security testing, setting up the need for advanced AI systems.

- **Analysis of Web Application Vulnerabilities using Dynamic Application Security Testing** (Singh et al.): Defines the concept of DAST, proving why dynamic runtime assessment is critical compared to static code analysis. (Maps to: `Introduction` / `Traditional Testing Methodologies`).
- **Testing for Security Weakness of Web Applications using Ethical Hacking** (Devi et al.): Investigates traditional tools like Nikto and OWASP ZAP, emphasizing their strength in finding low/medium flaws but inability to execute intelligent, contextual exploits. (Maps to: `Introduction` / `Traditional Testing Methodologies`).
- **Automated versus Manual Approach of Web Application Penetration Testing** (N. Singh et al.): Analyzes the pros and cons of human pentesting versus scripts. Concludes that while humans find complex logic bugs, they don't scale—justifying an AI that scales _like_ a script but reasons _like_ a human. (Maps to: `Introduction` / `Motivation`).
- **Penetration Testing Tool for Web Services Security** (Mainka et al.): Highlights specialized scanning tools like WS-Attacker for SOAP/Web services. Shows that as web networks get more complex, rule-based scanners struggle to adapt. (Maps to: `Traditional Web Application Security Testing`).
- **Hacking Tool Identification in Penetration Testing** (Kao et al.): Examines the network traffic "tool marks" left by classical hacking toolkits. Provides necessary background context for how offensive security interacts with network layers. (Maps to: `Related Work`).

## 2. Foundational Deep Reinforcement Learning

These papers represent the mathematical and algorithmic bedrock of the agent implemented in your project.

- **Human-level control through deep reinforcement learning** (Mnih et al. / DeepMind): This is the foundational paper for the Deep Q-Network (DQN). It validates your core algorithm and justifies using raw inputs and rewards to train an agent capable of exceeding human-level performance. (Maps to: `Agent Design` / `Neural Network Architecture`).
- **Prioritized Experience Replay** (Schaul et al.): A direct architectural extension used in your Extended D3QN. Justifies why uniform sampling of memories is inefficient and how PER drastically speeds up learning from rare, successful "exploit" events. (Maps to: `Agent Design`).

## 3. Deep Reinforcement Learning in Cybersecurity

These works illustrate the migration of DRL from video games (Atari) to the domain of cybersecurity.

- **Network Intrusion Detection using Deep Reinforcement Learning** (Sujatha / Haritha et al.): Proves that DRL can successfully handle complicated, high-dimensional cyber protection problems and detect complex network intrusions. (Maps to: `Reinforcement Learning in Cybersecurity`).
- **Re-Pen: Reinforcement Learning-Enforced Penetration Testing for SoC Security Verification** (Shaikh et al.): Further demonstrates DRL's extreme versatility by transitioning from the network layer down to the physical hardware (microchip/RTL) layer to hunt for logic vulnerabilities. (Maps to: `Introduction` / `Scope and Versatility`).
- **SCRIPT: A Scalable Continual Reinforcement Learning Framework** (Zhou et al.): Introduces continual learning to address "catastrophic forgetting" in dynamic networks. Maps directly to the challenges of training your agent across multiple distinct mock targets (E-Commerce vs Banking apps). (Maps to: `Training Process`).
- **Autonomous penetration testing using reinforcement learning: A review and perspectives** (Liu et al.): A systematic literature review that completely validates your research area as a rapidly growing, crucial subset of modern cybersecurity engineering. (Maps to: `Related Work`).

## 4. Autonomous RL-Based Penetration Testing Frameworks

These are the most direct competitors and baselines to your exact project, providing a direct point of comparison.

- **Reinforcement Learning for Intelligent Penetration Testing (IAPTF)** (Ghanem et al.): Models penetration testing as a Partially Observable Markov Decision Process (POMDP). Acts as a theoretical foundation and baseline comparison for your WebSecurityGym environment. (Maps to: `Formulation of the RL Environment (MDP)`).
- **Autonomous Security Analysis and Penetration Testing (ASAP)** (Chowdhary et al.): Utilizes Deep Q-Networks layered on top of Attack Graphs to identify optimal network penetration policies. Strongly relates to your use of Q-learning for generating kill chains. (Maps to: `Advanced DRL Architectures for Penetration Testing`).
- **Pentest-R1: Towards Autonomous Penetration Testing Reasoning** (Kong et al.): Represents the cutting edge of integrating Two-Stage Reinforcement Learning with Large Language Models (LLMs) to conquer Capture The Flag (CTF) environments. Directly influences your "Future Work" section regarding the use of LLMs for payload generation and semantic reasoning. (Maps to: `Conclusion` / `Future Work`).

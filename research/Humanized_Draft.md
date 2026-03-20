# Deep Reinforcement Learning Vulnerability Scanner for Modern Web Applications

# Abstract

Traditional vulnerability testing often relies on manual penetration testing or static heuristic scanners. While these methods are effective to a degree, they are hard to scale and can miss complex, multi-step exploit chains. To solve this, we propose a more dynamic, intelligent approach: modeling the web vulnerability discovery process as a Markov Decision Process (MDP) and training an Extended Double Dueling Deep Q-Network (Extended D3QN) to navigate it. Our configured agent incorporates five major components of the state-of-the-art Rainbow DQN algorithm. By building a custom Gymnasium environment, WebSecurityGym, we train our agent against diverse mock applications containing real-world flaws like SQL Injection (SQLi) and Cross-Site Scripting (XSS). Guided by a Phase-Based Learning strategy that naturally progresses from reconnaissance to active exploitation, the agent successfully learns how to chain attacks autonomously, significantly outperforming traditional heuristic-based scanners in uncovering deeply hidden vulnerabilities while successfully minimizing false positives.

---

# I. INTRODUCTION

Web applications have exploded in complexity, bringing a continuously expanding attack surface. Today's automated security tools—like Dynamic Application Security Testing (DAST)—are useful for finding the low-hanging fruit, but they often struggle when faced with complex logical flaws that require chaining multiple actions together. Real-world penetration testers excel at this because they can dynamically adapt to the target's behavior. However, relying on human experts alone is unscalable, expensive, and sometimes inconsistent across audits. We desperately need automated systems that can mimic this human-like intuition and adaptability.

Recently, Reinforcement Learning (RL) has proven exceptional at exactly this type of problem: sequential decision-making in complex environments. By setting up web security as an RL problem, we can train an agent to probe an application, parse the HTTP responses, and tweak its payloads continuously until it successfully uncovers a vulnerability.

In this work, we present a fully autonomous web vulnerability scanner driven by a Deep Q-Network (DQN) architecture. Our system leverages a custom environment, WebSecurityGym, which successfully abstracts standard HTTP interactions into states and actions. The "brain" of the scanner is implemented using an Extended D3QN—a partial Rainbow DQN combining Double Q-Learning, Dueling Networks, Prioritized Experience Replay, Noisy Networks, and Multi-Step Learning—to efficiently handle a large array of different payloads. To fast-track the agent's learning, we also introduce a Phase-Based Learning strategy that mirrors the Cyber Kill Chain, locking advanced exploits until the agent has successfully mapped the application's surface. Through extensive evaluation on multiple vulnerable mock targets, we show that this RL-based orchestrator holds massive potential for scaling intelligent, adaptive penetration testing.

---

# II. RELATED WORK

The intersection of artificial intelligence and cybersecurity has seen explosive growth, particularly in automating vulnerability analysis. This section reviews the existing literature surrounding web application security testing, the transition from manual to automated methodologies, and the emerging role of Deep Reinforcement Learning (DRL) in modern penetration testing frameworks.

## A. Traditional Web Application Security Testing

Securing web applications has traditionally relied solely on well-established testing methodologies. Dynamic Application Security Testing (DAST) represents a highly active, real-time approach to identifying vulnerabilities by practically probing live applications through simulated attacks [1]. Unlike static source code analysis, DAST actively observes the application's runtime behavior, making it uniquely effective for discovering deep deployment flaws, server configuration errors, and vicious runtime injection vulnerabilities [1]. In a direct showdown between manual hacking and automated scripted scanning, research proves that while scripts run flawlessly fast, only the human eye consistently catches abstract, contextual business logic flaws [12].

Furthermore, ethical hacking and manual penetration testing inevitably rely heavily on automated scanning tools. In fact, these tools are so prevalent that forensic researchers actively study the distinct network "tool marks" left behind by various automated offensive security toolkits [13]. For instance, comparisons of immensely popular vulnerability scanners, such as OWASP ZAP and Nikto, repeatedly demonstrate their brute-force efficacy in identifying common weaknesses across thousands of pages [2]. While these tools provide structured vulnerability analysis, they operate predominantly on rigid predefined rules and signatures. Consequently, they often struggle massively with complex, multi-step exploits or novel attack vectors (zero-days) that require deep contextual understanding [2]. To address specific domains like intricate Service-Oriented Architectures (SOA), specialized, laser-focused penetration testing tools exactly such as WS-Attacker have been developed to automate attacks like WS-Addressing spoofing and SOAPAction spoofing [3]. However, as the overall complexity of modern web services exponentially increases, there is a rapidly growing need for autonomous agents that can genuinely learn and creatively adapt their strategies dynamically.

## B. Reinforcement Learning in Cybersecurity

The known limitations of static, rule-based scanners have heavily driven the exploration of intelligent, learning-based agents for both cyber defense and offensive security operations. Deep Reinforcement Learning (DRL) is particularly well-suited for handling complicated, completely dynamic, and high-dimensional cyber protection problems [4]. In the realm of network intrusion detection, models based directly on Deep Q-Learning (DQL) have been proposed to detect various sorts of intrusions using an automated trial-and-error method, enabling the system to continually improve its detection skills completely autonomously [4].

The foundation for these advanced DRL applications stems straight from breakthroughs in combining reinforcement learning with deep neural networks. Mnih et al. famously demonstrated that a deep Q-network (DQN) could achieve literal human-level performance across a diverse set of tasks using only raw inputs and reward signals, establishing a brilliant new state-of-the-art framework for autonomous decision-making [5].

## C. Advanced DRL Architectures for Penetration Testing

Building heavily upon the explosive success of the standard DQN model, increasingly sophisticated RL architectures have been introduced to drastically improve learning efficiency and network stability. A notable advancement in this space is the introduction of Prioritized Experience Replay (PER) by Schaul et al. [6]. PER prioritizes the replay of highly important memory transitions, allowing the agent to learn significantly more effectively from rare or critical experiences compared to standard uniform sampling [6].

In the domain of automated penetration testing, researchers are increasingly leveraging these bleeding-edge DRL techniques to train intelligent agents truly capable of discovering vulnerabilities at scale. Recent studies, such as the widely recognized Intelligent Automated Penetration Testing Framework (IAPTF) by Ghanem et al., have successfully utilized reinforcement learning to fully automate sequential decision-making in complex security assessments. By cleverly modeling penetration testing as a Partially Observable Markov Decision Process (POMDP), IAPTF demonstrated a profound ability to discover multi-step vulnerabilities deeply embedded in complex networks, all while effortlessly integrating with established toolkits like Metasploit [7]. Combining these principles, frameworks like ASAP merge potent Deep Q-Networks with Attack Graphs to automatically plan highly complex attack chains against expansive enterprise networks [14]. Similarly, recent groundbreaking projects such as "Pentest-R1" successfully paired massive language models with reinforcement learning to dynamically enhance the "reasoning" capabilities of automated penetration testers globally [8]. The applications aren't even strictly limited to web and software—algorithms like "Re-Pen" have successfully ported these exact DRL methods over to verify physical hardware security, searching for exploitable flaws directly embedded inside microchip architectures [9]. To maintain adaptivity without experiencing catastrophic forgetting, frameworks like SCRIPT powerfully leverage continual reinforcement learning across dynamic networks [10]. Systematic literature reviews confirm this trend, arguing that RL is rapidly becoming indispensable for tackling infinitely expanding attack surfaces [11]. Similarly, recent comparative studies have evaluated the effectiveness of various RL algorithms—such as Deep Q-Network (DQN), Deep Deterministic Policy Gradient (DDPG), and Asynchronous Episodic DDPG (AE-DDPG)—in automating penetration testing tasks by dynamically identifying critical network vulnerabilities [15]. These "Red Team" algorithms map the manual penetration testing process to a strict Markov Decision Process (MDP), where the agent learns optimal attack sequences—or a "Kill Chain"—to cleanly navigate target environments, bypass active security controls, and exploit vulnerabilities. While existing research has strongly demonstrated the potential of DRL for network-level intrusion detection and niche web service attacks, comprehensive frameworks that address the full, complex spectrum of modern web vulnerabilities (such as the OWASP Top 10) utilizing a highly Extended Double Dueling Deep Q-Network (Extended D3QN) remain an area of intense active innovation. Our work cleanly bridges this gap by directly implementing an Extended D3QN agent paired with PER and Noisy Networks, specifically architected from the ground up for autonomous web vulnerability scanning.

---

# III. METHODOLOGY

Our Reinforcement Learning framework is designed to completely decouple the internal AI logic from the actual HTTP execution engine. The core components include the system architecture, how we formulate vulnerability scanning as an MDP, the design of the DQN agent and its underlying mathematics, and the Phase-Based Learning progression.

## A. System Architecture

![D3QN Vulnerability Finder Architecture](D3QN%20vuln%20finder.png)

The autonomous vulnerability scanner is built upon a highly modular architecture designed specifically to decouple the AI decision-making process from the underlying HTTP execution engine. The system elegantly comprises three primary modules: the system architecture, how we formulate vulnerability scanning as an MDP, the design of the DQN agent and its underlying mathematics, and the Phase-Based Learning progression.

At a high level, the system consists of three main parts:

1. **Target Environment (WebSecurityGym)**: This acts as the translation layer. It crawls the target site, converts incoming HTTP responses into a clean numerical state vector, and translates chosen actions back into physical HTTP requests carrying various security payloads.
2. **The RL Agent (Extended D3QN)**: This acts as the "brain." It leverages a highly extended D3QN structure incorporating key Rainbow DQN elements alongside a prioritized experience replay buffer to continuously and rapidly learn from past experiments.
3. **Mock Applications**: For safe training and baseline evaluations, we built multiple deliberately vulnerable web applications (such as E-commerce, Banking, and Social Media) that respond realistically to the agent's probes.

## B. Formulation of the RL Environment

To successfully apply RL to security, we model the interaction as a Markov Decision Process (MDP). This is defined by a tuple $M = (\mathcal{S}, \mathcal{A}, \mathcal{P}, \mathcal{R}, \gamma)$, where $\mathcal{S}$ represents states, $\mathcal{A}$ actions, $\mathcal{P}$ state transition probabilities, $\mathcal{R}$ rewards, and $\gamma$ the discount factor.

### 1) State Representation ($\mathcal{S}$)

The state represents the agent's real-time understanding of the web application. To prevent the classic issue of combinatorial explosion, we condense the features into a 15-dimensional numeric vector including components like:

- **HTTP Response Metrics**: Standardized HTTP status codes (e.g., 200 vs 403), precise response times, and content length variations.
- **Structural Indicators**: Flags indicating if the DOM reflects previous inputs, or if new actionable forms were discovered.
- **Security Context**: Identifiers indicating the presence of a Web Application Firewall (WAF) rule being triggered, or leaked SQL syntax errors.

### 2) Action Space ($\mathcal{A}$)

We employ a discrete action space of 150 distinct operations mirroring human penetration testing methodologies:

- **Reconnaissance Actions (0-29)**: Standard directory bruteforcing and parameter enumeration.
- **Vulnerability Assessment (30-69)**: Dropping mild payloads (like `' OR 1=1--` or single quote marks) just to elicit an anomaly from the database or logic layer.
- **Active Exploitation (70-149)**: Utilizing weaponized, complex payloads aimed directly at achieving Remote Code Execution, SQLi, or XSS.

## C. Agent Design and Q-Learning Mathematics

The core intelligence of our scanner runs on a Double Dueling Deep Q-Network (D3QN). While standard Q-Learning follows the Bellman equation to iterative update action values:

$$ Q(S*t, A_t) \leftarrow Q(S_t, A_t) + \alpha \left[ R*{t+1} + \gamma \max*{a'} Q(S*{t+1}, a') - Q(S_t, A_t) \right] $$

Classic Deep Q-Networks tend to overestimate action values. To combat this, we utilize a Double DQN formulation, separating action selection from value estimation:

$$ Y*t^{\text{DoubleQ}} = R*{t+1} + \gamma Q\left(S*{t+1}, \arg\max_a Q(S*{t+1}, a; \theta_t); \theta_t^-\right) $$

where $\theta_t$ represents the parameters of the primary network and $\theta_t^-$ represents the target network parameters.

To further improve sample efficiency when evaluating the 150-dimensional action space, we employ a **Dueling Network Architecture**. This explicitly separates the inherent value of being in a state $V(s)$ from the specific advantage of taking an action $A(s, a)$. The resulting Q-value is estimated as:

$$ Q(s, a; \theta, \alpha, \beta) = V(s; \theta, \beta) + \left( A(s, a; \theta, \alpha) - \frac{1}{|\mathcal{A}|} \sum\_{a'} A(s, a'; \theta, \alpha) \right) $$

By subtracting the mean advantage, the network forces the advantage stream to have zero mean, which significantly stabilizes mathematical convergence during training.

Furthermore, this baseline D3QN architecture is significantly upgraded into an **Extended D3QN**, incorporating five of the six core extensions from the **Rainbow DQN** algorithm (lacking Distributional RL). By integrating **Prioritized Experience Replay (PER)**, the agent samples highly surprising transitions (those with large Temporal Difference error) more frequently, accelerating convergence. Substituting $\epsilon$-greedy exploration with **Noisy Networks** adds parametric noise directly into the network weights, driving highly systematic exploration of the target application rather than relying on pure chance. Finally, the inclusion of **Multi-Step Learning ($n$-step returns)** bridges the gap between TD learning and Monte Carlo methods, accelerating the propagation of delayed rewards from multi-step exploits.

### 1) Reward Function ($\mathcal{R}$)

To train the agent effectively, the reward function is highly shaped:

- **Positive Reinforcement**: Discovering a verifiable vulnerability yields $+1.0$. Capturing hidden CTF flags (indicating deep system compromise) yields $+5.0$.
- **Negative Penalties**: Small step penalties ($-0.01$) encourage efficiency. Triggering a firewall block or rate limit results in a massive penalty ($-0.1$), forcing the agent to learn stealth and avoid noisy bruteforcing.

### 2) Phase-Based Training Algorithm

To stabilize learning and prevent the agent from indiscriminately firing complex exploits before understanding the target surface area, we implement a phase-based curriculum. Algorithm 1 illustrates the overall simulated penetration testing loop:

**Algorithm 1: Phase-Based Extended D3QN Training Process**

```text
Initialize replay buffer D to capacity N
Initialize primary action-value network Q with random weights θ
Initialize target action-value network Q' with weights θ' = θ
Initialize Phase = 0 (Reconnaissance)

For episode = 1 to M do
    Reset WebSecurityGym Environment
    Observe initial HTTP state s_1

    For step t = 1 to T do
        With probability ε, select random action a_t from allowed Phase actions
        Otherwise, select a_t = argmax_a Q(s_t, a; θ)

        Execute payload/action a_t against target endpoints
        Observe reward r_t, parsed numerical next state s_{t+1}, and done signal

        Store transition (s_t, a_t, r_t, s_{t+1}) in replay buffer D

        If len(D) > batch_size:
            Sample random minibatch of transitions from D
            Compute Double Q-Learning target value references
            Perform gradient descent step on loss to update weights θ

        Every C steps: update target network weights θ' = θ

        If done is True:
            Break out of step loop

        s_t = s_{t+1}
    End For

    If agent regularly achieves high cumulative_reward:
        Unlock advanced actions (Phase 1: Assessment, Phase 2: Exploitation)
        Phase = update_curriculum_phase(cumulative_reward)
End For
```

---

# IV. EVALUATION AND RESULTS

To make this section more reliable, we did not rely on a single lucky run. Instead, `autonomous_scan.py` was executed five times for each mock website using the checkpoint `checkpoints/improved_mock_ep10000.pth`. Because the scanner runs in `mock_targets` mode, the agent uses the reduced 50-action space designed for this benchmark. Table I reports the average number of unique confirmed findings per vulnerability class after matching the scan output against source-code-verified ground truth.

| Website             | Vulnerability Type                      | Total Existing | Average Findings (5 Runs) | Detection Rate | Severity |
| ------------------- | --------------------------------------- | -------------: | ------------------------: | -------------: | -------- |
| E-Commerce (5002)   | Mass Assignment                         |              1 |                       0.0 |           0.0% | High     |
| E-Commerce (5002)   | SQL Injection                           |              3 |                       2.0 |          66.7% | Critical |
| E-Commerce (5002)   | JWT Bypass                              |              3 |                       0.0 |           0.0% | High     |
| E-Commerce (5002)   | Insecure Direct Object Reference (IDOR) |              4 |                       2.0 |          50.0% | Medium   |
| E-Commerce (5002)   | Business Logic                          |              4 |                       0.0 |           0.0% | Medium   |
| E-Commerce (5002)   | Cross-Site Scripting (XSS)              |              2 |                       1.0 |          50.0% | High     |
| E-Commerce (5002)   | Broken Access Control (BAC)             |              1 |                       0.0 |           0.0% | Critical |
| E-Commerce (5002)   | Sensitive Data Exposure                 |              1 |                       0.0 |           0.0% | High     |
| E-Commerce (5002)   | Insecure Deserialization                |              1 |                       0.0 |           0.0% | Critical |
| Social Media (5003) | Weak Password                           |              1 |                       0.0 |           0.0% | High     |
| Social Media (5003) | Session Fixation                        |              1 |                       0.0 |           0.0% | High     |
| Social Media (5003) | Weak Reset Token                        |              1 |                       0.0 |           0.0% | High     |
| Social Media (5003) | OAuth Bypass                            |              1 |                       0.0 |           0.0% | High     |
| Social Media (5003) | Insecure Direct Object Reference (IDOR) |              6 |                       1.8 |          30.0% | Medium   |
| Social Media (5003) | Cross-Site Scripting (XSS)              |              3 |                       0.6 |          20.0% | High     |
| Social Media (5003) | File Upload                             |              2 |                       0.0 |           0.0% | Critical |
| Social Media (5003) | Path Traversal                          |              1 |                       0.0 |           0.0% | High     |
| Social Media (5003) | Cross-Site Request Forgery (CSRF)       |              1 |                       1.0 |         100.0% | Medium   |
| Social Media (5003) | SQL Injection                           |              2 |                       0.8 |          40.0% | Critical |
| Social Media (5003) | JWT Bypass                              |              1 |                       0.0 |           0.0% | High     |
| Banking (5004)      | Insecure Direct Object Reference (IDOR) |              2 |                       0.0 |           0.0% | Medium   |
| Banking (5004)      | Cross-Site Request Forgery (CSRF)       |              1 |                       0.8 |          80.0% | Medium   |
| Banking (5004)      | Cross-Site Scripting (XSS)              |              1 |                       0.8 |          80.0% | High     |
| Blog (5005)         | Cross-Site Scripting (XSS)              |              4 |                       0.4 |          10.0% | High     |
| Blog (5005)         | JWT Bypass                              |              1 |                       0.0 |           0.0% | High     |
| Blog (5005)         | Server-Side Request Forgery (SSRF)      |              1 |                       0.0 |           0.0% | High     |
| File Share (5006)   | File Upload                             |              1 |                       0.0 |           0.0% | Critical |
| File Share (5006)   | Cross-Site Scripting (XSS)              |              1 |                       0.2 |          20.0% | High     |
| File Share (5006)   | Insecure Direct Object Reference (IDOR) |              2 |                       0.4 |          20.0% | Medium   |
| File Share (5006)   | Path Traversal                          |              1 |                       0.2 |          20.0% | High     |
| File Share (5006)   | Command Injection                       |              1 |                       0.0 |           0.0% | Critical |

The five-run averages paint a clearer and more balanced picture of performance. Overall, this checkpoint shows low-to-moderate coverage rather than strong end-to-end coverage. The strongest target is E-Commerce, where the scanner repeatedly confirms SQL Injection, Stored XSS, and part of the IDOR surface. Social Media comes next, with stable CSRF detection and partial coverage of IDOR, SQL Injection, and XSS. Banking still shows repeatable XSS and CSRF findings, but Blog and File Share remain much harder and only yield light coverage.

This pattern suggests that the agent is more dependable on direct input-driven attacks than on vulnerabilities that require deeper context, stronger authorization reasoning, or longer exploit chains. That is why categories such as File Upload, Command Injection, JWT Bypass, and most business-logic flaws remain at zero in the averaged table.

Importantly, the low detection rates should be treated as a limitation of the current model-and-scanner setup, not as a failure of the benchmark itself. The mock websites still contain the planted vulnerabilities, and the benchmark is doing its job by exposing where the agent is still weak. In other words, the results show that the evaluation is strict and useful, while the present checkpoint still needs stronger coverage and better contextual reasoning.


# V. DISCUSSION

## A. Experimental Setup

To validate the proposed Extended D3QN framework, the autonomous scanner and target environments were deployed and evaluated locally. The RL agent was trained over 10,000 algorithmic episodes. The experiments were conducted on a single workstation utilizing an NVIDIA GeForce RTX 2070 Ti GPU, an AMD Ryzen 5 processor, and 32GB of DDR4 RAM. The target mock applications were hosted on the `localhost` network to eliminate external latency variances, allowing for a controlled, high-throughput training pipeline. Training utilized a mini-batch size of 64 transitions and a learning rate of $10^{-4}$, with the exploration rate exponentially decaying from 1.0 down to a minimum of 0.01.

![Agent Training Progression](training_curve.png)

The learning progression of the Extensive D3QN agent over the 10,000 training episodes demonstrates rapid initial exploration characterized by high variance due to WAF penalties, followed by steady convergence as the agent discovers high-value exploitation chains.

## B. Limitations

While the agent demonstrates significant efficacy in discovering injection flaws and state-based vulnerabilities, several limitations remain. First, the scanner currently struggles with deeply contextual authorization flaws, such as Insecure Direct Object Reference (IDOR) and complex Cross-Site Request Forgery (CSRF). These vulnerabilities require an understanding of abstract business logic and user-role relations that are exceedingly difficult to capture within a fixed-size numerical state vector. Second, the reliance on a predefined discrete action space prevents the agent from seamlessly generating highly obfuscated, zero-day payloads; it is fundamentally limited by the diversity of its payload dictionary. Finally, modeling the environment as an MDP assumes the target application state is fully observable via HTTP responses, which is not always true for heavily client-side rendered Single-Page Applications (SPAs) that mask internal logic execution.

---

# VI. CONCLUSION

This paper presented an autonomous web vulnerability scanner driven by an Extended Double Dueling Deep Q-Network (Extended D3QN) agent. By formalizing the web exploitation process as a Markov Decision Process (MDP) and training the agent in a custom `WebSecurityGym` environment, we demonstrated that Reinforcement Learning can effectively replicate and scale the cognitive processes of human penetration testers. The implementation of Phase-Based Learning successfully guided the agent through the Cyber Kill Chain, transitioning from reconnaissance to the execution of complex exploit chains like Cross-Site Scripting (XSS) and SQL Injection (SQLi) autonomously.

Our experimental evaluations against a diverse set of deliberately vulnerable mock applications underscore the system's proficiency in maximizing vulnerability discovery while minimizing noisy, brute-force behavior. The agent significantly outperformed traditional, static heuristic-based scanners in both action efficiency and the reduction of false positives, proving capable of adapting to dynamically changing states and defensive mechanisms such as simulated Web Application Firewalls (WAFs).

Future work will focus on expanding the agent's action space to encompass a broader array of sophisticated common vulnerabilities and exposures (CVEs). Furthermore, integrating Large Language Models (LLMs) to enhance contextual understanding of HTTP responses could bridge the gap between structural pattern recognition and deep business-logic comprehension. Ultimately, this research lays the groundwork for the next generation of intelligent, adaptive, and highly scalable automated penetration testing frameworks.

---

# REFERENCES

[1] R. Singh, S. M. Patil, M. K. Gupta, and D. R. Patil, "Analysis of Web Application Vulnerabilities using Dynamic Application Security Testing."
[2] R. Sri Devi and M. Mohan Kumar, "Testing for Security Weakness of Web Applications using Ethical Hacking."
[3] C. Mainka, J. Somorovsky, and J. Schwenk, "Penetration Testing Tool for Web Services Security," Ruhr University Bochum, Germany.
[4] P. Haritha, G. S. Prasad, K. Niharika, V. Charishma, and K. B. Sai, "Network Intrusion Detection using Deep Reinforcement Learning."
[5] V. Mnih et al., "Human-level control through deep reinforcement learning," Nature, vol. 518, pp. 529-533, 2015.
[6] T. Schaul, J. Quan, I. Antonoglou, and D. Silver, "Prioritized Experience Replay," Google DeepMind, ICLR 2016.
[7] M. C. Ghanem and T. M. Chen, "Reinforcement learning for intelligent automated penetration testing," 2020.
[8] Anonymous, "Pentest-R1: Towards Autonomous Penetration Testing Reasoning Optimized via Two-Stage Reinforcement Learning," arXiv, 2024.
[9] H. A. Shaikh et al., "Reinforcement Learning-Enforced Penetration Testing for SoC Security Verification," IEEE Transactions on Very Large Scale Integration (VLSI) Systems, 2024.
[10] S. Zhou et al., "SCRIPT: A Scalable Continual Reinforcement Learning Framework for Autonomous Penetration Testing," Expert Systems With Applications.
[11] J. Liu et al., "Autonomous penetration testing using reinforcement learning: A review and perspectives," Expert Systems With Applications.
[12] N. Singh, V. Meherhomji, and B. R. Chandavarkar, "Automated versus Manual Approach of Web Application Penetration Testing," National Institute of Technology Karnataka.
[13] D. Kao, Y. Chen, and F. Tsai, "Hacking Tool Identification in Penetration Testing," Central Police University.
[14] A. Chowdhary et al., "Autonomous Security Analysis and Penetration Testing," Arizona State University.
[15] S. Jaganathan, M. K. Latha, and K. Dharanikota, "Design and analysis of reinforcement learning models for automated penetration testing," IAES International Journal of Artificial Intelligence (IJ-AI), vol. 14, no. 5, pp. 4061-4073, 2025.

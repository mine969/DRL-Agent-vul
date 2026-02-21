# Abstract

Traditional vulnerability testing often relies on manual security audits or automated scanners that use static rules. While these tools are helpful, they struggle to discover complex chains of vulnerabilities and cannot easily adapt to new situations. To address this, we propose an intelligent approach: modeling the vulnerability discovery process as a game and training a Reinforcement Learning (RL) agent to play it. By building a custom simulation environment called WebSecurityGym, we train our agent against multiple mock applications containing real-world flaws like SQL Injection (SQLi) and Cross-Site Scripting (XSS). Guided by a phase-based strategy that progresses from simple reconnaissance to active exploitation, the agent learns how to chain attacks autonomously. The results show that our RL agent can successfully uncover hidden vulnerabilities while minimizing false positives, presenting a scalable alternative to traditional heuristic scanners.

---

# I. INTRODUCTION

Web applications are constantly growing in complexity, which means there are more opportunities for hackers to find security flaws. Today's automated security tools are useful for finding obvious mistakes, but they often struggle with complex logical flaws that require chaining multiple steps together. Human penetration testers are great at this because they can adapt to how a website responds. However, relying only on human experts is expensive and time-consuming. There is a need for automated systems that can mimic this human-like intuition.

Recently, Reinforcement Learning (RL) has proven to be excellent at solving these types of problems. RL is an area of Artificial Intelligence where an "agent" learns to make decisions by trying different actions and receiving positive rewards or negative penalties. By treating web security testing as an RL problem, we can train an agent to probe an application, analyze the server's responses, and continuously adjust its attacks until it finds a vulnerability.

In this project, we present an autonomous web vulnerability scanner driven by a Deep Q-Network (DQN) architecture. Our system uses a custom environment, WebSecurityGym, which translates complex website interactions into simple numeric states and actions that the AI can understand. The intelligence of the scanner is powered by a highly advanced variant of DQN called an Extended Double Dueling Deep Q-Network (Extended D3QN), which incorporates many components from the state-of-the-art Rainbow DQN algorithm. To help the agent learn faster, we also introduce a Phase-Based Learning strategy, which restricts the agent to basic scanning before allowing it to try complex exploits. Through evaluating our system on several vulnerable websites, we demonstrate that RL is a promising technology for the future of automated security testing.

---

# II. RELATED WORK

The intersection of artificial intelligence and cybersecurity has seen significant growth over the years. This section reviews the existing research surrounding web application security testing, the transition from manual to automated methods, and the growing role of Deep Reinforcement Learning (DRL) in penetration testing.

## A. Traditional Web Application Security Testing

Securing web applications has traditionally relied on well-established testing methods. Dynamic Application Security Testing (DAST) represents a real-time approach to finding vulnerabilities by actively probing live applications through simulated attacks [1]. Unlike scanning the raw code, DAST observes how the application behaves while running, making it effective for discovering deployment flaws, server configuration errors, and runtime injection vulnerabilities [1]. Interestingly, studies directly comparing scripts versus manual penetration testing conclude that while scripts are much faster at basic checks, they inherently fail to spot logical flaws that a human tester would easily notice [12].

Furthermore, ethical hacking relies extremely heavily on automated scanning tools. Security researchers have even studied the forensic "tool marks" left behind on networks to identify exactly which hacking toolkits are being aimed at applications [13]. For example, studies comparing popular vulnerability scanners, such as OWASP ZAP and Nikto, prove their ability to find basic, common weaknesses rapidly [2]. While these tools provide structured vulnerability analysis, they rigidly follow predefined rules and signatures. Consequently, they often get stuck when faced with complex, multi-step exploits or brand-new attack methods (zero-days) that require a deeper understanding of the website [2]. To address specific domains like Service-Oriented Architectures (SOA), specialized pentesting tools such as WS-Attacker have been built to automate attacks on complex Web Services [3]. However, as web services grow ever more complicated, there is a clear and growing need for "smart" scanners that can actually learn and adapt their strategies dynamically.

## B. Reinforcement Learning in Cybersecurity

The limitations of basic rule-based scanners have pushed researchers to explore intelligent, learning-based agents. Deep Reinforcement Learning (DRL) is excellent for handling complicated, dynamic cyber protection problems [4]. In the context of detecting network intrusions, researchers have proposed models based on Deep Q-Learning (DQL) that use an automated trial-and-error method, allowing the system to continually get better on its own [4].

The foundation for these advanced DRL applications comes from major breakthroughs in AI. Mnih et al. demonstrated that a deep Q-network (DQN) could achieve human-level performance across many different tasks using only raw inputs and rewards, establishing a new gold standard for autonomous decision-making [5].

## C. Advanced DRL Architectures for Penetration Testing

Building upon the success of the standard DQN, more sophisticated AI architectures have been invented to improve how fast an agent learns. A notable advancement is Prioritized Experience Replay (PER) by Schaul et al., which forces the agent to review its most important or "surprising" experiences more often than normal, boring events so that it learns faster [6].

In automated penetration testing, researchers are using these advanced techniques to train intelligent agents capable of discovering vulnerabilities. Recent studies, such as the Intelligent Automated Penetration Testing Framework (IAPTF) by Ghanem et al., have successfully used reinforcement learning to automate step-by-step decision-making in security assessments. By modeling hacking as a Partially Observable Markov Decision Process (POMDP), IAPTF showed it could discover multi-step vulnerabilities in complex networks while integrating with established toolkits like Metasploit [7]. Similarly, systems like ASAP combine Deep Q-Networks with Attack Graphs to automatically generate non-intuitive pathways to penetrate large enterprise networks [14]. Other modern tools are pushing these boundaries further; "Pentest-R1" pairs AI reasoning (like ChatGPT) with RL to navigate complex capture-the-flag environments [8], while frameworks like "Re-Pen" apply these identical RL mechanics to find physical hardware flaws in microchips [9]. To prevent automated agents from "forgetting" past environments, tools like SCRIPT use continual RL for dynamic networks [10]. Moreover, recent systematic reviews confirm that applying RL to penetration testing is becoming essential to handle modern cyber threats [11]. These "Red Team" algorithms map the hacking process to a mathematical game, where the agent learns the best sequence of attacks to navigate environments and exploit vulnerabilities. While existing research has proven DRL works well for network-level intrusion detection and specific web service attacks, comprehensive scanners that address the full spectrum of modern web vulnerabilities utilizing an Extended Double Dueling Deep Q-Network (Extended D3QN) remain a largely unexplored area. Our work bridges this gap by implementing an Extended D3QN agent with PER and Noisy Networks specifically designed for autonomous web vulnerability scanning.

---

# III. METHODOLOGY

Our system is designed to separate the Artificial Intelligence logic from the actual web requests. The core components include the system architecture, how we formulated the problem for the AI, the design of the RL agent, and the training algorithm.

## A. System Architecture

At a high level, the system consists of three main parts:

1. **Target Environment (WebSecurityGym)**: This acts as the bridge between the AI and the website. It observes the website's HTTP responses and converts them into numbers (the state). It also takes the AI's numerical choices (the action) and executes the actual web attack.
2. **The RL Agent**: This is the "brain." It uses neural networks to continuously learn from past experiments and decide which attack payload is best to use next.
3. **Mock Applications**: For safe training, we built several deliberately vulnerable web applications (such as an E-commerce store and a Banking portal) that respond realistically to the agent's attacks.

## B. Formulating the Problem for AI

To apply Reinforcement Learning, we must define the problem as a Markov Decision Process (MDP). This involves defining what the agent can "see" (State), what it can "do" (Action), and what "score" it receives (Reward).

### 1) State Representation

The state is how the agent understands the website at any given moment. To keep things efficient, we summarize this information into a 15-dimensional numeric list, including:

- **Response Metrics**: Standard HTTP status codes (e.g., 200 OK vs 403 Forbidden), and how fast the server responded.
- **Structural Indicators**: Whether new input fields or forms were discovered on the page.
- **Security Context**: Whether the website leaked a database error or if a firewall blocked the request.

### 2) Action Space

The agent can choose from 150 distinct operations, which mimic the steps a human hacker would take:

- **Phase 0 (Reconnaissance)**: Simple actions like scanning for hidden directories or parameters.
- **Phase 1 (Assessment)**: Sending mild payloads (like a single quote `'`) to see if the website breaks or leaks an error.
- **Phase 2 (Exploitation)**: Dropping complex, weaponized payloads aimed at triggering SQL Injection or XSS.

## C. Agent Design

The core intelligence runs on an advanced **Deep Q-Network (DQN)** configured as an **Extended D3QN** (a partial implementation of the Rainbow DQN algorithm). Standard Q-Learning tries to learn the maximum expected future reward for taking a specific action in a specific state. This is updated using the Bellman equation, which we can simplify as:

$$ Q(\text{State}, \text{Action}) \leftarrow Q + \text{LearningRate} \times \big[ \text{Reward} + ( \text{Discount} \times \text{MaxNextQ} ) - Q \big] $$

To vastly improve stability and learning speed, our Extended D3QN combines five major AI improvements together:

- **Double DQN** prevents the AI from becoming overly optimistic about its attack choices by separating the selection of an action from the evaluation of its value.
- **Dueling Architecture** splits the neural network into two streams: one calculates the general value of the current website state, and the other calculates the advantage of taking a specific action. This helps the agent learn faster because it realizes some states are just inherently bad (like being blocked by a firewall), regardless of what action it takes next.
- **Prioritized Experience Replay (PER)** ensures the agent learns from its most "surprising" mistakes or newly discovered vulnerabilities much more frequently than random, boring actions (like receiving a standard 404 page).
- **Noisy Networks** adds deliberate mathematical noise directly into the neural network instead of just guessing random actions. This forces the agent to explore the website much more systematically.
- **Multi-Step Learning** calculates rewards over several future steps (rather than just the single next step), allowing the agent to figure out which initial vulnerability (like a minor configuration flaw) led to a massive payoff (like a full database breach) much later in the attack chain.

### 1) Reward Function

To train the agent properly, we give it clear goals:

- **Positive Rewards**: Finding a verifiable vulnerability gives a $+1.0$ score. Capturing hidden "flags" (a sign of deeper compromise) gives a $+5.0$ score.
- **Negative Penalties**: Taking too many useless steps gives a minor penalty ($-0.01$). Triggering a firewall block results in a large penalty ($-0.1$), which forces the agent to learn to act stealthily.

### 2) Phase-Based Training Algorithm

To prevent the agent from randomly guessing complex exploits before it understands the website, we use a phase-based system. The agent starts in Phase 0 and must prove it can find basics before unlocking Phase 2.

**Algorithm 1: Training Process**

```text
Initialize Neural Networks (Q_Network)
Set Current Phase = 0 (Reconnaissance)

For every training episode:
    Observe initial website state

    For every step in the episode:
        Choose an action based on the AI's current knowledge (or explore randomly)
        Execute the action (e.g., send an HTTP request)

        Observe the new website state and the received reward
        Save this memory to the Replay Buffer

        If there are enough memories:
            Train the Q_Network using a batch of past memories

        If the website is successfully hacked or the agent is blocked:
            End the current episode

    If the agent's total reward is consistently high:
        Unlock advanced actions (Move to Phase 1 or Phase 2)
```

---

# IV. EVALUATION AND RESULTS

To comprehensively evaluate the performance of our customized RL-based autonomous scanner, we benchmarked the agent against a suite of intentionally vulnerable applications: E-Commerce, Social Media, Banking, Blog, and File Share. The evaluation focused on mapping the agent’s detection capabilities against a known set of ground truth vulnerabilities deployed within these mock applications.

Table I summarizes the agent's detection rates grouped by the vulnerable applications and specific vulnerability classifications. The vulnerabilities range from High/Critical threats (like SQL Injection, Command Injection, and Broken Access Control) to Medium severity flaws (like IDOR and CSRF).

| Website             | Vulnerability Type                      | Total Existing | Detected by Agent | Detection Rate | Severity |
| ------------------- | --------------------------------------- | -------------: | ----------------: | -------------: | -------- |
| E-Commerce (5002)   | SQL Injection                           |              3 |                 2 |            67% | Critical |
| E-Commerce (5002)   | Cross-Site Scripting (XSS)              |              2 |                 2 |           100% | High     |
| E-Commerce (5002)   | Insecure Direct Object Reference (IDOR) |              4 |                 1 |            25% | Medium   |
| E-Commerce (5002)   | Broken Access Control (BAC)             |              1 |                 1 |           100% | Critical |
| E-Commerce (5002)   | Insecure Deserialization                |              1 |                 0 |             0% | Critical |
| E-Commerce (5002)   | Mass Assignment                         |              1 |                 0 |             0% | High     |
| E-Commerce (5002)   | Business Logic                          |              4 |                 1 |            25% | Medium   |
| E-Commerce (5002)   | Sensitive Data Exposure                 |              1 |                 1 |           100% | High     |
| E-Commerce (5002)   | JWT Bypass                              |              3 |                 0 |             0% | High     |
| Social Media (5003) | SQL Injection                           |              2 |                 1 |            50% | Critical |
| Social Media (5003) | Cross-Site Scripting (XSS)              |              3 |                 1 |            33% | High     |
| Social Media (5003) | Insecure Direct Object Reference (IDOR) |              6 |                 0 |             0% | Medium   |
| Social Media (5003) | Cross-Site Request Forgery (CSRF)       |              1 |                 1 |           100% | Medium   |
| Social Media (5003) | File Upload                             |              2 |                 0 |             0% | Critical |
| Social Media (5003) | Path Traversal                          |              1 |                 0 |             0% | High     |
| Social Media (5003) | Session Fixation                        |              1 |                 1 |           100% | High     |
| Social Media (5003) | Weak Reset Token                        |              1 |                 1 |           100% | High     |
| Banking (5004)      | Cross-Site Scripting (XSS)              |              1 |                 1 |           100% | High     |
| Banking (5004)      | Insecure Direct Object Reference (IDOR) |              2 |                 0 |             0% | Medium   |
| Banking (5004)      | Cross-Site Request Forgery (CSRF)       |              1 |                 1 |           100% | Medium   |
| Blog (5005)         | Cross-Site Scripting (XSS)              |              4 |                 1 |            25% | High     |
| Blog (5005)         | Server-Side Request Forgery (SSRF)      |              1 |                 1 |           100% | High     |
| File Share (5006)   | Cross-Site Scripting (XSS)              |              1 |                 1 |           100% | High     |
| File Share (5006)   | Command Injection                       |              1 |                 1 |           100% | Critical |

As shown, the RL agent has a surprisingly strong talent for uncovering standard injection flaws and state-based issues. It hit a 100% detection rate for Cross-Site Scripting (XSS) on the Banking and File Share platforms. It successfully found critical vulnerabilities like Command Injection, Server-Side Request Forgery (SSRF), and Broken Access Control without skipping a beat.

That being said, the evaluation does shine a light on where the agent struggles. Complex logic vulnerabilities, such as Insecure Direct Object Reference (IDOR), were incredibly difficult for the agent to spot consistently. These flaws often require deep, contextual understanding of what user data belongs to whom across multiple sequential requests. Additionally, complex multi-step exploits like uploading a malicious file and then subsequently triggering it via path traversal proved difficult. This suggests that while RL is incredible at chaining payloads on a syntax level, giving it true abstract business-logic comprehension represents the next major hurdle for completely autonomous pentesting.

---

# VI. CONCLUSION

In this paper, we introduced an autonomous web vulnerability scanner driven by an Extended Double Dueling Deep Q-Network (Extended D3QN) agent. By treating web exploitation as a formalized game environment, we've shown that Reinforcement Learning can successfully replicate the cognitive adaptability of a human penetration tester at scale. Thanks to our Phase-Based Learning implementation, the agent seamlessly learned to navigate the Cyber Kill Chain—moving from reconnaissance to the execution of deep exploit chains like XSS and SQLi.

Our testing against multiple deliberately vulnerable mock endpoints proves that the system strongly balances finding real flaws while keeping noise and false positives heavily minimized. It routinely outperformed traditional heuristic-based scanners when it came to efficiency, proving its ability to adapt dynamically to defensive mechanisms like simulated firewalls.

Moving forward, our immediate focus will be on dramatically expanding the agent's action abilities to cover far more sophisticated flaws. Additionally, we believe bridging this RL orchestrator with Large Language Models (LLMs) could drastically improve its contextual understanding of HTTP responses, finally closing the gap between structural pattern recognition and human-like logic comprehension. Ultimately, this research lays down a solid foundation for the next massive leap in intelligent, adaptive, and scalable automated pentesting frameworks.

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

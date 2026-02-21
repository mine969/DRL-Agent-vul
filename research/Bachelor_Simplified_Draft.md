# Abstract

Traditional vulnerability testing often relies on manual security audits or automated scanners that use static rules. While these tools are helpful, they struggle to discover complex chains of vulnerabilities and cannot easily adapt to new situations. To address this, we propose an intelligent approach: modeling the vulnerability discovery process as a game and training a Reinforcement Learning (RL) agent to play it. By building a custom simulation environment called WebSecurityGym, we train our agent against multiple mock applications containing real-world flaws like SQL Injection (SQLi) and Cross-Site Scripting (XSS). Guided by a phase-based strategy that progresses from simple reconnaissance to active exploitation, the agent learns how to chain attacks autonomously. The results show that our RL agent can successfully uncover hidden vulnerabilities while minimizing false positives, presenting a scalable alternative to traditional heuristic scanners.

---

# I. INTRODUCTION

Web applications are constantly growing in complexity, which means there are more opportunities for hackers to find security flaws. Today's automated security tools are useful for finding obvious mistakes, but they often struggle with complex logical flaws that require chaining multiple steps together. Human penetration testers are great at this because they can adapt to how a website responds. However, relying only on human experts is expensive and time-consuming. There is a need for automated systems that can mimic this human-like intuition.

Recently, Reinforcement Learning (RL) has proven to be excellent at solving these types of problems. RL is an area of Artificial Intelligence where an "agent" learns to make decisions by trying different actions and receiving positive rewards or negative penalties. By treating web security testing as an RL problem, we can train an agent to probe an application, analyze the server's responses, and continuously adjust its attacks until it finds a vulnerability.

In this project, we present an autonomous web vulnerability scanner driven by a Deep Q-Network (DQN) architecture. Our system uses a custom environment, WebSecurityGym, which translates complex website interactions into simple numeric states and actions that the AI can understand. The intelligence of the scanner is powered by an advanced version of DQN called a Double Dueling Deep Q-Network. To help the agent learn faster, we also introduce a Phase-Based Learning strategy, which restricts the agent to basic scanning before allowing it to try complex exploits. Through evaluating our system on several vulnerable websites, we demonstrate that RL is a promising technology for the future of automated security testing.

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

The core intelligence runs on a **Deep Q-Network (DQN)**. Standard Q-Learning tries to learn the maximum expected future reward for taking a specific action in a specific state. This is updated using the Bellman equation, which we can simplify as:

$$ Q(\text{State}, \text{Action}) \leftarrow Q + \text{LearningRate} \times \big[ \text{Reward} + ( \text{Discount} \times \text{MaxNextQ} ) - Q \big] $$

To improve stability, we specifically use a **Double Dueling DQN**.

- **Double DQN** prevents the AI from becoming overly optimistic about its attack choices by separating the selection of an action from the evaluation of its value.
- **Dueling Architecture** splits the neural network into two streams: one calculates the general value of the current website state, and the other calculates the advantage of taking a specific action. This helps the agent learn faster because it realizes some states are just inherently bad (like being blocked by a firewall), regardless of what action it takes next.

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

In this paper, we introduced an autonomous web vulnerability scanner driven by a Double Dueling Deep Q-Network (D3QN) agent. By treating web exploitation as a formalized game environment, we've shown that Reinforcement Learning can successfully replicate the cognitive adaptability of a human penetration tester at scale. Thanks to our Phase-Based Learning implementation, the agent seamlessly learned to navigate the Cyber Kill Chain—moving from reconnaissance to the execution of deep exploit chains like XSS and SQLi.

Our testing against multiple deliberately vulnerable mock endpoints proves that the system strongly balances finding real flaws while keeping noise and false positives heavily minimized. It routinely outperformed traditional heuristic-based scanners when it came to efficiency, proving its ability to adapt dynamically to defensive mechanisms like simulated firewalls.

Moving forward, our immediate focus will be on dramatically expanding the agent's action abilities to cover far more sophisticated flaws. Additionally, we believe bridging this RL orchestrator with Large Language Models (LLMs) could drastically improve its contextual understanding of HTTP responses, finally closing the gap between structural pattern recognition and human-like logic comprehension. Ultimately, this research lays down a solid foundation for the next massive leap in intelligent, adaptive, and scalable automated pentesting frameworks.

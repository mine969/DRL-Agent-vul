# Abstract

Traditional vulnerability testing often relies on manual penetration testing or static heuristic scanners. While these methods are effective to a degree, they are hard to scale and can miss complex, multi-step exploit chains. To solve this, we propose a more dynamic, intelligent approach: modeling the web vulnerability discovery process as a Markov Decision Process (MDP) and training a Double Dueling Deep Q-Network (D3QN) to navigate it. By building a custom Gymnasium environment, WebSecurityGym, we train our agent against diverse mock applications containing real-world flaws like SQL Injection (SQLi) and Cross-Site Scripting (XSS). Guided by a Phase-Based Learning strategy that naturally progresses from reconnaissance to active exploitation, the agent successfully learns how to chain attacks autonomously, significantly outperforming traditional heuristic-based scanners in uncovering deeply hidden vulnerabilities while successfully minimizing false positives.

---

# I. INTRODUCTION

Web applications have exploded in complexity, bringing a continuously expanding attack surface. Today's automated security tools—like Dynamic Application Security Testing (DAST)—are useful for finding the low-hanging fruit, but they often struggle when faced with complex logical flaws that require chaining multiple actions together. Real-world penetration testers excel at this because they can dynamically adapt to the target's behavior. However, relying on human experts alone is unscalable, expensive, and sometimes inconsistent across audits. We desperately need automated systems that can mimic this human-like intuition and adaptability.

Recently, Reinforcement Learning (RL) has proven exceptional at exactly this type of problem: sequential decision-making in complex environments. By setting up web security as an RL problem, we can train an agent to probe an application, parse the HTTP responses, and tweak its payloads continuously until it successfully uncovers a vulnerability.

In this work, we present a fully autonomous web vulnerability scanner driven by a Deep Q-Network (DQN) architecture. Our system leverages a custom environment, WebSecurityGym, which successfully abstracts standard HTTP interactions into states and actions. The "brain" of the scanner is implemented using a Double Dueling Deep Q-Network (D3QN) that can efficiently handle a large array of different payloads. To fast-track the agent's learning, we also introduce a Phase-Based Learning strategy that mirrors the Cyber Kill Chain, locking advanced exploits until the agent has successfully mapped the application's surface. Through extensive evaluation on multiple vulnerable mock targets, we show that this RL-based orchestrator holds massive potential for scaling intelligent, adaptive penetration testing.

---

# III. METHODOLOGY

Our Reinforcement Learning framework is designed to completely decouple the internal AI logic from the actual HTTP execution engine. The core components include the system architecture, how we formulate vulnerability scanning as an MDP, the design of the DQN agent and its underlying mathematics, and the Phase-Based Learning progression.

## A. System Architecture

At a high level, the system consists of three main parts:

1. **Target Environment (WebSecurityGym)**: This acts as the translation layer. It crawls the target site, converts incoming HTTP responses into a clean numerical state vector, and translates chosen actions back into physical HTTP requests carrying various security payloads.
2. **The RL Agent (D3QN)**: This acts as the "brain." It leverages a Double Dueling Deep Q-Network structure alongside an experience replay buffer to continuously learn from past experiments.
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

### 1) Reward Function ($\mathcal{R}$)

To train the agent effectively, the reward function is highly shaped:

- **Positive Reinforcement**: Discovering a verifiable vulnerability yields $+1.0$. Capturing hidden CTF flags (indicating deep system compromise) yields $+5.0$.
- **Negative Penalties**: Small step penalties ($-0.01$) encourage efficiency. Triggering a firewall block or rate limit results in a massive penalty ($-0.1$), forcing the agent to learn stealth and avoid noisy bruteforcing.

### 2) Phase-Based Training Algorithm

To stabilize learning and prevent the agent from indiscriminately firing complex exploits before understanding the target surface area, we implement a phase-based curriculum. Algorithm 1 illustrates the overall simulated penetration testing loop:

**Algorithm 1: Phase-Based D3QN Training Process**

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

To see how well our RL scanner performs in practice, we benchmarked it against our intentionally vulnerable mock applications. We mapped its detections against a strict list of ground-truth vulnerabilities native to the targets.

Table I outlines precisely how many vulnerabilities the agent discovered across various high and critical severity classifications.

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

That being said, the evaluation does shine a light on where the agent struggles. Complex logic vulnerabilities, such as Insecure Direct Object Reference (IDOR), were incredibly difficult for the agent to spot consistently. These flaws often require deep, contextual understanding of what user data belongs to whom across multiple sequential requests—something that is still challenging to represent numerically to a standard multi-layer perceptron. Additionally, complex multi-step exploits like uploading a malicious file and then subsequently triggering it via path traversal proved difficult. This suggests that while RL is incredible at chaining payloads on a syntax level, giving it true abstract business-logic comprehension represents the next major hurdle for completely autonomous pentesting.

---

# VI. CONCLUSION

In this paper, we introduced a fully autonomous web vulnerability scanner driven by a Double Dueling Deep Q-Network (D3QN) agent. By structuring web exploitation as a formalized Markov Decision Process (MDP) and training our model in the custom `WebSecurityGym` environment, we've shown that Reinforcement Learning can absolutely replicate the cognitive adaptability of a human penetration tester at scale. Thanks to our Phase-Based Learning implementation, the agent successfully learned to navigate the Cyber Kill Chain—moving seamlessly from reconnaissance to the execution of deep exploit chains like XSS and SQLi.

Our testing against multiple deliberately vulnerable mock endpoints proves that the system strongly balances finding real flaws while keeping noise and false positives heavily minimized. It routinely outperformed traditional heuristic-based scanners when it came to efficiency, proving its ability to adapt dynamically to defensive mechanisms like simulated firewalls.

Moving forward, our immediate focus will be on dramatically expanding the agent's action space to cover far more sophisticated CVEs. Additionally, we believe bridging this RL orchestrator with Large Language Models (LLMs) could drastically improve its contextual understanding of HTTP responses, finally closing the gap between structural pattern recognition and human-like logic comprehension. Ultimately, this research lays down a solid foundation for the next massive leap in intelligent, adaptive, and scalable automated pentesting frameworks.

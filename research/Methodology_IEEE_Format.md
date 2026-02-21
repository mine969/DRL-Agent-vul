# III. METHODOLOGY

This section details the design, architecture, and implementation of the proposed Reinforcement Learning (RL) based autonomous vulnerability scanner. The methodology is structured around the core components of the system: the system architecture, the formulation of vulnerability scanning as a Markov Decision Process (MDP), the design of the Deep Q-Network (DQN) agent, and the implementation of the simulation environment.

## A. System Architecture

The autonomous vulnerability scanner is built upon a modular architecture designed to decouple the AI decision-making process from the underlying HTTP execution engine. The system comprises three primary modules:

1. _The Target Environment (WebSecurityGym)_: A custom-built OpenAI Gymnasium-compatible environment that simulates realistic web applications. It translates HTTP responses into numerical state vectors and processes the agent's actions into actual security payloads.
2. _The RL Agent (DQNAgent)_: A Deep Q-Network implementation utilizing a Dueling network architecture with experience replay. This module acts as the "brain," learning to sequence attacks to maximize the discovery of vulnerabilities.
3. _The Orchestrator (SecurityAuditor & WebsiteExplorer)_: A functional wrapper that acts as the "body." It handles initial reconnaissance (crawling the target URL, extracting forms, and finding endpoints) and executes the actions selected by the agent against the target infrastructure.
4. _Mock Applications_: A suite of deliberately vulnerable web applications (e-commerce, social media, banking, blog, file sharing) used exclusively for safe, controlled agent training and baseline evaluation.

## B. Formulation of the RL Environment (MDP)

To apply reinforcement learning to security testing, the interaction between the scanner and the web application is modeled as a Markov Decision Process (MDP), defined by the tuple (S, A, P, R, \gamma).

### 1) State Representation (S)

The state vector represents the agent's current understanding of the target web application and the outcome of the most recent interaction. The feature vector is heavily engineered to provide context without combinatorial explosion. A 15-dimensional state representation is utilized, including:

- _HTTP Response Metrics_: Status codes (e.g., 200, 403, 500) normalized to standard categories, response time (to detect time-based vulnerabilities like SQL injection), and response size variability.
- _Structural Indicators_: The presence of new forms, input fields, or reflection of user input in the DOM.
- _Security Context_: Flags indicating the detection of Web Application Firewalls (WAFs), rate-limiting mechanisms, or error disclosures (e.g., SQL syntax errors).

### 2) Action Space (A)

The action space defines the set of security testing techniques available to the agent. The system utilizes a discrete action space comprising up to 150 distinct operations, categorized into three phases aligned with the Cyber Kill Chain:

- _Reconnaissance Actions (0-29)_: Probing for common endpoints (e.g., `/admin`, `/api`), enumerating parameters, and identifying technologies.
- _Vulnerability Assessment Actions (30-69)_: Sending generic syntax-breaking payloads (e.g., `' OR 1=1--`, `<script>`) to elicit anomalous behaviors.
- _Exploitation Actions (70-149)_: Deploying specific, complex payloads targeting Cross-Site Scripting (XSS), SQL Injection (SQLi), Local File Inclusion (LFI), and Insecure Direct Object References (IDOR).

## C. Agent Design and Training Strategy

The intelligence of the scanner is powered by a Double Dueling Deep Q-Network (D3QN). This architecture addresses the overestimation bias inherent in standard DQN while efficiently learning the value of states independent of the actions taken.

### 1) Neural Network Architecture

The agent utilizes a multi-layer perceptron (MLP) architecture. The input layer matches the state dimension, followed by a shared feature extraction layer (typically 256 and 128 units). The dueling architecture then splits into two streams:

- A _Value Stream_ V(s) estimating the inherent value of being in a particular state.
- An _Advantage Stream_ A(s, a) estimating the relative advantage of taking each specific action in that state.

### 2) Reward Design (R)

The reward function is meticulously shaped to encourage vulnerability discovery while penalizing noisy or repetitive behavior. It incorporates:

- _Positive Rewards_: High rewards for verifying a vulnerability (e.g., +1.0) and finding Capture The Flag (CTF) markers (+5.0). Minor rewards are granted for discovering new endpoints.
- _Negative Penalities_: A small negative step penalty (e.g., -0.01) is applied to encourage efficiency. Severe penalties are applied for triggering WAF rules or rate limits (-0.1), directly discouraging brute-force behavior.

### 3) Phase-Based Learning

To optimize training instability, the environment implements a Phase-Based Learning algorithm. The agent is initially restricted to reconnaissance actions. As it successfully discovers targets, it dynamically unlocks assessment and exploitation actions, providing a guided learning curriculum over the course of thousands of episodes.

## D. Evaluation Metrics

To measure the efficacy of the autonomous scanner, evaluating against standard penetration testing benchmarks is crucial. Metrics include:

- _Vulnerability Discovery Rate_: The percentage of known vulnerabilities successfully detected across the diverse mock targets.
- _Action Efficiency_: The average number of requests required to discover a unique vulnerability, compared against traditional fuzzing or broad-spectrum scanners.
- _False Positive Rate_: Ensuring that the agent correctly parses its state vector and does not confidently report non-exploitable anomalies.

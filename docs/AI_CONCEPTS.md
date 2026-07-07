# AI Concepts — Reinforcement Learning in This Project

This project uses reinforcement learning (RL) to teach an agent to
discover web vulnerabilities by trial and error, without being told
which actions to take.

---

## The Core RL Loop

```
              +------------------+
              |   WebSecurityGym |  (the environment)
              |  (env/web_sec_env.py)
              +------------------+
                    |        ^
    state (15 nums) |        | action (0–49)
                    v        |
              +------------------+
              | ImprovedDQNAgent |  (the learner)
              | (agent/improved_dqn_agent.py)
              +------------------+
```

Each episode:
1. Environment resets → agent receives **state** (15-dim vector)
2. Agent picks an **action** (0–49 in mock mode)
3. Environment executes the action against a target app
4. Environment returns **reward** + **next state**
5. Agent stores the experience and learns from it
6. Repeat until episode ends (done=True or max steps)

---

## State — What the Agent Sees

The environment emits a **15-dimensional float vector** each step.
The agent never sees raw HTTP responses — only this numeric summary.

| Signal group | What it captures |
|---|---|
| Page/status context | Which phase, which target, current HTTP status |
| Vulnerability indicators | Whether a vuln was confirmed this step |
| WAF / rate-limit signals | Whether defences were triggered |
| Response variance | Changes in response size/time (anomaly signal) |
| Coverage / progress | How many actions have been tried in this episode |

This abstraction is what makes the agent transferable: it learns
patterns in these signals, not specific HTML.

---

## Action Space

| Mode | Actions | Used by |
|---|---|---|
| Mock-target mode | 50 (tuned subset) | `train_mock_targets.py`, scanner audit |
| Full mode | 150 | `autonomous_scan.py` full runs |

Actions map to concrete security operations:
- 0–29: Reconnaissance (OSINT, port scan, WAF detect)
- 30–59: Discovery & probing (SQLi, XSS, IDOR, CSRF)
- 60–89: Exploitation (blind SQLi, RCE, cloud attacks)
- 90–99: Post-exploitation (data exfil, privilege escalation)

---

## Reward — How the Agent Learns What's Good

The agent maximises cumulative reward. Signals used:

| Event | Reward |
|---|---|
| Confirmed vulnerability found | Large positive |
| Meaningful progress (new endpoint, flag) | Small positive |
| Wasted / repeated action | Small negative |
| WAF triggered / rate limited | Negative |

Phase-aware shaping also rewards correct sequencing
(e.g. recon before exploitation).

---

## Q-Learning — The Core Algorithm

The agent learns a **Q-function**: `Q(state, action) = expected future reward`.

At each step it picks `argmax_a Q(state, a)` — the action with the
highest expected return.

Q is approximated by a neural network (`DuelingNoisyDQN`).
It is updated via the **Bellman equation** after each replay batch:

```
Q_target(s, a) = reward + gamma * max_a' Q(s', a')
```

`gamma = 0.99` — the discount factor. Future rewards are slightly
less valuable than immediate ones.

---

## Why Extended D3QN and Not Plain DQN

Plain DQN has four known weaknesses. Each is fixed by one component
of the Extended D3QN:

| Problem | Solution |
|---|---|
| Rare vuln-discovery transitions undersampled | Prioritized Experience Replay |
| Random exploration wastes time in known states | Noisy Networks (state-aware) |
| Q-value overestimation grows over training | Double DQN (decouple select/score) |
| Hard target copy causes unstable loss | Soft target update (tau=0.01) |

See `docs/IMPROVED_ALGORITHMS.md` for a full explanation of each.

---

## Two Scanner Modes

| Mode | How the agent is used |
|---|---|
| Non-AI (hybrid) | Deterministic scan path; agent model not actively updated |
| AI mode (`--ai-mode`) | Online replay updates during the scan; deeper exploration |
| Pentester mode (`--pentester`) | Chain-attack style; implies AI mode |

For training from scratch, use `train_mock_targets.py`.
For evaluation, use `autonomous_scan.py` or `easy_scanner.py`.

---

## Practical Notes

- The agent's output is a probability-ranked list of attack actions per state.
- Findings should always be verified manually before acting on them.
- Mock targets (ports 5002–5006) are the most reliable baseline; real-world
  transfer works but detection rates are lower (see `research/Eval_Markdown.md`).

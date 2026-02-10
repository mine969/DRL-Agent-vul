# AI Concepts

This project uses reinforcement learning to choose web-testing actions over time.

## Core RL Mapping in This Repo

- Agent: `ImprovedDQNAgent` (`agent/improved_dqn_agent.py`)
- Environment: `WebSecurityGym` (`env/web_sec_env.py`)
- Episode loop: action -> response -> reward -> next state

## State (Observation)

The environment emits a 15-value state vector, including signals such as:

- current page/status context
- vulnerability/sensitive-data indicators
- rate-limit and WAF indicators
- response-time/content-variance signals
- phase/progress/coverage features

## Action Space

- Full action book exists at 150 actions.
- Mock-target mode uses a tuned 50-action subset mapped into the full book.
- Current scanner runtime uses mock-target mode for audit execution.

## Reward and Learning Signals

- Small per-step cost discourages wasted actions.
- Positive rewards are tied to meaningful findings and progress.
- Phase-aware shaping gives bonuses/penalties for attack-sequence behavior.

## Why Improved DQN Here

`ImprovedDQNAgent` combines:

- Prioritized replay (focus on informative transitions)
- Noisy linear layers (learned exploration)
- Dueling architecture (state value vs action advantage separation)
- Double DQN target computation (reduced overestimation)

This improves sample efficiency and stability versus a basic DQN baseline.

## AI Mode vs Non-AI Mode (Scanner)

- Non-AI mode: deterministic scanning path with false-positive filtering.
- AI mode (`--ai-mode`): online replay updates and deeper AI-led behavior.
- Pentester mode (`--pentester`): chain-style deep pass, implying AI mode.

## Practical Interpretation

Treat output as model-driven security signals. Use manual analyst review before acting on findings in real environments.

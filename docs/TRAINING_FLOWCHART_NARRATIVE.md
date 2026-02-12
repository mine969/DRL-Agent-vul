# Training Flowchart Narrative (How It Really Runs)

I read the training code directly (`train_mock_targets.py`, `agent/improved_dqn_agent.py`, `env/web_sec_env.py`, and `start_services.py`).
This write-up is not a usage manual. It is the actual story of what happens in this project during training, written so you can turn it into a flowchart.

## The Main Training Story (from `train_mock_targets.py`)

1. **Training starts with one assumption:** the five mock web apps are already running on localhost ports `5002` to `5006`.
2. The trainer creates `MockTargetsTrainer`, then builds `ImprovedDQNAgent(state_dim=15, action_dim=50, PER=True, Noisy=True, n_step=1)`.
3. The trainer tries to resume from the newest checkpoint matching `checkpoints/improved_mock_ep*.pth`.
4. If no checkpoint is found, it tries loading base weights from `dqn_web_sec_model.pth`.
5. If that also fails, it starts with random weights and sets start episode to `1`.
6. Training enters the outer episode loop: `for episode in range(start_episode, total_episodes + 1)`.
7. On each episode, target rotates using `TARGETS[episode % 5]` (Banking, Blog, E-Commerce, File Share, Social in this file's list order).
8. A fresh environment is created per episode: `WebSecurityGym(target_url=..., mode="mock_targets")`.
9. Environment reset clears session state, clears discovered vulnerabilities, resets phase tracking, and calls target `POST /api/reset`.
10. Episode state variables begin: `total_reward=0`, `vulns=0`, `steps=0`, `done=False`.
11. Inner loop runs while `not done` and `steps < 50`.
12. Agent chooses action with `agent.act(state)` using argmax Q-values from the noisy dueling network.
13. Environment step executes with `env.step(action)` and returns `(next_state, reward, terminated, truncated, info)`.
14. Trainer computes `done = terminated or truncated`, stores transition with `agent.remember(...)`, then learns immediately with `agent.replay()`.
15. Episode stats update: add reward; if `reward >= 1.0`, increment vulnerability counter.
16. State moves forward (`state = next_state`) and step counter increments.
17. Every 10 episodes, trainer prints progress log (episode, target, reward, vuln hits).
18. Every 50 episodes, trainer saves checkpoint to `checkpoints/improved_mock_ep{episode}.pth`.
19. If user interrupts (`Ctrl+C`), it saves checkpoint for current episode before exiting.

## What Actually Happens Inside `env.step()`

1. Each step starts with a base penalty `-0.01` (pushes agent to be efficient).
2. In mock mode, 50-action ID is remapped to selected IDs in the full 150-action book.
3. Phase shaping runs first: reward bonus for phase-consistent action, penalty when skipping locked phase.
4. Chosen action function is executed (navigation, IDOR probes, SQLi/XSS tests, CSRF, traversal, etc.).
5. Anti-farming logic applies diminishing returns for repeating the same action too often.
6. Coverage bonus is added if action reaches a new page.
7. Response is analyzed for vulnerability signals and flags.
8. Reward from action is added to step reward.
9. Step ends with new 15-feature observation vector and `info` metadata.

## Reward Logic That Matters for the Flowchart

1. **Immediate confirmed path:** if response header contains `X-Vuln-Confirmed`, reward is granted quickly (base vulnerability reward, plus extra for XSS/CSRF and CTF flag cases).
2. **Dense shaping path:** small rewards for useful progress (forms, params) and penalties for noisy failures.
3. **WAF/Rate-limit path:** explicit penalties when firewall/rate limiting is detected.
4. **Indicator matching path:** response content is checked against vulnerability-specific indicator sets.
5. **Duplicate-hit suppression:** first discovery gets high reward; repeated same vuln-page combo gets tiny reward.
6. **Near-hit shaping:** for XSS/CSRF-like signs, a smaller bonus can still be added.

## What Actually Happens Inside `agent.replay()`

1. Replay starts only when memory size reaches batch size (`64` by default).
2. Batch is sampled from Prioritized Replay (high-TD-error transitions sampled more often).
3. Current Q-values come from online network; next action is selected by online network.
4. Next action value is evaluated by target network (Double DQN split).
5. TD target is computed: `r + (1-done) * gamma * next_q`.
6. Weighted MSE loss is computed using PER importance-sampling weights.
7. Backprop runs with gradient clipping (`max_norm=1.0`), then optimizer step.
8. PER priorities are updated from new TD errors.
9. Target network gets soft update (`tau=0.01`) every learning step.

## Flowchart-Ready Decision Nodes

Use these as your diamond boxes:

- **Checkpoint exists?** -> load checkpoint / try base model / random init.
- **Episode finished?** -> keep stepping / close episode.
- **Reached max steps?** (`steps >= 50` in trainer) -> truncate episode.
- **Action valid for phase?** -> add bonus or phase-skip penalty.
- **Vulnerability confirmed?** -> mark found, add high reward.
- **Memory enough for replay?** -> train now / skip training this step.
- **Episode % 50 == 0?** -> save checkpoint.
- **KeyboardInterrupt?** -> emergency checkpoint then stop.

## Loops to Draw Explicitly

- **Outer loop:** episodes (`start_episode` to requested total).
- **Middle rotation:** target selection changes every episode.
- **Inner loop:** steps inside one episode.
- **Learning loop:** replay called every step (but active only when buffer is big enough).

## Optional Branch: `quick_train_5000.py`

If your lecturer asks for an alternative branch in the same flowchart, add this side path:

1. Script scans available checkpoints from both patterns (`improved_mock_ep*.pth` and `quick_train_ep*.pth`).
2. It attempts loading newest to oldest until one works.
3. Training runs up to episode `10000`.
4. Inner step cap is `75` (not `50`).
5. Replay is called every 4 steps instead of every step.
6. Checkpoint save interval is every `100` episodes.

## One-Line Flow Skeleton (for quick drawing)

Start -> Init Agent -> Load/Resume? -> Episode Loop -> Pick Target -> Reset Env -> Step Loop -> Act -> Env Step/Reward -> Remember -> Replay? -> Done? -> Log/Checkpoint -> Next Episode -> End

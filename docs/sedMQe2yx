# How Training Really Happens in This Project

I went through the code path that actually runs training (`train_mock_targets.py`, `quick_train_5000.py`, `agent/improved_dqn_agent.py`, and `env/web_sec_env.py`).
This write-up is not a user guide. It is the real sequence of what the system does, written in plain human language so you can turn it into a flowchart.

## The full training flow (step by step)

1. The training script starts with one goal: run many episodes while rotating through five local vulnerable apps (e-commerce, social, banking, blog, file sharing).
2. It builds the DRL brain as an `ImprovedDQNAgent` with a 15-value state vector and a 50-action training space.
3. Inside that agent, two neural networks are created: an online Q-network (learns every update) and a target network (moves slowly for stability).
4. A prioritized replay buffer is created so important experiences are sampled more often than random ones.
5. Noisy network layers are enabled, so exploration comes from learned noise in weights instead of classic epsilon-greedy randomness.
6. Before training starts, the script tries to recover progress from checkpoints.
7. If a checkpoint can be loaded, training resumes from the next episode number.
8. If no checkpoint works, the process falls back to base weights or fresh random initialization.

9. The episode loop begins.
10. At the start of each episode, one target URL is selected using round-robin rotation so the agent keeps seeing different applications.
11. A `WebSecurityGym` environment is created in `mock_targets` mode.
12. `env.reset()` wipes the temporary state: cookies, auth token, step counters, discovered vulnerabilities, page history, phase progression, and reward trackers.
13. During reset, the environment also calls the target app reset endpoint (`POST /api/reset`) to put the web app back into a clean, repeatable condition.
14. Initial observation is returned as a 15-dimensional state vector.

15. Now the inner step loop runs until done or step cap.
16. Agent reads current state and picks one action index.
17. In mock mode, that action index (0-49) is translated to the matching full action id from the bigger action book.
18. The environment checks kill-chain phase logic (recon -> discovery -> exploit -> post-exploit).
19. If an action is from a locked phase, a penalty is applied.
20. If action order follows the current phase, small bonuses are applied and later phases unlock gradually.

21. The mapped action function executes (HTTP request, payload, probe, auth test, IDOR/XSS/SQLi/etc attempt).
22. Response is analyzed for multiple signals: status codes, headers, payload reflection, CTF markers, vulnerability indicators, and content variance.
23. Reward is calculated from several parts at once:
    - base time cost
    - vulnerability confirmation reward
    - extra reward when strong evidence appears (for example confirmed headers or flags)
    - penalties for WAF/rate limits/crash-like behavior
    - anti-farming reduction if the same low-value action is repeated too much
    - small coverage bonus for reaching new pages
24. Environment returns `(next_state, reward, terminated, truncated, info)`.
25. Trainer sets `done = terminated or truncated` and accumulates episode totals.

26. The transition `(state, action, reward, next_state, done)` is pushed into replay memory.
27. Learning update is attempted through `agent.replay()`.
28. If replay memory has fewer samples than batch size, update is skipped.
29. Once memory is large enough, one gradient update runs:
    - sample prioritized batch + importance weights
    - compute current Q-values
    - use Double DQN target calculation (online network chooses next action, target network evaluates it)
    - compute TD error and weighted loss
    - backpropagate, clip gradients, optimizer step
    - write TD-error priorities back to replay buffer
    - soft-update target network using tau
30. State pointer moves to `next_state`, then the loop repeats.

31. Episode closes when done or max steps reached.
32. Periodic logging prints reward and vulnerability count.
33. On checkpoint interval, model state is saved (`q_network`, `target_network`, optimizer, training step count, config fields).
34. Next episode begins unless max episode count is reached.

35. If user interrupts training (`Ctrl+C`), the script writes an emergency checkpoint before exiting.
36. Final output of training is one or more `.pth` files that can be resumed or used for scanning.

## Flowchart decisions to draw as diamond nodes

- Checkpoint available and loadable?
- Episode limit reached?
- Step loop done?
- Action phase valid/unlocked?
- Vulnerability confirmed in response?
- Replay memory >= batch size?
- Checkpoint save interval reached?
- Interrupted by user?

## Practical note on script variants

This repo has two active training loops with the same core logic:

- `train_mock_targets.py`: standard loop, saves every 50 episodes, shorter per-episode cap.
- `quick_train_5000.py`: long-run loop (up to 10,000), tries multiple checkpoint naming patterns, saves every 100 episodes, and trains every few steps for throughput.

For a lecturer flowchart, the structure above is still the right backbone; only frequency values (step cap, save interval, total episodes) change between scripts.

# Detailed Training Process From Scratch

This is the full process for a clean training run in this project, written to be converted into a flowchart.

## 1) Preparation Phase

1. Install dependencies from `requirements.txt`.
2. Start all 5 local vulnerable apps using `start_services.py`.
3. Keep service terminal open because training sends live HTTP requests to ports `5002` to `5006`.
4. Start training in fresh mode (no checkpoint resume path).

## 2) Agent Initialization Phase

1. Create `ImprovedDQNAgent` with:
   - `state_dim=15`
   - `action_dim=50` (mock target action space)
   - prioritized replay enabled
   - noisy networks enabled
   - `n_step=1`
2. Build online Q-network and target network.
3. Copy online weights to target network.
4. Initialize replay buffer and optimizer.
5. Set starting episode to `1` for scratch training.

## 3) Episode Orchestration Phase

1. Enter episode loop (`episode = 1` to configured max).
2. Pick target URL by round-robin rotation across the 5 mock apps.
3. Create environment: `WebSecurityGym(target_url, mode="mock_targets")`.
4. Call `env.reset()`.
5. Reset result includes:
   - clean session/cookies/auth state
   - reset vulnerability tracking
   - reset kill-chain phase tracking
   - call target `POST /api/reset` to restore app state
6. Initialize episode counters: reward sum, vuln hits, step count, done flag.

## 4) Step Execution Phase (Inner Loop)

Repeat while episode is not done and max step limit not reached.

1. Agent chooses action from current state using argmax Q-value.
2. Environment maps 50-action ID to selected full action ID.
3. Environment applies phase check (bonus or penalty).
4. Environment executes action function (navigation or attack attempt).
5. Environment computes step reward:
   - base time penalty
   - vulnerability confirmation reward when indicators/headers match
   - WAF/rate-limit penalties
   - anti-farming reduction for repeated same actions
   - optional exploration coverage bonus
6. Environment returns `next_state`, `reward`, `terminated`, `truncated`, `info`.
7. Trainer sets `done = terminated or truncated`.
8. Trainer stores transition in replay memory.
9. Trainer calls learning step (`replay`).
10. Update episode totals and move to `next_state`.

## 5) Learning Update Phase (`replay`)

1. Check replay memory size.
2. If memory is below batch size, skip gradient update.
3. If memory is ready:
   - sample prioritized batch
   - compute current Q-values from online network
   - compute next action with online network
   - evaluate next action with target network (Double DQN)
   - compute TD target and weighted loss
   - backpropagate and update online network
   - update replay priorities using TD error
   - soft-update target network (`tau=0.01`)

## 6) Episode Closeout Phase

1. Exit inner loop when done or step cap reached.
2. Count vulnerability hit when step reward crosses confirmation threshold.
3. Log progress every 10 episodes.
4. Save checkpoint at configured interval (commonly every 50 or 100 episodes depending on script).

## 7) Training End Phase

1. Continue until max episodes reached.
2. On `Ctrl+C`, save emergency checkpoint before exit.
3. Final output is trained checkpoint files in `checkpoints/`.

## Flowchart Blocks You Should Draw

- Start training
- Services running?
- Fresh run mode?
- Initialize agent
- Episode loop
- Target select
- Environment reset
- Step loop
- Action execute
- Reward + next state
- Replay memory ready?
- Gradient update
- Episode done?
- Save checkpoint?
- More episodes?
- End training

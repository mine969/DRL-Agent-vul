# Training Flowchart Notes (Simple)

This is the short version of how training runs, just enough to draw a flowchart.

## Main Flow

Start
-> Start mock target services (ports 5002-5006)
-> Initialize trainer + ImprovedDQNAgent (50 actions)
-> Check latest checkpoint
-> [Checkpoint found?]
   - Yes: load and continue from next episode
   - No: try base model / start fresh
-> Episode loop begins

Inside each episode:

-> Select target URL (rotating across 5 apps)
-> Create env in `mock_targets` mode
-> Reset env (including target `/api/reset`)
-> Step loop begins (`while not done and steps < 50`)
-> Agent picks action
-> Env executes action and returns reward + next state
-> Store transition in replay memory
-> [Memory >= batch size?]
   - Yes: run replay/training step
   - No: skip learning this step
-> Update total reward and step count
-> [Episode done?]
   - No: continue step loop
   - Yes: end episode

After each episode:

-> [Episode % 10 == 0?] log progress
-> [Episode % 50 == 0?] save checkpoint
-> [More episodes left?]
   - Yes: next episode
   - No: finish

Stop

## Good Diamond Nodes for Your Flowchart

- Checkpoint found?
- Memory enough to train?
- Episode done?
- Save checkpoint now?
- More episodes left?

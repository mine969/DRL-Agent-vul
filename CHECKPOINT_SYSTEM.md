# 📁 Checkpoint System Explanation

## How Checkpoints Work

### ✅ Static Files (Never Overwritten!)

Every 20 episodes, a **separate, permanent checkpoint file** is saved:

```
checkpoints/
├── dqn_checkpoint_ep20.pth   ✅ Saved (already exists)
├── dqn_checkpoint_ep40.pth   ⏳ Will be saved
├── dqn_checkpoint_ep60.pth   ⏳ Will be saved
├── dqn_checkpoint_ep80.pth   ⏳ Will be saved
├── dqn_checkpoint_ep100.pth  ⏳ Will be saved
├── dqn_checkpoint_ep120.pth  ⏳ Will be saved
├── ...
├── dqn_checkpoint_ep480.pth  ⏳ Will be saved
└── dqn_checkpoint_ep500.pth  ⏳ Will be saved (final)
```

**Each file is unique and permanent!** They are **never overwritten**.

### 📊 What You Get

After 500 episodes, you'll have:

- **25 checkpoint files** (one every 20 episodes)
- **1 final model** (`dqn_web_sec_model.pth`)

Total: **26 model files** you can choose from!

### 🔄 Rolling Back

You can use **any** checkpoint at any time:

```bash
# Use episode 100 checkpoint
python scan.py
# When asked: checkpoints/dqn_checkpoint_ep100.pth

# Use episode 200 checkpoint
python scan.py
# When asked: checkpoints/dqn_checkpoint_ep200.pth

# Use episode 500 (best quality)
python scan.py
# When asked: dqn_web_sec_model.pth
```

### 🎯 Resume Training

The `find_latest_checkpoint()` function automatically finds the **highest episode number** and resumes from there:

```python
# If you have: ep20, ep40, ep60
# It will resume from: ep60

# If you have: ep20, ep40, ep60, ep80, ep100
# It will resume from: ep100
```

### 💾 File Sizes

Each checkpoint is approximately:

- **~1.6 MB** per file
- **25 checkpoints** = ~40 MB total
- **Very manageable!**

### 🗑️ Cleanup (Optional)

If you want to save space, you can delete older checkpoints:

```bash
# Keep only every 100 episodes
del checkpoints\dqn_checkpoint_ep20.pth
del checkpoints\dqn_checkpoint_ep40.pth
del checkpoints\dqn_checkpoint_ep60.pth
del checkpoints\dqn_checkpoint_ep80.pth
# Keep ep100, ep200, ep300, ep400, ep500
```

But with only ~40 MB total, you can easily **keep them all**!

### 📈 Recommended Checkpoints to Keep

| Checkpoint | Quality   | Use Case         |
| ---------- | --------- | ---------------- |
| ep20       | Basic     | Quick testing    |
| ep100      | Good      | General scanning |
| ep200      | Very Good | Production use   |
| ep300      | Excellent | High accuracy    |
| ep500      | Best      | Maximum quality  |

### 🎮 Example Usage

**Scenario 1: Compare Performance**

```bash
# Test with ep100
python scan.py  # Use checkpoints/dqn_checkpoint_ep100.pth

# Test with ep300
python scan.py  # Use checkpoints/dqn_checkpoint_ep300.pth

# Compare results!
```

**Scenario 2: Rollback if Needed**

```bash
# If ep500 performs worse than ep400 (rare but possible)
# Just use ep400 instead!
python scan.py  # Use checkpoints/dqn_checkpoint_ep400.pth
```

**Scenario 3: Resume Training**

```bash
# Training stopped at ep240?
# Just run train.py again
python train.py
# It will automatically resume from ep240!
```

## Summary

✅ **All checkpoints are static** - never overwritten
✅ **You can roll back** to any episode
✅ **Automatic resume** from latest checkpoint
✅ **25+ model versions** to choose from
✅ **Small file sizes** (~1.6 MB each)

You have complete control over which model version to use! 🎉

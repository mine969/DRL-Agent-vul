# 🧹 Project Cleanup Guide

## Files You Can Safely Delete

### ❌ Unnecessary Files

1. **`CyberBattleSim/`** (folder)

   - This was attempted to install but not used
   - **Size**: Large (121 files)
   - **Safe to delete**: YES

   ```bash
   rmdir /s CyberBattleSim
   ```

2. **`external_env_adapter.py`**

   - Template for external environments
   - Not needed if you're only scanning websites
   - **Safe to delete**: YES (unless you plan to use CyberBattleSim)

3. **`TRANSFER_LEARNING.md`**

   - Research notes about pre-trained models
   - Not essential for operation
   - **Safe to delete**: YES (informational only)

4. **`dqn_web_sec_model.pth`** (if training is still running)
   - Old model from previous training
   - Will be replaced when current training finishes
   - **Safe to delete**: YES (will be regenerated)

### ✅ Essential Files (KEEP THESE!)

**Core Scripts:**

- ✅ `scan.py` - **Main scanner** (easiest to use)
- ✅ `autonomous_scan.py` - Advanced scanner
- ✅ `train.py` - Training script
- ✅ `deploy_agent.py` - Quick testing tool

**Documentation:**

- ✅ `BEGINNER_GUIDE.md` - Complete beginner's guide
- ✅ `QUICK_START.md` - Quick start for scan.py
- ✅ `AUTONOMOUS_SCAN_GUIDE.md` - Advanced usage
- ✅ `DEPLOYMENT_GUIDE.md` - Deployment guide

**Code:**

- ✅ `agent/` - DQN agent code
- ✅ `env/` - Environment code
- ✅ `requirements.txt` - Dependencies

**Generated:**

- ✅ `checkpoints/` - Training checkpoints (IMPORTANT!)
- ✅ `.git/` - Version control

## Recommended Cleanup

### Option 1: Quick Cleanup (Remove Unused)

```bash
# Delete CyberBattleSim folder
rmdir /s CyberBattleSim

# Delete external adapter (if not using)
del external_env_adapter.py
```

### Option 2: Minimal Setup (Keep Only Essentials)

```bash
# Delete all optional files
rmdir /s CyberBattleSim
del external_env_adapter.py
del TRANSFER_LEARNING.md
del DEPLOYMENT_GUIDE.md
del AUTONOMOUS_SCAN_GUIDE.md
```

**Keep only:**

- `scan.py` (main tool)
- `BEGINNER_GUIDE.md` (instructions)
- `QUICK_START.md` (quick reference)
- Core folders (agent, env, checkpoints)

## File Size Summary

| Item                    | Size        | Needed?                            |
| ----------------------- | ----------- | ---------------------------------- |
| CyberBattleSim/         | ~50MB+      | ❌ No                              |
| external_env_adapter.py | 3KB         | ❌ No (unless using external envs) |
| TRANSFER_LEARNING.md    | 3KB         | ❌ No (just info)                  |
| dqn_web_sec_model.pth   | 81KB        | ⚠️ Will be replaced                |
| checkpoints/            | Growing     | ✅ YES - Keep!                     |
| All .md guides          | ~25KB total | ⚠️ Optional (but helpful)          |

## What to Keep Based on Use Case

### If You Only Want to Scan Websites:

**Keep:**

- `scan.py`
- `autonomous_scan.py`
- `agent/` and `env/` folders
- `checkpoints/` folder
- `BEGINNER_GUIDE.md`
- `QUICK_START.md`

**Delete:**

- `CyberBattleSim/`
- `external_env_adapter.py`
- `TRANSFER_LEARNING.md`
- `DEPLOYMENT_GUIDE.md`
- `AUTONOMOUS_SCAN_GUIDE.md`

### If You Want Everything (Development):

**Keep everything** except:

- `CyberBattleSim/` (unless you plan to use it)

## Safe Cleanup Command

```bash
# Navigate to project folder
cd d:\github\RL

# Remove CyberBattleSim (largest unnecessary folder)
rmdir /s /q CyberBattleSim

# Remove external adapter if not needed
del external_env_adapter.py

# Optional: Remove extra documentation
del TRANSFER_LEARNING.md
```

## ⚠️ DO NOT DELETE

- ❌ `checkpoints/` - Contains your training progress!
- ❌ `agent/` - Core AI code
- ❌ `env/` - Environment code
- ❌ `train.py` - Needed for training
- ❌ `scan.py` - Main scanning tool
- ❌ `requirements.txt` - Dependencies

## After Cleanup

Your minimal project structure:

```
d:/github/RL/
├── agent/              ✅ Keep
├── env/                ✅ Keep
├── checkpoints/        ✅ Keep
├── scan.py             ✅ Keep
├── train.py            ✅ Keep
├── BEGINNER_GUIDE.md   ✅ Keep
├── QUICK_START.md      ✅ Keep
└── requirements.txt    ✅ Keep
```

**Total size after cleanup**: ~5-10MB (vs current ~50MB+)

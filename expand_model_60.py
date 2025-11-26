"""
Expand DRL Model from 52 to 60 Actions
======================================

This script uses transfer learning to expand the existing model
from 52 actions to 60 actions, preserving all learned knowledge.

Usage:
    python expand_model_60.py
"""

import torch
import torch.nn as nn
from agent.dqn_agent import DQNAgent

def expand_model():
    """Expand model from 52 to 60 actions using transfer learning."""
    
    print("=" * 70)
    print("🧠 EXPANDING MODEL: 52 → 60 ACTIONS")
    print("=" * 70)
    
    # Load existing 52-action model
    print("\n1️⃣ Loading existing 52-action model...")
    old_agent = DQNAgent(state_dim=11, action_dim=52)
    
    try:
        device = torch.device("cuda" if torch.cuda.is_available() else "mps" if torch.backends.mps.is_available() else "cpu")
        old_agent.brain.load_state_dict(torch.load("dqn_web_sec_model.pth", map_location=device))
        print("   ✅ Loaded existing model")
    except:
        print("   ⚠️  No existing model found, will create fresh 60-action model")
        new_agent = DQNAgent(state_dim=11, action_dim=60)
        torch.save(new_agent.brain.state_dict(), "dqn_web_sec_model_60.pth")
        print("\n✅ Created fresh 60-action model: dqn_web_sec_model_60.pth")
        return
    
    # Create new 60-action model
    print("\n2️⃣ Creating new 60-action model...")
    new_agent = DQNAgent(state_dim=11, action_dim=60)
    
    # Transfer weights
    print("\n3️⃣ Transferring learned weights...")
    
    old_state = old_agent.brain.state_dict()
    new_state = new_agent.brain.state_dict()
    
    # Copy all shared layers
    for key in old_state.keys():
        if 'advantage_stream.2' in key:
            # Final advantage layer: needs expansion from 52 to 60
            if 'weight' in key:
                old_weights = old_state[key]  # Shape: [52, 512]
                new_weights = new_state[key]  # Shape: [60, 512]
                
                # Copy first 52 rows (existing actions)
                new_weights[:52, :] = old_weights
                # Remaining 8 rows already randomly initialized
                
                new_state[key] = new_weights
                print(f"   ✓ Expanded {key}: {old_weights.shape} → {new_weights.shape}")
                
            elif 'bias' in key:
                old_bias = old_state[key]  # Shape: [52]
                new_bias = new_state[key]  # Shape: [60]
                
                # Copy first 52 values
                new_bias[:52] = old_bias
                # Remaining 8 already randomly initialized
                
                new_state[key] = new_bias
                print(f"   ✓ Expanded {key}: {old_bias.shape} → {new_bias.shape}")
        else:
            # All other layers copy directly (same dimensions)
            new_state[key] = old_state[key]
            print(f"   ✓ Copied {key}")
    
    # Load transferred weights
    new_agent.brain.load_state_dict(new_state)
    
    # Save expanded model
    print("\n4️⃣ Saving expanded model...")
    torch.save(new_agent.brain.state_dict(), "dqn_web_sec_model_60.pth")
    
    print("\n" + "=" * 70)
    print("✅ MODEL EXPANSION COMPLETE")
    print("=" * 70)
    print("Old Model: 52 actions")
    print("New Model: 60 actions")
    print("Preserved: Actions 0-51 (all existing knowledge)")
    print("New: Actions 52-59 (initialized randomly)")
    print("\nSaved to: dqn_web_sec_model_60.pth")
    print("\nNext step: Run multi-target training to fine-tune")
    print("=" * 70)

if __name__ == "__main__":
    expand_model()

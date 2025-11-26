"""
Check Action Count in Checkpoints
==================================
This script inspects checkpoint files to determine how many actions they have.
"""

import torch
import os

def check_checkpoint_actions(checkpoint_path):
    """Check how many actions a checkpoint has."""
    try:
        state_dict = torch.load(checkpoint_path, map_location='cpu')
        
        # Check the advantage stream output layer
        if 'advantage_stream.2.weight' in state_dict:
            action_count = state_dict['advantage_stream.2.weight'].shape[0]
            return action_count
        elif 'advantage_stream.4.weight' in state_dict:
            action_count = state_dict['advantage_stream.4.weight'].shape[0]
            return action_count
        else:
            return None
    except Exception as e:
        return f"Error: {e}"

if __name__ == "__main__":
    checkpoint_dir = "checkpoints"
    
    print("="*70)
    print("🔍 CHECKPOINT ACTION COUNT ANALYSIS")
    print("="*70)
    
    if not os.path.exists(checkpoint_dir):
        print(f"❌ Checkpoint directory not found: {checkpoint_dir}")
        exit(1)
    
    checkpoints = [f for f in os.listdir(checkpoint_dir) if f.endswith('.pth')]
    checkpoints.sort()
    
    if not checkpoints:
        print("❌ No checkpoints found")
        exit(1)
    
    print(f"\nFound {len(checkpoints)} checkpoint(s):\n")
    
    for checkpoint_file in checkpoints:
        checkpoint_path = os.path.join(checkpoint_dir, checkpoint_file)
        action_count = check_checkpoint_actions(checkpoint_path)
        
        if isinstance(action_count, int):
            icon = "✅" if action_count == 60 else "⚠️"
            print(f"{icon} {checkpoint_file:30s} → {action_count} actions")
        else:
            print(f"❌ {checkpoint_file:30s} → {action_count}")
    
    print("\n" + "="*70)
    print("💡 Use checkpoints with 60 actions for Ultra brain transfer")
    print("="*70)

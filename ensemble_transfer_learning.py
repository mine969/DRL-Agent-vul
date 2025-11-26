"""
Transfer Learning: Smart Weight Transfer from Old Checkpoints
==============================================================
Transfers compatible weights from old checkpoints (52 actions) to new architecture (100 actions).
"""

import torch
import torch.nn as nn
from agent.dqn_agent import DQNAgent
import os

def smart_transfer_learning(old_checkpoints, output_path):
    """
    Smart transfer learning that handles dimension mismatches.
    Creates a new 100-action checkpoint and transfers compatible weights.
    """
    print("=" * 70)
    print("SMART TRANSFER LEARNING: 52 Actions → 100 Actions")
    print("=" * 70)
    
    # Create new agent with 100 actions
    print("\n🔧 Creating new agent (state_dim=11, action_dim=100, neurons=8192)...")
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    new_agent = DQNAgent(state_dim=11, action_dim=100)
    new_state_dict = new_agent.brain.state_dict()
    
    print(f"   ✓ New architecture created")
    print(f"   ✓ Device: {device}")
    
    # Load old checkpoints and transfer compatible weights
    transferred_layers = []
    
    for i, checkpoint_path in enumerate(old_checkpoints):
        if not os.path.exists(checkpoint_path):
            print(f"\n⚠️  Checkpoint not found: {checkpoint_path}")
            continue
        
        print(f"\n📦 Loading checkpoint {i+1}: {checkpoint_path}")
        old_state_dict = torch.load(checkpoint_path, map_location='cpu')
        
        # Transfer compatible layers
        for key in old_state_dict.keys():
            old_shape = old_state_dict[key].shape
            new_shape = new_state_dict[key].shape
            
            # Only transfer if shapes match OR if we can partially transfer
            if old_shape == new_shape:
                # Perfect match - transfer directly
                new_state_dict[key] = old_state_dict[key]
                if key not in transferred_layers:
                    transferred_layers.append(key)
                    print(f"   ✓ Transferred: {key} {old_shape}")
            
            elif len(old_shape) == len(new_shape):
                # Partial match - transfer what we can
                if 'fc1' in key or 'fc2' in key:
                    # Hidden layers - can transfer fully
                    if old_shape == new_shape:
                        new_state_dict[key] = old_state_dict[key]
                        if key not in transferred_layers:
                            transferred_layers.append(key)
                            print(f"   ✓ Transferred: {key} {old_shape}")
                
                elif 'fc3' in key:
                    # Output layer - partial transfer for first 52 actions
                    if 'weight' in key:
                        # Transfer weights for first 52 actions
                        new_state_dict[key][:52, :] = old_state_dict[key]
                        if key not in transferred_layers:
                            transferred_layers.append(key)
                            print(f"   ✓ Partial transfer: {key} (52/{new_shape[0]} actions)")
                    elif 'bias' in key:
                        # Transfer bias for first 52 actions
                        new_state_dict[key][:52] = old_state_dict[key]
                        if key not in transferred_layers:
                            transferred_layers.append(key)
                            print(f"   ✓ Partial transfer: {key} (52/{new_shape[0]} actions)")
    
    # Load the new state dict into the agent
    new_agent.brain.load_state_dict(new_state_dict)
    
    # Save the new checkpoint
    print(f"\n💾 Saving new checkpoint to: {output_path}")
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    torch.save(new_state_dict, output_path)
    
    # Verify
    file_size = os.path.getsize(output_path) / (1024 * 1024)  # MB
    print(f"   ✓ File size: {file_size:.2f} MB")
    print(f"   ✓ Total parameters: {sum(p.numel() for p in new_state_dict.values()):,}")
    print(f"   ✓ Transferred layers: {len(set(transferred_layers))}")
    
    print("\n" + "=" * 70)
    print("✅ SMART TRANSFER LEARNING COMPLETE!")
    print("=" * 70)
    print(f"\nTransferred knowledge from old checkpoints to new 100-action agent.")
    print(f"The agent will start with learned patterns for the first 52 actions,")
    print(f"and will learn the new 48 actions (OSINT + Real-World) from scratch.")
    print("\nStart training with:")
    print(f"   python train_multi_target.py --episodes 1000")
    print("=" * 70)
    
    return True

def main():
    # Old checkpoint paths
    old_checkpoints = [
        "checkpoints/dqn_checkpoint_ep1000.pth",
        "multi_target_ep327.pth"
    ]
    
    # Output path
    output = "checkpoints/multi_target_8k_ep0.pth"
    
    # Smart transfer
    smart_transfer_learning(old_checkpoints, output)

if __name__ == "__main__":
    main()

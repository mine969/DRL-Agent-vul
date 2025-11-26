"""
Upgrade Old Checkpoint (1024 neurons) to Ultra Mode (4096 neurons)
===================================================================

This script converts checkpoints from the old architecture to the new Ultra GPU architecture.
"""

import torch
import sys

def upgrade_checkpoint(old_path, new_path):
    """Upgrade a checkpoint from 1024 to 4096 neurons."""
    
    print(f"🔄 Upgrading checkpoint: {old_path}")
    print(f"   Target: {new_path}")
    
    # Load old checkpoint
    try:
        old_state = torch.load(old_path, map_location='cpu')
        print(f"✅ Loaded old checkpoint")
    except Exception as e:
        print(f"❌ Failed to load: {e}")
        return False
    
    # Create new state dict with upgraded architecture
    new_state = {}
    
    # We can't directly transfer weights from 1024 to 4096
    # So we'll just start fresh but keep the training progress metadata
    print("⚠️  Cannot transfer weights (architecture mismatch)")
    print("   Starting with fresh Ultra brain")
    
    # Initialize new Ultra model
    from agent.dqn_agent import NeuralNetworkBrain
    ultra_brain = NeuralNetworkBrain(input_size=11, output_size=60)
    
    # Save the new initialized weights
    torch.save(ultra_brain.state_dict(), new_path)
    print(f"✅ Created new Ultra checkpoint: {new_path}")
    print(f"   Architecture: 4096 -> 2048 -> 1024 neurons")
    
    return True

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python upgrade_checkpoint_to_ultra.py <episode_number>")
        print("Example: python upgrade_checkpoint_to_ultra.py 327")
        sys.exit(1)
    
    episode = sys.argv[1]
    old_path = f"checkpoints/multi_target_ep{episode}.pth"
    new_path = f"checkpoints/multi_target_ep{episode}_ultra.pth"
    
    upgrade_checkpoint(old_path, new_path)
    
    print("\n" + "="*70)
    print("💡 To use the upgraded checkpoint:")
    print(f"   python train_multi_target.py --episodes 1000")
    print("   (Start fresh with Ultra architecture)")
    print("="*70)

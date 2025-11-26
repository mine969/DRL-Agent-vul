"""
Check Multi-Target Training Checkpoint
=======================================
This script analyzes a checkpoint to see what the agent learned.
"""

import torch
import os
import sys
import io

# Force UTF-8 encoding for Windows consoles
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')


def check_checkpoint(episode_num):
    checkpoint_path = f"checkpoints/multi_target_ep{episode_num}.pth"
    
    if not os.path.exists(checkpoint_path):
        print(f"❌ Checkpoint not found: {checkpoint_path}")
        print(f"\n📁 Available checkpoints:")
        
        if os.path.exists("checkpoints"):
            checkpoints = [f for f in os.listdir("checkpoints") if f.startswith("multi_target_ep")]
            if checkpoints:
                for cp in sorted(checkpoints):
                    size = os.path.getsize(f"checkpoints/{cp}") / 1024 / 1024
                    print(f"   ✓ {cp} ({size:.2f} MB)")
            else:
                print("   No checkpoints found yet")
        else:
            print("   Checkpoints directory doesn't exist")
        
        print(f"\n💡 Training is still in progress!")
        print(f"   The checkpoint will be saved when episode {episode_num} completes.")
        return
    
    print(f"📊 Analyzing checkpoint: {checkpoint_path}")
    print("=" * 70)
    
    # Load checkpoint
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    state_dict = torch.load(checkpoint_path, map_location=device)
    
    print(f"\n✅ Checkpoint loaded successfully!")
    print(f"   Device: {device}")
    print(f"   File size: {os.path.getsize(checkpoint_path) / 1024 / 1024:.2f} MB")
    
    # Analyze network structure
    print(f"\n🧠 Neural Network Structure:")
    print("-" * 70)
    
    layer_count = 0
    total_params = 0
    
    for key, value in state_dict.items():
        layer_count += 1
        params = value.numel()
        total_params += params
        print(f"   {layer_count}. {key:40} Shape: {str(list(value.shape)):20} Params: {params:,}")
    
    print("-" * 70)
    print(f"   Total Layers: {layer_count}")
    print(f"   Total Parameters: {total_params:,}")
    
    # Check output layer (action space)
    if 'advantage_stream.2.bias' in state_dict:
        action_count = state_dict['advantage_stream.2.bias'].shape[0]
        print(f"\n🎯 Action Space: {action_count} actions")
        print(f"   The agent can perform {action_count} different attacks!")
    
    # Analyze weight statistics
    print(f"\n📈 Weight Statistics:")
    print("-" * 70)
    
    for key, value in state_dict.items():
        if 'weight' in key:
            weights = value.cpu().numpy()
            print(f"   {key:40}")
            print(f"      Mean: {weights.mean():8.4f}  Std: {weights.std():8.4f}")
            print(f"      Min:  {weights.min():8.4f}  Max: {weights.max():8.4f}")
    
    print("\n" + "=" * 70)
    print("✅ Analysis complete!")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        episode = int(sys.argv[1])
    else:
        episode = 400  # Default
    
    print(f"🔍 Checking checkpoint for episode {episode}...")
    print()
    check_checkpoint(episode)

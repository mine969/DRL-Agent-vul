"""
Merge Multi-Target and Juice Shop Models
=========================================

Combines knowledge from multi_target_8k_ep5000.pth and juiceshop_8k_ep614.pth
using weighted averaging.
"""

import torch
from agent.dqn_agent import DQNAgent

def merge_models(model1_path, model2_path, output_path, weight1=0.7, weight2=0.3):
    """
    Merge two models using weighted averaging.
    
    Args:
        model1_path: Path to first model (e.g., multi_target_8k_ep5000.pth)
        model2_path: Path to second model (e.g., juiceshop_8k_ep614.pth)
        output_path: Path to save merged model
        weight1: Weight for first model (default 0.7 = 70%)
        weight2: Weight for second model (default 0.3 = 30%)
    """
    print(f"🔀 Merging models...")
    print(f"  Model 1: {model1_path} (weight: {weight1})")
    print(f"  Model 2: {model2_path} (weight: {weight2})")
    
    # Load both models
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    state_dict1 = torch.load(model1_path, map_location=device)
    state_dict2 = torch.load(model2_path, map_location=device)
    
    # Merge weights
    merged_state_dict = {}
    for key in state_dict1.keys():
        if key in state_dict2:
            # Weighted average
            merged_state_dict[key] = weight1 * state_dict1[key] + weight2 * state_dict2[key]
        else:
            # Only in model1
            merged_state_dict[key] = state_dict1[key]
    
    # Add any keys only in model2
    for key in state_dict2.keys():
        if key not in merged_state_dict:
            merged_state_dict[key] = state_dict2[key]
    
    # Save merged model
    torch.save(merged_state_dict, output_path)
    print(f"✅ Merged model saved to: {output_path}")
    print(f"   This model combines:")
    print(f"   - 70% multi-target knowledge (5000 episodes)")
    print(f"   - 30% Juice Shop specialization (614 episodes)")
    
    return output_path


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Merge two DQN models')
    parser.add_argument('--model1', default='checkpoints/multi_target_8k_ep5000.pth',
                        help='First model (multi-target)')
    parser.add_argument('--model2', default='checkpoints/juiceshop_8k_ep614.pth',
                        help='Second model (Juice Shop)')
    parser.add_argument('--output', default='checkpoints/merged_5000_614.pth',
                        help='Output path for merged model')
    parser.add_argument('--weight1', type=float, default=0.7,
                        help='Weight for first model (0-1)')
    parser.add_argument('--weight2', type=float, default=0.3,
                        help='Weight for second model (0-1)')
    
    args = parser.parse_args()
    
    # Normalize weights
    total = args.weight1 + args.weight2
    w1 = args.weight1 / total
    w2 = args.weight2 / total
    
    merge_models(args.model1, args.model2, args.output, w1, w2)
    
    print("\n📊 Next steps:")
    print(f"1. Test merged model:")
    print(f"   python evaluate_multi_target.py --model {args.output} --episodes 10")
    print(f"\n2. Continue training from merged model:")
    print(f"   python train_multi_target.py --model {args.output} --episodes 7000")

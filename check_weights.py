import torch
import numpy as np

def check_weights(model_path):
    print(f"Analyzing weights for {model_path}...")
    try:
        device = torch.device("cpu")
        state_dict = torch.load(model_path, map_location=device)
        
        # Get the final layer weights (Advantage stream)
        # Shape should be [52, 512]
        weights = state_dict.get('advantage_stream.2.weight')
        biases = state_dict.get('advantage_stream.2.bias')
        
        if weights is None:
            print("Could not find advantage_stream.2.weight")
            return

        print(f"Weight shape: {weights.shape}")
        
        if weights.shape[0] != 52:
            print("Model does not have 52 actions.")
            return

        # Split into old (48) and new (4)
        old_weights = weights[:48, :].numpy()
        new_weights = weights[48:, :].numpy()
        
        print("\n--- Statistics ---")
        print(f"Old 48 Actions - Mean: {np.mean(old_weights):.6f}, Std: {np.std(old_weights):.6f}")
        print(f"New  4 Actions - Mean: {np.mean(new_weights):.6f}, Std: {np.std(new_weights):.6f}")
        
        # Check if new weights look "raw" (e.g. significantly different distribution)
        # Often initialized weights are smaller or have specific distribution (Xavier/Kaiming)
        # Trained weights usually drift.
        
        diff_mean = abs(np.mean(old_weights) - np.mean(new_weights))
        print(f"\nDifference in Mean: {diff_mean:.6f}")
        
        if diff_mean > 0.05: # Heuristic threshold
            print("\n⚠️  The new actions look significantly different from the old ones.")
            print("   This suggests they might NOT be fully fine-tuned yet.")
        else:
            print("\n✅ The new actions have similar statistics to the old ones.")
            print("   They might have been fine-tuned, or the initialization was very good.")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_weights("dqn_web_sec_model.pth")

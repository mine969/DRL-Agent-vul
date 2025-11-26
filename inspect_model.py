import torch
import os

def inspect_checkpoint(path):
    print(f"Inspecting {path}...")
    if not os.path.exists(path):
        print("File not found.")
        return

    try:
        device = torch.device("cpu")
        state_dict = torch.load(path, map_location=device)
        
        for key, value in state_dict.items():
            if "advantage_stream.2" in key:
                print(f"  {key}: {value.shape}")
            elif "action_stream" in key: # Check if there are other relevant layers
                 print(f"  {key}: {value.shape}")
                 
    except Exception as e:
        print(f"Error loading checkpoint: {e}")

if __name__ == "__main__":
    inspect_checkpoint("dqn_web_sec_model.pth")
    inspect_checkpoint("dqn_web_sec_model_52.pth")
    inspect_checkpoint("dqn_web_sec_model_backup_v1.pth")

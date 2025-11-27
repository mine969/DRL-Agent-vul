
import torch
import sys

checkpoint_path = "checkpoints/multi_target_8k_ep700.pth"
print(f"Attempting to load {checkpoint_path}...")

try:
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    checkpoint = torch.load(checkpoint_path, map_location=device)
    print("✅ Checkpoint loaded successfully!")
    print(f"Keys: {list(checkpoint.keys())[:5]}")
except Exception as e:
    print(f"❌ Failed to load checkpoint: {e}")
    sys.exit(1)


import torch
import torch.nn as nn
import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from agent.dqn_agent import NeuralNetworkBrain

def upgrade_model_architecture():
    """
    Performs 'Brain Surgery' on the AI model.
    Transfers knowledge from the old brain (45 actions) to the new brain (48 actions).
    """
    model_path = "dqn_web_sec_model.pth"
    backup_path = "dqn_web_sec_model_backup_v1.pth"
    
    if not os.path.exists(model_path):
        print(f"❌ Model file {model_path} not found. You can just start training from scratch.")
        return

    print(f"🏥 Starting Brain Surgery on {model_path}...")
    
    # 1. Load the old model state
    # We need to handle the loading carefully since the class definition has changed
    old_state_dict = torch.load(model_path, map_location=torch.device('cpu'))
    
    # Detect old output size from the weights
    # The advantage stream's last layer weight has shape [output_size, 256]
    old_output_size = old_state_dict['advantage_stream.2.weight'].shape[0]
    old_input_size = old_state_dict['feature_layer.0.weight'].shape[1]
    old_hidden_size = old_state_dict['feature_layer.0.weight'].shape[0]
    
    print(f"ℹ️  Old Brain: {old_input_size} inputs -> {old_hidden_size} hidden -> {old_output_size} actions")
    
    if old_output_size == 48 and old_input_size == 11 and old_hidden_size == 1024:
        print("✅ Model is already up to date! No surgery needed.")
        return

    # 2. Create the new brain
    new_output_size = 48
    print(f"ℹ️  New Brain: 11 inputs -> 1024 hidden -> {new_output_size} actions")
    
    # We assume input size is 11 (observation space)
    new_brain = NeuralNetworkBrain(input_size=11, output_size=new_output_size)
    new_state_dict = new_brain.state_dict()
    
    # 3. Transfer Weights
    print("🔄 Transferring knowledge...")
    
    for key in old_state_dict:
        if key in new_state_dict:
            # If shapes match, just copy (Feature layers, Value stream)
            if old_state_dict[key].shape == new_state_dict[key].shape:
                new_state_dict[key] = old_state_dict[key]
            
            # If shapes don't match (Input Layer or Output Layer), we need to graft
            else:
                print(f"   - Adapting layer: {key}")
                
                # CASE 1: INPUT LAYER (512 -> 1024 hidden)
                # Old: [512, 11] -> New: [1024, 11]
                if 'feature_layer.0.weight' in key:
                    # 1. Get old weights [512, 11]
                    old_w = old_state_dict['feature_layer.0.weight']
                    
                    # 2. Expand Output (512 -> 1024)
                    # We copy the 512 weights twice to fill the 1024 slots
                    new_state_dict[key][:512, :] = old_w
                    new_state_dict[key][512:, :] = old_w + torch.randn_like(old_w) * 0.01 # Add noise
                    
                elif 'feature_layer.0.bias' in key:
                    new_state_dict[key][:512] = old_state_dict['feature_layer.0.bias']
                    new_state_dict[key][512:] = old_state_dict['feature_layer.0.bias']
                
                # CASE 2: HIDDEN LAYERS (512 -> 1024)
                # We need to map the old 512x512 to new 1024x1024
                # This is a heuristic mapping
                elif 'feature_layer.3.weight' in key: # This is the new middle layer
                     # Initialize as Identity-like to pass information through
                     nn.init.eye_(new_state_dict[key])
                     
                elif 'feature_layer.6.weight' in key: # This is the bottleneck layer (1024 -> 512)
                    # Map old 2nd layer (512->512) here?
                    # Let's use old L2 weights [512, 512] and duplicate them input-wise
                    old_w = old_state_dict['feature_layer.2.weight'] # [512, 512]
                    new_state_dict[key][:, :512] = old_w * 0.5
                    new_state_dict[key][:, 512:] = old_w * 0.5
                    
                # CASE 3: OUTPUT STREAMS (256 -> 512)
                elif 'value_stream.0.weight' in key or 'advantage_stream.0.weight' in key:
                    # Old: [256, 512] -> New: [512, 512]
                    # We can just copy the old weights into the first half of rows?
                    # No, input is 512 (same), output is 512 (was 256)
                    old_k = key.replace('stream.0', 'stream.0') # Same name
                    if old_k in old_state_dict:
                         old_w = old_state_dict[old_k] # [256, 512]
                         new_state_dict[key][:256, :] = old_w
                         new_state_dict[key][256:, :] = old_w # Duplicate output neurons
                         
                elif 'value_stream.0.bias' in key or 'advantage_stream.0.bias' in key:
                     old_k = key
                     if old_k in old_state_dict:
                         new_state_dict[key][:256] = old_state_dict[old_k]
                         new_state_dict[key][256:] = old_state_dict[old_k]

                # CASE 4: FINAL OUTPUT (45 -> 48)
                elif 'weight' in key and 'advantage_stream.2' in key:
                    # Input is now 512 (was 256)
                    # Output is 48 (was 45 or 48)
                    # Shape: [48, 512] <- [48, 256]
                    old_w = old_state_dict[key] # [48, 256]
                    new_state_dict[key][:, :256] = old_w * 0.5
                    new_state_dict[key][:, 256:] = old_w * 0.5

    # 4. Save the new model
    # First backup the old one
    if os.path.exists(backup_path):
        os.remove(backup_path)
    os.rename(model_path, backup_path)
    print(f"📦 Backed up old model to {backup_path}")
    
    # Save new one
    torch.save(new_state_dict, model_path)
    print(f"✅ Successfully saved upgraded model to {model_path}")
    print("\n🚀 You can now run the agent without retraining from scratch!")
    print("   The agent retains previous knowledge and will explore the 3 new actions.")

if __name__ == "__main__":
    upgrade_model_architecture()

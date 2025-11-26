"""
Transfer Learning Script - Expand Model from 48 to 52 Actions
==============================================================

This script performs "brain surgery" on the existing model:
1. Loads the 48-action model
2. Expands the output layer to 52 actions
3. Fine-tunes on the new action space

This is MUCH faster than retraining from scratch!
"""

import torch
import torch.nn as nn
from agent.dqn_agent import DQNAgent
from env.web_sec_env import WebSecurityGym
import os

def expand_model_48_to_52(old_model_path: str = "dqn_web_sec_model.pth", 
                          new_model_path: str = "dqn_web_sec_model_52.pth"):
    """
    Expands a 48-action model to 52 actions using transfer learning.
    """
    print("🧠 Starting Transfer Learning (Brain Surgery)...")
    print("=" * 70)
    
    # 1. Load old model (48 actions)
    print("\n📂 Loading existing model to check dimensions...")
    
    if not os.path.exists(old_model_path):
        print(f"❌ Error: Model not found at {old_model_path}")
        print("   Please ensure you have a trained model first!")
        return False
    
    device = torch.device("cuda" if torch.cuda.is_available() else 
                         "mps" if torch.backends.mps.is_available() else "cpu")
    
    # Load state dict first to check dimensions
    state_dict = torch.load(old_model_path, map_location=device)
    
    # Check output layer size (advantage_stream.2.bias is a good indicator)
    # It should be 48 for old model, 52 for new model
    output_bias = state_dict.get('advantage_stream.2.bias')
    
    if output_bias is not None and output_bias.shape[0] == 52:
        print(f"✅ Model {old_model_path} is ALREADY expanded to 52 actions!")
        print("   Skipping brain surgery...")
        
        # If the target file doesn't exist, copy the source to target so fine-tuning works
        if not os.path.exists(new_model_path):
            print(f"   Copying to {new_model_path} for consistency...")
            torch.save(state_dict, new_model_path)
            
        return True
        
    print(f"ℹ️  Model has {output_bias.shape[0]} actions. Proceeding with expansion...")
    old_agent = DQNAgent(state_dim=11, action_dim=48)
    old_agent.brain.load_state_dict(state_dict)
    print(f"✅ Loaded 48-action model from {old_model_path}")
    
    # 2. Create new model (52 actions)
    print("\n🔧 Creating expanded 52-action model...")
    new_agent = DQNAgent(state_dim=11, action_dim=52)
    
    # 3. Transfer weights (Brain Surgery!)
    print("\n💉 Performing brain surgery (transferring weights)...")
    
    old_state_dict = old_agent.brain.state_dict()
    new_state_dict = new_agent.brain.state_dict()
    
    # Copy all layers
    for name, param in old_state_dict.items():
        if 'advantage_stream.2' in name:  # Final output layer of advantage stream
            # For the final advantage layer, copy the first 48 actions, leave 4 new ones random
            if 'weight' in name:
                # Copy weights for first 48 actions
                new_state_dict[name][:48, :] = param
                print(f"   ✓ Transferred 48/52 advantage weights (4 new neurons initialized randomly)")
            elif 'bias' in name:
                # Copy biases for first 48 actions
                new_state_dict[name][:48] = param
                print(f"   ✓ Transferred 48/52 advantage biases")
        else:
            # Copy all other layers completely
            new_state_dict[name] = param
            print(f"   ✓ Transferred: {name}")
    
    new_agent.brain.load_state_dict(new_state_dict)
    new_agent.target_brain.load_state_dict(new_state_dict)
    
    # 4. Save the expanded model
    print(f"\n💾 Saving expanded model to {new_model_path}...")
    torch.save(new_agent.brain.state_dict(), new_model_path)
    print("✅ Brain surgery complete!")
    
    print("\n" + "=" * 70)
    print("📊 Summary:")
    print(f"   Old model: 48 actions")
    print(f"   New model: 52 actions")
    print(f"   Transferred: 48 actions (100% of old knowledge)")
    print(f"   New actions: 4 (Cookie attacks - will learn during fine-tuning)")
    print("=" * 70)
    
    return True

def fine_tune_model(model_path: str = "dqn_web_sec_model_52.pth", 
                    episodes: int = 100):
    """
    Fine-tunes the expanded model on the new action space.
    This is much faster than full training!
    """
    print("\n🎯 Starting Fine-Tuning...")
    print("=" * 70)
    print(f"Training for {episodes} episodes (much faster than full training!)")
    print("=" * 70)
    
    # Start target app
    from env.target_app import app
    import threading
    import time
    
    server_thread = threading.Thread(target=lambda: app.run(port=5001, debug=False, use_reloader=False), daemon=True)
    server_thread.start()
    time.sleep(2)
    
    # Initialize environment and agent
    env = WebSecurityGym()
    agent = DQNAgent(state_dim=11, action_dim=52)
    
    # Load the expanded model
    device = torch.device("cuda" if torch.cuda.is_available() else 
                         "mps" if torch.backends.mps.is_available() else "cpu")
    agent.brain.load_state_dict(torch.load(model_path, map_location=device))
    agent.target_brain.load_state_dict(agent.brain.state_dict())
    
    # Reduce exploration (we already know most attacks)
    agent.epsilon = 0.3  # Lower than default (0.9)
    agent.epsilon_decay = 0.99
    
    print("\n🚀 Fine-tuning in progress...\n")
    
    for episode in range(episodes):
        state, _ = env.reset()
        episode_score = 0
        done = False
        
        while not done:
            action = agent.act(state)
            next_state, reward, terminated, truncated, _ = env.step(action)
            done = terminated or truncated
            
            agent.remember(state, action, reward, next_state, done)
            agent.replay()
            
            state = next_state
            episode_score += reward
        
        print(f"Episode: {episode+1}/{episodes}, Score: {episode_score:.1f}, Epsilon: {agent.epsilon:.3f}")
        
        # Save checkpoint every 20 episodes
        if (episode + 1) % 20 == 0:
            checkpoint_path = f"checkpoints/transfer_learning_ep{episode+1}.pth"
            os.makedirs("checkpoints", exist_ok=True)
            torch.save(agent.brain.state_dict(), checkpoint_path)
            print(f"💾 Checkpoint saved: {checkpoint_path}")
    
    # Save final model
    final_path = "dqn_web_sec_model.pth"
    torch.save(agent.brain.state_dict(), final_path)
    print(f"\n✅ Fine-tuning complete! Model saved to {final_path}")
    print("   Your scanner can now use this model with all 52 actions!")

if __name__ == "__main__":
    print("\n" + "=" * 70)
    print("🧠 TRANSFER LEARNING - Expand Model 48→52 Actions")
    print("=" * 70)
    
    # Step 1: Brain Surgery
    success = expand_model_48_to_52()
    
    if success:
        # Step 2: Fine-tune
        print("\n")
        response = input("Do you want to fine-tune now? (y/n): ")
        if response.lower() == 'y':
            fine_tune_model(episodes=100)
        else:
            print("\n💡 You can fine-tune later by running:")
            print("   python transfer_learning.py")
            print("\n   Or manually call: fine_tune_model()")

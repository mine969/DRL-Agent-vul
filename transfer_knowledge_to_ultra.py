"""
Knowledge Transfer: Old Brain (1024) → Ultra Brain (4096)
==========================================================

This script uses "Knowledge Distillation" to transfer learning from the old
checkpoint to the new Ultra architecture.

Method:
1. Load old 1024-neuron teacher brain
2. Create new 4096-neuron student brain
3. Generate synthetic training data
4. Teacher predicts Q-values for each state
5. Student learns to mimic teacher's predictions
6. Save the pre-trained Ultra brain
"""

import torch
import torch.nn as nn
import torch.optim as optim
import numpy as np
from agent.dqn_agent import NeuralNetworkBrain
import sys

class OldBrain(nn.Module):
    """The OLD 1024-neuron architecture."""
    def __init__(self, input_size: int, output_size: int):
        super(OldBrain, self).__init__()
        
        self.feature_layer = nn.Sequential(
            nn.Linear(input_size, 1024),
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(1024, 1024),
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(1024, 512),
            nn.ReLU()
        )
        
        self.value_stream = nn.Sequential(
            nn.Linear(512, 512),
            nn.ReLU(),
            nn.Linear(512, 1) 
        )
        
        self.advantage_stream = nn.Sequential(
            nn.Linear(512, 512),
            nn.ReLU(),
            nn.Linear(512, output_size) 
        )
        
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        features = self.feature_layer(x)
        values = self.value_stream(features)
        advantages = self.advantage_stream(features)
        q_values = values + (advantages - advantages.mean(dim=1, keepdim=True))
        return q_values


def transfer_knowledge(old_checkpoint_path, new_checkpoint_path, num_samples=10000):
    """Transfer knowledge from old brain to new Ultra brain."""
    
    print("="*70)
    print("🧠 KNOWLEDGE TRANSFER: 1024 → 4096 NEURONS")
    print("="*70)
    
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Device: {device}")
    
    # 1. Load OLD teacher brain
    print("\n📚 Loading old teacher brain (1024 neurons, 52 actions)...")
    teacher = OldBrain(input_size=11, output_size=52).to(device)
    try:
        teacher.load_state_dict(torch.load(old_checkpoint_path, map_location=device))
        teacher.eval()
        print("✅ Teacher loaded successfully")
    except Exception as e:
        print(f"❌ Failed to load teacher: {e}")
        return False
    
    # 2. Create NEW student brain
    print("\n🎓 Creating new Ultra student brain (4096 neurons, 60 actions)...")
    student = NeuralNetworkBrain(input_size=11, output_size=60).to(device)
    optimizer = optim.Adam(student.parameters(), lr=0.001)
    loss_fn = nn.MSELoss()
    print("✅ Student created")
    
    # 3. Generate synthetic training data
    print(f"\n🔬 Generating {num_samples} synthetic states...")
    # Create realistic state distributions based on observation space
    states = np.random.rand(num_samples, 11).astype(np.float32)
    # Normalize to realistic ranges
    states[:, 0] = np.random.randint(0, 6, num_samples)  # Page ID (0-5)
    states[:, 1] = np.random.choice([200, 404, 500], num_samples)  # Status codes
    states[:, 2:7] = np.random.randint(0, 2, (num_samples, 5))  # Binary flags
    states[:, 7] = np.random.rand(num_samples) * 5  # Response time (0-5s)
    states[:, 8] = np.random.rand(num_samples) * 5  # Content variance
    states[:, 9] = np.random.randint(0, 10, num_samples)  # Input count
    states[:, 10] = np.random.randint(0, 3, num_samples)  # Business context
    
    states_tensor = torch.FloatTensor(states).to(device)
    print("✅ Synthetic states generated")
    
    # 4. Knowledge Distillation
    print("\n🎯 Distilling knowledge (Student learns from Teacher)...")
    batch_size = 256
    epochs = 50
    
    for epoch in range(epochs):
        total_loss = 0
        num_batches = 0
        
        # Mini-batch training
        for i in range(0, num_samples, batch_size):
            batch = states_tensor[i:i+batch_size]
            
            # Teacher predictions (ground truth) - 52 actions
            with torch.no_grad():
                teacher_q_values = teacher(batch)
                # Pad from 52 to 60 actions (new OSINT actions get neutral values)
                padding = torch.zeros(teacher_q_values.shape[0], 8, device=device)
                teacher_q_values = torch.cat([teacher_q_values, padding], dim=1)
            
            # Student predictions - 60 actions
            student_q_values = student(batch)
            
            # Calculate loss (how different is student from teacher?)
            loss = loss_fn(student_q_values, teacher_q_values)
            
            # Update student
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()
            
            total_loss += loss.item()
            num_batches += 1
        
        avg_loss = total_loss / num_batches
        if (epoch + 1) % 10 == 0:
            print(f"   Epoch {epoch+1}/{epochs} | Loss: {avg_loss:.4f}")
    
    print("✅ Knowledge transfer complete!")
    
    # 5. Save the pre-trained Ultra brain
    print(f"\n💾 Saving pre-trained Ultra brain...")
    torch.save(student.state_dict(), new_checkpoint_path)
    print(f"✅ Saved: {new_checkpoint_path}")
    
    # 6. Verification
    print("\n🔍 Verification:")
    test_state = torch.FloatTensor([[0, 200, 1, 0, 0, 0, 0, 0.5, 0.3, 3, 1]]).to(device)
    with torch.no_grad():
        teacher_pred = teacher(test_state)
        student_pred = student(test_state)
        similarity = torch.nn.functional.cosine_similarity(teacher_pred, student_pred)
        print(f"   Teacher-Student Similarity: {similarity.item():.2%}")
    
    print("\n" + "="*70)
    print("✅ KNOWLEDGE TRANSFER SUCCESSFUL!")
    print("="*70)
    print("\nThe Ultra brain now has a head start with knowledge from episode 327!")
    print("\nNext steps:")
    print("1. The new model is saved as: dqn_web_sec_model_ultra.pth")
    print("2. Rename it to: dqn_web_sec_model.pth")
    print("3. Run: python train_multi_target.py --episodes 1000")
    print("="*70)
    
    return True


if __name__ == "__main__":
    old_checkpoint = "checkpoints/multi_target_ep327.pth"
    new_checkpoint = "dqn_web_sec_model_ultra.pth"
    
    print("\n🚀 Starting Knowledge Transfer Process...\n")
    success = transfer_knowledge(old_checkpoint, new_checkpoint, num_samples=10000)
    
    if success:
        print("\n✅ Transfer complete! Your Ultra brain is ready to train.")
    else:
        print("\n❌ Transfer failed. Starting fresh might be better.")

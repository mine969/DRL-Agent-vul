import sys
import os
os.chdir('d:\\github\\DRL Agents\\DQN web vul')

# Capture full traceback
import traceback
import io

try:
    # Import and run
    from train_mock_targets import MockTargetsTrainer, TARGETS
    
    print(f"TARGETS length: {len(TARGETS)}")
    print(f"First target: {TARGETS[0]}")
    
    trainer = MockTargetsTrainer()
    print("✅ Trainer created")
    
    # Try to train 1 episode
    trainer.train(total_episodes=1)
    
except Exception as e:
    # Get full traceback
    exc_buffer = io.StringIO()
    traceback.print_exc(file=exc_buffer)
    full_error = exc_buffer.getvalue()
    
    print("\n" + "="*70)
    print("FULL ERROR TRACEBACK:")
    print("="*70)
    print(full_error)
    print("="*70)

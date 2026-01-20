"""
Simple benchmark that measures pure agent + environment performance
without relying on complex attack implementations.
"""
import time
import numpy as np
import torch
from env.web_sec_env import WebSecurityGym
from agent.improved_dqn_agent import ImprovedDQNAgent

def benchmark():
    print("\n🚀 DRL Web Security Agent - Hardware Benchmark (Simplified)")
    print("=" * 60)
    print(f"Checking hardware acceleration...")
    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"Device: {device.upper()}")
    if device == "cuda":
        print(f"GPU: {torch.cuda.get_device_name(0)}")
    
    print("\nInitializing Environment & Agent (Mock Mode)...")
    
    try:
        # Initialize environment
        env = WebSecurityGym(
            target_url="http://localhost:5002", 
            mode="mock_targets", 
            verbose=False
        )
        
        state_dim = env.observation_space.shape[0]
        action_dim = env.action_space.n
        
        print(f"State Dimension: {state_dim}")
        print(f"Action Space: {action_dim} actions")
        
        # Initialize Agent
        agent = ImprovedDQNAgent(
            state_dim, 
            action_dim, 
            use_prioritized_replay=True,
            seed=42
        )
        
        # Fill buffer with random experiences
        print("\nWarming up memory buffer (random actions)...")
        state, _ = env.reset(seed=42)
        
        for i in range(agent.batch_size + 10):
            action = env.action_space.sample()
            # Create fake transition (don't actually execute)
            next_state = np.random.rand(state_dim).astype(np.float32)
            reward = np.random.rand() - 0.5
            done = (i % 20 == 0)
            
            agent.remember(state, action, reward, next_state, done)
            state = next_state if not done else np.random.rand(state_dim).astype(np.float32)
        
        # BENCHMARK: Pure Agent Performance
        TEST_ITERATIONS = 200
        print(f"\n⏱️  Running Benchmark ({TEST_ITERATIONS} iterations)...")
        print("   Measuring: Action Selection + Replay Training")
        print("   (No network calls - pure ML performance)")
        
        start_time = time.time()
        
        state = np.random.rand(state_dim).astype(np.float32)
        
        for i in range(TEST_ITERATIONS):
            # 1. Select Action (Forward pass through network)
            action = agent.act(state)
            
            # 2. Simulate environment step
            next_state = np.random.rand(state_dim).astype(np.float32)
            reward = np.random.rand() - 0.5
            done = (i % 25 == 0)
            
            # 3. Store experience
            agent.remember(state, action, reward, next_state, done)
            
            # 4. Train (Replay - backward pass)
            if i % 4 == 0:  # Train every 4 steps (realistic)
                agent.replay()
            
            state = next_state
            
            # Progress indicator
            if i % 20 == 0:
                print(".", end="", flush=True)
        
        end_time = time.time()
        
        # ANALYSIS
        duration = end_time - start_time
        iterations_per_sec = TEST_ITERATIONS / duration
        
        print("\n\n✅ Benchmark Complete!")
        print("=" * 60)
        print(f"⚡ Processing Speed: {iterations_per_sec:.2f} iterations/second")
        print(f"   Time per iteration: {(duration/TEST_ITERATIONS)*1000:.2f} ms")
        print("=" * 60)
        
        # ESTIMATION FOR REAL TRAINING
        # In real training, we do 1 step per iteration
        # Assume 75 steps per episode on average
        AVG_STEPS_PER_EP = 75
        TARGET_EPISODES = 5000
        
        # Account for network overhead (HTTP requests are slow)
        # Estimate 50% slowdown due to network I/O
        NETWORK_OVERHEAD_FACTOR = 0.5
        
        effective_sps = iterations_per_sec * NETWORK_OVERHEAD_FACTOR
        total_steps = TARGET_EPISODES * AVG_STEPS_PER_EP
        total_seconds = total_steps / effective_sps
        
        hours = int(total_seconds // 3600)
        minutes = int((total_seconds % 3600) // 60)
        
        print(f"\n📊 Estimated Training Time for {TARGET_EPISODES} Episodes:")
        print(f"   Conservative Estimate: ~{hours}h {minutes}m")
        print(f"   (Includes network I/O overhead)")
        print("=" * 60)
        
        # Performance classification
        if iterations_per_sec > 100:
            perf_class = "🚀 EXCELLENT (High-end GPU)"
        elif iterations_per_sec > 50:
            perf_class = "✅ GOOD (Mid-range GPU/Fast CPU)"
        elif iterations_per_sec > 20:
            perf_class = "⚠️  MODERATE (CPU-only)"
        else:
            perf_class = "🐌 SLOW (Consider reducing episodes)"
        
        print(f"\nPerformance Classification: {perf_class}")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ Benchmark Failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    benchmark()

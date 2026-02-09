
import requests
import sys
import os

# Add local path to import env
sys.path.append(os.getcwd())

from env.web_sec_env import WebSecurityGym
from gymnasium import spaces

def verify_banking_actions():
    print("🚀 Starting Verification for Banking App Smart Actions...")
    
    # Initialize Env for Banking
    banking_url = "http://localhost:5004"
    try:
        # Check if running
        requests.get(banking_url, timeout=2)
    except:
        print(f"❌ Banking App not running at {banking_url}. Please start services.")
        return

    env = WebSecurityGym(target_url=banking_url, mode="mock_targets", verbose=True)
    
    print(f"✅ Environment initialized for {banking_url}")
    print(f"✅ Action Space Size: {env.action_space.n} (Should be 50)")

    # Reset Env
    print("🔄 Resetting Environment...")
    env.reset()
    
    print(f"🔍 Debug Info:")
    print(f"  - Target URL: {env.target_url}")
    print(f"  - Inferred App Tag: {env._infer_app_tag()}")
    if hasattr(env, 'port_map'):
        print(f"  - Port Map: {env.port_map}")
    else:
        print(f"  - Port Map: Not found!")

    # Test CSRF Smart Action (Action 42 -> Mapped to 83 -> attack_smart_csrf -> attack_csrf_money_transfer)
    print("\n[Test 1] Testing Smart CSRF (Action 42)...")
    obs, reward, terminated, truncated, info = env.step(42)
    print(f"👉 Reward: {reward}")
    print(f"👉 Info: {info}")
    
    if reward > 0:
        print("✅ SUCCESS: Smart CSRF Action detected vulnerability in Banking App!")
    else:
        print("⚠️ FAILURE: Smart CSRF Action did not return check/reward. Check logs.")

    # Test XSS Smart Action (Action 33 -> Mapped to 66 -> attack_smart_xss_stored -> attack_xss_transfer)
    print("\n[Test 2] Testing Smart XSS (Action 33)...")
    obs, reward, terminated, truncated, info = env.step(33)
    print(f"👉 Reward: {reward}")
    print(f"👉 Info: {info}")
    
    if reward > 0:
        print("✅ SUCCESS: Smart XSS Action detected vulnerability in Banking App!")
    else:
        print("⚠️ FAILURE: Smart XSS Action did not return check/reward. Check logs.")

    env.close()

if __name__ == "__main__":
    verify_banking_actions()

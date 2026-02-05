import sys
import os
import time

# Add current directory to path
sys.path.append(os.getcwd())

from env.web_sec_env import WebSecurityGym


def verify_actions():
    target_url = "http://localhost:5002"  # E-Commerce
    print(f"🎯 Initializing Environment for {target_url}...", flush=True)

    env = WebSecurityGym(target_url=target_url, mode="mock_targets", verbose=True)
    env.reset()

    # We need to find the action ID for attack_xss_stored
    # Looking at web_sec_env.py, we can iterate to find it or just try the method directly if possible
    # But environment step takes an integer.
    # Let's try to map it.

    # In web_sec_env.py, the action_map is built in __init__.
    # Let's inspect it or just try the known ID range.
    # Based on previous file views, XSS actions are likely around 30-40.

    print("\n🧐 Searching for 'attack_xss_stored' action ID...", flush=True)

    # In mock_targets mode, we use mock_action_map to map to action_book
    xss_action_id = -1

    # We know from inspection that:
    # 33 -> 66 (attack_xss_stored_posts)
    # 34 -> 67 (attack_xss_stored_comments)

    target_actions = [33, 34]

    # Try both actions
    for action_id in target_actions:
        full_id = env.mock_action_map.get(action_id)
        method = env.action_book.get(full_id)

        print(
            f"\n🚀 Executing Action {action_id} -> {full_id} ({method.__name__})...",
            flush=True,
        )

        # Manually set the token to ensure we are 'logged in' for the environment check
        print("🔑 Manually setting auth token...", flush=True)
        env.auth_token = "test_token"

        obs, reward, terminated, truncated, info = env.step(action_id)

        print(f"  📊 Result for Action {action_id}:")
        print(f"    Reward: {reward}")
        # print(f"    Info: {info}")

        if reward >= 1.0:
            print(f"    ✅ SUCCESS: High reward received for {method.__name__}!")
        else:
            print(f"    ❌ FAILURE: Low reward received for {method.__name__}.")

    return


if __name__ == "__main__":
    verify_actions()

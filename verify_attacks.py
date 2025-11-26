import requests
from env.web_sec_env import WebSecurityGym

def verify_attacks():
    print("🚀 Starting Manual Verification of Attacks...")
    env = WebSecurityGym()
    
    # Test 1: SSRF Internal
    print("\n[1] Testing SSRF Internal...")
    r, reward = env.attack_ssrf_internal()
    if reward > 0:
        print(f"✅ SSRF Internal SUCCESS! Reward: {reward}")
    else:
        print(f"❌ SSRF Internal FAILED. Reward: {reward}")
        if r is not None: 
            print(f"   URL: {r.url}")
            print(f"   Status: {r.status_code}")
            print(f"   Text: {r.text}")

    # Test 2: Open Redirect
    print("\n[2] Testing Open Redirect...")
    r, reward = env.attack_open_redirect()
    if reward > 0:
        print(f"✅ Open Redirect SUCCESS! Reward: {reward}")
    else:
        print(f"❌ Open Redirect FAILED. Reward: {reward}")
        if r is not None: 
            print(f"   URL: {r.url}")
            print(f"   Status: {r.status_code}")
            print(f"   Text: {r.text[:200]}...") # Truncate if too long

    # Test 3: SQLi API Login
    print("\n[3] Testing SQLi API Login...")
    r, reward = env.attack_sqli_api_login()
    if reward > 0:
        print(f"✅ SQLi API Login SUCCESS! Reward: {reward}")
    else:
        print(f"❌ SQLi API Login FAILED. Reward: {reward}")
        if r is not None: 
            print(f"   URL: {r.url}")
            print(f"   Status: {r.status_code}")
            print(f"   Text: {r.text}")

    # Test 4: CSRF Transfer
    print("\n[4] Testing CSRF Transfer...")
    r, reward = env.attack_csrf_transfer()
    if reward > 0:
        print(f"✅ CSRF Transfer SUCCESS! Reward: {reward}")
    else:
        print(f"❌ CSRF Transfer FAILED. Reward: {reward}")
        if r is not None: 
            print(f"   URL: {r.url}")
            print(f"   Status: {r.status_code}")
            print(f"   Text: {r.text}")

if __name__ == "__main__":
    verify_attacks()

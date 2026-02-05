import requests
import time
import sys
import os

# Add parent dir to path to import PayloadManager
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from agent.payload_manager import PayloadManager


def test_xss_detection():
    url = "http://localhost:5002"
    pm = PayloadManager()
    pm.seed(42)

    # 1. Register & Login to get session
    session = requests.Session()
    session.post(
        f"{url}/register",
        data={
            "username": "testuser",
            "password": "password123",
            "email": "test@example.com",
        },
    )
    session.post(
        f"{url}/login", data={"username": "testuser", "password": "password123"}
    )

    # 2. Get XSS payloads
    payloads = pm.xss_payloads + pm.xss_polyglots + pm.xss_csp_bypass

    print(f"Testing {len(payloads)} XSS payloads...")

    success_count = 0
    fail_count = 0

    for payload in payloads:
        # Test Posts Endpoint
        try:
            r = session.post(
                f"{url}/api/posts",
                json={"title": "Test", "content": payload},
                timeout=2,
            )
            if "X-Vuln-Confirmed" in r.headers:
                print(f"✅ DETECTED: {payload[:50]}...")
                success_count += 1
            else:
                print(f"❌ MISSED:   {payload[:50]}...")
                fail_count += 1
        except Exception as e:
            print(f"⚠️ ERROR: {e}")
            fail_count += 1

    print("\n--- RESULTS ---")
    print(f"Total:   {len(payloads)}")
    print(f"Success: {success_count}")
    print(f"Failed:  {fail_count}")

    if fail_count == 0:
        print("\n🎉 ALL PAYLOADS DETECTED!")
    else:
        print(f"\n⚠️ {fail_count} payloads were not detected.")


if __name__ == "__main__":
    # Check if target app is running
    try:
        requests.get("http://localhost:5002", timeout=1)
    except:
        print("❌ Error: E-Commerce app is not running on http://localhost:5002")
        print("Please run: python env/target_app_ecommerce.py")
        sys.exit(1)

    test_xss_detection()

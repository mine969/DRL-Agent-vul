import requests
import sys

TARGETS = [
    {"name": "Banking App", "url": "http://127.0.0.1:5004"},
    {"name": "Blog Platform", "url": "http://127.0.0.1:5005"},
    {"name": "E-Commerce", "url": "http://127.0.0.1:5002"},
    {"name": "File Share", "url": "http://127.0.0.1:5006"},
    {"name": "Social Media", "url": "http://127.0.0.1:5003"}
]

print("🔍 Verifying service connectivity...")
all_good = True

for target in TARGETS:
    try:
        response = requests.get(target['url'], timeout=2)
        if response.status_code == 200:
            print(f"✅ {target['name']} is UP ({target['url']})")
        else:
            print(f"⚠️  {target['name']} returned status {response.status_code}")
            all_good = False
    except Exception as e:
        print(f"❌ {target['name']} is DOWN ({target['url']}) - {e}")
        all_good = False

if all_good:
    print("\n🎉 All services are reachable!")
    sys.exit(0)
else:
    print("\n💥 Some services are not reachable.")
    sys.exit(1)

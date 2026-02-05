import subprocess
import sys
import os

# Single target, low depth, just to prove it doesn't crash on emojis
url = "http://localhost:5002"
model = "checkpoints/improved_mock_ep4300.pth"

print(f"[TEST] Testing Quick Fix on {url}...")

# Force UTF-8
env = os.environ.copy()
env["PYTHONIOENCODING"] = "utf-8"

cmd = [
    sys.executable, "autonomous_scan.py", 
    url, 
    "--model", model, 
    "--depth", "5", 
    "--ai-mode" # Ensure emojis are printed
]

try:
    result = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", env=env, timeout=60)
    print(result.stdout)
    if result.returncode == 0:
        print("\n[PASS] QUICK TEST PASSED! No Unicode Errors.")
    else:
        print("\n[FAIL] FAILED with code", result.returncode)
        print(result.stderr)
        
except Exception as e:
    print(f"\n[ERR] SCRIPT ERROR: {e}")

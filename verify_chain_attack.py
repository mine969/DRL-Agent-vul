import subprocess
import sys
import os

# Test TARGET: Social Media (Complex target good for chains)
url = "http://localhost:5003"
model = "checkpoints/improved_mock_ep4300.pth"

print(f"[TEST] TESTING CHAIN ATTACK (PENTESTER MODE) ON {url}")
print(f"[INFO] Model: {model}")
print("-" * 60)

# Command with --pentester flag
# This triggers:
# 1. AI Mode (Recon)
# 2. High Intensity (50+ steps)
# 3. Online Learning
cmd = [
    sys.executable,
    "autonomous_scan.py",
    url,
    "--model",
    model,
    "--pentester",  # <--- THE KEY FLAG
    "--depth",
    "10",  # Keep Recon short to get to attacks faster
]

try:
    # Run with output streaming to see what happens
    env = os.environ.copy()
    env["PYTHONIOENCODING"] = "utf-8"
    subprocess.run(cmd, check=True, env=env)
except subprocess.CalledProcessError as e:
    print(f"❌ Scan failed with error code {e.returncode}")
except KeyboardInterrupt:
    print("\n[STOP] Test stopped by user")

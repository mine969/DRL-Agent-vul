import subprocess
import sys
import time
import os

targets = [
    "http://localhost:5002", # E-Commerce
    "http://localhost:5003", # Social
    "http://localhost:5004", # Banking
    "http://localhost:5005", # Blog
    "http://localhost:5006"  # FileShare
]

model = "checkpoints/improved_mock_ep4300.pth"

print(f"🔍 Starting Verification Scan on {len(targets)} targets using {model}...")

results = {}

for url in targets:
    print(f"\n👉 Scanning {url}...")
    start = time.time()
    try:
        # Run autonomous_scan.py with a timeout to prevent hanging
        # Using depth=20 to ensure we find pages, intensity=10 for enough tries
        cmd = [sys.executable, "autonomous_scan.py", url, "--model", model, "--depth", "20", "--intensity", "10", "--ai-mode"]
        
        # Capture output
        # FORCE UTF-8 ENCODING to prevent Windows cp1252 crashes on emojis
        env = sys.environment.copy() if hasattr(sys, 'environment') else os.environ.copy()
        env["PYTHONIOENCODING"] = "utf-8"
        
        process = subprocess.run(cmd, capture_output=True, text=True, timeout=300, encoding="utf-8", env=env)
        
        output = process.stdout
        if "SUCCESS!" in output: # Matches both "✨ SUCCESS!" and "[!] SUCCESS!"
            findings = output.count("🚨 CONFIRMED")
            results[url] = f"✅ PASSED ({findings} findings)"
        else:
             print(f"DEBUG OUTPUT FOR {url}:\n{output[-500:]}")
             print(f"DEBUG ERROR FOR {url}:\n{process.stderr[-500:]}")
             results[url] = "❌ FAILED (No findings)"
             
    except subprocess.TimeoutExpired:
        results[url] = "⚠️ TIMEOUT"
    except Exception as e:
        results[url] = f"⚠️ ERROR: {e}"

print("\n📊 SUMMARY:")
for url, res in results.items():
    print(f"  {url}: {res}")

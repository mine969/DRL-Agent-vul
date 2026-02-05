"""
Simple Service Starter for Training
===================================

Starts all mock web applications for DRL agent training.
This is a simplified version focused on reliability for training.

Usage:
    python start_services.py

Author: DRL Web Security Team
"""

import subprocess
import sys
import time
import os
import io

# Fix Windows console encoding for emojis
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

# Target applications for training
TARGETS = [
    {"name": "E-Commerce", "script": "env/target_app_ecommerce.py", "port": 5002},
    {"name": "Social Media", "script": "env/target_app_social.py", "port": 5003},
    {"name": "Banking App", "script": "env/target_app_banking.py", "port": 5004},
    {"name": "Blog Platform", "script": "env/target_app_blog.py", "port": 5005},
    {"name": "File Share", "script": "env/target_app_fileshare.py", "port": 5006},
]


def main():
    """Start all mock applications for training."""
    processes = []

    print("🚀 Starting 5 mock applications for DRL training...")
    print("=" * 60)

    # Create logs directory
    os.makedirs("logs", exist_ok=True)

    # Start each application
    for target in TARGETS:
        script_path = target["script"]

        # Check if script exists
        if not os.path.exists(script_path):
            print(f"⚠️  SKIP: {script_path} not found")
            continue

        print(f"📦 Starting {target['name']} on port {target['port']}...")

        try:
            # Create log file
            log_name = target["name"].replace(" ", "_").lower()
            log_file = open(f"logs/{log_name}.log", "w")

            # Determine correct Python executable
            # If running in venv, use venv python; otherwise use sys.executable
            if hasattr(sys, "real_prefix") or (
                hasattr(sys, "base_prefix") and sys.base_prefix != sys.prefix
            ):
                # Running in venv
                python_exe = sys.executable
            else:
                # Not in venv, try to find venv python
                venv_python = os.path.join(
                    os.getcwd(), ".venv", "Scripts", "python.exe"
                )
                if os.path.exists(venv_python):
                    python_exe = venv_python
                else:
                    python_exe = sys.executable

            # Start the Flask app
            process = subprocess.Popen(
                [python_exe, script_path],
                stdout=log_file,
                stderr=subprocess.STDOUT,
                cwd=os.getcwd(),
            )

            processes.append(
                {
                    "process": process,
                    "name": target["name"],
                    "port": target["port"],
                    "log_file": log_file,
                }
            )

            print(f"   ✅ Started (PID: {process.pid})")

            # Brief pause between starts
            time.sleep(0.5)

        except Exception as e:
            print(f"   ❌ Failed: {e}")

    if not processes:
        print("\n❌ No applications started! Check file paths.")
        return

    print(f"\n✅ {len(processes)} applications running!")
    print("\n🌐 Available for training:")
    for proc in processes:
        print(f"   • {proc['name']}: http://localhost:{proc['port']}")

    print("\n⚠️  Keep this window open for training")
    print("   Press Ctrl+C to stop all applications\n")

    try:
        # Keep running until interrupted
        while True:
            time.sleep(1)
            # Check if any process died
            for proc_info in processes[:]:
                if proc_info["process"].poll() is not None:
                    print(f"⚠️  {proc_info['name']} stopped unexpectedly")
                    processes.remove(proc_info)

            if not processes:
                print("❌ All applications stopped")
                break

    except KeyboardInterrupt:
        print("\n🛑 Shutting down applications...")

    # Clean shutdown
    for proc_info in processes:
        try:
            proc_info["process"].terminate()
            proc_info["process"].wait(timeout=3)
            proc_info["log_file"].close()
            print(f"   ✅ Stopped {proc_info['name']}")
        except:
            try:
                proc_info["process"].kill()
                proc_info["process"].wait()
            except:
                pass

    print("✅ All applications stopped. Safe to close window.")


if __name__ == "__main__":
    main()

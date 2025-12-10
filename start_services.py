import subprocess
import sys
import time
import os

TARGETS = [
    {"name": "Banking App", "script": "env/target_app_banking.py", "port": 5004},
    {"name": "Blog Platform", "script": "env/target_app_blog.py", "port": 5005},
    {"name": "E-Commerce", "script": "env/target_app_ecommerce.py", "port": 5002},
    {"name": "File Share", "script": "env/target_app_fileshare.py", "port": 5006},
    {"name": "Social Media", "script": "env/target_app_social.py", "port": 5003}
]

def start_services():
    processes = []
    print("🚀 Starting all mock web applications...")
    
    os.makedirs("logs", exist_ok=True)
    
    for target in TARGETS:
        print(f"   Starting {target['name']} on port {target['port']}...")
        log_file = open(f"logs/{target['name'].replace(' ', '_').lower()}.log", "w")
        p = subprocess.Popen(
            [sys.executable, target['script']],
            cwd=os.getcwd(),
            stdout=log_file,
            stderr=subprocess.STDOUT
        )
        processes.append(p)
        
    print("\n✅ All services started! They are running in the background.")
    print("⚠️  DO NOT CLOSE THIS WINDOW if you want them to keep running.")
    print("   Press Ctrl+C to stop all services.")
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n🛑 Stopping all services...")
        for p in processes:
            p.terminate()
        print("✅ Done.")

if __name__ == "__main__":
    start_services()

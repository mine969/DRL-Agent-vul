"""
Service Manager
===============

Manages starting and stopping all mock target applications.
Provides a clean interface for managing multiple services.

Usage:
    python start_services.py

Author: DRL Web Security Team
Date: 2025
"""

import subprocess
import sys
import time
import os
from typing import List, Dict, Optional
from pathlib import Path

try:
    from config import get_config, EnvironmentConfig
    _CONFIG_AVAILABLE = True
except ImportError:
    _CONFIG_AVAILABLE = False
    # Fallback configuration
    TARGETS = [
        {"name": "Banking App", "script": "env/target_app_banking.py", "port": 5004},
        {"name": "Blog Platform", "script": "env/target_app_blog.py", "port": 5005},
        {"name": "E-Commerce", "script": "env/target_app_ecommerce.py", "port": 5002},
        {"name": "File Share", "script": "env/target_app_fileshare.py", "port": 5006},
        {"name": "Social Media", "script": "env/target_app_social.py", "port": 5003}
    ]


def get_targets() -> List[Dict[str, any]]:
    """
    Get list of target applications to start.
    
    Returns:
        List of target dictionaries with name, script, and port
    """
    if _CONFIG_AVAILABLE:
        config = get_config()
        targets = []
        for key, target_info in config.environment.mock_targets.items():
            targets.append({
                "name": target_info["name"],
                "script": target_info["script"],
                "port": target_info["port"],
                "url": target_info["url"]
            })
        return targets
    else:
        return TARGETS


def start_services() -> List[subprocess.Popen]:
    """
    Start all mock web applications.
    
    Returns:
        List of subprocess.Popen objects for each service
        
    Raises:
        OSError: If unable to start a service
        FileNotFoundError: If a target script doesn't exist
    """
    targets = get_targets()
    processes: List[subprocess.Popen] = []
    
    print("🚀 Starting all mock web applications...")
    print(f"   Found {len(targets)} target applications\n")
    
    # Ensure logs directory exists
    logs_dir = Path("logs")
    logs_dir.mkdir(exist_ok=True)
    
    # Start each service
    for target in targets:
        script_path = Path(target["script"])
        
        # Validate script exists
        if not script_path.exists():
            print(f"⚠️  Warning: Script not found: {script_path}")
            continue
        
        print(f"   Starting {target['name']} on port {target['port']}...")
        
        try:
            # Open log file
            log_filename = target['name'].replace(' ', '_').lower().replace('-', '_')
            log_file = open(logs_dir / f"{log_filename}.log", "w", encoding="utf-8")
            
            # Start process
            process = subprocess.Popen(
                [sys.executable, str(script_path)],
                cwd=os.getcwd(),
                stdout=log_file,
                stderr=subprocess.STDOUT,
                text=True
            )
            
            processes.append({
                "process": process,
                "target": target,
                "log_file": log_file
            })
            
            # Give service time to start
            time.sleep(0.5)
            
        except Exception as e:
            print(f"   ❌ Failed to start {target['name']}: {e}")
            continue
    
    if processes:
        print(f"\n✅ Started {len(processes)} services successfully!")
        print("⚠️  DO NOT CLOSE THIS WINDOW if you want them to keep running.")
        print("   Press Ctrl+C to stop all services.\n")
        
        # Print service URLs
        print("Available Services:")
        for proc_info in processes:
            target = proc_info["target"]
            url = target.get('url', f"http://localhost:{target['port']}")
            print(f"   • {target['name']}: {url}")
    else:
        print("\n❌ No services started!")
    
    return processes


def stop_services(processes: List[Dict]) -> None:
    """
    Stop all running services gracefully.
    
    Args:
        processes: List of process dictionaries from start_services()
    """
    if not processes:
        return
    
    print("\n🛑 Stopping all services...")
    
    for proc_info in processes:
        process = proc_info["process"]
        target = proc_info["target"]
        log_file = proc_info.get("log_file")
        
        try:
            print(f"   Stopping {target['name']}...")
            process.terminate()
            
            # Wait for graceful shutdown
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                # Force kill if doesn't terminate gracefully
                process.kill()
                process.wait()
            
            # Close log file
            if log_file:
                log_file.close()
                
        except Exception as e:
            print(f"   ⚠️  Error stopping {target['name']}: {e}")
    
    print("✅ All services stopped.")


def main():
    """Main entry point for service manager."""
    processes = []
    
    try:
        processes = start_services()
        
        # Keep running until interrupted
        if processes:
            while True:
                time.sleep(1)
                # Check if any process has died
                for proc_info in processes[:]:
                    if proc_info["process"].poll() is not None:
                        target = proc_info["target"]
                        print(f"\n⚠️  Service died: {target['name']} (PID: {proc_info['process'].pid})")
                        processes.remove(proc_info)
                
                if not processes:
                    print("\n⚠️  All services have stopped.")
                    break
                    
    except KeyboardInterrupt:
        pass  # Handle in finally block
    finally:
        stop_services(processes)


if __name__ == "__main__":
    main()

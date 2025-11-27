# 🎭 MAC Address Spoofing Guide

## ⚠️ Important Note

MAC address changes require **administrator/root privileges** and are done at the **operating system level**, not in Python. The scanner cannot do this automatically.

## Windows

### Method 1: Registry Edit (Permanent)

```powershell
# Run PowerShell as Administrator

# 1. Find your network adapter name
Get-NetAdapter

# 2. Set new MAC address (replace "Ethernet" with your adapter name)
Set-NetAdapter -Name "Ethernet" -MacAddress "02-00-00-00-00-01"

# 3. Restart adapter
Restart-NetAdapter -Name "Ethernet"
```

### Method 2: Device Manager (GUI)

1. Open Device Manager
2. Network Adapters → Right-click your adapter → Properties
3. Advanced tab → Find "Network Address" or "Locally Administered Address"
4. Enter new MAC: `020000000001` (no dashes)
5. Restart adapter

### Method 3: Using Technitium MAC Address Changer (Free Tool)

- Download: https://technitium.com/tmac/
- GUI-based, very easy to use
- Can randomize MAC automatically

## Linux

### Temporary Change (Until Reboot)

```bash
# 1. Bring interface down
sudo ip link set dev eth0 down

# 2. Change MAC address
sudo ip link set dev eth0 address 02:00:00:00:00:01

# 3. Bring interface up
sudo ip link set dev eth0 up

# Verify
ip link show eth0
```

### Permanent Change (NetworkManager)

```bash
# Edit connection
sudo nmcli connection modify "Wired connection 1" wifi.cloned-mac-address 02:00:00:00:00:01

# Restart NetworkManager
sudo systemctl restart NetworkManager
```

### Using macchanger (Recommended)

```bash
# Install
sudo apt install macchanger

# Random MAC
sudo macchanger -r eth0

# Specific MAC
sudo macchanger -m 02:00:00:00:00:01 eth0

# Reset to original
sudo macchanger -p eth0
```

## macOS

```bash
# 1. Find your interface
networksetup -listallhardwareports

# 2. Change MAC (temporary)
sudo ifconfig en0 ether 02:00:00:00:00:01

# 3. Restart WiFi
sudo ifconfig en0 down
sudo ifconfig en0 up
```

## Best Practices

### 1. Use Valid MAC Prefixes

- Start with `02:` for locally administered addresses
- Avoid using real vendor prefixes (can be detected)

### 2. Randomize Regularly

```bash
# Linux: Randomize before each scan
sudo macchanger -r eth0
```

### 3. Combine with Other Stealth

- MAC spoofing + VPN + Proxy = Maximum anonymity
- Change MAC → Connect to VPN → Use scanner with proxies

## Integration with Scanner

Since MAC changes require admin/root, you must do it **before** running the scanner:

```bash
# Linux Example:
sudo macchanger -r eth0
python autonomous_scan.py https://target.com --stealth paranoid --proxies proxies.txt

# Windows Example (PowerShell as Admin):
Set-NetAdapter -Name "Ethernet" -MacAddress "02-00-00-00-00-01"
Restart-NetAdapter -Name "Ethernet"
python autonomous_scan.py https://target.com --stealth paranoid --proxies proxies.txt
```

## Automation Script (Linux)

Create `spoof_and_scan.sh`:

```bash
#!/bin/bash

# Spoof MAC
echo "[*] Spoofing MAC address..."
sudo macchanger -r eth0

# Run scanner
echo "[*] Starting scan..."
python autonomous_scan.py "$1" --stealth paranoid --proxies proxies.txt

# Reset MAC (optional)
echo "[*] Resetting MAC..."
sudo macchanger -p eth0
```

Usage:

```bash
chmod +x spoof_and_scan.sh
sudo ./spoof_and_scan.sh https://target.com
```

## Detection Risks

**MAC spoofing is effective for:**

- ✅ Local network anonymity
- ✅ Bypassing MAC-based access control
- ✅ Avoiding device fingerprinting on LAN

**MAC spoofing does NOT help with:**

- ❌ Internet-level tracking (MAC doesn't leave your router)
- ❌ Cloudflare detection (they see your IP, not MAC)
- ❌ ISP tracking

**For internet scanning, use:**

- IP rotation (proxies) ← Most important
- VPN
- Stealth mode (paranoid)

## Troubleshooting

### "Operation not permitted"

- You need root/admin privileges
- Run with `sudo` (Linux) or as Administrator (Windows)

### MAC change doesn't persist

- Use permanent methods (NetworkManager on Linux, Registry on Windows)
- Or add to startup script

### Network stops working

- Reset to original MAC: `sudo macchanger -p eth0`
- Restart network service

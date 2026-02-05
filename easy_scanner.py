"""
Easy Scanner - User Friendly Interface for AI Security Auditor
Does not require any technical knowledge or command line arguments.
"""
import os
import sys
import glob
import re
import subprocess
import time
import webbrowser

# ANSI Colors
CYAN = "\033[96m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
RESET = "\033[0m"
BOLD = "\033[1m"

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def print_banner():
    clear_screen()
    print(f"{CYAN}{BOLD}")
    print("================================================================")
    print("================================================================")
    print("      [+] AI VULNERABILITY SCANNER - MOCK TARGETS [+]")
    print("================================================================")
    print(f"{RESET}")

def get_checkpoints():
    """Find available model checkpoints"""
    checkpoints = glob.glob("checkpoints/improved_mock_ep*.pth")
    if not checkpoints:
        return []
    
    checkpoint_data = []
    for path in checkpoints:
        filename = os.path.basename(path)
        match = re.search(r'ep(\d+)', filename)
        ep = int(match.group(1)) if match else 0
        checkpoint_data.append({'path': path, 'ep': ep, 'name': filename})
    
    # Sort by episode count (descending)
    checkpoint_data.sort(key=lambda x: x['ep'], reverse=True)
    return checkpoint_data

def select_model():
    print(f"{YELLOW}[?] Select AI Brain Model:{RESET}")
    models = get_checkpoints()
    
    if not models:
        print(f"{RED}[!] No models found in checkpoints/ folder!{RESET}")
        input("Press Enter to exit...")
        sys.exit(1)
        
    print(f"   {BOLD}0. Auto-Select Best Model (Episode {models[0]['ep']}){RESET}")
    for i, m in enumerate(models[:5], 1):
        print(f"   {i}. {m['name']} (Trained for {m['ep']} episodes)")
        
    choice = input(f"\n{CYAN}>>> Select option (0-{min(5, len(models))}): {RESET}")
    if not choice or choice == '0':
        return models[0]['path']
    
    try:
        idx = int(choice) - 1
        if 0 <= idx < len(models):
            return models[idx]['path']
    except:
        pass
    
    print(f"{RED}Invalid selection, defaulting to best model.{RESET}")
    time.sleep(1)
    return models[0]['path']

def select_target():
    print(f"\n{YELLOW}[?] Select Target Application:{RESET}")
    targets = [
        {"name": "E-Commerce (Shop)", "url": "http://localhost:5002"},
        {"name": "Social Media (Connect)", "url": "http://localhost:5003"},
        {"name": "Online Banking (Finance)", "url": "http://localhost:5004"},
        {"name": "Secure Blog (Content)", "url": "http://localhost:5005"},
        {"name": "File Share (Storage)", "url": "http://localhost:5006"},
        {"name": "File Share (Storage)", "url": "http://localhost:5006"},
        {"name": "Custom URL", "url": "CUSTOM"},
        {"name": "Scan ALL Mock Sites", "url": "ALL"}
    ]
    
    for i, t in enumerate(targets, 1):
        if t['url'] == "ALL":
             print(f"   {i}. {BOLD}{t['name']:<25}{RESET}")
        else:
             print(f"   {i}. {t['name']:<25} - {t['url']}")
        
    choice = input(f"\n{CYAN}>>> Select target (1-7): {RESET}")
    
    try:
        idx = int(choice) - 1
        if 0 <= idx < len(targets):
            selected = targets[idx]
            
            if selected['url'] == "ALL":
                 # Return list of all localhost targets
                 return [t['url'] for t in targets if "localhost" in t['url']]
            
            if selected['url'] == "CUSTOM":
                custom_url = input(f"{YELLOW}>>> Enter Target URL (e.g. http://example.com): {RESET}")
                if not custom_url.startswith("http"):
                    custom_url = "http://" + custom_url
                return [custom_url]
            
            return [selected['url']]
    except:
        pass
        
    print(f"{RED}Invalid selection!{RESET}")
    return []

def get_scan_config():
    """Returns interactive scan configuration"""
    print(f"\n{YELLOW}[?] Select Scan Profile:{RESET}")
    print(f"   {BOLD}1. Quick Scan   {RESET} (Depth=10, Intensity=3, No Persistence) - Fast check")
    
    print(f"   {BOLD}2. Deep Scan    {RESET} (Depth=30, Intensity=7, Persistence=On) - Thorough")
    print(f"   {BOLD}3. Aggressive   {RESET} (Depth=50, Intensity=10, Persistence=On) - Maximum Impact")
    print(f"   {BOLD}4. Full AI (Pentester){RESET} (Chain Attacks, Online Learning) - Unleashed")
    print(f"   {BOLD}5. Custom Config{RESET} - Manually set parameters")
    
    choice = input(f"\n{CYAN}>>> Select profile (1-5) [Default: 2]: {RESET}")
    
    if choice == '1':
        return {"depth": 10, "intensity": 3, "persist": False, "ai_mode": False, "pentester": False}
    elif choice == '3':
        return {"depth": 50, "intensity": 10, "persist": True, "ai_mode": False, "pentester": False}
    elif choice == '4':
        print(f"\n{YELLOW}[!] Enabling Full AI Unleashed Mode (Chain Attacks + Learning){RESET}")
        return {"depth": 50, "intensity": 50, "persist": True, "ai_mode": True, "pentester": True}
    elif choice == '5':
        try:
            d = int(input(f"   - Enter Crawl Depth (1-100): "))
            i = int(input(f"   - Enter Attack Intensity (1-20): "))
            p = input(f"   - Enable Persistence (Scan until found)? (Y/n): ").lower() != 'n'
            ai = input(f"   - Enable AI Recon Mode? (Y/n): ").lower() == 'y'
            pent = input(f"   - Enable Pentester/Chain Attacks? (Y/n): ").lower() == 'y'
            return {"depth": d, "intensity": i, "persist": p, "ai_mode": ai, "pentester": pent}
        except:
            print(f"{RED}Invalid input, using Default Deep Scan.{RESET}")
            return {"depth": 30, "intensity": 7, "persist": True, "ai_mode": False, "pentester": False}
    else:
        # Default to Deep Scan (Option 2)
        return {"depth": 30, "intensity": 7, "persist": True, "ai_mode": False, "pentester": False}

def find_latest_report():
    """Finds the most recently created Markdown report."""
    list_of_files = glob.glob('reports/*.md') 
    if not list_of_files:
        return None
    latest_file = max(list_of_files, key=os.path.getctime)
    return latest_file

def open_report(report_path):
    """Opens the report in the default browser/viewer."""
    try:
        abs_path = os.path.abspath(report_path)
        print(f"Opening: {abs_path}")
        webbrowser.open(abs_path)
    except Exception as e:
        print(f"{RED}Failed to open report: {e}{RESET}")

def main():
    while True:
        print_banner()
        
        # 1. Model
        model_path = select_model()
        # 1. Model
        model_path = select_model()
        print(f"{GREEN}[OK] Loaded Model: {os.path.basename(model_path)}{RESET}")
        
        # 2. Target
        target_urls = select_target()
        if not target_urls:
            time.sleep(1)
            continue
            
        if len(target_urls) > 1:
            print(f"{GREEN}[OK] Selected {len(target_urls)} Targets for Batch Scan{RESET}")
        else:
            print(f"{GREEN}[OK] Target Set: {target_urls[0]}{RESET}")
        
        # 3. Get optimized scan config
        config = get_scan_config()
        print(f"{GREEN}[OK] Scan Configured: Depth={config['depth']}, Intensity={config['intensity']}{RESET}")
        
        # Confirm
        print(f"\n{YELLOW}Ready to scan {len(target_urls)} target(s)?{RESET}")
        input(f"Press {BOLD}ENTER{RESET} to start scanning...")
        
        # Batch Scan Loop
        for i, url in enumerate(target_urls, 1):
            if len(target_urls) > 1:
                print(f"\n{CYAN}{BOLD}>>> STARTING SCAN {i}/{len(target_urls)}: {url}{RESET}")
            
            # Build Command
            cmd = [
                sys.executable, "autonomous_scan.py",
                url,
                "--model", model_path,
                "--depth", str(config['depth']),
                "--intensity", str(config['intensity'])
            ]
            
            if config.get('persist'):
                cmd.append("--persist")
            if config.get('ai_mode'):
                cmd.append("--ai-mode")
            if config.get('pentester'):
                cmd.append("--pentester")
                
            # Run
            print(f"\n{CYAN}🔍 Scanning {url}... (Press Ctrl+C to skip/stop){RESET}\n")
            try:
                subprocess.run(cmd)
            except KeyboardInterrupt:
                print(f"\n{RED}🛑 Scan interrupted by user.{RESET}")
                if len(target_urls) > 1:
                    skip = input(f"\n{YELLOW}Skip remaining targets? (y/N): {RESET}")
                    if skip.lower() == 'y':
                        break
        
        print(f"\n{YELLOW}Batch Scan finished.{RESET}")
        
        # Check for report (just check the latest one generated)
        latest_report = find_latest_report()
        if latest_report:
            print(f"\n{GREEN}[+] Latest Report: {latest_report}{RESET}")
            open_invitation = input(f"{CYAN}>>> Open latest report? (Y/n): {RESET}")
            if open_invitation.lower() != 'n':
                open_report(latest_report)
        else:
             print(f"\n{RED}[!] No report found.{RESET}")
        choice = input(f"\n{CYAN}>>> Scan another target? (y/n): {RESET}")
        if choice.lower() != 'y':
            print("Goodbye!")
            break

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nGoodbye!")

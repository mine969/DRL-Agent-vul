#!/usr/bin/env python3
"""
Simple Web Security Scanner - Interactive Mode

Just run this script and enter a website URL!
No need to edit code or remember command-line arguments.
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from autonomous_scan import SecurityAuditor

def print_banner():
    """Display welcome banner"""
    print("\n" + "="*70)
    print("🛡️  AI-POWERED WEB SECURITY SCANNER")
    print("="*70)
    print("\nThis tool will automatically:")
    print("  1. Crawl the website to discover all pages")
    print("  2. Find hidden endpoints (admin, api, etc.)")
    print("  3. Test each page for security vulnerabilities")
    print("  4. Generate detailed reports (HTML, TXT, MD)")
    print("\n⚠️  IMPORTANT: Only scan websites you own or have permission to test!")
    print("="*70 + "\n")

def get_user_input():
    """Get target URL from user"""
    while True:
        target = input("🎯 Enter website URL or IP (e.g., http://localhost/dvwa): ").strip()
        
        if not target:
            print("❌ Please enter a valid URL or IP address\n")
            continue
        
        # Add http:// if not present
        if not target.startswith(('http://', 'https://')):
            print(f"ℹ️  Adding 'http://' prefix...")
            target = 'http://' + target
        
        # Confirm with user
        print(f"\n📍 Target: {target}")
        confirm = input("Is this correct? (y/n): ").strip().lower()
        
        if confirm in ['y', 'yes']:
            return target
        print()

def get_scan_options():
    """Get optional scan parameters"""
    print("\n⚙️  Scan Options (press Enter for defaults)")
    print("-"*70)
    
    # Crawl depth
    while True:
        depth_input = input("Max pages to crawl [default: 30]: ").strip()
        if not depth_input:
            depth = 30
            break
        try:
            depth = int(depth_input)
            if depth > 0:
                break
            print("❌ Please enter a positive number")
        except ValueError:
            print("❌ Please enter a valid number")
    
    # Test episodes
    while True:
        episodes_input = input("Test episodes per page [default: 3]: ").strip()
        if not episodes_input:
            episodes = 3
            break
        try:
            episodes = int(episodes_input)
            if episodes > 0:
                break
            print("❌ Please enter a positive number")
        except ValueError:
            print("❌ Please enter a valid number")
    
    # Model path
    model_input = input("Model file [default: dqn_web_sec_model.pth]: ").strip()
    model = model_input if model_input else "dqn_web_sec_model.pth"
    
    return depth, episodes, model

def main():
    """Main interactive function"""
    print_banner()
    
    # Get target from user
    target = get_user_input()
    
    # Ask if user wants to customize options
    print("\nWould you like to customize scan options?")
    customize = input("(y/n) [default: n]: ").strip().lower()
    
    if customize in ['y', 'yes']:
        depth, episodes, model = get_scan_options()
    else:
        depth = 30
        episodes = 3
        model = "dqn_web_sec_model.pth"
    
    # Display scan configuration
    print("\n" + "="*70)
    print("SCAN CONFIGURATION")
    print("="*70)
    print(f"Target URL:       {target}")
    print(f"Max Pages:        {depth}")
    print(f"Episodes/Page:    {episodes}")
    print(f"Model:            {model}")
    print("="*70)
    
    # Final confirmation
    print("\n⚠️  Ready to start scanning!")
    start = input("Press Enter to begin (or Ctrl+C to cancel)...")
    
    print("\n🚀 Starting scan...\n")
    
    try:
        # Create and run scanner
        agent = SecurityAuditor(target, model)
        findings = agent.start_audit(crawl_depth=depth, test_intensity=episodes)
        
        print("\n" + "="*70)
        print("✅ SCAN COMPLETE!")
        print("="*70)
        print(f"\nFound {len(findings)} vulnerabilities")
        print("\n📁 Reports have been saved in the reports/ directory:")
        print("   - reports/vulnerability_report_*.md   (Markdown)")
        print("   - vulnerability_report_*.txt  (Plain text)")
        print("   - vulnerability_report_*.md   (Markdown)")
        print("\n💡 Tip: Open the HTML file in your browser for the best experience!")
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Scan cancelled by user")
        sys.exit(0)
    except FileNotFoundError:
        print(f"\n❌ Error: Model file '{model}' not found!")
        print("\n💡 Make sure you have trained the model first:")
        print("   python train.py")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error during scan: {str(e)}")
        print("\n💡 Common issues:")
        print("   - Make sure the target website is accessible")
        print("   - Check if you have trained the model (python train.py)")
        print("   - Verify you have permission to scan the target")
        sys.exit(1)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Goodbye!")
        sys.exit(0)

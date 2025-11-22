"""
AI-Powered Web Security Scanner - GUI Application

Modern, accessible GUI for the security scanner with:
- Clean, professional design
- Dark theme
- Progress tracking
- Real-time logs
- Easy model selection
- Report viewing
- Command-line automation support (NEW!)

Usage:
    GUI Mode:       python scanner_gui.py
    Automated Mode: python scanner_gui.py --auto --target http://site.com --depth 50
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, filedialog, messagebox
import threading
import os
import sys
import glob
import argparse
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from autonomous_scan import AutonomousSecurityAgent

class SecurityScannerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("🛡️ AI-Powered Web Security Scanner")
        self.root.geometry("900x700")
        self.root.minsize(800, 600)
        
        # Configure dark theme colors
        self.bg_dark = "#1e1e2e"
        self.bg_medium = "#2a2a3e"
        self.bg_light = "#363654"
        self.accent = "#667eea"
        self.accent_hover = "#764ba2"
        self.text_color = "#e0e0e0"
        self.success = "#28a745"
        self.warning = "#ffc107"
        self.danger = "#dc3545"
        
        self.root.configure(bg=self.bg_dark)
        
        # Variables
        self.target_url = tk.StringVar()
        self.crawl_depth = tk.IntVar(value=30)
        self.test_episodes = tk.IntVar(value=3)
        self.model_path = tk.StringVar(value="dqn_web_sec_model.pth")
        self.is_scanning = False
        
        self.setup_ui()
        self.load_available_models()
        
    def setup_ui(self):
        """Setup the user interface"""
        
        # Header
        header_frame = tk.Frame(self.root, bg=self.bg_medium, height=80)
        header_frame.pack(fill=tk.X, padx=0, pady=0)
        header_frame.pack_propagate(False)
        
        title_label = tk.Label(
            header_frame,
            text="🛡️ AI-Powered Web Security Scanner",
            font=("Segoe UI", 20, "bold"),
            bg=self.bg_medium,
            fg=self.text_color
        )
        title_label.pack(pady=20)
        
        # Main container
        main_frame = tk.Frame(self.root, bg=self.bg_dark)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Left panel - Configuration
        left_panel = tk.Frame(main_frame, bg=self.bg_medium, width=400)
        left_panel.pack(side=tk.LEFT, fill=tk.BOTH, padx=(0, 10))
        
        config_label = tk.Label(
            left_panel,
            text="⚙️ Configuration",
            font=("Segoe UI", 14, "bold"),
            bg=self.bg_medium,
            fg=self.text_color
        )
        config_label.pack(pady=(15, 10), padx=15, anchor=tk.W)
        
        # Target URL
        self.create_input_field(
            left_panel,
            "🎯 Target URL:",
            self.target_url,
            "http://localhost/dvwa"
        )
        
        # Crawl Depth
        self.create_slider_field(
            left_panel,
            "🕷️ Crawl Depth:",
            self.crawl_depth,
            1, 100, 30
        )
        
        # Test Episodes
        self.create_slider_field(
            left_panel,
            "🔄 Test Episodes per Page:",
            self.test_episodes,
            1, 10, 3
        )
        
        # Model Selection
        self.create_model_selector(left_panel)
        
        # Scan Button
        self.scan_button = tk.Button(
            left_panel,
            text="🚀 Start Scan",
            font=("Segoe UI", 12, "bold"),
            bg=self.accent,
            fg="white",
            activebackground=self.accent_hover,
            activeforeground="white",
            relief=tk.FLAT,
            cursor="hand2",
            command=self.start_scan,
            height=2
        )
        self.scan_button.pack(pady=20, padx=15, fill=tk.X)
        
        # Stop Button
        self.stop_button = tk.Button(
            left_panel,
            text="⏹️ Stop Scan",
            font=("Segoe UI", 12, "bold"),
            bg=self.danger,
            fg="white",
            activebackground="#c82333",
            activeforeground="white",
            relief=tk.FLAT,
            cursor="hand2",
            command=self.stop_scan,
            height=2,
            state=tk.DISABLED
        )
        self.stop_button.pack(pady=(0, 20), padx=15, fill=tk.X)
        
        # Right panel - Output
        right_panel = tk.Frame(main_frame, bg=self.bg_medium)
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        output_label = tk.Label(
            right_panel,
            text="📊 Scan Output",
            font=("Segoe UI", 14, "bold"),
            bg=self.bg_medium,
            fg=self.text_color
        )
        output_label.pack(pady=(15, 10), padx=15, anchor=tk.W)
        
        # Progress Bar
        self.progress = ttk.Progressbar(
            right_panel,
            mode='indeterminate',
            length=300
        )
        self.progress.pack(pady=10, padx=15, fill=tk.X)
        
        # Status Label
        self.status_label = tk.Label(
            right_panel,
            text="Ready to scan",
            font=("Segoe UI", 10),
            bg=self.bg_medium,
            fg=self.text_color
        )
        self.status_label.pack(pady=5, padx=15, anchor=tk.W)
        
        # Output Text Area
        self.output_text = scrolledtext.ScrolledText(
            right_panel,
            wrap=tk.WORD,
            font=("Consolas", 9),
            bg=self.bg_dark,
            fg=self.text_color,
            insertbackground=self.text_color,
            relief=tk.FLAT,
            padx=10,
            pady=10
        )
        self.output_text.pack(pady=10, padx=15, fill=tk.BOTH, expand=True)
        
        # Buttons Frame
        button_frame = tk.Frame(right_panel, bg=self.bg_medium)
        button_frame.pack(pady=10, padx=15, fill=tk.X)
        
        # View Report Button
        self.view_report_button = tk.Button(
            button_frame,
            text="📄 View HTML Report",
            font=("Segoe UI", 10),
            bg=self.success,
            fg="white",
            activebackground="#218838",
            activeforeground="white",
            relief=tk.FLAT,
            cursor="hand2",
            command=self.view_report,
            state=tk.DISABLED
        )
        self.view_report_button.pack(side=tk.LEFT, padx=(0, 5), fill=tk.X, expand=True)
        
        # Clear Log Button
        clear_button = tk.Button(
            button_frame,
            text="🗑️ Clear Log",
            font=("Segoe UI", 10),
            bg=self.bg_light,
            fg=self.text_color,
            activebackground="#4a4a68",
            activeforeground=self.text_color,
            relief=tk.FLAT,
            cursor="hand2",
            command=self.clear_log
        )
        clear_button.pack(side=tk.RIGHT, fill=tk.X, expand=True)
        
        # Footer
        footer = tk.Label(
            self.root,
            text="⚠️ For Authorized Security Testing Only | AI-Powered Scanner v1.0",
            font=("Segoe UI", 8),
            bg=self.bg_medium,
            fg=self.text_color,
            pady=10
        )
        footer.pack(side=tk.BOTTOM, fill=tk.X)
        
    def create_input_field(self, parent, label_text, variable, placeholder):
        """Create a labeled input field"""
        frame = tk.Frame(parent, bg=self.bg_medium)
        frame.pack(pady=10, padx=15, fill=tk.X)
        
        label = tk.Label(
            frame,
            text=label_text,
            font=("Segoe UI", 10, "bold"),
            bg=self.bg_medium,
            fg=self.text_color
        )
        label.pack(anchor=tk.W, pady=(0, 5))
        
        entry = tk.Entry(
            frame,
            textvariable=variable,
            font=("Segoe UI", 10),
            bg=self.bg_dark,
            fg=self.text_color,
            insertbackground=self.text_color,
            relief=tk.FLAT,
            highlightthickness=1,
            highlightbackground=self.bg_light,
            highlightcolor=self.accent
        )
        entry.pack(fill=tk.X, ipady=5)
        entry.insert(0, placeholder)
        
    def create_slider_field(self, parent, label_text, variable, from_, to, default):
        """Create a labeled slider field"""
        frame = tk.Frame(parent, bg=self.bg_medium)
        frame.pack(pady=10, padx=15, fill=tk.X)
        
        label_frame = tk.Frame(frame, bg=self.bg_medium)
        label_frame.pack(fill=tk.X, pady=(0, 5))
        
        label = tk.Label(
            label_frame,
            text=label_text,
            font=("Segoe UI", 10, "bold"),
            bg=self.bg_medium,
            fg=self.text_color
        )
        label.pack(side=tk.LEFT)
        
        value_label = tk.Label(
            label_frame,
            textvariable=variable,
            font=("Segoe UI", 10),
            bg=self.bg_medium,
            fg=self.accent
        )
        value_label.pack(side=tk.RIGHT)
        
        slider = tk.Scale(
            frame,
            from_=from_,
            to=to,
            orient=tk.HORIZONTAL,
            variable=variable,
            bg=self.bg_medium,
            fg=self.text_color,
            troughcolor=self.bg_dark,
            highlightthickness=0,
            showvalue=False,
            activebackground=self.accent
        )
        slider.pack(fill=tk.X)
        slider.set(default)
        
    def create_model_selector(self, parent):
        """Create model selection dropdown"""
        frame = tk.Frame(parent, bg=self.bg_medium)
        frame.pack(pady=10, padx=15, fill=tk.X)
        
        label = tk.Label(
            frame,
            text="🤖 AI Model:",
            font=("Segoe UI", 10, "bold"),
            bg=self.bg_medium,
            fg=self.text_color
        )
        label.pack(anchor=tk.W, pady=(0, 5))
        
        self.model_combo = ttk.Combobox(
            frame,
            textvariable=self.model_path,
            font=("Segoe UI", 9),
            state="readonly"
        )
        self.model_combo.pack(fill=tk.X, ipady=3)
        
    def load_available_models(self):
        """Load available model files"""
        models = []
        
        # Check for final model
        if os.path.exists("dqn_web_sec_model.pth"):
            models.append("dqn_web_sec_model.pth (Final - Best Quality)")
        
        # Check for checkpoints
        checkpoints = glob.glob("checkpoints/dqn_checkpoint_ep*.pth")
        checkpoints.sort(reverse=True)
        
        for cp in checkpoints:
            ep_num = cp.split("ep")[1].split(".pth")[0]
            models.append(f"{cp} (Episode {ep_num})")
        
        if models:
            self.model_combo['values'] = models
            self.model_combo.current(0)
        else:
            self.model_combo['values'] = ["No models found - train first!"]
            self.model_combo.current(0)
            
    def log(self, message, level="INFO"):
        """Add message to output log"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        # Color coding
        if level == "SUCCESS":
            prefix = "✅"
        elif level == "ERROR":
            prefix = "❌"
        elif level == "WARNING":
            prefix = "⚠️"
        else:
            prefix = "ℹ️"
        
        formatted_message = f"[{timestamp}] {prefix} {message}\n"
        
        self.output_text.insert(tk.END, formatted_message)
        self.output_text.see(tk.END)
        self.root.update()
        
    def clear_log(self):
        """Clear the output log"""
        self.output_text.delete(1.0, tk.END)
        
    def update_status(self, message):
        """Update status label"""
        self.status_label.config(text=message)
        self.root.update()
        
    def start_scan(self):
        """Start the security scan"""
        # Validate input
        target = self.target_url.get().strip()
        if not target:
            messagebox.showerror("Error", "Please enter a target URL!")
            return
        
        # Add http:// if not present
        if not target.startswith(('http://', 'https://')):
            target = 'http://' + target
            self.target_url.set(target)
        
        # Get model path (remove description)
        model = self.model_path.get().split(" (")[0]
        
        if not os.path.exists(model):
            messagebox.showerror("Error", f"Model file not found: {model}\nPlease train the model first!")
            return
        
        # Confirm scan
        if not messagebox.askyesno(
            "Confirm Scan",
            f"Start scanning:\n\n"
            f"Target: {target}\n"
            f"Depth: {self.crawl_depth.get()} pages\n"
            f"Episodes: {self.test_episodes.get()}\n"
            f"Model: {model}\n\n"
            f"⚠️ Make sure you have permission to test this target!"
        ):
            return
        
        # Disable controls
        self.scan_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        self.is_scanning = True
        
        # Start progress bar
        self.progress.start(10)
        
        # Clear log
        self.clear_log()
        
        # Run scan in thread
        scan_thread = threading.Thread(
            target=self.run_scan,
            args=(target, model),
            daemon=True
        )
        scan_thread.start()
        
    def run_scan(self, target, model):
        """Run the actual scan"""
        try:
            self.log(f"Starting scan on {target}", "INFO")
            self.log(f"Using model: {model}", "INFO")
            self.update_status("Scanning in progress...")
            
            # Create scanner
            agent = AutonomousSecurityAgent(target, model)
            
            # Run scan
            findings = agent.scan(
                crawl_depth=self.crawl_depth.get(),
                test_episodes=self.test_episodes.get()
            )
            
            # Scan complete
            if self.is_scanning:
                self.log(f"Scan complete! Found {len(findings)} vulnerabilities", "SUCCESS")
                self.update_status(f"Scan complete - {len(findings)} vulnerabilities found")
                self.view_report_button.config(state=tk.NORMAL)
                
                messagebox.showinfo(
                    "Scan Complete",
                    f"Scan finished successfully!\n\n"
                    f"Vulnerabilities found: {len(findings)}\n\n"
                    f"Reports have been saved:\n"
                    f"- vulnerability_report_*.html\n"
                    f"- vulnerability_report_*.txt\n"
                    f"- vulnerability_report_*.md"
                )
            
        except Exception as e:
            self.log(f"Error during scan: {str(e)}", "ERROR")
            self.update_status("Scan failed")
            messagebox.showerror("Scan Error", f"An error occurred:\n\n{str(e)}")
        
        finally:
            # Re-enable controls
            self.progress.stop()
            self.scan_button.config(state=tk.NORMAL)
            self.stop_button.config(state=tk.DISABLED)
            self.is_scanning = False
            
    def stop_scan(self):
        """Stop the current scan"""
        if messagebox.askyesno("Stop Scan", "Are you sure you want to stop the scan?"):
            self.is_scanning = False
            self.log("Scan stopped by user", "WARNING")
            self.update_status("Scan stopped")
            self.progress.stop()
            self.scan_button.config(state=tk.NORMAL)
            self.stop_button.config(state=tk.DISABLED)
            
    def view_report(self):
        """Open the latest HTML report"""
        reports = glob.glob("vulnerability_report_*.html")
        if reports:
            latest_report = max(reports, key=os.path.getctime)
            os.startfile(latest_report)
            self.log(f"Opening report: {latest_report}", "INFO")
        else:
            messagebox.showwarning("No Reports", "No reports found. Run a scan first!")

def main():
    """Main entry point with automation support"""
    parser = argparse.ArgumentParser(
        description='AI-Powered Web Security Scanner',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # GUI Mode (interactive)
  python scanner_gui.py
  
  # Automated Mode (headless)
  python scanner_gui.py --auto --target http://localhost/dvwa
  python scanner_gui.py --auto --target http://site.com --depth 50 --episodes 5
  python scanner_gui.py --auto --target http://site.com --model checkpoints/dqn_checkpoint_ep500.pth
  
  # Batch Processing
  python scanner_gui.py --auto --target http://site1.com --depth 30
  python scanner_gui.py --auto --target http://site2.com --depth 30
        """
    )
    
    parser.add_argument(
        '--auto',
        action='store_true',
        help='Run in automated mode (no GUI, direct scan)'
    )
    
    parser.add_argument(
        '--target',
        type=str,
        help='Target URL to scan (required for --auto mode)'
    )
    
    parser.add_argument(
        '--depth',
        type=int,
        default=30,
        help='Crawl depth (default: 30)'
    )
    
    parser.add_argument(
        '--episodes',
        type=int,
        default=3,
        help='Test episodes per page (default: 3)'
    )
    
    parser.add_argument(
        '--model',
        type=str,
        default='dqn_web_sec_model.pth',
        help='Model file to use (default: dqn_web_sec_model.pth)'
    )
    
    args = parser.parse_args()
    
    # Automated mode (no GUI)
    if args.auto:
        if not args.target:
            print("❌ Error: --target is required in automated mode")
            print("\nUsage: python scanner_gui.py --auto --target http://site.com")
            sys.exit(1)
        
        # Add http:// if not present
        target = args.target
        if not target.startswith(('http://', 'https://')):
            target = 'http://' + target
        
        # Check model exists
        if not os.path.exists(args.model):
            print(f"❌ Error: Model file not found: {args.model}")
            print("\n💡 Available models:")
            if os.path.exists("dqn_web_sec_model.pth"):
                print("   - dqn_web_sec_model.pth (final model)")
            checkpoints = glob.glob("checkpoints/dqn_checkpoint_ep*.pth")
            for cp in sorted(checkpoints, reverse=True)[:5]:
                print(f"   - {cp}")
            sys.exit(1)
        
        print("="*70)
        print("🛡️  AI-POWERED WEB SECURITY SCANNER - AUTOMATED MODE")
        print("="*70)
        print(f"\n🎯 Target:       {target}")
        print(f"🕷️  Crawl Depth:  {args.depth} pages")
        print(f"🔄 Episodes:     {args.episodes} per page")
        print(f"🤖 Model:        {args.model}")
        print("\n" + "="*70)
        print("⚠️  Make sure you have permission to test this target!")
        print("="*70 + "\n")
        
        try:
            # Import here to avoid GUI dependencies in headless mode
            from autonomous_scan import AutonomousSecurityAgent
            
            print(f"[{datetime.now().strftime('%H:%M:%S')}] ℹ️  Starting scan...")
            
            # Create scanner
            agent = AutonomousSecurityAgent(target, args.model)
            
            # Run scan
            findings = agent.scan(
                crawl_depth=args.depth,
                test_episodes=args.episodes
            )
            
            print(f"\n[{datetime.now().strftime('%H:%M:%S')}] ✅ Scan complete!")
            print(f"\n📊 Results:")
            print(f"   - Vulnerabilities found: {len(findings)}")
            print(f"\n📁 Reports saved:")
            
            # Find latest reports
            html_reports = glob.glob("vulnerability_report_*.html")
            txt_reports = glob.glob("vulnerability_report_*.txt")
            md_reports = glob.glob("vulnerability_report_*.md")
            
            if html_reports:
                latest_html = max(html_reports, key=os.path.getctime)
                print(f"   - {latest_html} (HTML)")
            if txt_reports:
                latest_txt = max(txt_reports, key=os.path.getctime)
                print(f"   - {latest_txt} (TXT)")
            if md_reports:
                latest_md = max(md_reports, key=os.path.getctime)
                print(f"   - {latest_md} (MD)")
            
            print("\n" + "="*70)
            print("✅ Automated scan completed successfully!")
            print("="*70)
            
        except Exception as e:
            print(f"\n❌ Error during scan: {str(e)}")
            sys.exit(1)
    
    # GUI mode (interactive)
    else:
        root = tk.Tk()
        app = SecurityScannerGUI(root)
        root.mainloop()

if __name__ == "__main__":
    main()


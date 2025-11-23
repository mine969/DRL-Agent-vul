"""
AI-Powered Web Security Scanner - GUI Application
=================================================

Modern, accessible GUI for the security scanner with:
- Clean, professional design
- Dark theme
- Progress tracking
- Real-time logs
- Easy model selection
- Report viewing
- Command-line automation support
- ONE-CLICK EXPLOIT GENERATOR (NEW!)

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
import json
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from autonomous_scan import SecurityAuditor

class ExploitGenerator:
    """Generates ready-to-use exploits from vulnerability data"""
    
    @staticmethod
    def generate_curl(vuln):
        """Generate a curl command for the exploit"""
        url = vuln.get('url', 'http://target.com')
        method = vuln.get('method', 'GET')
        payload = vuln.get('payload', '')
        param = vuln.get('parameter', 'q')
        
        if method == 'GET':
            # Handle query parameters
            separator = '&' if '?' in url else '?'
            
            if '=' in payload:
                # Payload is likely "param=value"
                full_url = f"{url}{separator}{payload}"
            else:
                # Payload is just value, use default param
                full_url = f"{url}{separator}{param}={payload}"
                
            return f"curl -v '{full_url}'"
        
        elif method == 'POST':
            # Handle JSON or Form data
            if '=' in payload or '{' in payload:
                data = payload
            else:
                data = f"{param}={payload}"
            return f"curl -v -X POST '{url}' -d '{data}'"
            
        return f"# Method {method} not supported for auto-generation"

    @staticmethod
    def generate_python(vuln):
        """Generate a Python script for the exploit"""
        url = vuln.get('url', 'http://target.com')
        method = vuln.get('method', 'GET')
        payload = vuln.get('payload', '')
        param = vuln.get('parameter', 'q')
        
        script = f"""import requests

target_url = "{url}"
payload = "{payload}"

print(f"[*] Exploiting {vuln.get('type', 'Vulnerability')}...")
"""
        
        if method == 'GET':
            if '=' in payload:
                # Parse payload into dict if possible, or just append to URL
                script += f"""
# GET Request Exploit
# Payload contains parameters: {payload}
full_url = f"{{target_url}}?{{payload}}" if "?" not in target_url else f"{{target_url}}&{{payload}}"
response = requests.get(full_url)
"""
            else:
                script += f"""
# GET Request Exploit
params = {{'{param}': payload}}
response = requests.get(target_url, params=params)
"""
        elif method == 'POST':
            script += f"""
# POST Request Exploit
# Ensure payload is correctly formatted (JSON or form data)
data = payload 
# If payload is 'param=value', requests will handle it as string body
response = requests.post(target_url, data=data, headers={{'Content-Type': 'application/x-www-form-urlencoded'}})
"""
            
        script += """
print(f"[*] Status Code: {response.status_code}")
print(f"[*] Response Body Preview: {response.text[:200]}...")
if response.status_code == 200:
    print("[+] Exploit sent successfully!")
else:
    print("[-] Server returned error.")
"""
        return script

    @staticmethod
    def get_steps(vuln):
        """Get step-by-step hacking instructions"""
        v_type = vuln.get('type', 'Unknown')
        
        steps = {
            'SQL Injection': [
                "1. Identify the vulnerable parameter (e.g., 'id', 'q').",
                "2. Inject the SQL payload to manipulate the query.",
                "3. Observe the response for database errors or data leakage.",
                "4. Use UNION SELECT to extract data from other tables."
            ],
            'XSS': [
                "1. Find a reflection point where input is echoed back.",
                "2. Inject the script payload.",
                "3. If the script executes (e.g., alert pops up), it's vulnerable.",
                "4. Use this to steal cookies or redirect users."
            ],
            'IDOR': [
                "1. Identify the object ID in the URL or request body.",
                "2. Change the ID to another user's ID.",
                "3. Check if you can access the other user's data.",
                "4. This confirms broken access control."
            ],
            'SSRF': [
                "1. Find a parameter that takes a URL.",
                "2. Input an internal IP (e.g., 127.0.0.1) or cloud metadata URL.",
                "3. Check if the server returns internal data.",
                "4. This allows mapping the internal network."
            ]
        }
        
        default_steps = [
            "1. Analyze the request and response.",
            "2. Replay the request with the malicious payload.",
            "3. Verify the security impact.",
            "4. Report the finding."
        ]
        
        # Fuzzy match key
        for key in steps:
            if key.lower() in v_type.lower():
                return "\n".join(steps[key])
                
        return "\n".join(default_steps)

class SecurityScannerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("🛡️ AI-Powered Web Security Scanner & Exploiter")
        self.root.geometry("1200x800")
        self.root.minsize(1000, 700)
        
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
        self.code_bg = "#11111b"
        
        self.root.configure(bg=self.bg_dark)
        
        # Variables
        self.target_url = tk.StringVar()
        self.crawl_depth = tk.IntVar(value=30)
        self.test_episodes = tk.IntVar(value=3)
        self.model_path = tk.StringVar(value="dqn_web_sec_model.pth")
        self.is_scanning = False
        self.findings = []
        
        self.setup_ui()
        self.load_available_models()
        
    def setup_ui(self):
        """Setup the user interface"""
        
        # Header
        header_frame = tk.Frame(self.root, bg=self.bg_medium, height=70)
        header_frame.pack(fill=tk.X, padx=0, pady=0)
        header_frame.pack_propagate(False)
        
        title_label = tk.Label(
            header_frame,
            text="🛡️ AI-Powered Web Security Scanner & Exploiter",
            font=("Segoe UI", 18, "bold"),
            bg=self.bg_medium,
            fg=self.text_color
        )
        title_label.pack(pady=15)
        
        # Main container (Split into Left Config, Middle Log, Right Exploit)
        main_pane = tk.PanedWindow(self.root, bg=self.bg_dark, orient=tk.HORIZONTAL)
        main_pane.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # === LEFT PANEL: CONFIGURATION ===
        left_panel = tk.Frame(main_pane, bg=self.bg_medium, width=300)
        main_pane.add(left_panel, minsize=250)
        
        config_label = tk.Label(left_panel, text="⚙️ Configuration", font=("Segoe UI", 12, "bold"), bg=self.bg_medium, fg=self.text_color)
        config_label.pack(pady=(15, 10), padx=15, anchor=tk.W)
        
        self.create_input_field(left_panel, "🎯 Target URL:", self.target_url, "http://localhost:5000")
        self.create_slider_field(left_panel, "🕷️ Crawl Depth:", self.crawl_depth, 1, 100, 30)
        self.create_slider_field(left_panel, "🔄 Intensity:", self.test_episodes, 1, 10, 3)
        self.create_model_selector(left_panel)
        
        self.scan_button = tk.Button(left_panel, text="🚀 Start Scan", font=("Segoe UI", 11, "bold"), bg=self.accent, fg="white", relief=tk.FLAT, cursor="hand2", command=self.start_scan, height=2)
        self.scan_button.pack(pady=15, padx=15, fill=tk.X)
        
        self.stop_button = tk.Button(left_panel, text="⏹️ Stop Scan", font=("Segoe UI", 11, "bold"), bg=self.danger, fg="white", relief=tk.FLAT, cursor="hand2", command=self.stop_scan, height=2, state=tk.DISABLED)
        self.stop_button.pack(pady=(0, 15), padx=15, fill=tk.X)
        
        # === MIDDLE PANEL: LOGS & FINDINGS ===
        middle_panel = tk.Frame(main_pane, bg=self.bg_medium)
        main_pane.add(middle_panel, minsize=350)
        
        log_label = tk.Label(middle_panel, text="📊 Live Scan Logs", font=("Segoe UI", 12, "bold"), bg=self.bg_medium, fg=self.text_color)
        log_label.pack(pady=(15, 5), padx=15, anchor=tk.W)
        
        self.progress = ttk.Progressbar(middle_panel, mode='indeterminate')
        self.progress.pack(pady=5, padx=15, fill=tk.X)
        
        self.status_label = tk.Label(middle_panel, text="Ready to scan", font=("Segoe UI", 9), bg=self.bg_medium, fg=self.text_color)
        self.status_label.pack(pady=0, padx=15, anchor=tk.W)
        
        self.output_text = scrolledtext.ScrolledText(middle_panel, wrap=tk.WORD, font=("Consolas", 9), bg=self.bg_dark, fg=self.text_color, relief=tk.FLAT, height=15)
        self.output_text.pack(pady=10, padx=15, fill=tk.BOTH, expand=True)
        
        findings_label = tk.Label(middle_panel, text="🚨 Vulnerabilities Found (Click to Exploit)", font=("Segoe UI", 12, "bold"), bg=self.bg_medium, fg=self.warning)
        findings_label.pack(pady=(10, 5), padx=15, anchor=tk.W)
        
        # Listbox for findings
        self.findings_list = tk.Listbox(middle_panel, font=("Segoe UI", 10), bg=self.bg_dark, fg=self.text_color, selectbackground=self.accent, relief=tk.FLAT, height=10)
        self.findings_list.pack(pady=10, padx=15, fill=tk.BOTH, expand=True)
        self.findings_list.bind('<<ListboxSelect>>', self.on_finding_select)
        
        # === RIGHT PANEL: EXPLOIT GENERATOR ===
        right_panel = tk.Frame(main_pane, bg=self.bg_medium)
        main_pane.add(right_panel, minsize=350)
        
        exploit_label = tk.Label(right_panel, text="💣 Exploit Generator", font=("Segoe UI", 12, "bold"), bg=self.bg_medium, fg=self.danger)
        exploit_label.pack(pady=(15, 10), padx=15, anchor=tk.W)
        
        # Exploit details text area
        self.exploit_text = scrolledtext.ScrolledText(right_panel, wrap=tk.WORD, font=("Consolas", 10), bg=self.code_bg, fg="#00ff00", relief=tk.FLAT, insertbackground="white")
        self.exploit_text.pack(pady=10, padx=15, fill=tk.BOTH, expand=True)
        self.exploit_text.insert(tk.END, "// Select a vulnerability to generate exploit...")
        
        btn_frame = tk.Frame(right_panel, bg=self.bg_medium)
        btn_frame.pack(pady=10, padx=15, fill=tk.X)
        
        self.copy_btn = tk.Button(btn_frame, text="📋 Copy Exploit", bg=self.accent, fg="white", relief=tk.FLAT, command=self.copy_exploit)
        self.copy_btn.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        
        self.view_report_btn = tk.Button(btn_frame, text="📄 View Full Report", bg=self.success, fg="white", relief=tk.FLAT, command=self.view_report, state=tk.DISABLED)
        self.view_report_btn.pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=(5, 0))
        
    def create_input_field(self, parent, label_text, variable, placeholder):
        frame = tk.Frame(parent, bg=self.bg_medium)
        frame.pack(pady=5, padx=15, fill=tk.X)
        tk.Label(frame, text=label_text, font=("Segoe UI", 9, "bold"), bg=self.bg_medium, fg=self.text_color).pack(anchor=tk.W)
        entry = tk.Entry(frame, textvariable=variable, font=("Segoe UI", 9), bg=self.bg_dark, fg=self.text_color, relief=tk.FLAT, insertbackground="white")
        entry.pack(fill=tk.X, ipady=3)
        entry.insert(0, placeholder)
        
    def create_slider_field(self, parent, label_text, variable, from_, to, default):
        frame = tk.Frame(parent, bg=self.bg_medium)
        frame.pack(pady=5, padx=15, fill=tk.X)
        tk.Label(frame, text=label_text, font=("Segoe UI", 9, "bold"), bg=self.bg_medium, fg=self.text_color).pack(anchor=tk.W)
        tk.Scale(frame, from_=from_, to=to, orient=tk.HORIZONTAL, variable=variable, bg=self.bg_medium, fg=self.text_color, troughcolor=self.bg_dark, showvalue=True, highlightthickness=0).pack(fill=tk.X)
        variable.set(default)

    def create_model_selector(self, parent):
        frame = tk.Frame(parent, bg=self.bg_medium)
        frame.pack(pady=5, padx=15, fill=tk.X)
        tk.Label(frame, text="🤖 AI Model:", font=("Segoe UI", 9, "bold"), bg=self.bg_medium, fg=self.text_color).pack(anchor=tk.W)
        self.model_combo = ttk.Combobox(frame, textvariable=self.model_path, state="readonly")
        self.model_combo.pack(fill=tk.X)

    def load_available_models(self):
        models = []
        if os.path.exists("dqn_web_sec_model.pth"):
            models.append("dqn_web_sec_model.pth (Final)")
        checkpoints = glob.glob("checkpoints/dqn_checkpoint_ep*.pth")
        for cp in sorted(checkpoints, reverse=True):
            models.append(cp)
        if models:
            self.model_combo['values'] = models
            self.model_combo.current(0)
        else:
            self.model_combo['values'] = ["No models found"]
            self.model_combo.current(0)

    def log(self, message, level="INFO"):
        timestamp = datetime.now().strftime("%H:%M:%S")
        prefix = "✅" if level == "SUCCESS" else "❌" if level == "ERROR" else "⚠️" if level == "WARNING" else "ℹ️"
        self.output_text.insert(tk.END, f"[{timestamp}] {prefix} {message}\n")
        self.output_text.see(tk.END)
        
    def add_finding(self, finding):
        """Add a finding to the listbox"""
        self.findings.append(finding)
        display_text = f"{finding.get('type', 'Vuln')} - {finding.get('url', 'URL')}"
        self.findings_list.insert(tk.END, display_text)
        self.findings_list.see(tk.END)
        
    def on_finding_select(self, event):
        """Handle selection of a finding"""
        selection = self.findings_list.curselection()
        if not selection:
            return
            
        index = selection[0]
        finding = self.findings[index]
        
        # Generate Exploit Content
        content = f"""# 🚨 VULNERABILITY DETECTED
Type: {finding.get('type')}
URL:  {finding.get('url')}
Payload: {finding.get('payload')}

# 🛠️ HOW TO EXPLOIT
{ExploitGenerator.get_steps(finding)}

# 💻 CURL COMMAND
{ExploitGenerator.generate_curl(finding)}

# 🐍 PYTHON EXPLOIT SCRIPT
{ExploitGenerator.generate_python(finding)}
"""
        self.exploit_text.delete(1.0, tk.END)
        self.exploit_text.insert(tk.END, content)
        
    def copy_exploit(self):
        content = self.exploit_text.get(1.0, tk.END)
        self.root.clipboard_clear()
        self.root.clipboard_append(content)
        messagebox.showinfo("Copied", "Exploit details copied to clipboard!")

    def start_scan(self):
        target = self.target_url.get().strip()
        if not target: return
        if not target.startswith(('http://', 'https://')): target = 'http://' + target
        
        model = self.model_path.get().split(" (")[0]
        
        self.scan_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        self.is_scanning = True
        self.progress.start(10)
        self.output_text.delete(1.0, tk.END)
        self.findings_list.delete(0, tk.END)
        self.findings = []
        self.exploit_text.delete(1.0, tk.END)
        self.exploit_text.insert(tk.END, "// Scanning in progress... Vulnerabilities will appear here.")
        
        threading.Thread(target=self.run_scan, args=(target, model), daemon=True).start()

    def run_scan(self, target, model):
        try:
            self.log(f"Starting scan on {target}", "INFO")
            auditor = SecurityAuditor(target, model)
            
            # Monkey patch the auditor's log_finding to update GUI in real-time
            original_log_finding = auditor.log_finding
            
            def gui_log_finding(finding):
                original_log_finding(finding)
                self.root.after(0, lambda: self.add_finding(finding))
                self.root.after(0, lambda: self.log(f"FOUND: {finding.get('type')} at {finding.get('url')}", "WARNING"))
            
            auditor.log_finding = gui_log_finding
            
            findings = auditor.start_audit(crawl_depth=self.crawl_depth.get(), test_intensity=self.test_episodes.get())
            
            self.root.after(0, lambda: self.scan_complete(len(findings)))
            
        except Exception as e:
            self.root.after(0, lambda: self.log(f"Error: {str(e)}", "ERROR"))
            self.root.after(0, lambda: self.stop_scan())

    def scan_complete(self, count):
        self.log(f"Scan complete! Found {count} vulnerabilities", "SUCCESS")
        self.progress.stop()
        self.scan_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        self.view_report_btn.config(state=tk.NORMAL)
        self.is_scanning = False
        messagebox.showinfo("Scan Complete", f"Found {count} vulnerabilities!\nClick on them in the list to generate exploits.")

    def stop_scan(self):
        self.is_scanning = False
        self.progress.stop()
        self.scan_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        self.log("Scan stopped", "WARNING")

    def view_report(self):
        reports = glob.glob("reports/vulnerability_report_*.html")
        if reports:
            latest = max(reports, key=os.path.getctime)
            os.startfile(latest)

def main():
    # Argument parsing for automated mode (kept from previous version)
    parser = argparse.ArgumentParser(description='AI-Powered Web Security Scanner')
    parser.add_argument('--auto', action='store_true', help='Run in automated mode')
    parser.add_argument('--target', type=str, help='Target URL')
    parser.add_argument('--depth', type=int, default=30, help='Crawl depth')
    parser.add_argument('--episodes', type=int, default=3, help='Test episodes')
    parser.add_argument('--model', type=str, default='dqn_web_sec_model.pth', help='Model file')
    args = parser.parse_args()
    
    if args.auto:
        # ... (Automated mode logic - simplified for brevity as GUI is focus)
        print("Starting automated scan...")
        from autonomous_scan import SecurityAuditor
        agent = SecurityAuditor(args.target, args.model)
        agent.start_audit(crawl_depth=args.depth, test_intensity=args.episodes)
    else:
        root = tk.Tk()
        app = SecurityScannerGUI(root)
        root.mainloop()

if __name__ == "__main__":
    main()


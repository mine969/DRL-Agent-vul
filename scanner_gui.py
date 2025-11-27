"""
AI-Powered Web Security Scanner - GUI Application
=================================================

Modern, accessible GUI for the security scanner with:
- Cyberpunk/Red Team Aesthetic
- Real-time logs & Progress tracking
- ONE-CLICK FLASH ATTACK
- Exploit Generation
- Report Management

Usage:
    python scanner_gui.py
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
            separator = '&' if '?' in url else '?'
            if '=' in payload:
                full_url = f"{url}{separator}{payload}"
            else:
                full_url = f"{url}{separator}{param}={payload}"
            return f"curl -v '{full_url}'"
        
        elif method == 'POST':
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
                script += f"""
full_url = f"{{target_url}}?{{payload}}" if "?" not in target_url else f"{{target_url}}&{{payload}}"
response = requests.get(full_url)
"""
            else:
                script += f"""
params = {{'{param}': payload}}
response = requests.get(target_url, params=params)
"""
        elif method == 'POST':
            script += f"""
data = payload 
response = requests.post(target_url, data=data, headers={{'Content-Type': 'application/x-www-form-urlencoded'}})
"""
        script += """
print(f"[*] Status Code: {response.status_code}")
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
            'SQL': [
                "1. Identify the vulnerable parameter.",
                "2. Inject SQL payload to manipulate query.",
                "3. Check for database errors or data leakage.",
                "4. Dump database with UNION SELECT."
            ],
            'XSS': [
                "1. Find reflection point.",
                "2. Inject script payload.",
                "3. Verify execution (alert box).",
                "4. Steal cookies or redirect users."
            ],
            'OSINT': [
                "1. Analyze the exposed file.",
                "2. Look for secrets, keys, or config data.",
                "3. Use data to pivot to other systems."
            ],
            'Upload': [
                "1. Upload a malicious file (e.g., PHP shell).",
                "2. Access the file via the web server.",
                "3. Execute commands on the server."
            ]
        }
        
        for key in steps:
            if key.lower() in v_type.lower():
                return "\n".join(steps[key])
                
        return "1. Analyze request.\n2. Replay with payload.\n3. Verify impact.\n4. Report finding."

class SecurityScannerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("💀 DRL AI RED TEAM - AUTONOMOUS ATTACKER")
        self.root.geometry("1280x850")
        self.root.minsize(1100, 750)
        
        # Cyberpunk / Red Team Theme
        self.colors = {
            "bg_dark": "#0a0a0a",      # Pitch Black
            "bg_panel": "#111111",     # Very Dark Grey
            "accent": "#00ff00",       # Hacker Green
            "accent_dim": "#008f00",   # Dim Green
            "text": "#00ff00",         # Green Text
            "text_dim": "#aaaaaa",     # Grey Text
            "danger": "#ff0000",       # Red
            "warning": "#ffaa00",      # Orange
            "highlight": "#222222"     # Highlight
        }
        
        self.root.configure(bg=self.colors["bg_dark"])
        
        # Variables
        self.target_url = tk.StringVar()
        self.crawl_depth = tk.IntVar(value=30)
        self.test_episodes = tk.IntVar(value=3)
        self.model_path = tk.StringVar(value="dqn_web_sec_model.pth")
        self.scan_mode = tk.StringVar(value="auto")
        self.specific_attack_type = tk.StringVar()
        
        self.setup_ui()
        self.load_available_models()
        
    def setup_ui(self):
        """Setup the Cyberpunk UI"""
        
        # Custom Style for Progress Bar
        style = ttk.Style()
        style.theme_use('clam')
        style.configure("Horizontal.TProgressbar", foreground=self.colors['accent'], background=self.colors['accent'], troughcolor=self.colors['bg_panel'], bordercolor=self.colors['bg_panel'], lightcolor=self.colors['accent'], darkcolor=self.colors['accent'])
        
        # Header
        header_frame = tk.Frame(self.root, bg=self.colors["bg_dark"], height=80)
        header_frame.pack(fill=tk.X, padx=0, pady=0)
        header_frame.pack_propagate(False)
        
        title_label = tk.Label(
            header_frame,
            text="💀 DRL AI RED TEAM",
            font=("Courier New", 24, "bold"),
            bg=self.colors["bg_dark"],
            fg=self.colors["danger"]
        )
        title_label.pack(pady=(20, 5))
        
        subtitle_label = tk.Label(
            header_frame,
            text="AUTONOMOUS VULNERABILITY SCANNER & EXPLOITER",
            font=("Courier New", 10, "bold"),
            bg=self.colors["bg_dark"],
            fg=self.colors["text_dim"]
        )
        subtitle_label.pack(pady=0)
        
        # Main Layout
        main_pane = tk.PanedWindow(self.root, bg=self.colors["bg_dark"], orient=tk.HORIZONTAL, sashwidth=4, sashrelief=tk.FLAT)
        main_pane.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # === LEFT: MISSION CONTROL ===
        left_panel = tk.Frame(main_pane, bg=self.colors["bg_panel"], width=320)
        main_pane.add(left_panel, minsize=300)
        
        self.add_section_header(left_panel, "🎯 MISSION PARAMETERS")
        
        self.create_input_field(left_panel, "TARGET URL:", self.target_url, "localhost:5001")
        self.create_slider_field(left_panel, "CRAWL DEPTH:", self.crawl_depth, 1, 100, 30)
        self.create_slider_field(left_panel, "ATTACK INTENSITY:", self.test_episodes, 1, 10, 3)
        self.create_model_selector(left_panel)
        
        # SCAN MODES
        self.add_section_header(left_panel, "⚙️ SCAN MODE")
        
        modes_frame = tk.Frame(left_panel, bg=self.colors["bg_panel"])
        modes_frame.pack(fill=tk.X, padx=15, pady=5)
        
        tk.Radiobutton(modes_frame, text="🤖 FULL AUTO (AI AGENT)", variable=self.scan_mode, value="auto", bg=self.colors["bg_panel"], fg=self.colors["text"], selectcolor=self.colors["bg_dark"], activebackground=self.colors["bg_panel"], activeforeground=self.colors["accent"], font=("Consolas", 9), command=self.toggle_attack_selector).pack(anchor=tk.W)
        tk.Radiobutton(modes_frame, text="🕵️ SUPER OSINT MODE", variable=self.scan_mode, value="osint", bg=self.colors["bg_panel"], fg=self.colors["text"], selectcolor=self.colors["bg_dark"], activebackground=self.colors["bg_panel"], activeforeground=self.colors["accent"], font=("Consolas", 9), command=self.toggle_attack_selector).pack(anchor=tk.W)
        tk.Radiobutton(modes_frame, text="🎯 SPECIFIC ATTACK", variable=self.scan_mode, value="specific", bg=self.colors["bg_panel"], fg=self.colors["text"], selectcolor=self.colors["bg_dark"], activebackground=self.colors["bg_panel"], activeforeground=self.colors["accent"], font=("Consolas", 9), command=self.toggle_attack_selector).pack(anchor=tk.W)
        
        # Attack Selector (Hidden by default)
        self.attack_frame = tk.Frame(left_panel, bg=self.colors["bg_panel"])
        self.attack_frame.pack(fill=tk.X, padx=15, pady=5)
        tk.Label(self.attack_frame, text="ATTACK TYPE:", font=("Courier New", 9, "bold"), bg=self.colors["bg_panel"], fg=self.colors["text"]).pack(anchor=tk.W)
        self.attack_combo = ttk.Combobox(self.attack_frame, textvariable=self.specific_attack_type, state="readonly")
        self.attack_combo['values'] = ["SQL Injection", "XSS", "SSRF", "Command Injection", "LFI", "RFI", "Broken Access Control", "XXE"]
        self.attack_combo.current(0)
        self.attack_combo.pack(fill=tk.X)
        self.attack_combo.config(state=tk.DISABLED)
        
        tk.Frame(left_panel, bg=self.colors["bg_panel"], height=10).pack() # Spacer
        
        # ONE CLICK BUTTONS
        self.flash_btn = tk.Button(left_panel, text="⚡ FLASH ATTACK (ONE-CLICK)", font=("Courier New", 12, "bold"), bg=self.colors["accent"], fg="black", activebackground="white", activeforeground="black", relief=tk.FLAT, cursor="hand2", command=self.flash_attack, height=2)
        self.flash_btn.pack(pady=5, padx=15, fill=tk.X)
        
        self.scan_button = tk.Button(left_panel, text="🚀 LAUNCH SCAN", font=("Courier New", 11, "bold"), bg=self.colors["highlight"], fg=self.colors["accent"], relief=tk.FLAT, cursor="hand2", command=self.start_scan, height=2)
        self.scan_button.pack(pady=5, padx=15, fill=tk.X)
        
        self.stop_button = tk.Button(left_panel, text="⏹️ ABORT MISSION", font=("Courier New", 11, "bold"), bg=self.colors["danger"], fg="white", relief=tk.FLAT, cursor="hand2", command=self.stop_scan, height=2, state=tk.DISABLED)
        self.stop_button.pack(pady=(5, 15), padx=15, fill=tk.X)
        
        # === MIDDLE: TERMINAL & INTEL ===
        middle_panel = tk.Frame(main_pane, bg=self.colors["bg_panel"])
        main_pane.add(middle_panel, minsize=400)
        
        self.add_section_header(middle_panel, "📟 LIVE TERMINAL LOGS")
        
        self.progress = ttk.Progressbar(middle_panel, mode='indeterminate', style="Horizontal.TProgressbar")
        self.progress.pack(pady=5, padx=15, fill=tk.X)
        
        self.output_text = scrolledtext.ScrolledText(middle_panel, wrap=tk.WORD, font=("Consolas", 9), bg="black", fg=self.colors["text"], relief=tk.FLAT, height=15, insertbackground=self.colors["accent"])
        self.output_text.pack(pady=10, padx=15, fill=tk.BOTH, expand=True)
        
        self.add_section_header(middle_panel, "🚨 DETECTED VULNERABILITIES")
        
        self.findings_list = tk.Listbox(middle_panel, font=("Consolas", 10), bg="black", fg=self.colors["warning"], selectbackground=self.colors["accent"], selectforeground="black", relief=tk.FLAT, height=10)
        self.findings_list.pack(pady=10, padx=15, fill=tk.BOTH, expand=True)
        self.findings_list.bind('<<ListboxSelect>>', self.on_finding_select)
        
        # === RIGHT: WEAPONIZATION ===
        right_panel = tk.Frame(main_pane, bg=self.colors["bg_panel"])
        main_pane.add(right_panel, minsize=350)
        
        self.add_section_header(right_panel, "💣 EXPLOIT FACTORY")
        
        self.exploit_text = scrolledtext.ScrolledText(right_panel, wrap=tk.WORD, font=("Consolas", 10), bg="black", fg=self.colors["danger"], relief=tk.FLAT, insertbackground="white")
        self.exploit_text.pack(pady=10, padx=15, fill=tk.BOTH, expand=True)
        self.exploit_text.insert(tk.END, "// Select a vulnerability to generate exploit payload...")
        
        btn_frame = tk.Frame(right_panel, bg=self.colors["bg_panel"])
        btn_frame.pack(pady=10, padx=15, fill=tk.X)
        
        self.copy_btn = tk.Button(btn_frame, text="📋 COPY PAYLOAD", bg=self.colors["highlight"], fg="white", relief=tk.FLAT, command=self.copy_exploit)
        self.copy_btn.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        
        self.view_report_btn = tk.Button(btn_frame, text="📄 OPEN REPORT", bg=self.colors["highlight"], fg="white", relief=tk.FLAT, command=self.view_report, state=tk.DISABLED)
        self.view_report_btn.pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=(5, 0))

    def toggle_attack_selector(self):
        if self.scan_mode.get() == "specific":
            self.attack_combo.config(state="readonly")
        else:
            self.attack_combo.config(state=tk.DISABLED)

    def add_section_header(self, parent, text):
        tk.Label(parent, text=text, font=("Courier New", 12, "bold"), bg=self.colors["bg_panel"], fg=self.colors["text_dim"]).pack(pady=(15, 5), padx=15, anchor=tk.W)

    def create_input_field(self, parent, label_text, variable, placeholder):
        frame = tk.Frame(parent, bg=self.colors["bg_panel"])
        frame.pack(pady=5, padx=15, fill=tk.X)
        tk.Label(frame, text=label_text, font=("Courier New", 9, "bold"), bg=self.colors["bg_panel"], fg=self.colors["text"]).pack(anchor=tk.W)
        entry = tk.Entry(frame, textvariable=variable, font=("Consolas", 10), bg="black", fg="white", relief=tk.FLAT, insertbackground="white")
        entry.pack(fill=tk.X, ipady=5)
        entry.insert(0, placeholder)

    def create_slider_field(self, parent, label_text, variable, from_, to, default):
        frame = tk.Frame(parent, bg=self.colors["bg_panel"])
        frame.pack(pady=5, padx=15, fill=tk.X)
        tk.Label(frame, text=label_text, font=("Courier New", 9, "bold"), bg=self.colors["bg_panel"], fg=self.colors["text"]).pack(anchor=tk.W)
        tk.Scale(frame, from_=from_, to=to, orient=tk.HORIZONTAL, variable=variable, bg=self.colors["bg_panel"], fg=self.colors["accent"], troughcolor="black", showvalue=True, highlightthickness=0).pack(fill=tk.X)
        variable.set(default)

    def create_model_selector(self, parent):
        frame = tk.Frame(parent, bg=self.colors["bg_panel"])
        frame.pack(pady=5, padx=15, fill=tk.X)
        tk.Label(frame, text="BRAIN MODEL:", font=("Courier New", 9, "bold"), bg=self.colors["bg_panel"], fg=self.colors["text"]).pack(anchor=tk.W)
        
        combo_frame = tk.Frame(frame, bg=self.colors["bg_panel"])
        combo_frame.pack(fill=tk.X)
        
        self.model_combo = ttk.Combobox(combo_frame, textvariable=self.model_path, state="readonly")
        self.model_combo.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        browse_btn = tk.Button(combo_frame, text="📂", font=("Consolas", 8), command=self.browse_model, bg=self.colors["highlight"], fg="white", relief=tk.FLAT, width=3)
        browse_btn.pack(side=tk.RIGHT, padx=(5, 0))

    def browse_model(self):
        filename = filedialog.askopenfilename(initialdir="checkpoints", title="Select Model File", filetypes=(("PyTorch Models", "*.pth"), ("All Files", "*.*")))
        if filename:
            self.model_path.set(filename)

    def load_available_models(self):
        models = []
        if os.path.exists("dqn_web_sec_model.pth"):
            models.append("dqn_web_sec_model.pth (Final)")
        checkpoints = glob.glob("checkpoints/dqn_checkpoint_ep*.pth") + glob.glob("checkpoints/multi_target_*.pth")
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
        prefix = "[+]" if level == "SUCCESS" else "[-]" if level == "ERROR" else "[!]" if level == "WARNING" else "[*]"
        color = self.colors["accent"] if level == "SUCCESS" else self.colors["danger"] if level == "ERROR" else self.colors["warning"] if level == "WARNING" else self.colors["text_dim"]
        
        self.output_text.tag_config(level, foreground=color)
        self.output_text.insert(tk.END, f"{prefix} {timestamp} {message}\n", level)
        self.output_text.see(tk.END)

    def add_finding(self, finding):
        self.findings.append(finding)
        display_text = f"[{finding.get('type', 'Vuln')}] {finding.get('url', 'URL')}"
        self.findings_list.insert(tk.END, display_text)
        self.findings_list.see(tk.END)

    def on_finding_select(self, event):
        selection = self.findings_list.curselection()
        if not selection: return
        index = selection[0]
        finding = self.findings[index]
        
        content = f"""# 🚨 VULNERABILITY DETECTED
Type: {finding.get('type')}
URL:  {finding.get('url')}
Payload: {finding.get('payload')}

# 🛠️ ATTACK VECTOR
{ExploitGenerator.get_steps(finding)}

# 💻 CURL EXPLOIT
{ExploitGenerator.generate_curl(finding)}

# 🐍 PYTHON EXPLOIT
{ExploitGenerator.generate_python(finding)}
"""
        self.exploit_text.delete(1.0, tk.END)
        self.exploit_text.insert(tk.END, content)

    def copy_exploit(self):
        content = self.exploit_text.get(1.0, tk.END)
        self.root.clipboard_clear()
        self.root.clipboard_append(content)
        messagebox.showinfo("COPIED", "Exploit payload copied to clipboard.")

    def flash_attack(self):
        """One-Click Attack Mode"""
        self.crawl_depth.set(10)
        self.test_episodes.set(1)
        self.scan_mode.set("auto")
        self.start_scan()

    def start_scan(self):
        target = self.target_url.get().strip()
        if not target: return
        if not target.startswith(('http://', 'https://')): target = 'http://' + target
        
        model_selection = self.model_path.get()
        if " (Final)" in model_selection:
            model = model_selection.replace(" (Final)", "")
        else:
            model = model_selection
            
        mode = self.scan_mode.get()
        specific_attack = self.specific_attack_type.get() if mode == "specific" else None
        
        self.scan_button.config(state=tk.DISABLED)
        self.flash_btn.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        self.is_scanning = True
        self.progress.start(10)
        self.output_text.delete(1.0, tk.END)
        self.findings_list.delete(0, tk.END)
        self.findings = []
        self.exploit_text.delete(1.0, tk.END)
        self.exploit_text.insert(tk.END, "// Scanning target... Awaiting findings...")
        
        threading.Thread(target=self.run_scan, args=(target, model, mode, specific_attack), daemon=True).start()

    def run_scan(self, target, model, mode, specific_attack):
        # Redirect stdout to GUI
        class StdoutRedirector:
            def __init__(self, text_widget):
                self.text_widget = text_widget
            def write(self, string):
                self.text_widget.after(0, lambda: self.text_widget.insert(tk.END, string))
                self.text_widget.after(0, lambda: self.text_widget.see(tk.END))
            def flush(self):
                pass
                
        old_stdout = sys.stdout
        sys.stdout = StdoutRedirector(self.output_text)
        
        try:
            self.log(f"INITIATING ATTACK SEQUENCE ON {target}", "INFO")
            self.log(f"MODE: {mode.upper()} | MODEL: {os.path.basename(model)}", "INFO")
            
            auditor = SecurityAuditor(target, model)
            
            # Hook the log_finding callback
            original_log_finding = auditor.log_finding
            def gui_log_finding(finding):
                original_log_finding(finding)
                self.root.after(0, lambda: self.add_finding(finding))
                self.root.after(0, lambda: self.log(f"VULNERABILITY CONFIRMED: {finding.get('type')}", "WARNING"))
            
            auditor.log_finding = gui_log_finding
            
            findings = auditor.start_audit(
                crawl_depth=self.crawl_depth.get(), 
                test_intensity=self.test_episodes.get(),
                scan_mode=mode,
                specific_attack=specific_attack
            )
            
            self.root.after(0, lambda: self.scan_complete(len(findings)))
            
        except Exception as e:
            self.root.after(0, lambda: self.log(f"SYSTEM ERROR: {str(e)}", "ERROR"))
            self.root.after(0, lambda: self.stop_scan())
        finally:
            sys.stdout = old_stdout

    def scan_complete(self, count):
        self.log(f"MISSION COMPLETE. {count} TARGETS COMPROMISED.", "SUCCESS")
        self.progress.stop()
        self.scan_button.config(state=tk.NORMAL)
        self.flash_btn.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        self.view_report_btn.config(state=tk.NORMAL)
        self.is_scanning = False
        messagebox.showinfo("MISSION COMPLETE", f"Scan finished.\nFound {count} vulnerabilities.")

    def stop_scan(self):
        self.is_scanning = False
        self.progress.stop()
        self.scan_button.config(state=tk.NORMAL)
        self.flash_btn.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        self.log("MISSION ABORTED BY USER", "WARNING")

    def view_report(self):
        reports = glob.glob("reports/vulnerability_report_*.html")
        if reports:
            latest = max(reports, key=os.path.getctime)
            os.startfile(latest)

if __name__ == "__main__":
    root = tk.Tk()
    app = SecurityScannerGUI(root)
    root.mainloop()

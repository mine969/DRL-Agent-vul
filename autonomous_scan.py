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
import random
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
import time

# Import internal modules
from agent.dqn_agent import DQNAgent
from env.web_sec_env import WebSecEnv
from utils.report_generator import ReportGenerator
from utils.vulnerability_database import VULNERABILITY_DATABASE
from utils.zero_day_hunter import ZeroDayHunter
from utils.target_hunter import TargetHunter

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


class ProxyRotator:
    """
    Rotates through a list of proxies to avoid IP bans.
    """
    def __init__(self, proxy_list: List[str] = None):
        self.proxy_list = proxy_list or []
        self.current_index = 0
        
    def get_next_proxy(self) -> Optional[Dict[str, str]]:
        """Get the next proxy in rotation."""
        if not self.proxy_list:
            return None
        
        proxy = self.proxy_list[self.current_index]
        self.current_index = (self.current_index + 1) % len(self.proxy_list)
        
        return {
            'http': proxy,
            'https': proxy
        }
    
    def add_proxy(self, proxy: str):
        """Add a proxy to the rotation list."""
        self.proxy_list.append(proxy)


class RequestObfuscator:
    """
    Advanced request obfuscation to avoid pattern detection.
    """
    
    COMMON_REFERRERS = [
        'https://www.google.com/search?q=',
        'https://www.bing.com/search?q=',
        'https://duckduckgo.com/?q=',
        'https://www.facebook.com/',
        'https://twitter.com/',
        'https://www.linkedin.com/',
        'https://www.reddit.com/',
    ]
    
    def __init__(self, stealth_level: str = "medium"):
        """
        stealth_level: low, medium, high, paranoid
        """
        self.stealth_level = stealth_level
        self.delays = {
            'low': (0.1, 0.5),
            'medium': (0.5, 2.0),
            'high': (1.0, 5.0),
            'paranoid': (5.0, 15.0)
        }
    
    def shuffle_urls(self, urls: List[str]) -> List[str]:
        """Randomize URL order to avoid sequential scanning patterns."""
        shuffled = urls.copy()
        random.shuffle(shuffled)
        return shuffled
    
    def get_fake_referrer(self, target_url: str = None) -> str:
        """Generate a believable referrer header."""
        referrer = random.choice(self.COMMON_REFERRERS)
        
        if target_url and 'google.com' in referrer:
            # Make it look like we came from a Google search
            domain = urlparse(target_url).netloc
            referrer += domain.replace('www.', '')
        
        return referrer
    
    def get_delay(self) -> float:
        """Get randomized delay based on stealth level."""
        min_delay, max_delay = self.delays.get(self.stealth_level, (0.5, 2.0))
        return random.uniform(min_delay, max_delay)
    
    def add_noise_to_request(self, kwargs: dict):
        """Add random noise to request to vary fingerprint."""
        if 'headers' not in kwargs:
            kwargs['headers'] = {}
        
        # Random Accept-Language
        languages = ['en-US,en;q=0.9', 'en-GB,en;q=0.9', 'en-US,en;q=0.5']
        kwargs['headers']['Accept-Language'] = random.choice(languages)
        
        # Random DNT header (sometimes omit it)
        if random.random() > 0.5:
            kwargs['headers']['DNT'] = '1'
        
        # Fake referrer
        kwargs['headers']['Referer'] = self.get_fake_referrer()
        
        # Vary Accept header slightly
        accept_headers = [
            'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8'
        ]
        kwargs['headers']['Accept'] = random.choice(accept_headers)


class OptimizedSession:
    """
    A high-performance HTTP session with IP rotation and stealth features.
    """
    
    USER_AGENTS = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15',
    ]
    
    def __init__(self, pool_connections: int = 10, pool_maxsize: int = 20, 
                 use_proxies: bool = False, proxy_list: List[str] = None,
                 stealth_level: str = "medium"):
        self.session = requests.Session()
        self.use_proxies = use_proxies
        self.proxy_rotator = ProxyRotator(proxy_list) if use_proxies else None
        self.obfuscator = RequestObfuscator(stealth_level)
        
        # Retry logic
        retry_strategy = Retry(
            total=3,
            backoff_factor=0.3,
            status_forcelist=[429, 500, 502, 503, 504]
        )
        
        adapter = HTTPAdapter(
            pool_connections=pool_connections,
            pool_maxsize=pool_maxsize,
            max_retries=retry_strategy
        )
        
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
        self.timeout = 5
    
    def _get_random_headers(self) -> Dict[str, str]:
        """Generate randomized headers to avoid fingerprinting."""
        return {
            'User-Agent': random.choice(self.USER_AGENTS),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        }
    
    def _apply_stealth(self, kwargs: dict):
        """Apply stealth features to the request."""
        # Random User-Agent
        if 'headers' not in kwargs:
            kwargs['headers'] = {}
        kwargs['headers'].update(self._get_random_headers())
        
        # Add obfuscation noise
        self.obfuscator.add_noise_to_request(kwargs)
        
        # Proxy rotation
        if self.use_proxies and self.proxy_rotator:
            proxy = self.proxy_rotator.get_next_proxy()
            if proxy:
                kwargs['proxies'] = proxy
        
        # Stealth-level delay
        delay = self.obfuscator.get_delay()
        time.sleep(delay)
    
    def get(self, url: str, **kwargs) -> requests.Response:
        """Send a GET request with stealth features."""
        kwargs.setdefault('timeout', self.timeout)
        self._apply_stealth(kwargs)
        return self.session.get(url, **kwargs)

    def post(self, url: str, **kwargs) -> requests.Response:
        """Send a POST request with stealth features."""
        kwargs.setdefault('timeout', self.timeout)
        self._apply_stealth(kwargs)
        return self.session.post(url, **kwargs)
    
    def close(self):
        """Close the session."""
        self.session.close()


class WaybackMachine:
    """
    Integrates with Archive.org to find historical URLs.
    """
    def __init__(self, domain):
        self.domain = domain
        self.cdx_api = "http://web.archive.org/cdx/search/cdx"
        
    def get_historical_urls(self, limit=500):
        print(f"🌍 Querying Wayback Machine for {self.domain}...")
        params = {
            'url': f'*.{self.domain}/*',
            'collapse': 'urlkey',
            'output': 'json',
            'fl': 'original',
            'limit': limit,
            'filter': 'statuscode:200'
        }
        
        try:
            response = requests.get(self.cdx_api, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                if data:
                    # Skip header row
                    urls = [row[0] for row in data[1:]]
                    print(f"  ✅ Wayback Machine found {len(urls)} historical URLs")
                    return urls
            return []
        except Exception as e:
            print(f"  ⚠️ Wayback Machine error: {e}")
            return []

class WebsiteExplorer:
    """
    Responsible for Reconnaissance (Phase 1).
    Its job is to find all the pages on the website so we know what to attack.
    """
    
    def __init__(self, base_url: str, use_proxies: bool = False, proxy_list: List[str] = None, stealth_level: str = "medium"):
        self.base_url = base_url.rstrip('/')
        self.domain = urlparse(base_url).netloc
        self.discovered_urls: Set[str] = set()
        self.session = OptimizedSession(use_proxies=use_proxies, proxy_list=proxy_list, stealth_level=stealth_level)
        self.wayback = WaybackMachine(self.domain)
        self.obfuscator = RequestObfuscator(stealth_level)
        
    def scan_ports(self, ports: List[int] = None) -> List[str]:
        """
        Scans common web ports to find hidden services.
        """
        if ports is None:
            # Common web ports
            ports = [80, 443, 8080, 8443, 8000, 8008, 8888, 3000, 5000, 9000, 9200, 9443]
            
        print(f"🔌 Scanning {len(ports)} common ports on {self.domain}...")
        open_services = []
        
        import socket
        
        for port in ports:
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(1.0) # Fast timeout
                result = sock.connect_ex((self.domain, port))
                sock.close()
                
                if result == 0:
                    # Port is open, try to determine protocol
                    protocols = []
                    if port in [443, 8443, 9443]:
                        protocols = ["https"]
                    elif port in [80, 8080, 8000, 3000, 5000]:
                        protocols = ["http"]
                    else:
                        protocols = ["http", "https"]
                        
                    for proto in protocols:
                        url = f"{proto}://{self.domain}:{port}"
                        open_services.append(url)
                        print(f"  ✨ Found open service: {url}")
                        
            except Exception:
                pass
                
        return open_services

    def explore(self, max_pages: int = 50, auto_login: bool = True) -> List[str]:
        """
        Crawls the website to discover pages.
        """
        print(f"🕷️  Starting reconnaissance on: {self.base_url}")
        print(f"🎯 Target domain: {self.domain}\n")
        
        # --- PORT SCANNING ---
        # Check for other open ports first
        if "localhost" not in self.domain and "127.0.0.1" not in self.domain:
            found_services = self.scan_ports()
            for service in found_services:
                self.discovered_urls.add(service)
        
        # Try to authenticate first
        if auto_login:
            self.attempt_login()
            print()  # Blank line for readability
        
        # Queue: The list of pages we need to visit
        pages_to_visit: deque = deque([self.base_url])
        
        # Add discovered services to queue
        if "localhost" not in self.domain and "127.0.0.1" not in self.domain:
            for service in found_services:
                if service not in pages_to_visit:
                    pages_to_visit.append(service)
        
        visited_pages: Set[str] = set()
        
        # --- WAYBACK MACHINE INTEGRATION ---
        # Add historical URLs to the queue
        if "localhost" not in self.domain and "127.0.0.1" not in self.domain:
            historical_urls = self.wayback.get_historical_urls()
            for url in historical_urls:
                # Only add if it matches our domain
                if self.domain in url:
                    pages_to_visit.append(url)
                    self.discovered_urls.add(url)
        
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
        
        # Shuffle URLs to avoid sequential scanning pattern
        discovered_list = list(self.discovered_urls)
        return self.obfuscator.shuffle_urls(discovered_list)
    
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
    
    def __init__(self, base_url: str, model_path: str = "dqn_web_sec_model.pth", 
                 use_proxies: bool = False, proxy_list: List[str] = None,
                 stealth_level: str = "medium"):
        self.base_url = base_url
        self.explorer = WebsiteExplorer(base_url, use_proxies=use_proxies, proxy_list=proxy_list, stealth_level=stealth_level)
        
        # Initialize the AI Brain
        # State Dim 11: The agent sees 11 different things about the page
        # Action Dim 100: The agent can perform 100 different actions (Kill Chain Architecture)
        self.ai_agent = DQNAgent(state_dim=11, action_dim=100)
        
        self._load_ai_brain(model_path)
        
        # Initialize environment once to get the action book
        temp_env = WebSecEnv(target_url=base_url)
        self.action_map = {k: v.__name__ for k, v in temp_env.action_book.items()}
        
        # Store config for logging
        self.use_proxies = use_proxies
        self.proxy_count = len(proxy_list) if proxy_list else 0
        self.stealth_level = stealth_level
        self.stop_requested = False

    def stop(self):
        """Signal the auditor to stop scanning."""
        self.stop_requested = True


    def log_finding(self, finding):
        """Callback for logging findings (can be overridden by GUI)"""
        pass
    
    def _load_ai_brain(self, model_path):
        """Attempts to load the trained neural network (auto-loads latest checkpoint)."""
        try:
            from utils.model_loader import load_model_smart
            episode = load_model_smart(self.ai_agent, model_path=model_path, auto_checkpoint=True, verbose=True)
            self.ai_agent.brain.eval() # Set to evaluation mode (no learning, just doing)
            self.ai_agent.epsilon = 0.0    # Stop exploring randomly, use learned skills
            if episode > 0:
                print(f"📍 Resumed from Episode: {episode}\n")
        except Exception as e:
            print(f"⚠️  Could not load model")
            print(f"   Error details: {str(e)}")
            print("   The agent will act randomly (Untrained Mode)\n")

    def start_audit(self, crawl_depth: int = 30, test_intensity: int = 3, epsilon: float = 0.1, scan_mode: str = "auto", specific_attack: str = None) -> List[Finding]:
        """
        Runs the full security audit process.
        
        Scan Modes:
        - "auto": Use AI Agent to decide actions (Default)
        Scan Modes:
        - "auto": Use AI Agent to decide actions (Default)
        - "aggressive": High intensity, deeper crawl, more noise
        - "osint": Only perform OSINT actions
        - "specific": Only perform a specific type of attack
        """
        print("=" * 70)
        print(f"🤖 AUTONOMOUS AI SECURITY AUDITOR | MODE: {scan_mode.upper()}")
        if specific_attack:
            print(f"🎯 TARGETING: {specific_attack}")
        if self.use_proxies:
            print(f"🔒 STEALTH MODE: IP Rotation Enabled ({self.proxy_count} proxies)")
        else:
            print(f"⚠️  WARNING: No proxy rotation - Your IP is exposed!")
        print(f"🥷 STEALTH LEVEL: {self.stealth_level.upper()}")
        print("=" * 70)
        
        if scan_mode == "aggressive":
            print(f"🔥 AGGRESSIVE MODE ENGAGED: MAXIMIZING INTENSITY!")
            crawl_depth = int(crawl_depth * 2.0)  # Double depth
            test_intensity = int(test_intensity * 3) # Triple intensity
            epsilon = 0.4 # High random exploration for novel attacks
            
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
            if self.stop_requested:
                print("\n🛑 Scan aborted by user.")
                break
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

            # Zero-Day Hunter Mode
            if scan_mode == "zeroday":
                print(f"  💀 Running Zero-Day Hunter on {url}...")
                hunter = ZeroDayHunter()
                
                # 1. Check Weak Configurations
                print("    🔍 Checking for weak configurations...")
                config_findings = hunter.check_weak_configuration(url)
                for f in config_findings:
                    finding = Finding(
                        url=url + f['endpoint'],
                        vuln_type=f['type'],
                        confidence='High',
                        reward=50.0,
                        payload=f.get('description', ''),
                        method='GET'
                    )
                    findings.append(finding)
                    self.log_finding(finding)
                    print(f"      🚨 Found: {f['type']}")

                # 2. Fuzzing
                print("    💣 Fuzzing for anomalies...")
                # Simple fuzzing integration (sending payloads to URL params)
                if "?" in url:
                    base_url_only = url.split("?")[0]
                    params = url.split("?")[1]
                    # Very basic param parsing for demo
                    for param in params.split("&"):
                        if "=" in param:
                            key = param.split("=")[0]
                            
                            # Try a few fuzzing payloads
                            fuzz_payloads = hunter.generate_fuzzing_payloads('buffer_overflow')[:5] # Limit to 5 for speed
                            for payload in fuzz_payloads:
                                try:
                                    # Construct fuzzed URL
                                    fuzzed_url = f"{base_url_only}?{key}={payload}"
                                    # We use the session from explorer if possible, but here we just use requests for simplicity
                                    # In a real integration, we'd use self.explorer.session
                                    resp = requests.get(fuzzed_url, timeout=3)
                                    if resp.status_code >= 500 or resp.elapsed.total_seconds() > 2:
                                        finding = Finding(
                                            url=fuzzed_url,
                                            vuln_type="Potential Zero-Day (Anomaly)",
                                            confidence='Medium',
                                            reward=100.0,
                                            payload=payload,
                                            method='GET'
                                        )
                                        findings.append(finding)
                                        self.log_finding(finding)
                                        print(f"      🚨 Anomaly detected: {resp.status_code} / {resp.elapsed.total_seconds()}s")
                                except:
                                    pass
                return findings

            # Default AUTO mode (AI Agent)
            for _ in range(attempts):
                if self.stop_requested:
                    break
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
    def main():
        # Parse command line arguments
        parser = argparse.ArgumentParser(description='AI-Powered Autonomous Security Scanner')
        parser.add_argument('url', nargs='?', help='Target URL to scan (e.g., http://localhost:5000)')
        parser.add_argument('--depth', type=int, default=30, help='How many pages to crawl (Rec: 30 for new sites, 100+ for deep scan)')
        parser.add_argument('--intensity', type=int, default=3, help='Attack intensity 1-5 (Rec: 2 for new sites, 3 standard, 5 aggressive)')
        parser.add_argument('--model', default='dqn_web_sec_model.pth', help='Path to the trained AI model')
        parser.add_argument("--mode", type=str, default="auto", choices=["auto", "aggressive", "osint", "specific", "zeroday", "targetless"], help="Scan mode")
        parser.add_argument("--attack", type=str, help="Specific attack type (e.g., SQL, XSS)")
        parser.add_argument("--proxy-file", type=str, help="Path to proxy list file")
        parser.add_argument("--stealth", type=str, default="medium", choices=["low", "medium", "high", "paranoid"], help="Stealth level")
        
        # Hunting Arguments
        parser.add_argument("--dork", type=str, help="Google Dork query to find targets")
        parser.add_argument("--shodan-query", type=str, help="Shodan query to find targets")
        parser.add_argument("--shodan-key", type=str, default=os.getenv("SHODAN_API_KEY"), help="Shodan API Key")
        parser.add_argument("--crtsh", type=str, help="Domain to search in CRT.sh")
        parser.add_argument("--duckduckgo", type=str, help="DuckDuckGo query")
        parser.add_argument("--censys-query", type=str, help="Censys query")
        parser.add_argument("--censys-id", type=str, default=os.getenv("CENSYS_API_ID"), help="Censys API ID")
        parser.add_argument("--censys-secret", type=str, default=os.getenv("CENSYS_API_SECRET"), help="Censys API Secret")
        parser.add_argument("--limit", type=int, default=5, help="Max targets to hunt per source")
        
        # AUTO-GENERATE MODE
        parser.add_argument("--auto-generate", action="store_true", help="AUTO-GENERATE MODE: Automatically generate queries for target hunting")
        parser.add_argument("--auto-source", type=str, default="all", choices=["all", "google", "shodan", "crtsh", "duckduckgo", "censys"], help="Source for auto-generation")
        parser.add_argument("--auto-max", type=int, default=3, help="Max queries per source in auto-generate mode")

        args = parser.parse_args()
        
        # --- TARGET HUNTING LOGIC ---
        targets = []
        if args.url:
            targets.append(args.url)
        
        # AUTO-GENERATE MODE
        if args.auto_generate or args.mode == "targetless":
            print(f"\n🤖 AUTO-GENERATE MODE ACTIVATED!")
            hunter = TargetHunter(shodan_api_key=args.shodan_key)
            auto_targets = hunter.auto_generate_targets(source=args.auto_source, max_per_source=args.auto_max)
            targets.extend(auto_targets)
        
        # MANUAL QUERY MODE
        elif args.dork or args.shodan_query or args.crtsh or args.duckduckgo or args.censys_query:
            print(f"\n🌍 STARTING TARGET HUNTING...")
            hunter = TargetHunter(shodan_api_key=args.shodan_key)
            
            if args.dork:
                found = hunter.dork_google(args.dork, num_results=args.limit)
                print(f"  🔍 Google Dork found {len(found)} targets")
                targets.extend(found)
                
            if args.shodan_query:
                found = hunter.search_shodan(args.shodan_query, limit=args.limit)
                print(f"  🌐 Shodan found {len(found)} targets")
                targets.extend(found)
            
            if args.crtsh:
                found = hunter.search_crtsh(args.crtsh)
                print(f"  📜 CRT.sh found {len(found)} subdomains")
                targets.extend(found)
                
            if args.duckduckgo:
                found = hunter.search_duckduckgo(args.duckduckgo, num_results=args.limit)
                print(f"  🦆 DuckDuckGo found {len(found)} targets")
                targets.extend(found)
                
            if args.censys_query:
                found = hunter.search_censys(args.censys_query, args.censys_id, args.censys_secret, limit=args.limit)
                print(f"  👁️ Censys found {len(found)} targets")
                targets.extend(found)
                
            targets = list(set(targets)) # Remove duplicates
            print(f"✅ Total unique targets found: {len(targets)}\n")
            
        if not targets:
            print("❌ No targets specified. Use --url, hunting arguments (--dork, --shodan-query, etc.), or --auto-generate")
            return

        # Load proxies if provided
        proxies = []
        if args.proxy_file:
            try:
                with open(args.proxy_file, 'r') as f:
                    proxies = [line.strip() for line in f if line.strip()]
                print(f"✅ Loaded {len(proxies)} proxies from {args.proxy_file}")
            except Exception as e:
                print(f"❌ Error loading proxies: {e}")

        # --- SCANNING LOOP ---
        for i, target in enumerate(targets):
            print(f"\n{'='*60}")
            print(f"🚀 TARGET {i+1}/{len(targets)}: {target}")
            print(f"{'='*60}")
            
            try:
                auditor = SecurityAuditor(
                    base_url=target,
                    model_path=args.model,
                    use_proxies=bool(proxies),
                    proxy_list=proxies,
                    stealth_level=args.stealth
                )
                
                auditor.start_audit(
                    crawl_depth=args.depth,
                    test_intensity=args.intensity, # Changed from args.episodes to args.intensity
                    scan_mode=args.mode,
                    specific_attack=args.attack
                )
            except Exception as e:
                print(f"❌ Error scanning {target}: {e}")
                continue

    main()

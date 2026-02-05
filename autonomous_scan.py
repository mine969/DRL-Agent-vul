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
import re
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
from agent.improved_dqn_agent import ImprovedDQNAgent
from env.web_sec_env import WebSecEnv
from utils.report_generator import ReportGenerator, Finding
from utils.vulnerability_database import VULNERABILITY_DATABASE
from utils.zero_day_hunter import ZeroDayHunter
from utils.target_hunter import TargetHunter



# Removed ProxyRotator and RequestObfuscator classes - not needed for mock target scanning


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
    
    def __init__(self, pool_connections: int = 10, pool_maxsize: int = 20):
        self.session = requests.Session()
        
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
    
    def _apply_headers(self, kwargs: dict):
        """Apply basic headers to the request."""
        if 'headers' not in kwargs:
            kwargs['headers'] = {}
        kwargs['headers'].update(self._get_random_headers())
    
    def get(self, url: str, **kwargs) -> requests.Response:
        """Send a GET request."""
        kwargs.setdefault('timeout', self.timeout)
        self._apply_headers(kwargs)
        return self.session.get(url, **kwargs)

    def post(self, url: str, **kwargs) -> requests.Response:
        """Send a POST request."""
        kwargs.setdefault('timeout', self.timeout)
        self._apply_headers(kwargs)
        return self.session.post(url, **kwargs)
    
    def close(self):
        """Close the session."""
        self.session.close()


# Removed WaybackMachine class - not needed for localhost mock targets

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
                
                # AUTO-LOGIN: If we found a login page and haven't logged in yet
                if auto_login and not hasattr(self, 'is_logged_in'):
                    if "/login" in current_url or "/signin" in current_url or "login" in current_url.split('/')[-1]:
                        print(f"  🔍 Detected potential login page: {current_url}")
                        success = self.attempt_login(current_url)
                        if success:
                            self.is_logged_in = True
                            print("  ✅ Login Successful! Session authenticated.")
                
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
                    ('admin', 'admin123'),  # Mock targets default
                    ('admin', 'password'),
                    ('admin', 'admin'),
                    ('user', 'password'),
                    ('john_doe', 'password'),  # Mock target user
                    ('test', 'test'),
                    ('guest', 'guest'),
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
                    
                    # Check for success indicators
                    # 1. New cookies set? (Simple check)
                    # 2. Redirected to different page?
                    # 3. "Logout" or "Dashboard" in text?
                    
                    if "logout" in login_response.text.lower() or "dashboard" in login_response.text.lower() or "welcome" in login_response.text.lower():
                        print(f"  🔓 Login Successful! (Keyword match)")
                        return True
                    
                    # If we were redirected away from login and it's not the same page
                    if login_response.url != login_url and "login" not in login_response.url:
                        print(f"  🔓 Login Successful! (Redirected to {login_response.url})")
                        return True
                        
        except Exception as e:
            print(f"  ❌ Login Failed: {e}")
            
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
        # Optimized for mock targets - only check relevant paths
        if "localhost" in self.base_url or "127.0.0.1" in self.base_url:
            common_paths = [
                '/admin', '/login', '/dashboard', '/api', '/search',
                '/profile', '/user', '/upload', '/download', '/config',
                '/console', '/debug', '/test',
                '/products', '/cart', '/checkout', '/orders',
                '/register', '/logout', '/settings'
            ]
        else:
            # Full path list for real-world targets
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
                response = self.session.get(url, timeout=2)  # Fast timeout
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
        # State Dim 15: The agent sees 15 different features about the page (as per WebSecEnv)
        # Action Dim 50: The agent can perform 50 different actions (Mock Targets Mode)
        self.ai_agent = ImprovedDQNAgent(state_dim=15, action_dim=50)
        
        self._load_ai_brain(model_path)
        
        # Initialize environment once to get the action book
        temp_env = WebSecEnv(target_url=base_url, mode="mock_targets")
        
        # CORRECT MAPPING: Use mock_action_map to resolve the TRUE action name
        self.action_map = {}
        if hasattr(temp_env, 'mock_action_map'):
             for mock_id, real_id in temp_env.mock_action_map.items():
                 if real_id in temp_env.action_book:
                     self.action_map[mock_id] = temp_env.action_book[real_id].__name__
        else:
             self.action_map = {k: v.__name__ for k, v in temp_env.action_book.items()}
        
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
            
            # Support both brain (DQNAgent) and q_network (ImprovedDQNAgent)
            network = getattr(self.ai_agent, 'brain', None) or getattr(self.ai_agent, 'q_network', None)
            if network:
                network.eval()
            
            self.ai_agent.epsilon = 0.0    # Stop exploring randomly, use learned skills
            if episode > 0:
                print(f" (Resumed from Episode: {episode}\n")
        except Exception as e:
            print(f" (!) Could not load model: {e}")
            import traceback
            traceback.print_exc()
            print(f"   Detailed error: {str(e)}")
            print("   The agent will act randomly (Untrained Mode)\n")

    def start_audit(self, crawl_depth: int = 30, test_intensity: int = 3, epsilon: float = 0.1, persist: bool = False, ai_mode: bool = False, pentester: bool = False, render_callback: callable = None) -> List[Finding]:
        """Runs the full vulnerability scanning process."""
        print("=" * 70)
        mode_name = "FULL AI MODE" if ai_mode else "CLASSIC MODE"
        print(f"[AI] AI VULNERABILITY SCANNER - {mode_name}")
        print(f"[TARGET] Target: {self.base_url}")
        print("=" * 70)
        print()
        
        # --- Phase 1: Reconnaissance ---
        print("[*] PHASE 1: MAPPING THE TARGET")
        print("-" * 70)
        
        if pentester:
            print(" [X] CHAIN ATTACK MODE: ENABLED (Pentester Mode)")
            print("   - Using extended episodes (50+ steps) for multi-step exploitation")
            test_intensity = max(test_intensity, 50)
            ai_mode = True # Pentester implies AI mode for deep logic
            
        if ai_mode:
            print(" [!] AI-Driven Reconnaissance Engaged...")
            print(" [!] ONLINE LEARNING ACTIVE: Model will update in real-time based on findings.")
            # Enable training mode
            if hasattr(self.ai_agent, 'brain'):
                self.ai_agent.brain.train()
            elif hasattr(self.ai_agent, 'q_network'):
                self.ai_agent.q_network.train()
            
            # Enable exploration for learning
            epsilon = max(epsilon, 0.1) 
            self.ai_agent.epsilon = epsilon
            
            discovered_urls = self.explorer.explore(max_pages=crawl_depth // 2)
            print("\n[RECON] AI Agent taking control for Deep Exploration...")
            ai_urls = self._explore_with_ai(steps=30, render_callback=render_callback)
            if isinstance(discovered_urls, list):
                for url in ai_urls:
                    if url not in discovered_urls:
                        discovered_urls.append(url)
            else:
                discovered_urls.update(ai_urls)
            print(f"[STATS] AI discovered {len(ai_urls)} unique paths via interaction.")
        else:
            discovered_urls = self.explorer.explore(max_pages=crawl_depth)
            
        self.explorer.probe_common_endpoints()
        
        # --- Phase 2: Attack ---
        print("\n[ATTACK] PHASE 2: VULNERABILITY TESTING")
        print("-" * 70)
        
        all_findings: List[Finding] = []
        
        for url in discovered_urls:
            if self.stop_requested:
                print("\n[STOP] Scan aborted by user.")
                break
            print(f"\n[TARGET] Auditing: {url}")
            # Pass ai_mode and render_callback to _audit_page
            findings = self._audit_page(url, attempts=test_intensity, epsilon=epsilon, ai_mode=ai_mode, render_callback=render_callback)
            
            if findings:
                all_findings.extend(findings)
                print(f"  [VULN] Found {len(findings)} vulnerability(ies)!")
            else:
                print(f"  [OK] Page appears secure.")
        
        # --- Phase 3: Filter False Positives ---
        print("\n[FILTER] PHASE 3: FILTERING FALSE POSITIVES")
        print("-" * 70)
        
        from utils.false_positive_filter import apply_false_positive_filter
        
        original_count = len(all_findings)
        if ai_mode:
             pass
        else:
            all_findings = apply_false_positive_filter(all_findings, self.base_url)
        filtered_count = original_count - len(all_findings)
        
        if filtered_count > 0:
            print(f"  🗑️  Removed {filtered_count} false positive(s)")
        print(f"  ✅ {len(all_findings)} genuine finding(s) remain")
        
        if len(all_findings) == 0:
             print("  ⚠️ WARNING: Findings list is empty after filtering. Report will be empty.")
        
        # Save Online Session Model
        if ai_mode:
            try:
                timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                session_model_path = f"checkpoints/online_session_{timestamp}.pth"
                # Create checkpoint directory if it doesn't exist
                os.makedirs("checkpoints", exist_ok=True)
                
                # Save the model state
                import torch
                if hasattr(self.ai_agent, 'brain'):
                     torch.save(self.ai_agent.brain.state_dict(), session_model_path)
                elif hasattr(self.ai_agent, 'q_network'):
                     torch.save(self.ai_agent.q_network.state_dict(), session_model_path)
                     
                print(f"\n💾 Online Learning Session Saved: {session_model_path}")
            except Exception as e:
                print(f"❌ Failed to save online session model: {e}")

        else:
             print(f"  📝 Generating report with {len(all_findings)} findings.")
        
        # --- PERSISTENCE MODE CHECK ---
        if persist and not all_findings:
            print(f"\n[!] PERSISTENCE MODE ENGAGED: SCANNING UNTIL VULNERABILITIES FOUND...")
            max_retries = 50  # Virtually infinite
            current_retry = 0
            
            # Progressive Epsilon Increase
            current_epsilon = epsilon
            
            while not all_findings and current_retry < max_retries:
                current_retry += 1
                current_epsilon = min(current_epsilon + 0.10, 1.0)
                
                # Progressively increase intensity: Start adding +5, then +10, etc.
                extra_intensity = 5 + (current_retry * 2) 
                current_attempts = test_intensity + extra_intensity
                
                print(f"\n[+] RETRY {current_retry} | Intensity: {current_attempts} (+{extra_intensity}) | Epsilon: {current_epsilon:.2f}")
                
                # Re-scan all discovered URLs
                for url in discovered_urls:
                    if self.stop_requested: break
                    print(f"  [>] Re-Auditing: {url}")
                    
                    # More aggressive auditing
                    findings = self._audit_page(url, attempts=current_attempts, epsilon=current_epsilon)
                    if findings:
                        all_findings.extend(findings)
                
                if all_findings:
                    print(f"  [!] SUCCESS! Found {len(all_findings)} vulnerabilities after {current_retry} retries.")
                    break
        
        # --- Phase 4: Reporting ---
        self._generate_final_report(list(discovered_urls), all_findings)
        return all_findings

    def _explore_with_ai(self, steps: int, render_callback: callable = None) -> List[str]:
        """
        Uses the AI agent to navigate and discover URLs intelligently.
        """
        discovered = []
        try:
            from env.web_sec_env import WebSecEnv
            # Use a slightly longer episode for exploration
            env = WebSecEnv(self.base_url)
            env.max_steps_per_episode = steps
            
            state, _ = env.reset()
            discovered.append(self.base_url)
            
            print(" [AI-RECON] Starting 30-step exploration sequence...")
            
            for step in range(steps):
                action = self.ai_agent.act(state)
                next_state, reward, terminated, truncated, info = env.step(action)
                
                # RENDER LIVE VIEW
                if render_callback:
                    try:
                         content = ""
                         if hasattr(env, 'driver') and env.driver:
                             content = env.driver.page_source
                         elif hasattr(env, 'last_response') and env.last_response:
                             content = env.last_response.text
                         if content:
                             render_callback(content)
                    except:
                        pass
                
                # ONLINE LEARNING (Exploration Phase)
                if self.ai_agent.epsilon > 0: # If epsilon > 0, we imply we are learning/exploring
                     done = terminated or truncated
                     self.ai_agent.remember(state, action, reward, next_state, done)
                     self.ai_agent.replay() # No batch size arg

                url = info.get('url')
                if url and url not in discovered:
                    discovered.append(url)
                    print(f"    [+] Agent Found: {url}")
                
                state = next_state
                if terminated or truncated:
                    state, _ = env.reset()
            
            env.close()
            
        except ImportError:
            print("  [!] Could not import WebSecEnv for exploration.")
        except Exception as e:
            print(f"  [!] AI Exploration failed: {e}")
            
        return discovered

    def _audit_page(self, url: str, attempts: int = 3, epsilon: float = 0.1, ai_mode: bool = False, render_callback: callable = None) -> List[Finding]:
        """
        Deploys the AI Agent to test a specific page.
        """
        from utils.validator import VulnerabilityValidator
        validator = VulnerabilityValidator()
        findings = []
        
        try:
            # Enable exploration
            self.ai_agent.epsilon = epsilon
            
            # Pass discovered endpoints AND SESSION to the environment
            from env.web_sec_env import WebSecEnv
            env = WebSecEnv(
                target_url=url, 
                discovered_endpoints=list(self.explorer.discovered_urls) if hasattr(self.explorer, 'discovered_urls') else [],
                session=self.explorer.session.session,
                mode="mock_targets" 
            )
            env.max_steps_per_episode = attempts 
            
            # --- MAIN AI LOOP ---
            # Reset environment for new page
            # Backup cookies to persist authentication across resets
            try:
                cookies_backup = self.explorer.session.session.cookies.copy()
            except:
                cookies_backup = None

            state, _ = env.reset()
            
            # RESTORE COOKIES: Maintain the session established by the Explorer
            if cookies_backup:
                env.session.cookies.update(cookies_backup)
                env.auth_token = "EXISTING_SESSION"

            env.current_page_id = 0 # Force focus on current page (simplified)
            
            for step in range(attempts):
                # 1. AI Decides Action
                action = self.ai_agent.act(state, training=False) 
                
                # 2. Execute Action
                next_state, reward, terminated, truncated, info = env.step(action)
                
                # RENDER LIVE VIEW
                if render_callback:
                    try:
                        # Try to get HTML content (Selenium or Requests)
                        content = ""
                        if hasattr(env, 'driver') and env.driver:
                            content = env.driver.page_source
                        elif hasattr(env, 'last_response') and env.last_response:
                            content = env.last_response.text
                        
                        if content:
                            render_callback(content)
                    except Exception:
                        pass

                # 3. Learn (ONLINE LEARNING)
                if ai_mode:
                    # Remember experience
                    done = terminated or truncated
                    self.ai_agent.remember(state, action, reward, next_state, done)
                    # Train on this new experience
                    self.ai_agent.replay()
                    
                    if step % 5 == 0:
                        print(f"    🧠 [Online Learning] Updated brain weights (Reward: {reward:.2f})")
                
                # 4. Check for Findings 
                
                if reward > 0:
                    vuln_name = self._map_action_to_vuln(action)
                    
                    # PRIORITY 1: Explicit flag from Environment
                    env_confirmed = info.get('vuln_found', False)
                    
                    if env_confirmed or reward >= 0.1:
                        # FILTERING LOGIC
                        if not ai_mode:
                            # Classic Mode: Filter out navigation/probing actions
                            if "navigate_" in vuln_name or "probe_" in vuln_name:
                                continue
                        else:
                            # AI Mode: Report EVERYTHING the agent thinks is valuable
                             if "navigate_" in vuln_name or "probe_" in vuln_name:
                                 pass # Keep them

                        print(f"  ✨ POTENTIAL VULN: {vuln_name} (Reward: {reward})")
                        
                        # --- ROBUST VALIDATION ---
                        validation_result = False
                        if env.last_response:
                            validation_result = validator.validate(vuln_name, env.last_response, info.get('payload'))
                        else:
                            # Action failed or returned no response, skipping validation
                            pass
                        
                        if validation_result:
                            # HIGH CONFIDENCE (Validator Confirmed)
                            confidence = 'High' if env_confirmed else 'Medium'
                            finding = Finding(
                                url=info.get('url', url),
                                vuln_type=vuln_name,
                                confidence=confidence,
                                reward=reward,
                                payload=info.get('payload', ''),
                                method=info.get('method', 'GET')
                            )
                            # Avoid duplicates
                            if not any(f.vuln_type == finding.vuln_type and f.url == finding.url for f in findings):
                                findings.append(finding)
                                self.log_finding(finding)
                                print(f"    🚨 CONFIRMED: {vuln_name}")

                        elif env_confirmed:
                             # MEDIUM CONFIDENCE (Env Confirmed, Validator Rejected/Missed)
                             print(f"    ⚠️ VALIDATOR REJECTED (Env Confirmed!): {vuln_name}")
                             finding = Finding(
                                 url=info.get('url', url),
                                 vuln_type=vuln_name,
                                 confidence='Medium', 
                                 reward=reward,
                                 payload=info.get('payload', ''),
                                 method=info.get('method', 'GET')
                             )
                             if not any(f.vuln_type == finding.vuln_type and f.url == finding.url for f in findings):
                                 findings.append(finding)
                                 self.log_finding(finding)
                                 print(f"    🚨 KEPT (Env Confirmed): {vuln_name}")

                        else:
                            # LOW CONFIDENCE (Agent thinks so, but Env/Validator disagree)
                            # User Request: "even 2600 pth find with that vuln is found in training session check phyase 2 and fix phase 3 issue"
                            # We keep it as Low Confidence instead of rejecting.
                            print(f"    ⚠️ VALIDATOR REJECTED: {vuln_name}")
                            finding = Finding(
                                 url=info.get('url', url),
                                 vuln_type=vuln_name,
                                 confidence='Low (Validator Rejected)', 
                                 reward=reward,
                                 payload=info.get('payload', ''),
                                 method=info.get('method', 'GET')
                             )
                            if not any(f.vuln_type == finding.vuln_type and f.url == finding.url for f in findings):
                                 findings.append(finding)
                                 # Don't log to file/console as CONFIRMED, but keep in list for report
                                 print(f"    ⚠️ KEPT (Low Confidence): {vuln_name}")
                
                state = next_state
                
                if terminated or truncated:
                    break
        
        except Exception as e:
            print(f"  ❌ Error auditing page: {e}")
            
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
        parser = argparse.ArgumentParser(description='AI Vulnerability Scanner for Mock Targets')
        parser.add_argument('url', help='Target URL to scan (e.g., http://localhost:5002)')
        parser.add_argument('--depth', type=int, default=20, help='How many pages to crawl (default: 20)')
        parser.add_argument('--intensity', type=int, default=5, help='Attack intensity 1-10 (default: 5)')
        parser.add_argument('--model', default='dqn_web_sec_model.pth', help='Path to the trained AI model')
        parser.add_argument("--persist", action="store_true", default=False, help="Keep trying until a vulnerability is found")
        parser.add_argument("--ai-mode", action="store_true", default=False, help="Enable Full AI Capabilities (Recon + Unfiltered Attacks)")
        parser.add_argument("--pentester", action="store_true", default=False, help="Enable Chain Attacks (Deep Exploration, 50+ steps)")

        args = parser.parse_args()
        
        try:
            auditor = SecurityAuditor(
                base_url=args.url,
                model_path=args.model
            )
            
            auditor.start_audit(
                crawl_depth=args.depth,
                test_intensity=args.intensity,
                persist=args.persist,
                ai_mode=args.ai_mode,
                pentester=args.pentester
            )
        except Exception as e:
            print(f"(!) Error scanning {args.url}: {e}")
            import traceback
            traceback.print_exc()
            import traceback
            traceback.print_exc()

    main()

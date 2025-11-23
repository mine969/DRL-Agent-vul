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
        
    def explore(self, max_pages: int = 50) -> List[str]:
        """
        Crawls the website to discover pages.
        
        How it works:
        1. Start at the home page.
        2. Find all links on that page.
        3. Add new links to a 'to-do' list.
        4. Repeat until we've seen enough pages.
        """
        print(f"🕷️  Starting reconnaissance on: {self.base_url}")
        print(f"🎯 Target domain: {self.domain}\n")
        
        # Queue: The list of pages we need to visit
        pages_to_visit: deque = deque([self.base_url])
        visited_pages: Set[str] = set()
        
        while pages_to_visit and len(visited_pages) < max_pages:
            current_url = pages_to_visit.popleft()
            
            if current_url in visited_pages:
                continue
                
            print(f"📍 Exploring: {current_url}")
            
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
        for link in soup.find_all('a', href=True):
            full_url = urljoin(current_url, link['href'])
            
            # We only want to scan THIS website, not the whole internet
            if urlparse(full_url).netloc == self.domain:
                if full_url not in visited:
                    queue.append(full_url)

    def _log_interesting_elements(self, soup):
        """Helper to print if we found forms or inputs (attack surface)."""
        forms = soup.find_all('form')
        inputs = soup.find_all('input')
        if forms:
            print(f"  ✅ Found {len(forms)} form(s) - Good target!")
        if inputs:
            print(f"  ✅ Found {len(inputs)} input field(s)")

    def probe_common_endpoints(self) -> None:
        """
        Guesses common hidden pages (like /admin or /login) that might not be linked.
        """
        common_paths = [
            '/admin', '/login', '/dashboard', '/api', '/search',
            '/profile', '/user', '/upload', '/download', '/config',
            '/debug', '/test', '/dev', '/backup', '/files',
            '/robots.txt', '/sitemap.xml', '/.git', '/phpinfo.php'
        ]
        
        print("🔍 Probing for hidden endpoints...")
        
        for path in common_paths:
            url = self.base_url + path
            try:
                response = self.session.get(url)
                if response.status_code == 200:
                    print(f"  ✅ Discovered hidden page: {path}")
                    self.discovered_urls.add(url)
                elif response.status_code == 403:
                    print(f"  🔒 Found protected page: {path}")
                    self.discovered_urls.add(url)
            except:
                pass
        print()
    
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
        # State Dim 10: The agent sees 10 different things about the page
        # Action Dim 15: The agent can perform 15 different attacks/actions
        self.ai_agent = DQNAgent(state_dim=10, action_dim=15)
        
        self._load_ai_brain(model_path)
    
    def _load_ai_brain(self, model_path):
        """Attempts to load the trained neural network."""
        try:
            self.ai_agent.q_network.load_state_dict(torch.load(model_path))
            self.ai_agent.q_network.eval() # Set to evaluation mode (no learning, just doing)
            self.ai_agent.epsilon = 0.0    # Stop exploring randomly, use learned skills
            print(f"✅ Loaded AI Brain from: {model_path}\n")
        except:
            print(f"⚠️  Could not load model from {model_path}")
            print("   The agent will act randomly (Untrained Mode)\n")

    def start_audit(self, crawl_depth: int = 30, test_intensity: int = 3) -> List[Finding]:
        """
        Runs the full security audit process.
        
        Steps:
        1. Explore the website to find pages.
        2. Send the AI to attack each page.
        3. Generate a report of findings.
        """
        print("=" * 70)
        print("🤖 AUTONOMOUS AI SECURITY AUDITOR")
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
            findings = self._audit_page(url, attempts=test_intensity)
            
            if findings:
                all_findings.extend(findings)
                print(f"  🚨 Found {len(findings)} vulnerability(ies)!")
            else:
                print(f"  ✅ Page appears secure.")
        
        # --- Phase 3: Reporting ---
        self._generate_final_report(discovered_urls, all_findings)
        
        return all_findings
    
    def _audit_page(self, url: str, attempts: int = 3) -> List[Finding]:
        """
        Deploys the AI Agent to test a specific page.
        It runs for a few 'episodes' (attempts) to see if it can break it.
        """
        findings: List[Finding] = []
        
        try:
            # Create a temporary environment for this page
            env = WebSecEnv(target_url=url)
            
            for _ in range(attempts):
                state, _ = env.reset()
                done = False
                steps = 0
                
                # Let the agent interact with the page for up to 30 steps
                while not done and steps < 30:
                    action = self.ai_agent.act(state)
                    next_state, reward, terminated, truncated, _ = env.step(action)
                    done = terminated or truncated
                    
                    # If the agent gets a big reward (>50), it means it found something!
                    if reward > 50:
                        vuln_name = self._map_action_to_vuln(action)
                        findings.append(Finding(
                            url=url,
                            vuln_type=vuln_name,
                            confidence='High' if reward > 80 else 'Medium',
                            reward=reward
                        ))
                    
                    state = next_state
                    steps += 1
        except Exception as e:
            # If the page crashes or errors out, just move on
            pass
        
        return findings
    
    def _map_action_to_vuln(self, action: int) -> str:
        """Translates the Agent's action ID into a human-readable vulnerability name."""
        vuln_map = {
            3: "SQL Injection",
            4: "Cross-Site Scripting (XSS)",
            8: "Fuzzing / Anomaly",
            9: "Insecure Direct Object Reference (IDOR)",
            10: "Server-Side Request Forgery (SSRF)",
            13: "Time-Based SQL Injection",
            14: "Polyglot XSS"
        }
        return vuln_map.get(action, "Unknown Vulnerability")
    
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

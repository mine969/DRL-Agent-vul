"""
Optimized Autonomous Web Reconnaissance Agent

Performance improvements:
- O(1) queue operations using deque
- O(1) URL lookups using sets
- Session reuse for network efficiency
- Type hints for code quality
- Dataclasses for structured data
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

from agent.dqn_agent import DQNAgent
from env.web_sec_env import WebSecEnv

# Load vulnerability database from external file for better maintainability
VULNERABILITY_DATABASE = {
    "SQL Injection": {
        "impact": "CRITICAL",
        "cvss_score": 9.8,
        "description": "Allows attackers to execute arbitrary SQL commands on the database",
        "exploitation": [
            "1. Inject malicious SQL code through input fields",
            "2. Bypass authentication (login as admin without password)",
            "3. Extract entire database contents (usernames, passwords, credit cards)",
            "4. Modify or delete database records",
            "5. Execute administrative operations on the database"
        ],
        "damage_potential": [
            "Complete database compromise",
            "Theft of all user credentials and personal information",
            "Financial fraud through stolen payment information",
            "Data manipulation or deletion",
            "Potential server takeover through database functions"
        ],
        "real_world_impact": "Attackers can steal millions of user records, leading to identity theft, financial loss, and complete business shutdown. Examples: Equifax breach (2017), TalkTalk hack (2015).",
        "remediation": [
            "Use parameterized queries (prepared statements)",
            "Implement input validation and sanitization",
            "Apply principle of least privilege to database accounts",
            "Use ORM frameworks properly",
            "Regular security audits and penetration testing"
        ]
    },
    "Cross-Site Scripting (XSS)": {
        "impact": "HIGH",
        "cvss_score": 7.1,
        "description": "Allows attackers to inject malicious scripts into web pages viewed by other users",
        "exploitation": [
            "1. Inject JavaScript code through input fields or URLs",
            "2. Steal session cookies and authentication tokens",
            "3. Redirect users to phishing sites",
            "4. Modify page content to display fake information",
            "5. Perform actions on behalf of the victim user"
        ],
        "damage_potential": [
            "Session hijacking (account takeover)",
            "Credential theft through fake login forms",
            "Malware distribution",
            "Defacement of web pages",
            "Phishing attacks against other users"
        ],
        "real_world_impact": "Attackers can hijack user sessions, steal credentials, and spread malware. Commonly used in targeted attacks against high-value accounts.",
        "remediation": [
            "Encode all user input before displaying",
            "Implement Content Security Policy (CSP)",
            "Use HTTPOnly and Secure flags on cookies",
            "Validate and sanitize all input",
            "Use modern frameworks with built-in XSS protection"
        ]
    },
    "Command Injection": {
        "impact": "CRITICAL",
        "cvss_score": 9.9,
        "description": "Allows attackers to execute arbitrary system commands on the server",
        "exploitation": [
            "1. Inject shell commands through vulnerable input fields",
            "2. Execute system commands with web server privileges",
            "3. Read sensitive files (/etc/passwd, config files)",
            "4. Install backdoors and malware",
            "5. Pivot to internal network"
        ],
        "damage_potential": [
            "Complete server compromise",
            "Installation of persistent backdoors",
            "Data exfiltration",
            "Use server for cryptocurrency mining",
            "Lateral movement to other systems"
        ],
        "real_world_impact": "Full server takeover, allowing attackers to steal all data, install ransomware, or use the server for attacks on others. Can lead to complete business shutdown.",
        "remediation": [
            "Never pass user input to system commands",
            "Use safe APIs instead of shell commands",
            "Implement strict input validation with whitelists",
            "Run web applications with minimal privileges",
            "Use containerization and sandboxing"
        ]
    },
    "Insecure Direct Object Reference (IDOR)": {
        "impact": "MEDIUM",
        "cvss_score": 6.5,
        "description": "Allows attackers to access unauthorized resources by manipulating object references",
        "exploitation": [
            "1. Modify ID parameters in URLs or requests",
            "2. Access other users' profiles, documents, or data",
            "3. Enumerate all records by iterating IDs",
            "4. Modify or delete other users' resources",
            "5. Escalate privileges by accessing admin resources"
        ],
        "damage_potential": [
            "Privacy breach (viewing others' personal data)",
            "Data theft through enumeration",
            "Unauthorized modifications",
            "Privilege escalation",
            "Compliance violations (GDPR, HIPAA)"
        ],
        "real_world_impact": "Attackers can access sensitive personal information, medical records, or financial data of other users. Common in healthcare and financial applications.",
        "remediation": [
            "Implement proper access control checks",
            "Use indirect references (UUIDs instead of sequential IDs)",
            "Verify user authorization for each request",
            "Implement session-based access controls",
            "Log and monitor access patterns"
        ]
    },
    "Server-Side Request Forgery (SSRF)": {
        "impact": "HIGH",
        "cvss_score": 8.6,
        "description": "Allows attackers to make the server perform requests to arbitrary locations",
        "exploitation": [
            "1. Force server to access internal resources",
            "2. Scan internal network from the server",
            "3. Access cloud metadata services (AWS, Azure)",
            "4. Bypass firewall restrictions",
            "5. Interact with internal APIs and services"
        ],
        "damage_potential": [
            "Access to internal admin panels",
            "Cloud credential theft (AWS keys, etc.)",
            "Internal network reconnaissance",
            "Data exfiltration from internal systems",
            "Potential remote code execution on internal services"
        ],
        "real_world_impact": "Can lead to cloud account takeover, access to internal databases, and exposure of sensitive internal systems. Critical in cloud environments.",
        "remediation": [
            "Validate and sanitize all URLs",
            "Use allowlists for permitted destinations",
            "Disable unnecessary URL schemas (file://, gopher://)",
            "Implement network segmentation",
            "Use cloud instance metadata protection"
        ]
    }
}


@dataclass
class Finding:
    """Structured vulnerability finding"""
    url: str
    vuln_type: str
    confidence: str
    reward: float


class OptimizedSession:
    """Optimized HTTP session with connection pooling and retry logic"""
    
    def __init__(self, pool_connections: int = 10, pool_maxsize: int = 20):
        self.session = requests.Session()
        
        # Configure retry strategy
        retry_strategy = Retry(
            total=3,
            backoff_factor=0.3,
            status_forcelist=[429, 500, 502, 503, 504]
        )
        
        # Configure adapter with connection pooling
        adapter = HTTPAdapter(
            pool_connections=pool_connections,
            pool_maxsize=pool_maxsize,
            max_retries=retry_strategy
        )
        
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
        
        # Set default timeout
        self.timeout = 5
    
    def get(self, url: str, **kwargs) -> requests.Response:
        """GET request with default timeout"""
        kwargs.setdefault('timeout', self.timeout)
        return self.session.get(url, **kwargs)
    
    def close(self):
        """Close session and release connections"""
        self.session.close()


class ReconAgent:
    """Optimized agent for website reconnaissance"""
    
    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip('/')
        self.domain = urlparse(base_url).netloc
        self.discovered_urls: Set[str] = set()  # O(1) lookup
        self.session = OptimizedSession()
        
    def crawl(self, max_pages: int = 50) -> List[str]:
        """
        Crawl website using BFS with optimized data structures
        
        Time Complexity: O(n) where n is number of pages
        Space Complexity: O(n)
        """
        print(f"🕷️  Starting reconnaissance on: {self.base_url}")
        print(f"🎯 Target domain: {self.domain}\n")
        
        # Use deque for O(1) append/popleft operations
        to_visit: deque = deque([self.base_url])
        visited: Set[str] = set()  # O(1) membership testing
        
        while to_visit and len(visited) < max_pages:
            url = to_visit.popleft()  # O(1) operation
            
            if url in visited:
                continue
                
            print(f"📍 Crawling: {url}")
            
            try:
                response = self.session.get(url)
                visited.add(url)
                self.discovered_urls.add(url)
                
                # Parse HTML
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Extract and process links
                for link in soup.find_all('a', href=True):
                    full_url = urljoin(url, link['href'])
                    
                    # Only follow same-domain links
                    if urlparse(full_url).netloc == self.domain:
                        if full_url not in visited:  # O(1) check
                            to_visit.append(full_url)  # O(1) operation
                
                # Log interesting findings
                forms = soup.find_all('form')
                inputs = soup.find_all('input')
                if forms:
                    print(f"  ✅ Found {len(forms)} form(s)")
                if inputs:
                    print(f"  ✅ Found {len(inputs)} input field(s)")
                
            except Exception as e:
                print(f"  ❌ Error: {str(e)[:50]}")
        
        print(f"\n✅ Reconnaissance complete!")
        print(f"📊 Discovered {len(self.discovered_urls)} unique URLs\n")
        
        return list(self.discovered_urls)
    
    def discover_endpoints(self) -> None:
        """Probe for common endpoints"""
        common_paths = [
            '/admin', '/login', '/dashboard', '/api', '/search',
            '/profile', '/user', '/upload', '/download', '/config',
            '/debug', '/test', '/dev', '/backup', '/files',
            '/robots.txt', '/sitemap.xml', '/.git', '/phpinfo.php'
        ]
        
        print("🔍 Probing for common endpoints...")
        
        for path in common_paths:
            url = self.base_url + path
            try:
                response = self.session.get(url)
                if response.status_code == 200:
                    print(f"  ✅ Found: {path}")
                    self.discovered_urls.add(url)
                elif response.status_code == 403:
                    print(f"  🔒 Forbidden: {path}")
                    self.discovered_urls.add(url)
            except:
                pass
        
        print()
    
    def __del__(self):
        """Cleanup session on destruction"""
        if hasattr(self, 'session'):
            self.session.close()


class AutonomousSecurityAgent:
    """Optimized autonomous security scanner"""
    
    def __init__(self, base_url: str, model_path: str = "dqn_web_sec_model.pth"):
        self.base_url = base_url
        self.recon = ReconAgent(base_url)
        
        # Load trained DQN agent
        self.dqn_agent = DQNAgent(state_dim=10, action_dim=15)
        try:
            self.dqn_agent.q_network.load_state_dict(torch.load(model_path))
            self.dqn_agent.q_network.eval()
            self.dqn_agent.epsilon = 0.0
            print(f"✅ Loaded trained model from: {model_path}\n")
        except:
            print(f"⚠️  Could not load model from {model_path}")
            print("   Agent will use random exploration\n")
    
    def scan(self, crawl_depth: int = 30, test_episodes: int = 3) -> List[Finding]:
        """
        Full autonomous scan with optimized performance
        
        Args:
            crawl_depth: Maximum pages to crawl
            test_episodes: Test episodes per URL
            
        Returns:
            List of vulnerability findings
        """
        print("=" * 70)
        print("🤖 AUTONOMOUS SECURITY AGENT")
        print("=" * 70)
        print()
        
        # Phase 1: Reconnaissance
        print("📍 PHASE 1: RECONNAISSANCE")
        print("-" * 70)
        discovered = self.recon.crawl(max_pages=crawl_depth)
        self.recon.discover_endpoints()
        
        # Phase 2: Vulnerability Testing
        print("\n🔴 PHASE 2: VULNERABILITY TESTING")
        print("-" * 70)
        
        all_findings: List[Finding] = []
        
        for url in discovered:
            print(f"\n🎯 Testing: {url}")
            findings = self._test_url(url, episodes=test_episodes)
            
            if findings:
                all_findings.extend(findings)
                print(f"  🚨 Found {len(findings)} potential vulnerability(ies)")
            else:
                print(f"  ✅ No vulnerabilities detected")
        
        # Phase 3: Report
        self._print_summary(discovered, all_findings)
        self._save_reports(discovered, all_findings)
        
        return all_findings
    
    def _test_url(self, url: str, episodes: int = 3) -> List[Finding]:
        """Test URL for vulnerabilities"""
        findings: List[Finding] = []
        
        try:
            env = WebSecEnv(target_url=url)
            
            for _ in range(episodes):
                state, _ = env.reset()
                done = False
                step = 0
                
                while not done and step < 30:
                    action = self.dqn_agent.act(state)
                    next_state, reward, terminated, truncated, _ = env.step(action)
                    done = terminated or truncated
                    
                    # High reward indicates vulnerability
                    if reward > 50:
                        findings.append(Finding(
                            url=url,
                            vuln_type=self._get_vuln_type(action),
                            confidence='High' if reward > 80 else 'Medium',
                            reward=reward
                        ))
                    
                    state = next_state
                    step += 1
        except:
            pass
        
        return findings
    
    def _get_vuln_type(self, action: int) -> str:
        """Map action to vulnerability type"""
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
    
    def _print_summary(self, urls: List[str], findings: List[Finding]) -> None:
        """Print scan summary"""
        print("\n" + "=" * 70)
        print("📊 FINAL REPORT")
        print("=" * 70)
        print(f"\nTarget: {self.base_url}")
        print(f"Pages Discovered: {len(urls)}")
        print(f"Vulnerabilities Found: {len(findings)}")
        
        if findings:
            print("\n🔴 VULNERABILITIES:")
            for finding in findings:
                print(f"  - {finding.url}")
                print(f"    Type: {finding.vuln_type}")
                print(f"    Confidence: {finding.confidence}")
                print()
        else:
            print("\n✅ No vulnerabilities detected")
    
    def _save_reports(self, urls: List[str], findings: List[Finding]) -> None:
        """Generate and save all report formats"""
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Import report generator (will create this next)
        from utils.report_generator import ReportGenerator
        
        generator = ReportGenerator(self.base_url, timestamp)
        generator.generate_html_report(urls, findings, VULNERABILITY_DATABASE)
        generator.generate_txt_report(urls, findings, VULNERABILITY_DATABASE)
        generator.generate_md_report(urls, findings, VULNERABILITY_DATABASE)


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Optimized Autonomous Security Scanner')
    parser.add_argument('url', help='Target URL to scan')
    parser.add_argument('--depth', type=int, default=30, help='Crawl depth')
    parser.add_argument('--episodes', type=int, default=3, help='Test episodes per page')
    parser.add_argument('--model', default='dqn_web_sec_model.pth', help='Model file')
    
    args = parser.parse_args()
    
    agent = AutonomousSecurityAgent(args.url, args.model)
    agent.scan(crawl_depth=args.depth, test_episodes=args.episodes)

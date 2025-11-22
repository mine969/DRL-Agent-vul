"""
Autonomous Web Reconnaissance Agent

This agent crawls a target website, discovers pages/endpoints, and tests them for vulnerabilities.
Just provide the homepage URL and it will explore automatically!
"""

import torch
import numpy as np
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import re
from agent.dqn_agent import DQNAgent
from env.web_sec_env import WebSecEnv

class ReconAgent:
    """Agent that discovers and maps a target website"""
    
    def __init__(self, base_url):
        self.base_url = base_url.rstrip('/')
        self.domain = urlparse(base_url).netloc
        self.discovered_urls = set()
        self.tested_urls = set()
        self.vulnerabilities = []
        
    def crawl(self, max_pages=50):
        """
        Crawl the website starting from base_url
        
        Args:
            max_pages: Maximum number of pages to discover
        """
        print(f"🕷️  Starting reconnaissance on: {self.base_url}")
        print(f"🎯 Target domain: {self.domain}\n")
        
        to_visit = [self.base_url]
        visited = set()
        
        while to_visit and len(visited) < max_pages:
            url = to_visit.pop(0)
            
            if url in visited:
                continue
                
            print(f"📍 Crawling: {url}")
            
            try:
                response = requests.get(url, timeout=5)
                visited.add(url)
                self.discovered_urls.add(url)
                
                # Extract links from page
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Find all links
                for link in soup.find_all('a', href=True):
                    full_url = urljoin(url, link['href'])
                    
                    # Only follow links on same domain
                    if urlparse(full_url).netloc == self.domain:
                        if full_url not in visited and full_url not in to_visit:
                            to_visit.append(full_url)
                
                # Find forms (potential attack surfaces)
                forms = soup.find_all('form')
                if forms:
                    print(f"  ✅ Found {len(forms)} form(s)")
                
                # Find input fields
                inputs = soup.find_all('input')
                if inputs:
                    print(f"  ✅ Found {len(inputs)} input field(s)")
                
            except Exception as e:
                print(f"  ❌ Error crawling {url}: {str(e)[:50]}")
        
        print(f"\n✅ Reconnaissance complete!")
        print(f"📊 Discovered {len(self.discovered_urls)} unique URLs\n")
        
        return list(self.discovered_urls)
    
    def discover_endpoints(self):
        """
        Discover common endpoints using wordlist
        """
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
                response = requests.get(url, timeout=3)
                if response.status_code == 200:
                    print(f"  ✅ Found: {path}")
                    self.discovered_urls.add(url)
                elif response.status_code == 403:
                    print(f"  🔒 Forbidden: {path}")
                    self.discovered_urls.add(url)  # Still interesting!
            except:
                pass
        
        print()

class AutonomousSecurityAgent:
    """
    Combines reconnaissance with vulnerability testing
    """
    
    def __init__(self, base_url, model_path="dqn_web_sec_model.pth"):
        self.base_url = base_url
        self.recon = ReconAgent(base_url)
        
        # Load trained DQN agent
        self.dqn_agent = DQNAgent(state_dim=7, action_dim=15)
        try:
            self.dqn_agent.q_network.load_state_dict(torch.load(model_path))
            self.dqn_agent.q_network.eval()
            self.dqn_agent.epsilon = 0.0
            print(f"✅ Loaded trained model from: {model_path}\n")
        except:
            print(f"⚠️  Could not load model from {model_path}")
            print("   Agent will use random exploration\n")
    
    def scan(self, crawl_depth=30, test_episodes=5):
        """
        Full autonomous scan: discover + test
        
        Args:
            crawl_depth: How many pages to crawl
            test_episodes: How many test episodes per discovered URL
        """
        print("="*70)
        print("🤖 AUTONOMOUS SECURITY AGENT")
        print("="*70)
        print()
        
        # Phase 1: Reconnaissance
        print("📍 PHASE 1: RECONNAISSANCE")
        print("-"*70)
        discovered = self.recon.crawl(max_pages=crawl_depth)
        self.recon.discover_endpoints()
        
        # Phase 2: Vulnerability Testing
        print("\n🔴 PHASE 2: VULNERABILITY TESTING")
        print("-"*70)
        
        all_findings = []
        
        for url in discovered:
            print(f"\n🎯 Testing: {url}")
            findings = self.test_url(url, episodes=test_episodes)
            
            if findings:
                all_findings.extend(findings)
                print(f"  🚨 Found {len(findings)} potential vulnerability(ies)")
            else:
                print(f"  ✅ No vulnerabilities detected")
        
        # Phase 3: Report
        print("\n" + "="*70)
        print("📊 FINAL REPORT")
        print("="*70)
        print(f"\nTarget: {self.base_url}")
        print(f"Pages Discovered: {len(discovered)}")
        print(f"Vulnerabilities Found: {len(all_findings)}")
        
        if all_findings:
            print("\n🔴 VULNERABILITIES:")
            for finding in all_findings:
                print(f"  - {finding['url']}")
                print(f"    Type: {finding['type']}")
                print(f"    Confidence: {finding['confidence']}")
                print()
        else:
            print("\n✅ No vulnerabilities detected (or agent needs more training)")
        
        # Save report
        self.save_report(discovered, all_findings)
        
        return all_findings
    
    def test_url(self, url, episodes=3):
        """
        Test a specific URL for vulnerabilities using the trained agent
        """
        findings = []
        
        try:
            # Create environment for this specific URL
            env = WebSecEnv(target_url=url)
            
            for ep in range(episodes):
                state, _ = env.reset()
                done = False
                step = 0
                
                while not done and step < 30:
                    action = self.dqn_agent.act(state)
                    next_state, reward, terminated, truncated, info = env.step(action)
                    done = terminated or truncated
                    
                    # High reward = vulnerability found
                    if reward > 50:
                        findings.append({
                            'url': url,
                            'type': self.get_vuln_type(action),
                            'confidence': 'High' if reward > 80 else 'Medium',
                            'reward': reward
                        })
                    
                    state = next_state
                    step += 1
        except:
            pass  # URL might not be compatible with our environment
        
        return findings
    
    def get_vuln_type(self, action):
        """Map action to vulnerability type"""
        vuln_map = {
            3: "SQL Injection",
            4: "Cross-Site Scripting (XSS)",
            8: "Command Injection",
            9: "Insecure Direct Object Reference (IDOR)",
            10: "Server-Side Request Forgery (SSRF)",
            13: "SQL Injection (Advanced)",
            14: "XSS (Advanced)"
        }
        return vuln_map.get(action, "Unknown Vulnerability")
    
    def save_report(self, urls, findings):
        """Save scan report to file"""
        with open('scan_report.md', 'w') as f:
            f.write(f"# Security Scan Report\n\n")
            f.write(f"**Target**: {self.base_url}\n")
            f.write(f"**Date**: {__import__('datetime').datetime.now()}\n\n")
            
            f.write(f"## Discovered URLs ({len(urls)})\n\n")
            for url in urls:
                f.write(f"- {url}\n")
            
            f.write(f"\n## Vulnerabilities ({len(findings)})\n\n")
            if findings:
                for finding in findings:
                    f.write(f"### {finding['type']}\n")
                    f.write(f"- **URL**: {finding['url']}\n")
                    f.write(f"- **Confidence**: {finding['confidence']}\n\n")
            else:
                f.write("No vulnerabilities detected.\n")
        
        print(f"\n💾 Report saved to: scan_report.md")

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Autonomous Web Security Scanner")
    parser.add_argument("url", help="Target URL (e.g., http://localhost/dvwa)")
    parser.add_argument("--model", default="dqn_web_sec_model.pth", help="Trained model path")
    parser.add_argument("--depth", type=int, default=30, help="Crawl depth (max pages)")
    parser.add_argument("--episodes", type=int, default=3, help="Test episodes per URL")
    
    args = parser.parse_args()
    
    # Run autonomous scan
    agent = AutonomousSecurityAgent(args.url, args.model)
    agent.scan(crawl_depth=args.depth, test_episodes=args.episodes)

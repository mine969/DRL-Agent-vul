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
import datetime
from agent.dqn_agent import DQNAgent
from env.web_sec_env import WebSecEnv

# Vulnerability Knowledge Base
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
        """Generate comprehensive HTML vulnerability report"""
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"vulnerability_report_{timestamp}.html"
        
        # Calculate statistics
        critical_count = sum(1 for f in findings if VULNERABILITY_DATABASE.get(f['type'], {}).get('impact') == 'CRITICAL')
        high_count = sum(1 for f in findings if VULNERABILITY_DATABASE.get(f['type'], {}).get('impact') == 'HIGH')
        medium_count = sum(1 for f in findings if VULNERABILITY_DATABASE.get(f['type'], {}).get('impact') == 'MEDIUM')
        
        html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Security Vulnerability Report - {self.base_url}</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 20px;
            line-height: 1.6;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 10px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.3);
            overflow: hidden;
        }}
        .header {{
            background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
            color: white;
            padding: 40px;
            text-align: center;
        }}
        .header h1 {{ font-size: 2.5em; margin-bottom: 10px; }}
        .header p {{ font-size: 1.1em; opacity: 0.9; }}
        .stats {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            padding: 30px;
            background: #f8f9fa;
        }}
        .stat-card {{
            background: white;
            padding: 20px;
            border-radius: 8px;
            text-align: center;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        .stat-number {{
            font-size: 3em;
            font-weight: bold;
            margin: 10px 0;
        }}
        .stat-label {{ color: #666; font-size: 0.9em; }}
        .critical {{ color: #dc3545; }}
        .high {{ color: #fd7e14; }}
        .medium {{ color: #ffc107; }}
        .low {{ color: #28a745; }}
        .content {{ padding: 40px; }}
        .section {{ margin-bottom: 40px; }}
        .section h2 {{
            color: #2a5298;
            border-bottom: 3px solid #667eea;
            padding-bottom: 10px;
            margin-bottom: 20px;
        }}
        .vulnerability {{
            background: #fff;
            border-left: 5px solid #dc3545;
            padding: 25px;
            margin-bottom: 30px;
            border-radius: 5px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        .vulnerability.high {{ border-left-color: #fd7e14; }}
        .vulnerability.medium {{ border-left-color: #ffc107; }}
        .vulnerability.low {{ border-left-color: #28a745; }}
        .vuln-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 15px;
        }}
        .vuln-title {{ font-size: 1.5em; font-weight: bold; color: #333; }}
        .impact-badge {{
            padding: 8px 16px;
            border-radius: 20px;
            color: white;
            font-weight: bold;
            font-size: 0.9em;
        }}
        .impact-badge.CRITICAL {{ background: #dc3545; }}
        .impact-badge.HIGH {{ background: #fd7e14; }}
        .impact-badge.MEDIUM {{ background: #ffc107; color: #333; }}
        .impact-badge.LOW {{ background: #28a745; }}
        .cvss {{ 
            display: inline-block;
            background: #333;
            color: white;
            padding: 5px 12px;
            border-radius: 5px;
            margin-left: 10px;
            font-size: 0.9em;
        }}
        .vuln-url {{
            background: #f8f9fa;
            padding: 10px;
            border-radius: 5px;
            font-family: monospace;
            margin: 10px 0;
            word-break: break-all;
        }}
        .subsection {{
            margin: 20px 0;
        }}
        .subsection h4 {{
            color: #2a5298;
            margin-bottom: 10px;
            font-size: 1.1em;
        }}
        .subsection ul {{
            margin-left: 20px;
        }}
        .subsection li {{
            margin: 8px 0;
            color: #555;
        }}
        .alert-box {{
            background: #fff3cd;
            border: 1px solid #ffc107;
            border-radius: 5px;
            padding: 15px;
            margin: 15px 0;
        }}
        .alert-box strong {{ color: #856404; }}
        .remediation {{
            background: #d4edda;
            border: 1px solid #28a745;
            border-radius: 5px;
            padding: 15px;
            margin: 15px 0;
        }}
        .url-list {{
            background: #f8f9fa;
            padding: 20px;
            border-radius: 5px;
            max-height: 400px;
            overflow-y: auto;
        }}
        .url-list ul {{ list-style: none; }}
        .url-list li {{
            padding: 8px;
            border-bottom: 1px solid #dee2e6;
            font-family: monospace;
            font-size: 0.9em;
        }}
        .footer {{
            background: #2a5298;
            color: white;
            text-align: center;
            padding: 20px;
            font-size: 0.9em;
        }}
        @media print {{
            body {{ background: white; }}
            .container {{ box-shadow: none; }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🛡️ Security Vulnerability Report</h1>
            <p>Target: <strong>{self.base_url}</strong></p>
            <p>Generated: {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</p>
        </div>
        
        <div class="stats">
            <div class="stat-card">
                <div class="stat-label">Pages Discovered</div>
                <div class="stat-number">{len(urls)}</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">Total Vulnerabilities</div>
                <div class="stat-number critical">{len(findings)}</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">Critical Issues</div>
                <div class="stat-number critical">{critical_count}</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">High Severity</div>
                <div class="stat-number high">{high_count}</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">Medium Severity</div>
                <div class="stat-number medium">{medium_count}</div>
            </div>
        </div>
        
        <div class="content">
"""
        
        if findings:
            html_content += """
            <div class="section">
                <h2>🔴 Discovered Vulnerabilities</h2>
"""
            for idx, finding in enumerate(findings, 1):
                vuln_type = finding['type']
                vuln_info = VULNERABILITY_DATABASE.get(vuln_type, {})
                impact = vuln_info.get('impact', 'UNKNOWN')
                
                html_content += f"""
                <div class="vulnerability {impact.lower()}">
                    <div class="vuln-header">
                        <div class="vuln-title">#{idx}. {vuln_type}</div>
                        <div>
                            <span class="impact-badge {impact}">{impact}</span>
                            <span class="cvss">CVSS: {vuln_info.get('cvss_score', 'N/A')}</span>
                        </div>
                    </div>
                    
                    <div class="vuln-url">
                        <strong>Affected URL:</strong> {finding['url']}
                    </div>
                    
                    <div class="subsection">
                        <h4>📋 Description</h4>
                        <p>{vuln_info.get('description', 'No description available')}</p>
                    </div>
                    
                    <div class="alert-box">
                        <strong>⚠️ Real-World Impact:</strong><br>
                        {vuln_info.get('real_world_impact', 'Impact information not available')}
                    </div>
                    
                    <div class="subsection">
                        <h4>🎯 How Attackers Can Exploit This</h4>
                        <ul>
"""
                for step in vuln_info.get('exploitation', []):
                    html_content += f"                            <li>{step}</li>\n"
                
                html_content += """
                        </ul>
                    </div>
                    
                    <div class="subsection">
                        <h4>💥 Potential Damage</h4>
                        <ul>
"""
                for damage in vuln_info.get('damage_potential', []):
                    html_content += f"                            <li>{damage}</li>\n"
                
                html_content += """
                        </ul>
                    </div>
                    
                    <div class="remediation">
                        <h4>🛠️ How to Fix This</h4>
                        <ul>
"""
                for fix in vuln_info.get('remediation', []):
                    html_content += f"                            <li>{fix}</li>\n"
                
                html_content += """
                        </ul>
                    </div>
                </div>
"""
        else:
            html_content += """
            <div class="section">
                <h2>✅ No Vulnerabilities Detected</h2>
                <p>The scan did not detect any vulnerabilities. This could mean:</p>
                <ul>
                    <li>The website is well-secured</li>
                    <li>The AI agent needs more training</li>
                    <li>The website structure differs from the training environment</li>
                </ul>
            </div>
"""
        
        html_content += f"""
            <div class="section">
                <h2>📍 Discovered URLs ({len(urls)})</h2>
                <div class="url-list">
                    <ul>
"""
        for url in urls:
            html_content += f"                        <li>{url}</li>\n"
        
        html_content += """
                    </ul>
                </div>
            </div>
        </div>
        
        <div class="footer">
            <p>Generated by AI-Powered Security Scanner</p>
            <p><strong>⚠️ For Authorized Security Testing Only</strong></p>
        </div>
    </div>
</body>
</html>
"""
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print(f"\n💾 Detailed HTML report saved to: {filename}")
        print(f"   Open this file in your browser to view the full report")
        
        # Also save a simple markdown version
        md_filename = f"vulnerability_report_{timestamp}.md"
        with open(md_filename, 'w') as f:
            f.write(f"# Security Scan Report\n\n")
            f.write(f"**Target**: {self.base_url}\n")
            f.write(f"**Date**: {datetime.datetime.now()}\n\n")
            
            f.write(f"## Summary\n\n")
            f.write(f"- Pages Discovered: {len(urls)}\n")
            f.write(f"- Vulnerabilities Found: {len(findings)}\n")
            f.write(f"- Critical: {critical_count}\n")
            f.write(f"- High: {high_count}\n")
            f.write(f"- Medium: {medium_count}\n\n")
            
            if findings:
                f.write(f"## Vulnerabilities\n\n")
                for idx, finding in enumerate(findings, 1):
                    vuln_info = VULNERABILITY_DATABASE.get(finding['type'], {})
                    f.write(f"### {idx}. {finding['type']} ({vuln_info.get('impact', 'UNKNOWN')})\n\n")
                    f.write(f"- **URL**: {finding['url']}\n")
                    f.write(f"- **CVSS Score**: {vuln_info.get('cvss_score', 'N/A')}\n\n")
        
        print(f"💾 Markdown report saved to: {md_filename}")


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

"""Report generation utilities - separated for better code organization"""

from typing import List, Dict, Any
from dataclasses import dataclass
import datetime


@dataclass
class Finding:
    """Vulnerability finding structure"""
    url: str
    vuln_type: str
    confidence: str
    reward: float


class ReportGenerator:
    """Optimized report generator with template separation"""
    
    def __init__(self, base_url: str, timestamp: str):
        self.base_url = base_url
        self.timestamp = timestamp
    
    def generate_html_report(self, urls: List[str], findings: List[Finding], 
                            vuln_db: Dict[str, Any]) -> str:
        """Generate HTML report"""
        import os
        if not os.path.exists("reports"):
            os.makedirs("reports")
            
        filename = f"reports/vulnerability_report_{self.timestamp}.html"
        
        # Calculate statistics
        stats = self._calculate_stats(findings, vuln_db)
        
        # Generate HTML (template would ideally be in separate file)
        html = self._build_html_template(urls, findings, vuln_db, stats)
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(html)
        
        print(f"\n💾 HTML report saved to: {filename}")
        return filename
    
    def generate_txt_report(self, urls: List[str], findings: List[Finding],
                           vuln_db: Dict[str, Any]) -> str:
        """Generate plain text report"""
        import os
        if not os.path.exists("reports"):
            os.makedirs("reports")
            
        filename = f"reports/vulnerability_report_{self.timestamp}.txt"
        
        stats = self._calculate_stats(findings, vuln_db)
        
        with open(filename, 'w', encoding='utf-8') as f:
            self._write_txt_header(f, stats, len(urls), len(findings))
            self._write_txt_findings(f, findings, vuln_db)
            self._write_txt_urls(f, urls)
            self._write_txt_footer(f)
        
        print(f"💾 Text report saved to: {filename}")
        return filename
    
    def generate_md_report(self, urls: List[str], findings: List[Finding],
                          vuln_db: Dict[str, Any]) -> str:
        """Generate a clean, single Markdown report in the reports/ directory"""
        import os
        
        # Ensure reports directory exists
        if not os.path.exists("reports"):
            os.makedirs("reports")
            
        filename = f"reports/vulnerability_report_{self.timestamp}.md"
        
        stats = self._calculate_stats(findings, vuln_db)
        
        with open(filename, 'w', encoding='utf-8') as f:
            # Header
            f.write(f"# 🛡️ Security Scan Report\n\n")
            f.write(f"| Metadata | Value |\n")
            f.write(f"| :--- | :--- |\n")
            f.write(f"| **Target** | `{self.base_url}` |\n")
            f.write(f"| **Date** | {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')} |\n")
            f.write(f"| **Pages Scanned** | {len(urls)} |\n")
            f.write(f"| **Total Issues** | {len(findings)} |\n\n")
            
            # Executive Summary
            f.write(f"## 📊 Executive Summary\n\n")
            f.write(f"| Severity | Count | Status |\n")
            f.write(f"| :--- | :---: | :--- |\n")
            f.write(f"| 🔴 **CRITICAL** | {stats['critical']} | {'🚨 Action Required' if stats['critical'] > 0 else '✅ Clean'} |\n")
            f.write(f"| 🟠 **HIGH** | {stats['high']} | {'⚠️ Attention Needed' if stats['high'] > 0 else '✅ Clean'} |\n")
            f.write(f"| 🟡 **MEDIUM** | {stats['medium']} | {'⚠️ Review' if stats['medium'] > 0 else '✅ Clean'} |\n")
            f.write(f"| 🟢 **LOW** | {stats['low']} | {'ℹ️ Info' if stats['low'] > 0 else '✅ Clean'} |\n\n")
            
            if findings:
                f.write(f"## 🔴 Detailed Findings\n\n")
                for idx, finding in enumerate(findings, 1):
                    vuln_info = vuln_db.get(finding.vuln_type, {})
                    impact = vuln_info.get('impact', 'UNKNOWN')
                    emoji = "🔴" if impact == "CRITICAL" else "🟠" if impact == "HIGH" else "🟡"
                    
                    f.write(f"### {idx}. {emoji} {finding.vuln_type}\n\n")
                    f.write(f"> **Severity**: {impact} | **CVSS**: {vuln_info.get('cvss_score', 'N/A')} | **Confidence**: {finding.confidence}\n\n")
                    f.write(f"- **Vulnerable URL**: `{finding.url}`\n\n")
                    
                    f.write(f"**📝 Description**\n")
                    f.write(f"{vuln_info.get('description', 'N/A')}\n\n")
                    
                    f.write(f"**💥 Real-World Impact**\n")
                    f.write(f"{vuln_info.get('real_world_impact', 'N/A')}\n\n")
                    
                    # ADD EXPLOITATION STEPS
                    f.write(f"**⚔️ How to Exploit (Step-by-Step)**\n")
                    exploitation_steps = vuln_info.get('exploitation', [])
                    if exploitation_steps:
                        for step in exploitation_steps:
                            f.write(f"{step}\n")
                    else:
                        f.write(f"No exploitation steps available.\n")
                    f.write(f"\n")
                    
                    # ADD PROOF OF CONCEPT (COPY-PASTE READY)
                    f.write(f"**🧪 Proof of Concept (Copy & Paste)**\n")
                    f.write(f"```bash\n")
                    
                    # Generate specific PoC based on vulnerability type
                    vuln_type = finding.vuln_type
                    url = finding.url
                    
                    if "SQL Injection" in vuln_type:
                        f.write(f"# Test for SQL Injection\n")
                        f.write(f"curl -X POST '{url}' \\\n")
                        f.write(f"  -d \"username=admin' OR '1'='1&password=x\"\n\n")
                        f.write(f"# Time-based blind SQLi\n")
                        f.write(f"curl '{url}?id=1' OR SLEEP(5)--'\n\n")
                        f.write(f"# Extract database name\n")
                        f.write(f"curl '{url}?id=1' UNION SELECT database(),2,3--'\n")
                    
                    elif "XSS" in vuln_type:
                        f.write(f"# Test for XSS\n")
                        f.write(f"curl '{url}?q=<script>alert(1)</script>'\n\n")
                        f.write(f"# Advanced XSS payload\n")
                        f.write(f"curl '{url}?q=<img src=x onerror=alert(document.cookie)>'\n\n")
                        f.write(f"# Polyglot payload\n")
                        f.write(f"curl '{url}?q=javascript:/*--></title></style></textarea></script></xmp>\">\\\\'/*\\\"/*\\`/*\\' /*</template></noembed></noscript></title></style></script>--><svg/onload=alert(1)>'\n")
                    
                    elif "SSRF" in vuln_type:
                        f.write(f"# Test for SSRF\n")
                        f.write(f"curl '{url}?url=http://169.254.169.254/latest/meta-data/'\n\n")
                        f.write(f"# Try to access internal services\n")
                        f.write(f"curl '{url}?url=http://localhost:22'\n\n")
                        f.write(f"# AWS metadata\n")
                        f.write(f"curl '{url}?url=http://169.254.169.254/latest/meta-data/iam/security-credentials/'\n")
                    
                    elif "IDOR" in vuln_type:
                        f.write(f"# Test for IDOR\n")
                        f.write(f"curl '{url}?id=1'\n")
                        f.write(f"curl '{url}?id=2'\n")
                        f.write(f"curl '{url}?id=999'\n\n")
                        f.write(f"# Try accessing admin resources\n")
                        f.write(f"curl '{url}?uid=admin'\n")
                    
                    elif "Broken Access Control" in vuln_type:
                        f.write(f"# Test for BAC\n")
                        f.write(f"curl '{url}' \\\n")
                        f.write(f"  -H 'X-Original-URL: /admin'\n\n")
                        f.write(f"# Try direct access to admin endpoints\n")
                        f.write(f"curl '{url.rsplit('/', 1)[0]}/admin/users'\n")
                    
                    else:
                        f.write(f"# Manual testing required\n")
                        f.write(f"curl -v '{url}'\n")
                    
                    f.write(f"```\n\n")
                    
                    # ADD DAMAGE POTENTIAL
                    f.write(f"**💣 Potential Damage**\n")
                    damage_list = vuln_info.get('damage_potential', [])
                    if damage_list:
                        for damage in damage_list:
                            f.write(f"- {damage}\n")
                    else:
                        f.write(f"- No damage information available.\n")
                    f.write(f"\n")
                    
                    f.write(f"**🛠️ Remediation**\n")
                    for fix in vuln_info.get('remediation', []):
                        f.write(f"- {fix}\n")
                    f.write(f"\n---\n\n")
            else:
                f.write(f"## ✅ No Vulnerabilities Found\n")
                f.write(f"Great job! No security issues were detected during this scan.\n\n")
                
            f.write(f"\n*Generated by AI Security Scanner - For Authorized Use Only*")
        
        print(f"💾 Report saved to: {filename}")
        return filename
    
    def _calculate_stats(self, findings: List[Finding], vuln_db: Dict[str, Any]) -> Dict[str, int]:
        """Calculate vulnerability statistics"""
        stats = {'critical': 0, 'high': 0, 'medium': 0, 'low': 0}
        
        for finding in findings:
            impact = vuln_db.get(finding.vuln_type, {}).get('impact', '').upper()
            if impact in stats:
                stats[impact.lower()] += 1
        
        return stats
    
    def _write_txt_header(self, f, stats: Dict[str, int], url_count: int, vuln_count: int):
        """Write text report header"""
        f.write("=" * 70 + "\n")
        f.write("SECURITY VULNERABILITY REPORT\n")
        f.write("=" * 70 + "\n\n")
        f.write(f"Target: {self.base_url}\n")
        f.write(f"Scan Date: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Generated by: AI-Powered Security Scanner\n\n")
        
        f.write("-" * 70 + "\n")
        f.write("SUMMARY\n")
        f.write("-" * 70 + "\n")
        f.write(f"Pages Discovered:        {url_count}\n")
        f.write(f"Total Vulnerabilities:   {vuln_count}\n")
        f.write(f"  - Critical:            {stats['critical']}\n")
        f.write(f"  - High:                {stats['high']}\n")
        f.write(f"  - Medium:              {stats['medium']}\n\n")
    
    def _write_txt_findings(self, f, findings: List[Finding], vuln_db: Dict[str, Any]):
        """Write vulnerability findings to text report"""
        if findings:
            f.write("=" * 70 + "\n")
            f.write("VULNERABILITIES FOUND\n")
            f.write("=" * 70 + "\n\n")
            
            for idx, finding in enumerate(findings, 1):
                vuln_info = vuln_db.get(finding.vuln_type, {})
                impact = vuln_info.get('impact', 'UNKNOWN')
                
                f.write(f"[{idx}] {finding.vuln_type}\n")
                f.write("-" * 70 + "\n")
                f.write(f"Impact Level:  {impact}\n")
                f.write(f"CVSS Score:    {vuln_info.get('cvss_score', 'N/A')}\n")
                f.write(f"Affected URL:  {finding.url}\n\n")
                
                f.write(f"Description:\n")
                f.write(f"  {vuln_info.get('description', 'N/A')}\n\n")
                
                f.write(f"Real-World Impact:\n")
                f.write(f"  {vuln_info.get('real_world_impact', 'N/A')}\n\n")
                
                f.write(f"How Attackers Can Exploit:\n")
                for step in vuln_info.get('exploitation', []):
                    f.write(f"  {step}\n")
                f.write("\n")
                
                f.write(f"Potential Damage:\n")
                for damage in vuln_info.get('damage_potential', []):
                    f.write(f"  - {damage}\n")
                f.write("\n")
                
                f.write(f"How to Fix:\n")
                for fix in vuln_info.get('remediation', []):
                    f.write(f"  - {fix}\n")
                f.write("\n" + "=" * 70 + "\n\n")
        else:
            f.write("=" * 70 + "\n")
            f.write("NO VULNERABILITIES DETECTED\n")
            f.write("=" * 70 + "\n\n")
    
    def _write_txt_urls(self, f, urls: List[str]):
        """Write discovered URLs to text report"""
        f.write("=" * 70 + "\n")
        f.write("DISCOVERED URLS\n")
        f.write("=" * 70 + "\n\n")
        for idx, url in enumerate(urls, 1):
            f.write(f"{idx}. {url}\n")
    
    def _write_txt_footer(self, f):
        """Write text report footer"""
        f.write("\n" + "=" * 70 + "\n")
        f.write("END OF REPORT\n")
        f.write("=" * 70 + "\n")
        f.write("\nWARNING: For Authorized Security Testing Only!\n")
    
    def _build_html_template(self, urls: List[str], findings: List[Finding],
                            vuln_db: Dict[str, Any], stats: Dict[str, int]) -> str:
        """Build HTML report (simplified version - full template would be in separate file)"""
        # This is a simplified version - in production, use Jinja2 templates
        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Security Report - {self.base_url}</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }}
        .container {{ max-width: 1200px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; }}
        h1 {{ color: #2c3e50; }}
        .stats {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin: 20px 0; }}
        .stat-card {{ background: #ecf0f1; padding: 20px; border-radius: 8px; text-align: center; }}
        .stat-number {{ font-size: 2em; font-weight: bold; }}
        .critical {{ color: #e74c3c; }}
        .high {{ color: #e67e22; }}
        .medium {{ color: #f39c12; }}
        .vulnerability {{ background: #fff; border-left: 5px solid #e74c3c; padding: 20px; margin: 20px 0; border-radius: 5px; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>🛡️ Security Vulnerability Report</h1>
        <p><strong>Target:</strong> {self.base_url}</p>
        <p><strong>Generated:</strong> {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</p>
        
        <div class="stats">
            <div class="stat-card">
                <div>Pages Discovered</div>
                <div class="stat-number">{len(urls)}</div>
            </div>
            <div class="stat-card">
                <div>Total Vulnerabilities</div>
                <div class="stat-number critical">{len(findings)}</div>
            </div>
            <div class="stat-card">
                <div>Critical Issues</div>
                <div class="stat-number critical">{stats['critical']}</div>
            </div>
            <div class="stat-card">
                <div>High Severity</div>
                <div class="stat-number high">{stats['high']}</div>
            </div>
        </div>
        
        <h2>Vulnerabilities Found</h2>
"""
        
        for idx, finding in enumerate(findings, 1):
            vuln_info = vuln_db.get(finding.vuln_type, {})
            html += f"""
        <div class="vulnerability">
            <h3>#{idx}. {finding.vuln_type}</h3>
            <p><strong>Impact:</strong> {vuln_info.get('impact', 'UNKNOWN')}</p>
            <p><strong>CVSS Score:</strong> {vuln_info.get('cvss_score', 'N/A')}</p>
            <p><strong>URL:</strong> {finding.url}</p>
            <p>{vuln_info.get('description', '')}</p>
        </div>
"""
        
        html += """
    </div>
</body>
</html>
"""
        return html

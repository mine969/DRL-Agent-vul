"""
Zero-Day Hunter Module
======================

Advanced capability for discovering:
1. Zero-day vulnerabilities (novel attack vectors)
2. Weak configurations (security misconfigurations)
3. Latest CVEs (from online databases)
4. Fuzzing-based anomalies

This module uses:
- Mutation-based fuzzing
- CVE database integration
- Configuration scanning
- Anomaly detection
"""

import requests
import random
import json
from typing import List, Dict, Any
from datetime import datetime, timedelta


class ZeroDayHunter:
    """Advanced vulnerability discovery using fuzzing and CVE intelligence"""
    
    def __init__(self):
        self.cve_cache = []
        self.last_cve_fetch = None
        
        # Fuzzing templates for zero-day discovery
        self.fuzz_templates = {
            'buffer_overflow': [
                'A' * 1000,
                'A' * 5000,
                'A' * 10000,
                '%s' * 100,
                '%n' * 100,
            ],
            'format_string': [
                '%x' * 50,
                '%s%s%s%s%s',
                '%p%p%p%p',
                '%.1000d',
                '%n%n%n%n',
            ],
            'unicode_bypass': [
                '\u0000',
                '\u202e',  # Right-to-left override
                '\ufeff',  # Zero-width no-break space
                '\u200b',  # Zero-width space
                '\\u0000',
                '%u0000',
            ],
            'encoding_bypass': [
                '%2e%2e%2f',  # ../
                '%252e%252e%252f',  # Double encoded
                '..%c0%af',  # UTF-8 overlong
                '..%ef%bc%8f',  # Fullwidth slash
                '..%c1%9c',  # Overlong encoding
            ],
            'logic_bombs': [
                '2147483647',  # Max int32
                '-2147483648',  # Min int32
                '9999999999999999999',  # Huge number
                '0.0000000001',  # Tiny float
                'NaN',
                'Infinity',
                '-Infinity',
            ],
            'race_condition': [
                'CONCURRENT_REQUEST_1',
                'CONCURRENT_REQUEST_2',
                'RACE_CONDITION_TEST',
            ],
            'type_confusion': [
                '{"__proto__": {"isAdmin": true}}',
                '["constructor"]["prototype"]["isAdmin"] = true',
                'Object.prototype.isAdmin = true',
            ],
            'memory_corruption': [
                '\x00' * 1000,
                '\xff' * 1000,
                '\x90' * 1000,  # NOP sled
            ],
        }
        
        # Configuration weakness patterns
        self.config_checks = {
            'weak_ssl': [
                'TLS_RSA_WITH_RC4_128_MD5',
                'TLS_RSA_WITH_DES_CBC_SHA',
                'SSLv2',
                'SSLv3',
            ],
            'debug_enabled': [
                '/debug',
                '/trace',
                '?debug=true',
                '?trace=1',
                'X-Debug: 1',
            ],
            'default_creds': [
                ('admin', 'admin'),
                ('admin', 'password'),
                ('root', 'root'),
                ('admin', '123456'),
                ('administrator', 'administrator'),
            ],
            'exposed_endpoints': [
                '/.env',
                '/.git/config',
                '/phpinfo.php',
                '/server-status',
                '/actuator/health',
                '/metrics',
                '/.aws/credentials',
                '/config.json',
                '/web.config',
            ],
            'cors_misconfiguration': [
                'Origin: null',
                'Origin: http://evil.com',
                'Origin: http://localhost',
            ],
            'cache_poisoning': [
                'X-Forwarded-Host: evil.com',
                'X-Original-URL: /admin',
                'X-Rewrite-URL: /admin',
            ],
        }
    
    def fetch_latest_cves(self, limit=50) -> List[Dict[str, Any]]:
        """Fetch latest CVEs from NVD (National Vulnerability Database)"""
        # Cache CVEs for 1 hour
        if self.cve_cache and self.last_cve_fetch:
            if (datetime.now() - self.last_cve_fetch).seconds < 3600:
                return self.cve_cache
        
        try:
            # NVD API (free, no key required for basic usage)
            url = "https://services.nvd.nist.gov/rest/json/cves/2.0"
            
            # Get CVEs from last 30 days
            end_date = datetime.now()
            start_date = end_date - timedelta(days=30)
            
            params = {
                'pubStartDate': start_date.strftime('%Y-%m-%dT00:00:00.000'),
                'pubEndDate': end_date.strftime('%Y-%m-%dT23:59:59.999'),
                'resultsPerPage': limit,
            }
            
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                cves = []
                
                for item in data.get('vulnerabilities', []):
                    cve_data = item.get('cve', {})
                    cve_id = cve_data.get('id', '')
                    descriptions = cve_data.get('descriptions', [])
                    description = descriptions[0].get('value', '') if descriptions else ''
                    
                    # Extract CVSS score if available
                    metrics = cve_data.get('metrics', {})
                    cvss_score = 0.0
                    if 'cvssMetricV31' in metrics:
                        cvss_score = metrics['cvssMetricV31'][0].get('cvssData', {}).get('baseScore', 0.0)
                    
                    cves.append({
                        'id': cve_id,
                        'description': description,
                        'cvss_score': cvss_score,
                        'published': cve_data.get('published', ''),
                    })
                
                self.cve_cache = cves
                self.last_cve_fetch = datetime.now()
                return cves
            
        except Exception as e:
            print(f"⚠️ CVE fetch failed: {e}")
            return []
        
        return []
    
    def generate_fuzzing_payloads(self, category='all') -> List[str]:
        """Generate fuzzing payloads for zero-day discovery"""
        if category == 'all':
            payloads = []
            for cat_payloads in self.fuzz_templates.values():
                payloads.extend(cat_payloads)
            return payloads
        
        return self.fuzz_templates.get(category, [])
    
    def get_config_checks(self, category='all') -> List[Any]:
        """Get configuration weakness checks"""
        if category == 'all':
            checks = []
            for cat_checks in self.config_checks.values():
                if isinstance(cat_checks, list):
                    checks.extend(cat_checks)
            return checks
        
        return self.config_checks.get(category, [])
    
    def mutate_payload(self, base_payload: str, mutation_type='random') -> str:
        """Mutate a payload for zero-day discovery"""
        mutations = {
            'case_flip': lambda p: ''.join(c.upper() if random.random() > 0.5 else c.lower() for c in p),
            'char_insert': lambda p: p[:len(p)//2] + random.choice(['%00', '\x00', '\n', '\r']) + p[len(p)//2:],
            'char_delete': lambda p: p[:len(p)//2] + p[len(p)//2+1:] if len(p) > 1 else p,
            'repeat': lambda p: p * random.randint(2, 5),
            'reverse': lambda p: p[::-1],
            'url_encode': lambda p: ''.join(f'%{ord(c):02x}' for c in p),
            'double_encode': lambda p: ''.join(f'%25{ord(c):02x}' for c in p),
            'unicode': lambda p: ''.join(f'\\u{ord(c):04x}' for c in p),
        }
        
        if mutation_type == 'random':
            mutation_type = random.choice(list(mutations.keys()))
        
        return mutations.get(mutation_type, lambda p: p)(base_payload)
    
    def generate_cve_based_payloads(self, cve_list: List[Dict]) -> List[Dict[str, str]]:
        """Generate payloads based on recent CVEs"""
        payloads = []
        
        for cve in cve_list[:10]:  # Top 10 recent CVEs
            desc = cve['description'].lower()
            
            # Pattern matching for common vulnerability types
            if 'sql injection' in desc or 'sqli' in desc:
                payloads.append({
                    'type': 'SQL Injection',
                    'payload': "' OR 1=1-- (CVE-based)",
                    'cve': cve['id'],
                })
            
            elif 'cross-site scripting' in desc or 'xss' in desc:
                payloads.append({
                    'type': 'XSS',
                    'payload': "<script>alert('CVE')</script>",
                    'cve': cve['id'],
                })
            
            elif 'remote code execution' in desc or 'rce' in desc:
                payloads.append({
                    'type': 'RCE',
                    'payload': "; whoami",
                    'cve': cve['id'],
                })
            
            elif 'path traversal' in desc or 'directory traversal' in desc:
                payloads.append({
                    'type': 'Path Traversal',
                    'payload': "../../../../etc/passwd",
                    'cve': cve['id'],
                })
            
            elif 'deserialization' in desc:
                payloads.append({
                    'type': 'Deserialization',
                    'payload': 'O:8:"Evil":1:{s:4:"exec";s:6:"whoami";}',
                    'cve': cve['id'],
                })
        
        return payloads
    
    def check_weak_configuration(self, target_url: str) -> List[Dict[str, Any]]:
        """Check for weak configurations"""
        findings = []
        
        # Check for exposed files
        for endpoint in self.config_checks['exposed_endpoints']:
            try:
                response = requests.get(target_url + endpoint, timeout=5)
                if response.status_code == 200:
                    findings.append({
                        'type': 'Exposed File',
                        'endpoint': endpoint,
                        'severity': 'HIGH',
                        'description': f'Sensitive file exposed: {endpoint}',
                    })
            except:
                pass
        
        return findings
    
    def get_zero_day_actions(self) -> List[str]:
        """Get list of zero-day hunting actions"""
        return [
            'fuzz_buffer_overflow',
            'fuzz_format_string',
            'fuzz_unicode_bypass',
            'fuzz_encoding_bypass',
            'fuzz_logic_bombs',
            'fuzz_race_condition',
            'fuzz_type_confusion',
            'check_weak_ssl',
            'check_debug_enabled',
            'check_default_creds',
            'check_exposed_endpoints',
            'check_cors_misconfiguration',
            'check_cache_poisoning',
            'fetch_latest_cves',
            'mutate_known_payload',
        ]


# Singleton instance
zero_day_hunter = ZeroDayHunter()


if __name__ == "__main__":
    # Test the module
    hunter = ZeroDayHunter()
    
    print("🔍 Zero-Day Hunter Test")
    print("=" * 50)
    
    # Test CVE fetching
    print("\n📡 Fetching latest CVEs...")
    cves = hunter.fetch_latest_cves(limit=10)
    print(f"✅ Found {len(cves)} recent CVEs")
    for cve in cves[:3]:
        print(f"  - {cve['id']}: CVSS {cve['cvss_score']}")
    
    # Test fuzzing payloads
    print("\n💣 Generating fuzzing payloads...")
    fuzz_payloads = hunter.generate_fuzzing_payloads('buffer_overflow')
    print(f"✅ Generated {len(fuzz_payloads)} buffer overflow payloads")
    
    # Test mutation
    print("\n🧬 Testing payload mutation...")
    base = "' OR 1=1--"
    mutated = hunter.mutate_payload(base, 'url_encode')
    print(f"  Original: {base}")
    print(f"  Mutated:  {mutated}")
    
    # Test CVE-based payloads
    print("\n🎯 Generating CVE-based payloads...")
    cve_payloads = hunter.generate_cve_based_payloads(cves)
    print(f"✅ Generated {len(cve_payloads)} CVE-based payloads")
    
    print("\n✅ Zero-Day Hunter module ready!")

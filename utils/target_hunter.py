import requests
import random
import time
from urllib.parse import quote_plus
from bs4 import BeautifulSoup

class TargetHunter:
    """
    Advanced Target Discovery Module
    Uses Google Dorks and Shodan to find vulnerable targets.
    """
    
    def __init__(self, shodan_api_key=None):
        self.shodan_api_key = shodan_api_key
        self.shodan_base_url = "https://api.shodan.io"
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (X11; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/115.0'
        ]

    def dork_google(self, dork_query, num_results=10):
        """
        Performs a Google Dork search to find potential targets.
        WARNING: Automated scraping of Google is against TOS. Use with caution/proxies.
        """
        print(f"🔍 Dorking Google for: {dork_query}")
        results = set()
        
        # We'll use a few different search engines to avoid strict rate limits if possible, 
        # but for now let's try a basic Google scrape with headers.
        # A better approach for production is using the Custom Search JSON API.
        
        headers = {'User-Agent': random.choice(self.user_agents)}
        encoded_query = quote_plus(dork_query)
        url = f"https://www.google.com/search?q={encoded_query}&num={num_results}"
        
        try:
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                # This selector is fragile and changes often
                for a in soup.find_all('a', href=True):
                    href = a['href']
                    if href.startswith('http') and 'google.com' not in href:
                        # Basic filtering
                        results.add(href)
            elif response.status_code == 429:
                print("⚠️ Google Rate Limit Hit (429). Try again later or use proxies.")
        except Exception as e:
            print(f"❌ Dorking error: {e}")
            
        return list(results)

    def search_shodan(self, query, limit=5):
        """
        Searches Shodan for targets matching a query.
        Requires API Key.
        """
        if not self.shodan_api_key:
            print("⚠️ No Shodan API Key provided.")
            return []
            
        print(f"🌐 Searching Shodan for: {query}")
        targets = []
        
        try:
            url = f"{self.shodan_base_url}/shodan/host/search?key={self.shodan_api_key}&query={query}"
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                for match in data.get('matches', [])[:limit]:
                    ip_str = match.get('ip_str')
                    port = match.get('port')
                    if ip_str and port:
                        protocol = "https" if port == 443 else "http"
                        targets.append(f"{protocol}://{ip_str}:{port}")
            else:
                print(f"❌ Shodan API Error: {response.status_code} - {response.text}")
                
        except Exception as e:
            print(f"❌ Shodan error: {e}")
            
        return targets

    def search_crtsh(self, domain):
        """
        Searches crt.sh for subdomains (Certificate Transparency).
        """
        print(f"📜 Searching CRT.sh for: {domain}")
        results = set()
        try:
            url = f"https://crt.sh/?q=%25.{domain}&output=json"
            response = requests.get(url, timeout=15)
            if response.status_code == 200:
                data = response.json()
                for entry in data:
                    name_value = entry.get('name_value')
                    if name_value:
                        for sub in name_value.split('\n'):
                            if '*' not in sub:
                                results.add(f"https://{sub}")
                                results.add(f"http://{sub}")
            else:
                print(f"❌ CRT.sh Error: {response.status_code}")
        except Exception as e:
            print(f"❌ CRT.sh error: {e}")
        return list(results)

    def search_duckduckgo(self, query, num_results=10):
        """
        Searches DuckDuckGo for targets.
        """
        print(f"🦆 Searching DuckDuckGo for: {query}")
        results = set()
        try:
            # Using html.duckduckgo.com to avoid JS requirement
            headers = {'User-Agent': random.choice(self.user_agents)}
            url = f"https://html.duckduckgo.com/html/?q={quote_plus(query)}"
            response = requests.get(url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                for a in soup.find_all('a', class_='result__a'):
                    href = a.get('href')
                    if href and href.startswith('http'):
                        results.add(href)
        except Exception as e:
            print(f"❌ DuckDuckGo error: {e}")
        return list(results)[:num_results]

    def search_censys(self, query, api_id, api_secret, limit=5):
        """
        Searches Censys for targets.
        """
        if not api_id or not api_secret:
            print("⚠️ No Censys Credentials provided.")
            return []
            
        print(f"👁️ Searching Censys for: {query}")
        targets = []
        try:
            url = "https://search.censys.io/api/v2/hosts/search"
            auth = (api_id, api_secret)
            params = {'q': query, 'per_page': limit}
            
            response = requests.get(url, auth=auth, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                for hit in data.get('result', {}).get('hits', []):
                    ip = hit.get('ip')
                    if ip:
                        targets.append(f"http://{ip}") # Default to http, can check services for https
            else:
                print(f"❌ Censys API Error: {response.status_code}")
        except Exception as e:
            print(f"❌ Censys error: {e}")
        return targets

    def get_common_dorks(self):
        """Returns a list of effective dorks for bug bounty hunting."""
        return [
            'inurl:php?id=',
            'ext:php inurl:admin',
            'inurl:dashboard intitle:"dashboard"',
            'inurl:login intitle:"login"',
            'intext:"index of /" .env',
            'inurl:wp-content/uploads',
            'site:github.com "password"',
            'inurl:view/view.shtml',
            'intitle:"webcam 7"',
            'inurl:8080/jmx-console'
        ]

    def get_shodan_queries(self):
        """Returns common Shodan queries."""
        return [
            'product:"Apache Tomcat"',
            'product:"nginx"',
            'port:8080',
            'title:"Dashboard"',
            'html:"defaced"',
            'vuln:CVE-2023-23397'
        ]

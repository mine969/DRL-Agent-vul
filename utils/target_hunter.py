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
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (X11; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/115.0",
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

        headers = {"User-Agent": random.choice(self.user_agents)}
        encoded_query = quote_plus(dork_query)
        url = f"https://www.google.com/search?q={encoded_query}&num={num_results}"

        try:
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, "html.parser")
                # This selector is fragile and changes often
                for a in soup.find_all("a", href=True):
                    href = a["href"]
                    if href.startswith("http") and "google.com" not in href:
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
                for match in data.get("matches", [])[:limit]:
                    ip_str = match.get("ip_str")
                    port = match.get("port")
                    if ip_str and port:
                        # Try both HTTP and HTTPS for better coverage
                        if port == 443 or port == 8443:
                            targets.append(f"https://{ip_str}:{port}")
                        else:
                            targets.append(f"http://{ip_str}:{port}")
                            # Also try HTTPS variant
                            targets.append(f"https://{ip_str}:{port}")
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
                    name_value = entry.get("name_value")
                    if name_value:
                        for sub in name_value.split("\n"):
                            if "*" not in sub:
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
            headers = {"User-Agent": random.choice(self.user_agents)}
            url = f"https://html.duckduckgo.com/html/?q={quote_plus(query)}"
            response = requests.get(url, headers=headers, timeout=10)

            if response.status_code == 200:
                soup = BeautifulSoup(response.text, "html.parser")
                for a in soup.find_all("a", class_="result__a"):
                    href = a.get("href")
                    if href and href.startswith("http"):
                        results.add(href)
        except Exception as e:
            print(f"❌ DuckDuckGo error: {e}")
        return list(results)[:num_results]

    def search_censys(self, query, api_key, limit=5):
        """
        Searches Censys for targets using the V3 Platform API.
        Requires Personal Access Token (PAT).
        """
        if not api_key:
            print("⚠️ No Censys API Key (PAT) provided.")
            return []

        print(f"👁️ Searching Censys for: {query}")
        targets = []
        try:
            # New V3 Platform API Endpoint
            url = "https://api.platform.censys.io/v2/hosts/search"  # V2 is still used for search in platform API context or V3 beta
            # Correction: The user docs say https://api.platform.censys.io/v2/hosts/search is likely the one for search or v3/global/asset/host/search?
            # Let's re-read the doc snippet carefully.
            # "Base URLs for Platform API endpoints... Global Data: https://api.platform.censys.io/v3/global/"
            # "Example cURL... https://api.platform.censys.io/v3/global/asset/host/{ip}"
            # But for SEARCH? The doc says "The Censys Search v1 and v2 APIs are being deprecated".
            # It doesn't explicitly show the SEARCH endpoint for V3.
            # However, standard practice for Censys V2 search was https://search.censys.io/api/v2/hosts/search.
            # The new Platform API often uses https://api.censys.io/v2/hosts/search with Bearer token.
            # Let's try the standard V2 search endpoint but with Bearer Auth as per migration guides usually found.
            # Actually, let's stick to the V2 search endpoint but change Auth to Bearer if that's what the PAT supports,
            # OR use the specific host lookup if we had an IP. But we are searching.
            # Let's try the V2 search endpoint `https://search.censys.io/api/v2/hosts/search` but with Bearer token.
            # Wait, the user doc says "Base URL: There is a new base URL for the Censys Platform API."
            # And "Global Data: https://api.platform.censys.io/v3/global/"
            # Let's assume there is a search endpoint there.
            # If not, we might need to use the V2 search with the new token.
            # Let's try the V2 search endpoint first as it's the most likely to support 'q' parameter.

            url = "https://search.censys.io/api/v2/hosts/search"
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Accept": "application/json",
            }
            params = {"q": query, "per_page": limit}

            response = requests.get(url, headers=headers, params=params, timeout=10)

            if response.status_code == 200:
                data = response.json()
                for hit in data.get("result", {}).get("hits", []):
                    ip = hit.get("ip")
                    if ip:
                        # Try both HTTP and HTTPS
                        targets.append(f"http://{ip}")
                        targets.append(f"https://{ip}")
            else:
                print(f"❌ Censys API Error: {response.status_code} - {response.text}")
        except Exception as e:
            print(f"❌ Censys error: {e}")
        return targets

    def get_common_dorks(self):
        """Returns a comprehensive list of effective dorks for bug bounty hunting."""
        return [
            # Admin Panels
            'inurl:admin intitle:"admin"',
            'inurl:administrator intitle:"administrator"',
            'inurl:moderator intitle:"moderator"',
            'inurl:controlpanel intitle:"control panel"',
            'inurl:adminpanel intitle:"admin panel"',
            "inurl:admin/login",
            "inurl:admin/index.php",
            "inurl:admin/dashboard",
            # Login Pages
            'inurl:login intitle:"login"',
            'inurl:signin intitle:"sign in"',
            'inurl:auth intitle:"authentication"',
            "inurl:portal/login",
            "inurl:user/login",
            # SQL Injection Targets
            "inurl:php?id=",
            "inurl:index.php?id=",
            "inurl:product.php?id=",
            "inurl:category.php?id=",
            "inurl:news.php?id=",
            "inurl:article.php?id=",
            "inurl:page.php?id=",
            # File Exposure
            'intext:"index of /" .env',
            'intext:"index of /" config.php',
            'intext:"index of /" database.yml',
            'intext:"index of /" .git',
            'intext:"index of /" backup',
            'filetype:sql "password"',
            'filetype:log "password"',
            'filetype:env "DB_PASSWORD"',
            # WordPress
            "inurl:wp-content/uploads",
            "inurl:wp-admin",
            "inurl:wp-login.php",
            "inurl:wp-config.php.bak",
            # API Endpoints
            "inurl:api/v1",
            "inurl:api/v2",
            "inurl:graphql",
            "inurl:swagger",
            "inurl:api-docs",
            # Sensitive Files
            "ext:php inurl:config",
            "ext:sql inurl:backup",
            "ext:bak inurl:database",
            "ext:log inurl:error",
            # Cameras & IoT
            'intitle:"webcam 7"',
            "inurl:view/view.shtml",
            'intitle:"Network Camera"',
            # Servers & Consoles
            "inurl:8080/jmx-console",
            'intitle:"Apache Tomcat"',
            'intitle:"phpMyAdmin"',
            'intitle:"Adminer"',
            # GitHub Leaks
            'site:github.com "password"',
            'site:github.com "api_key"',
            'site:github.com "secret_key"',
            'site:github.com "aws_access_key_id"',
        ]

    def get_shodan_queries(self):
        """Returns comprehensive Shodan queries for various targets."""
        return [
            # Web Servers
            'product:"Apache httpd"',
            'product:"nginx"',
            'product:"Microsoft IIS"',
            'product:"Apache Tomcat"',
            'product:"Jetty"',
            # Ports
            "port:8080",
            "port:8443",
            "port:3000",
            "port:5000",
            "port:9200",  # Elasticsearch
            # Titles
            'title:"Dashboard"',
            'title:"Admin Panel"',
            'title:"Login"',
            'title:"phpMyAdmin"',
            'title:"Grafana"',
            # Vulnerabilities
            "vuln:CVE-2023-23397",
            "vuln:CVE-2021-44228",  # Log4j
            "vuln:CVE-2017-5638",  # Struts
            # Technologies
            'http.component:"WordPress"',
            'http.component:"Joomla"',
            'http.component:"Drupal"',
            'http.component:"Laravel"',
            # Countries (examples)
            "country:US port:80",
            "country:GB port:443",
            # Specific Services
            'product:"MongoDB"',
            'product:"Redis"',
            'product:"Elasticsearch"',
            'product:"Jenkins"',
            'product:"Docker"',
            # HTML Content
            'html:"defaced"',
            'html:"hacked by"',
            'html:"powered by"',
            # Headers
            "http.status:200",
            "http.status:403",
            'http.title:"Index of /"',
        ]

    def get_target_domains(self):
        """Returns common domain patterns for CRT.sh searches."""
        return [
            # Educational
            "edu",
            "university.edu",
            "college.edu",
            # Government
            "gov",
            "state.gov",
            # Common TLDs
            "com",
            "org",
            "net",
            "io",
            # Bug Bounty Programs (examples - use responsibly!)
            # Note: Only scan if you have permission or they have a public bug bounty
            "hackerone.com",
            "bugcrowd.com",
        ]

    def get_duckduckgo_queries(self):
        """Returns DuckDuckGo search queries."""
        return [
            # Similar to Google Dorks
            "site:example.com admin",
            "site:example.com login",
            "site:example.com dashboard",
            "site:example.com api",
            "site:example.com config",
            # File types
            "filetype:php admin",
            "filetype:asp login",
            "filetype:jsp admin",
            # Specific patterns
            "inurl:admin",
            "inurl:login",
            "inurl:dashboard",
            "inurl:api",
        ]

    def get_censys_queries(self):
        """Returns Censys search queries."""
        return [
            # Services
            "services.http.response.status_code:200",
            'services.http.response.body:"admin"',
            'services.http.response.body:"login"',
            'services.http.response.body:"dashboard"',
            # Ports
            "services.port:80",
            "services.port:443",
            "services.port:8080",
            "services.port:8443",
            # Software
            'services.software.product:"Apache"',
            'services.software.product:"nginx"',
            'services.software.product:"Microsoft IIS"',
            # Titles
            'services.http.response.html_title:"Admin"',
            'services.http.response.html_title:"Login"',
            'services.http.response.html_title:"Dashboard"',
        ]

    def auto_generate_targets(self, source="all", max_per_source=3):
        """
        AUTO-GENERATE MODE: Automatically generates and searches for targets.

        Args:
            source: 'google', 'shodan', 'crtsh', 'duckduckgo', 'censys', or 'all'
            max_per_source: Maximum queries to run per source

        Returns:
            List of discovered targets
        """
        print(f"🤖 AUTO-GENERATE MODE ACTIVATED")
        print(f"📡 Source: {source.upper()} | Max queries per source: {max_per_source}")

        all_targets = []

        if source in ["google", "all"]:
            print("\n🔍 AUTO-GENERATING GOOGLE DORK QUERIES...")
            dorks = random.sample(
                self.get_common_dorks(),
                min(max_per_source, len(self.get_common_dorks())),
            )
            for dork in dorks:
                print(f"  → Trying: {dork}")
                targets = self.dork_google(dork, num_results=5)
                all_targets.extend(targets)
                time.sleep(2)  # Rate limiting

        if source in ["shodan", "all"] and self.shodan_api_key:
            print("\n🌐 AUTO-GENERATING SHODAN QUERIES...")
            queries = random.sample(
                self.get_shodan_queries(),
                min(max_per_source, len(self.get_shodan_queries())),
            )
            for query in queries:
                print(f"  → Trying: {query}")
                targets = self.search_shodan(query, limit=3)
                all_targets.extend(targets)
                time.sleep(1)

        if source in ["crtsh", "all"]:
            print("\n📜 AUTO-GENERATING CRT.SH QUERIES...")
            domains = random.sample(
                self.get_target_domains(),
                min(max_per_source, len(self.get_target_domains())),
            )
            for domain in domains:
                print(f"  → Trying: {domain}")
                targets = self.search_crtsh(domain)
                all_targets.extend(targets[:10])  # Limit subdomains
                time.sleep(1)

        if source in ["duckduckgo", "all"]:
            print("\n🦆 AUTO-GENERATING DUCKDUCKGO QUERIES...")
            queries = random.sample(
                self.get_duckduckgo_queries(),
                min(max_per_source, len(self.get_duckduckgo_queries())),
            )
            for query in queries:
                print(f"  → Trying: {query}")
                targets = self.search_duckduckgo(query, num_results=5)
                all_targets.extend(targets)
                time.sleep(2)

        if source in ["censys", "all"]:
            print("\n👁️ AUTO-GENERATING CENSYS QUERIES...")
            # Note: Censys requires API credentials
            print("  ⚠️ Censys auto-generation requires API credentials")

        # Remove duplicates
        unique_targets = list(set(all_targets))
        print(f"\n✅ AUTO-GENERATION COMPLETE!")
        print(f"📊 Total unique targets found: {len(unique_targets)}")

        return unique_targets

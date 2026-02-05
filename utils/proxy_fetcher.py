"""
Proxy Fetcher - Automatically fetch free proxies from public sources
"""

import requests
from bs4 import BeautifulSoup
import time
from typing import List


class ProxyFetcher:
    """Fetch and validate free proxies from public sources"""

    @staticmethod
    def fetch_from_free_proxy_list() -> List[str]:
        """Fetch proxies from free-proxy-list.net"""
        proxies = []
        try:
            url = "https://free-proxy-list.net/"
            response = requests.get(url, timeout=10)
            soup = BeautifulSoup(response.content, "html.parser")

            table = soup.find("table", {"class": "table table-striped table-bordered"})
            if table:
                rows = table.find_all("tr")[1:]  # Skip header
                for row in rows[:50]:  # Get first 50
                    cols = row.find_all("td")
                    if len(cols) >= 7:
                        ip = cols[0].text.strip()
                        port = cols[1].text.strip()
                        https = cols[6].text.strip()

                        protocol = "https" if https == "yes" else "http"
                        proxies.append(f"{protocol}://{ip}:{port}")

            print(f"✅ Fetched {len(proxies)} proxies from free-proxy-list.net")
        except Exception as e:
            print(f"❌ Error fetching from free-proxy-list.net: {e}")

        return proxies

    @staticmethod
    def fetch_from_proxy_scrape() -> List[str]:
        """Fetch proxies from proxyscrape.com API"""
        proxies = []
        try:
            url = "https://api.proxyscrape.com/v2/?request=get&protocol=http&timeout=10000&country=all&ssl=all&anonymity=all"
            response = requests.get(url, timeout=10)

            if response.status_code == 200:
                proxy_list = response.text.strip().split("\n")
                for proxy in proxy_list[:50]:  # Limit to 50
                    if proxy.strip():
                        proxies.append(f"http://{proxy.strip()}")

            print(f"✅ Fetched {len(proxies)} proxies from proxyscrape.com")
        except Exception as e:
            print(f"❌ Error fetching from proxyscrape.com: {e}")

        return proxies

    @staticmethod
    def fetch_from_geonode() -> List[str]:
        """Fetch proxies from geonode.com API"""
        proxies = []
        try:
            url = "https://proxylist.geonode.com/api/proxy-list?limit=100&page=1&sort_by=lastChecked&sort_type=desc"
            response = requests.get(url, timeout=10)

            if response.status_code == 200:
                data = response.json()
                for proxy in data.get("data", [])[:50]:
                    ip = proxy.get("ip")
                    port = proxy.get("port")
                    protocols = proxy.get("protocols", [])

                    if ip and port and protocols:
                        protocol = protocols[0] if protocols else "http"
                        proxies.append(f"{protocol}://{ip}:{port}")

            print(f"✅ Fetched {len(proxies)} proxies from geonode.com")
        except Exception as e:
            print(f"❌ Error fetching from geonode.com: {e}")

        return proxies

    @staticmethod
    def fetch_from_proxy_list_download() -> List[str]:
        """Fetch proxies from proxy-list.download"""
        proxies = []
        try:
            url = "https://www.proxy-list.download/api/v1/get?type=http"
            response = requests.get(url, timeout=10)

            if response.status_code == 200:
                proxy_list = response.text.strip().split("\n")
                for proxy in proxy_list[:50]:
                    if proxy.strip():
                        proxies.append(f"http://{proxy.strip()}")

            print(f"✅ Fetched {len(proxies)} proxies from proxy-list.download")
        except Exception as e:
            print(f"❌ Error fetching from proxy-list.download: {e}")

        return proxies

    @staticmethod
    def fetch_from_pubproxy() -> List[str]:
        """Fetch proxies from pubproxy.com API"""
        proxies = []
        try:
            # Fetch multiple times to get more proxies
            for _ in range(5):
                url = "http://pubproxy.com/api/proxy?limit=5&format=txt&type=http"
                response = requests.get(url, timeout=10)

                if response.status_code == 200:
                    proxy_list = response.text.strip().split("\n")
                    for proxy in proxy_list:
                        if proxy.strip():
                            proxies.append(f"http://{proxy.strip()}")

                time.sleep(0.5)  # Rate limit

            print(f"✅ Fetched {len(proxies)} proxies from pubproxy.com")
        except Exception as e:
            print(f"❌ Error fetching from pubproxy.com: {e}")

        return proxies

    @staticmethod
    def fetch_from_github_proxy_list() -> List[str]:
        """Fetch proxies from GitHub proxy lists"""
        proxies = []
        try:
            # TheSpeedX/PROXY-List is a popular GitHub repo
            url = (
                "https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/http.txt"
            )
            response = requests.get(url, timeout=10)

            if response.status_code == 200:
                proxy_list = response.text.strip().split("\n")
                for proxy in proxy_list[:100]:
                    if proxy.strip() and ":" in proxy:
                        proxies.append(f"http://{proxy.strip()}")

            print(f"✅ Fetched {len(proxies)} proxies from GitHub")
        except Exception as e:
            print(f"❌ Error fetching from GitHub: {e}")

        return proxies

    @staticmethod
    def fetch_all() -> List[str]:
        """Fetch proxies from all sources"""
        print("🔍 Fetching free proxies from multiple sources...")

        all_proxies = []

        # Source 1: free-proxy-list.net
        all_proxies.extend(ProxyFetcher.fetch_from_free_proxy_list())
        time.sleep(1)

        # Source 2: proxyscrape.com
        all_proxies.extend(ProxyFetcher.fetch_from_proxy_scrape())
        time.sleep(1)

        # Source 3: geonode.com
        all_proxies.extend(ProxyFetcher.fetch_from_geonode())
        time.sleep(1)

        # Source 4: proxy-list.download
        all_proxies.extend(ProxyFetcher.fetch_from_proxy_list_download())
        time.sleep(1)

        # Source 5: pubproxy.com
        all_proxies.extend(ProxyFetcher.fetch_from_pubproxy())
        time.sleep(1)

        # Source 6: GitHub proxy lists
        all_proxies.extend(ProxyFetcher.fetch_from_github_proxy_list())

        # Remove duplicates
        all_proxies = list(set(all_proxies))

        print(f"\n✅ Total unique proxies fetched: {len(all_proxies)}")
        return all_proxies

    @staticmethod
    def save_to_file(proxies: List[str], filename: str = "proxies.txt"):
        """Save proxies to a file"""
        try:
            with open(filename, "w") as f:
                f.write("# Auto-fetched proxies\n")
                f.write(f"# Fetched at: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"# Total: {len(proxies)}\n\n")
                for proxy in proxies:
                    f.write(f"{proxy}\n")

            print(f"💾 Proxies saved to {filename}")
            return filename
        except Exception as e:
            print(f"❌ Error saving proxies: {e}")
            return None


if __name__ == "__main__":
    # Test the fetcher
    fetcher = ProxyFetcher()
    proxies = fetcher.fetch_all()

    if proxies:
        fetcher.save_to_file(proxies)
    else:
        print("❌ No proxies fetched.")

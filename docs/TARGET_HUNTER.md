# 🌍 Targetless Hunter Mode

The **Targetless Hunter** mode is a powerful feature that allows the AI Security Scanner to automatically discover potential targets using various OSINT (Open Source Intelligence) sources. Instead of providing a single URL, you provide search queries, and the scanner finds the targets for you.

## 🚀 Supported Sources

The scanner currently supports the following sources for target discovery:

### 1. 🔍 Google Dorks

Uses advanced Google search operators to find vulnerable websites.

- **Usage**: Provide a dork query (e.g., `inurl:php?id=`).
- **Limit**: Be careful with rate limits. The scanner attempts to be stealthy, but aggressive dorking can get your IP blocked by Google.

### 2. 🌐 Shodan

The search engine for Internet-connected devices.

- **Usage**: Provide a Shodan query (e.g., `product:"Apache Tomcat"`) and your **Shodan API Key**.
- **Capabilities**: Excellent for finding specific services, ports, and vulnerable versions.

### 3. 📜 CRT.sh (Certificate Transparency)

Finds subdomains by searching Certificate Transparency logs.

- **Usage**: Provide a domain name (e.g., `example.com`).
- **Benefit**: Completely passive and free. Great for mapping an organization's attack surface.

### 4. 🦆 DuckDuckGo

An alternative search engine to Google.

- **Usage**: Provide a search query.
- **Benefit**: Less strict rate limiting than Google, good for finding indexed pages.

### 5. 👁️ Censys

A search engine for finding hosts and services.

- **Usage**: Provide a query, **API ID**, and **API Secret**.
- **Benefit**: High-quality data on exposed services and hosts.

## 💻 CLI Usage

You can use the Targetless Hunter mode from the command line:

```bash
# Google Dorking
python autonomous_scan.py --mode targetless --dork "inurl:admin/login.php" --limit 10

# Shodan Search
python autonomous_scan.py --mode targetless --shodan-query "product:nginx" --shodan-key YOUR_KEY

# CRT.sh Subdomain Enumeration
python autonomous_scan.py --mode targetless --crtsh "example.com"

# DuckDuckGo Search
python autonomous_scan.py --mode targetless --duckduckgo "site:example.com filetype:pdf"

# Censys Search
python autonomous_scan.py --mode targetless --censys-query "services.port: 80" --censys-id YOUR_ID --censys-secret YOUR_SECRET

# Combined Hunting (All Sources)
python autonomous_scan.py --mode targetless \
    --dork "inurl:php?id=" \
    --shodan-query "product:nginx" --shodan-key KEY \
    --crtsh "example.com" \
    --duckduckgo "site:example.com" \
    --limit 10
```

## 🖥️ GUI Usage

1. Select **🌍 TARGETLESS HUNTER** from the "SCAN MODE" section.
2. The **Target Discovery** panel will appear.
3. Fill in the fields for the sources you want to use. You can use multiple sources simultaneously!
4. Click **🚀 LAUNCH SCAN**.
5. The scanner will aggregate unique targets from all sources and begin scanning them one by one.

## ⚠️ Legal & Ethical Warning

**Targetless Hunting is powerful but dangerous.**

- **Authorization**: Only scan targets you have permission to test or that fall within a Bug Bounty program's scope.
- **Scope**: Automated discovery can accidentally include out-of-scope targets. Verify targets before attacking.
- **Rate Limits**: Respect the rate limits of the search engines (Google, Shodan, etc.).

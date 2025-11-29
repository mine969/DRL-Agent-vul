# 🌍 Targetless Hunter Mode

The **Targetless Hunter** mode is a powerful feature that allows the AI Security Scanner to automatically discover potential targets using various OSINT (Open Source Intelligence) sources. Instead of providing a single URL, you can either provide search queries manually OR use **auto-generate mode** to let the scanner create queries automatically.

## 🚀 Supported Sources

The scanner currently supports the following sources for target discovery:

### 1. 🔍 Google Dorks

Uses advanced Google search operators to find vulnerable websites.

- **Usage**: Provide a dork query (e.g., `inurl:php?id=`) or use auto-generate.
- **Auto-Database**: 60+ pre-configured dorks (admin panels, SQL injection targets, file exposure, etc.)
- **Limit**: Be careful with rate limits. The scanner attempts to be stealthy, but aggressive dorking can get your IP blocked by Google.

### 2. 🌐 Shodan

The search engine for Internet-connected devices.

- **Usage**: Provide a Shodan query (e.g., `product:"Apache Tomcat"`) and your **Shodan API Key**, or use auto-generate.
- **Auto-Database**: 30+ pre-configured queries (web servers, ports, vulnerabilities, technologies)
- **Capabilities**: Excellent for finding specific services, ports, and vulnerable versions.

### 3. 📜 CRT.sh (Certificate Transparency)

Finds subdomains by searching Certificate Transparency logs.

- **Usage**: Provide a domain name (e.g., `example.com`) or use auto-generate.
- **Auto-Database**: Common TLDs and domain patterns
- **Benefit**: Completely passive and free. Great for mapping an organization's attack surface.

### 4. 🦆 DuckDuckGo

An alternative search engine to Google.

- **Usage**: Provide a search query or use auto-generate.
- **Auto-Database**: Pre-configured search patterns
- **Benefit**: Less strict rate limiting than Google, good for finding indexed pages.

### 5. 👁️ Censys

A search engine for finding hosts and services.

- **Usage**: Provide a query, **API ID**, and **API Secret**.
- **Auto-Database**: Pre-configured service and port queries
- **Benefit**: High-quality data on exposed services and hosts.

## 🤖 Auto-Generate Mode (NEW!)

**Auto-generate mode** automatically creates and runs queries from a database of 100+ pre-configured searches. No manual query creation needed!

### How It Works

The scanner randomly selects queries from comprehensive databases:

- **60+ Google Dorks**: Admin panels, SQL injection targets, file exposure, WordPress, APIs, GitHub leaks
- **30+ Shodan Queries**: Web servers, ports, CVEs, technologies, specific services
- **Domain Patterns**: Educational (.edu), government (.gov), common TLDs
- **DuckDuckGo Queries**: File types, URL patterns, site-specific searches
- **Censys Queries**: Services, ports, software, HTML titles

### CLI Usage - Auto-Generate

```bash
# Full Auto-Generate (All Sources)
python autonomous_scan.py --auto-generate

# Auto-Generate from Specific Source
python autonomous_scan.py --auto-generate --auto-source google
python autonomous_scan.py --auto-generate --auto-source shodan --shodan-key YOUR_KEY
python autonomous_scan.py --auto-generate --auto-source crtsh

# Control Query Count
python autonomous_scan.py --auto-generate --auto-max 5  # Run 5 queries per source

# Targetless Mode (Auto-triggers auto-generate)
python autonomous_scan.py --mode targetless
```

### Example Output

```
🤖 AUTO-GENERATE MODE ACTIVATED!
📡 Source: ALL | Max queries per source: 3

🔍 AUTO-GENERATING GOOGLE DORK QUERIES...
  → Trying: inurl:admin intitle:"admin"
  → Trying: inurl:php?id=
  → Trying: intext:"index of /" .env

🌐 AUTO-GENERATING SHODAN QUERIES...
  → Trying: product:"nginx"
  → Trying: port:8080
  → Trying: title:"Dashboard"

📜 AUTO-GENERATING CRT.SH QUERIES...
  → Trying: edu
  → Trying: gov

✅ AUTO-GENERATION COMPLETE!
📊 Total unique targets found: 47
```

## 💻 CLI Usage - Manual Queries

You can still provide manual queries if you prefer:

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
3. **Option A - Manual**: Fill in the fields for the sources you want to use.
4. **Option B - Auto**: Leave fields empty and the scanner will auto-generate queries.
5. Click **🚀 LAUNCH SCAN**.
6. The scanner will aggregate unique targets from all sources and begin scanning them one by one.

## 📊 Query Database Highlights

### Google Dorks (60+)

- Admin panels: `inurl:admin`, `inurl:administrator`, `inurl:controlpanel`
- SQL injection: `inurl:php?id=`, `inurl:product.php?id=`, `inurl:news.php?id=`
- File exposure: `intext:"index of /" .env`, `filetype:sql "password"`
- WordPress: `inurl:wp-admin`, `inurl:wp-config.php.bak`
- APIs: `inurl:api/v1`, `inurl:graphql`, `inurl:swagger`
- GitHub leaks: `site:github.com "password"`, `site:github.com "api_key"`

### Shodan Queries (30+)

- Web servers: `product:"Apache httpd"`, `product:"nginx"`, `product:"Microsoft IIS"`
- Ports: `port:8080`, `port:8443`, `port:9200`
- Vulnerabilities: `vuln:CVE-2021-44228` (Log4j), `vuln:CVE-2017-5638` (Struts)
- Technologies: `http.component:"WordPress"`, `http.component:"Laravel"`
- Services: `product:"MongoDB"`, `product:"Redis"`, `product:"Jenkins"`

## ⚠️ Legal & Ethical Warning

**Targetless Hunting is powerful but dangerous.**

- **Authorization**: Only scan targets you have permission to test or that fall within a Bug Bounty program's scope.
- **Scope**: Automated discovery can accidentally include out-of-scope targets. Verify targets before attacking.
- **Rate Limits**: Respect the rate limits of the search engines (Google, Shodan, etc.).
- **Responsibility**: Auto-generate mode can discover many targets quickly. Ensure you have permission for ALL discovered targets.

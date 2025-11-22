# Autonomous Web Security Scanner

## 🚀 Just Give It a Homepage!

The agent will automatically:

1. **Crawl** the website to discover all pages
2. **Find** common endpoints (admin, login, api, etc.)
3. **Test** each discovered page for vulnerabilities
4. **Report** all findings

## Quick Start

### Basic Scan (Just provide the homepage!)

```bash
python autonomous_scan.py http://localhost/dvwa
```

### Deeper Scan

```bash
python autonomous_scan.py http://localhost/dvwa --depth 50 --episodes 5
```

### Use Specific Model

```bash
python autonomous_scan.py http://your-site.com --model checkpoints/dqn_checkpoint_ep100.pth
```

## What It Does

### Phase 1: Reconnaissance 🕷️

- Crawls from homepage
- Follows all internal links
- Discovers pages automatically
- Probes for common endpoints:
  - `/admin`, `/login`, `/api`
  - `/upload`, `/download`, `/config`
  - `/debug`, `/test`, `/.git`
  - And 10+ more common paths

### Phase 2: Vulnerability Testing 🔴

- Tests each discovered URL
- Uses your trained DQN agent
- Tries multiple attack vectors
- Records successful exploits

### Phase 3: Reporting 📊

- Generates `scan_report.md`
- Lists all discovered URLs
- Details found vulnerabilities
- Includes confidence levels

## Example Output

```
==================================================================
🤖 AUTONOMOUS SECURITY AGENT
==================================================================

📍 PHASE 1: RECONNAISSANCE
----------------------------------------------------------------------
🕷️  Starting reconnaissance on: http://localhost/dvwa
🎯 Target domain: localhost

📍 Crawling: http://localhost/dvwa
  ✅ Found 3 form(s)
  ✅ Found 8 input field(s)

📍 Crawling: http://localhost/dvwa/login.php
  ✅ Found 1 form(s)
  ✅ Found 2 input field(s)

✅ Reconnaissance complete!
📊 Discovered 15 unique URLs

🔍 Probing for common endpoints...
  ✅ Found: /admin
  ✅ Found: /api
  🔒 Forbidden: /config

🔴 PHASE 2: VULNERABILITY TESTING
----------------------------------------------------------------------

🎯 Testing: http://localhost/dvwa/login.php
  🚨 Found 1 potential vulnerability(ies)

🎯 Testing: http://localhost/dvwa/vulnerabilities/sqli/
  🚨 Found 2 potential vulnerability(ies)

==================================================================
📊 FINAL REPORT
==================================================================

Target: http://localhost/dvwa
Pages Discovered: 15
Vulnerabilities Found: 3

🔴 VULNERABILITIES:
  - http://localhost/dvwa/login.php
    Type: SQL Injection (Advanced)
    Confidence: High

  - http://localhost/dvwa/vulnerabilities/sqli/
    Type: SQL Injection
    Confidence: High

💾 Report saved to: scan_report.md
```

## Parameters

- `url` - **Required**: Target homepage URL
- `--model` - Path to trained model (default: `dqn_web_sec_model.pth`)
- `--depth` - Max pages to crawl (default: 30)
- `--episodes` - Test episodes per URL (default: 3)

## Features

✅ **Automatic Discovery** - No need to specify pages manually
✅ **Smart Crawling** - Only follows links on same domain
✅ **Endpoint Probing** - Checks common paths automatically
✅ **Multi-Episode Testing** - Tests each page multiple times
✅ **Confidence Scoring** - High/Medium based on reward
✅ **Report Generation** - Saves detailed markdown report

## Comparison

### Old Way (Manual)

```bash
# You had to specify each URL
python deploy_agent.py --target http://site.com/login
python deploy_agent.py --target http://site.com/admin
python deploy_agent.py --target http://site.com/api
# ... repeat for every page
```

### New Way (Autonomous)

```bash
# Just give the homepage!
python autonomous_scan.py http://site.com
```

## Tips

1. **Start Small**: Use `--depth 10` for quick scans
2. **Go Deep**: Use `--depth 100` for thorough scans
3. **Multiple Runs**: Run with different checkpoints to compare
4. **Review Reports**: Check `scan_report.md` for details

## Limitations

- Only crawls same domain (won't follow external links)
- Respects basic crawling etiquette (timeouts, error handling)
- Agent effectiveness depends on training quality
- Some pages may not be compatible with the environment

## Safety

⚠️ **ONLY USE ON:**

- Your own websites
- Systems you have permission to test
- Lab environments (DVWA, WebGoat, etc.)

🚫 **NEVER USE ON:**

- Production systems without authorization
- Third-party websites
- Any system you don't own

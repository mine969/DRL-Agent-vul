# Utility Modules

Helper functions and utilities for the DRL Security Agent.

## 📁 Modules

### `anti_forensics.py` (200+ lines)

**Anti-Forensics & Track Covering**

**Features**:

- Log manipulation
- Timestamp modification
- Evidence cleanup
- Stealth operations

### `log_cleaner.py` (190+ lines)

**Log Cleanup Utilities**

**Features**:

- Web server log cleaning
- Database log removal
- System log sanitization
- Selective entry deletion

### `proxy_fetcher.py` (230+ lines)

**Proxy Management**

**Features**:

- Fetch free proxies
- Validate proxy functionality
- Rotate proxies
- Update `proxies.txt`

### `report_generator.py` (500+ lines)

**Scan Report Generation**

**Features**:

- HTML reports
- JSON export
- Markdown summaries
- Vulnerability statistics
- Timeline visualization
- Captured flags and evidence snippets

### `target_hunter.py` (530+ lines)

**Target Discovery**

**Features**:

- Subdomain enumeration
- Port scanning
- Service detection
- Technology fingerprinting
- Shodan/Censys integration

### `vulnerability_database.py` (600+ lines)

**Vulnerability Database**

**Features**:

- CVE lookup
- Exploit database
- Vulnerability scoring
- Patch information
- Attack patterns

### `zero_day_hunter.py` (360+ lines)

**Zero-Day Discovery**

**Features**:

- Anomaly detection
- Fuzzing techniques
- Novel vulnerability discovery
- Pattern analysis

## 🎯 Usage Examples

### Report Generation

```python
from utils.report_generator import generate_report

findings = [...]
generate_report(findings, output_file="scan_report.html")
```

### Target Discovery

```python
from utils.target_hunter import discover_targets

targets = discover_targets("example.com")
print(f"Found {len(targets)} subdomains")
```

### Proxy Management

```python
from utils.proxy_fetcher import fetch_proxies

proxies = fetch_proxies(count=100)
# Proxies saved to ../proxies.txt
```

### Log Cleanup

```python
from utils.log_cleaner import clean_logs

clean_logs(target="192.168.1.100", log_type="apache")
```

## 📚 Related Files

- `../autonomous_scan.py` - Uses these utilities
- `../scanner_gui.py` - GUI integration
- `../proxies.txt` - Proxy list

## 🔗 Documentation

See individual module docstrings for detailed API documentation.

---

**Utility modules for advanced security operations** 🛠️
